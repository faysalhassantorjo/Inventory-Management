from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.products.models import Category, Product, ProductSpecification, SKUSequence
from apps.inventory.models import InventoryMovement
from apps.orders.models import Customer, Order, OrderItem

User = get_user_model()


# ===========================================================================
# Helper Factories
# ===========================================================================

def make_category(name="Kurti"):
    return Category.objects.create(name=name)


def make_product(category=None, name="Eid Premium Kurti"):
    if category is None:
        category = make_category()
    return Product.objects.create(name=name, category=category)


def make_spec(product=None, size="36", stock=10, measurements=None):
    if product is None:
        product = make_product()
    return ProductSpecification.objects.create(
        product=product,
        size=size,
        stock=stock,
        measurements=measurements or {"Length": "35", "Width": "40"},
    )


def make_user(username="admin", is_staff=True, is_superuser=True):
    return User.objects.create_user(username=username, password="test1234", is_staff=is_staff, is_superuser=is_superuser)


# ===========================================================================
# Product & SKU Tests
# ===========================================================================

class SKUGenerationTest(TestCase):
    def test_sku_auto_generated(self):
        spec = make_spec()
        self.assertTrue(spec.sku.startswith("SKU"))

    def test_sku_globally_unique(self):
        s1 = make_spec(size="36")
        s2 = make_spec(size="38")
        self.assertNotEqual(s1.sku, s2.sku)

    def test_sku_sequential_format(self):
        # Reset sequence
        SKUSequence.objects.all().delete()
        p = make_product()
        s1 = ProductSpecification.objects.create(product=p, size="36", stock=0)
        s2 = ProductSpecification.objects.create(product=p, size="38", stock=0)
        n1 = int(s1.sku.replace("SKU", ""))
        n2 = int(s2.sku.replace("SKU", ""))
        self.assertEqual(n2, n1 + 1)

    def test_sku_not_changed_on_update(self):
        spec = make_spec()
        original_sku = spec.sku
        spec.stock = 999
        spec.save()
        spec.refresh_from_db()
        self.assertEqual(spec.sku, original_sku)


class ProductModelTest(TestCase):
    def test_product_creation(self):
        cat = make_category()
        product = Product.objects.create(name="Test Kurti", category=cat)
        self.assertEqual(product.name, "Test Kurti")
        self.assertTrue(product.is_active)

    def test_product_total_stock(self):
        p = make_product()
        make_spec(product=p, size="36", stock=10)
        make_spec(product=p, size="38", stock=7)
        make_spec(product=p, size="40", stock=4)
        self.assertEqual(p.total_stock, 21)

    def test_multiple_specs_on_product(self):
        p = make_product()
        for size in ["36", "38", "40", "42"]:
            make_spec(product=p, size=size, stock=5)
        self.assertEqual(p.specifications.count(), 4)

    def test_custom_measurements_stored(self):
        measurements = {"Length": "35", "Width": "40", "Sleeve": "22", "Shoulder": "15"}
        spec = make_spec(measurements=measurements)
        spec.refresh_from_db()
        self.assertEqual(spec.measurements["Sleeve"], "22")
        self.assertEqual(spec.measurements["Shoulder"], "15")

    def test_stock_cannot_be_negative_at_db_level(self):
        spec = make_spec(stock=5)
        with self.assertRaises(Exception):
            spec.stock = -1
            spec.save()
            # Force check constraint evaluation
            ProductSpecification.objects.get(pk=spec.pk)

    def test_category_slug_auto_generated(self):
        cat = Category.objects.create(name="Premium Kurti")
        self.assertEqual(cat.slug, "premium-kurti")

    def test_category_slug_unique(self):
        Category.objects.create(name="Kurti")
        cat2 = Category.objects.create(name="Kurti")
        self.assertNotEqual(cat2.slug, "kurti")
        self.assertTrue(cat2.slug.startswith("kurti-"))


# ===========================================================================
# Inventory Tests
# ===========================================================================

class InventoryTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.spec = make_spec(stock=10)

    def test_production_increases_stock(self):
        from apps.inventory.services import record_production
        record_production(self.spec, quantity=20, reference="BATCH-001", user=self.user)
        self.spec.refresh_from_db()
        self.assertEqual(self.spec.stock, 30)

    def test_production_creates_movement_record(self):
        from apps.inventory.services import record_production
        record_production(self.spec, quantity=20, reference="BATCH-001", user=self.user)
        movement = InventoryMovement.objects.get(sku=self.spec, movement_type='PRODUCTION')
        self.assertEqual(movement.quantity_change, 20)
        self.assertEqual(movement.user, self.user)

    def test_adjustment_changes_stock(self):
        from apps.inventory.services import record_adjustment
        record_adjustment(self.spec, quantity_change=-3, reason="Damaged", user=self.user)
        self.spec.refresh_from_db()
        self.assertEqual(self.spec.stock, 7)

    def test_adjustment_creates_movement_record(self):
        from apps.inventory.services import record_adjustment
        record_adjustment(self.spec, quantity_change=-3, reason="Damaged", user=self.user)
        movement = InventoryMovement.objects.get(sku=self.spec, movement_type='ADJUSTMENT')
        self.assertEqual(movement.quantity_change, -3)
        self.assertEqual(movement.reason, "Damaged")

    def test_adjustment_prevents_negative_stock(self):
        from apps.inventory.services import record_adjustment, InsufficientStockError
        with self.assertRaises(InsufficientStockError):
            record_adjustment(self.spec, quantity_change=-20, reason="Test", user=self.user)


# ===========================================================================
# Order Tests
# ===========================================================================

class OrderTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.customer = Customer.objects.create(name="Ayesha Rahman", phone="01900000001")
        self.spec = make_spec(stock=10)

    def test_order_creation(self):
        order = Order.objects.create(customer=self.customer, status='DRAFT', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=2)
        self.assertEqual(order.items.count(), 1)

    def test_order_confirmation_deducts_stock(self):
        from apps.orders.services import confirm_order
        order = Order.objects.create(customer=self.customer, status='PENDING', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=3)
        confirm_order(order, user=self.user)
        self.spec.refresh_from_db()
        self.assertEqual(self.spec.stock, 7)

    def test_order_confirmation_creates_movement(self):
        from apps.orders.services import confirm_order
        order = Order.objects.create(customer=self.customer, status='PENDING', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=3)
        confirm_order(order, user=self.user)
        movement = InventoryMovement.objects.get(sku=self.spec, movement_type='ORDER')
        self.assertEqual(movement.quantity_change, -3)

    def test_order_validation_insufficient_stock(self):
        from apps.orders.services import confirm_order, InsufficientStockError
        order = Order.objects.create(customer=self.customer, status='PENDING', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=100)
        with self.assertRaises(InsufficientStockError):
            confirm_order(order, user=self.user)

    def test_order_double_confirm_prevented(self):
        from apps.orders.services import confirm_order, OrderStatusError
        order = Order.objects.create(customer=self.customer, status='CONFIRMED', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=1)
        with self.assertRaises(OrderStatusError):
            confirm_order(order, user=self.user)

    def test_confirmed_order_has_status_confirmed(self):
        from apps.orders.services import confirm_order
        order = Order.objects.create(customer=self.customer, status='PENDING', created_by=self.user)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=2)
        confirm_order(order, user=self.user)
        order.refresh_from_db()
        self.assertEqual(order.status, 'CONFIRMED')

    def test_multiple_order_items(self):
        order = Order.objects.create(customer=self.customer, status='DRAFT', created_by=self.user)
        spec2 = make_spec(product=self.spec.product, size="38", stock=5)
        OrderItem.objects.create(order=order, sku=self.spec, quantity=2)
        OrderItem.objects.create(order=order, sku=spec2, quantity=1)
        self.assertEqual(order.items.count(), 2)


# ===========================================================================
# Permissions / Access Tests
# ===========================================================================

class PermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = make_user(username="admin")
        self.anonymous_protected_urls = [
            '/products/',
            '/inventory/movements/',
            '/orders/',
            '/purchasing/suppliers/',
        ]

    def test_anonymous_redirected_to_login(self):
        for url in self.anonymous_protected_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [301, 302], msg=f"Expected redirect for {url}")

    def test_admin_can_access_products(self):
        self.client.login(username="admin", password="test1234")
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_dashboard(self):
        self.client.login(username="admin", password="test1234")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


# ===========================================================================
# Supplier & Fabric Tests
# ===========================================================================

class FabricTest(TestCase):
    def setUp(self):
        self.user = make_user()
        from apps.suppliers.models import Supplier
        self.supplier = Supplier.objects.create(name="Dhaka Fabrics Ltd", phone="01711223344")

    def test_supplier_creation(self):
        from apps.suppliers.models import Supplier
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(self.supplier.name, "Dhaka Fabrics Ltd")

    def test_fabric_purchase_creation(self):
        from apps.fabrics.models import FabricPurchase
        import datetime
        from decimal import Decimal
        purchase = FabricPurchase.objects.create(
            supplier=self.supplier,
            fabric_name="Premium Silk",
            color="Red",
            quantity=Decimal("500.00"),
            unit="Meters",
            unit_price=Decimal("250.00"),
            total_price=Decimal("125000.00"),
            purchase_date=datetime.date.today(),
            created_by=self.user,
        )
        self.assertEqual(purchase.fabric_name, "Premium Silk")
        self.assertEqual(purchase.total_price, Decimal("125000.00"))

    def test_fabric_purchase_linked_to_supplier(self):
        from apps.fabrics.models import FabricPurchase
        import datetime
        from decimal import Decimal
        FabricPurchase.objects.create(
            supplier=self.supplier,
            fabric_name="Cotton",
            quantity=Decimal("100"),
            unit="Yards",
            unit_price=Decimal("80"),
            total_price=Decimal("8000"),
            purchase_date=datetime.date.today(),
        )
        self.assertEqual(self.supplier.fabric_purchases.count(), 1)
