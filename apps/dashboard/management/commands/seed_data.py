from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.products.models import Category, Product, ProductSpecification
from apps.inventory.models import InventoryMovement
from apps.suppliers.models import Supplier
from apps.fabrics.models import FabricPurchase
from apps.orders.models import Customer, Order, OrderItem
import datetime
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Customer.objects.all().delete()
        FabricPurchase.objects.all().delete()
        Supplier.objects.all().delete()
        InventoryMovement.objects.all().delete()
        ProductSpecification.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Users
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        # Categories
        cat_kurti = Category.objects.create(name="Kurti")
        cat_saree = Category.objects.create(name="Saree")
        cat_top = Category.objects.create(name="Top")

        # Products & Specs
        p1 = Product.objects.create(name="Eid Premium Kurti", category=cat_kurti, description="Premium Eid collection")
        spec1 = ProductSpecification.objects.create(product=p1, size="36", measurements={"Length": "35", "Width": "40", "Sleeve": "22"}, stock=0)
        spec2 = ProductSpecification.objects.create(product=p1, size="38", measurements={"Length": "36", "Width": "42", "Sleeve": "22.5"}, stock=0)
        
        p2 = Product.objects.create(name="Classic Cotton Kurti", category=cat_kurti, description="Everyday classic")
        spec3 = ProductSpecification.objects.create(product=p2, size="M", measurements={"Length": "40", "Chest": "38"}, stock=0)

        p3 = Product.objects.create(name="Elegant Silk Saree", category=cat_saree, description="Beautiful silk saree")
        spec4 = ProductSpecification.objects.create(product=p3, size="Free Size", measurements={"Length": "5.5 meters", "Width": "1.2 meters"}, stock=0)

        # Suppliers
        sup1 = Supplier.objects.create(name="Dhaka Fabrics Ltd", phone="01711223344", address="Gulshan, Dhaka")
        sup2 = Supplier.objects.create(name="Narayanganj Textiles", phone="01811223344", address="Narayanganj")

        # Fabric Purchases
        FabricPurchase.objects.create(supplier=sup1, fabric_name="Premium Silk", color="Red", quantity=Decimal('500'), unit="Meters", unit_price=Decimal('250.00'), total_price=Decimal('125000.00'), purchase_date=datetime.date.today())
        FabricPurchase.objects.create(supplier=sup2, fabric_name="Cotton Block Print", color="Blue/White", quantity=Decimal('1000'), unit="Yards", unit_price=Decimal('80.00'), total_price=Decimal('80000.00'), purchase_date=datetime.date.today())

        # Production (Inventory Movements)
        def add_stock(spec, qty, ref):
            spec.stock += qty
            spec.save()
            InventoryMovement.objects.create(
                sku=spec,
                quantity_change=qty,
                movement_type='PRODUCTION',
                reference_id=ref,
                reason="Initial production batch",
                user=admin_user
            )

        add_stock(spec1, 50, "PROD-001")
        add_stock(spec2, 30, "PROD-001")
        add_stock(spec3, 100, "PROD-002")
        add_stock(spec4, 25, "PROD-003")

        # Customers
        cust1 = Customer.objects.create(name="Ayesha Rahman", phone="01900000001", address="Dhanmondi, Dhaka")
        cust2 = Customer.objects.create(name="Farhana Islam", phone="01900000002", address="Banani, Dhaka")

        # Orders
        def create_order(customer, items_dict, status):
            order = Order.objects.create(customer=customer, status=status, created_by=admin_user)
            for spec, qty in items_dict.items():
                OrderItem.objects.create(order=order, sku=spec, quantity=qty)
                if status in ['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']:
                    spec.stock -= qty
                    spec.save()
                    InventoryMovement.objects.create(
                        sku=spec,
                        quantity_change=-qty,
                        movement_type='ORDER',
                        reference_id=f"Order #{order.id}",
                        user=admin_user
                    )
            return order

        create_order(cust1, {spec1: 2, spec4: 1}, 'DELIVERED')
        create_order(cust2, {spec2: 1, spec3: 3}, 'CONFIRMED')
        create_order(cust1, {spec3: 1}, 'PENDING')

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))
