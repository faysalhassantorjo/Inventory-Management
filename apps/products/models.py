from django.db import models, transaction
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/', blank=True, null=True
    )

    # Original/catalog price
    base_price = models.PositiveIntegerField(default=1000)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        return sum(spec.stock for spec in self.specifications.all())

    @property
    def active_discount(self):
        """
        Return the currently active discount for this product, or None.

        "Active" requires all three:
          - a Discount row exists (OneToOne -> at most one ever),
          - its is_active flag is True,
          - now falls within [starts_at, ends_at].

        (Previously this only checked existence, so an expired,
        future, or manually-disabled discount still applied to price.)
        """
        try:
            discount = self.discount
        except Discount.DoesNotExist:
            return None

        now = timezone.now()
        if discount.is_active and discount.starts_at <= now <= discount.ends_at:
            return discount
        return None

    @property
    def price(self):
        discount = self.active_discount

        if not discount:
            return self.base_price

        discount_amount = (
            Decimal(self.base_price) * discount.percentage
        ) / Decimal("100")

        discounted = Decimal(self.base_price) - discount_amount
        return int(discounted.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='products/images/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class SKUSequence(models.Model):
    """Singleton table to safely generate sequential SKUs under SQLite."""
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(id=1),
                name='sku_sequence_singleton',
            )
        ]

    @classmethod
    def next_sku(cls):
        """
        Atomically increment and return the next SKU string.
        Uses select_for_update where supported (PostgreSQL); on SQLite the
        transaction itself serialises concurrent writes.
        """
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(id=1)
            seq.last_number += 1
            seq.save(update_fields=['last_number'])
            return f"SKU{seq.last_number:04d}"


class ProductSpecification(models.Model):
    """
    Represents a single sellable size/variant of a Product.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='specifications'
    )
    size = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True, editable=False)
    measurements = models.JSONField(default=dict, blank=True)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name='spec_stock_non_negative',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = SKUSequence.next_sku()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} – {self.size} ({self.sku})"


class Discount(models.Model):
    """
    Time-limited percentage discount for a product.

    Example:
        Product: Eid Premium Kurti
        Percentage: 30%
        Starts: 2026-09-01
        Ends: 2026-09-10
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="discount",
    )

    percentage = models.PositiveIntegerField(default=0)

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]

        indexes = [
            models.Index(
                fields=["product", "is_active", "starts_at", "ends_at"]
            ),
        ]

    def clean(self):
        if self.percentage <= 0:
            raise ValidationError(
                {"percentage": "Discount must be greater than 0%."}
            )

        if self.percentage > 100:
            raise ValidationError(
                {"percentage": "Discount cannot exceed 100%."}
            )

        if self.starts_at >= self.ends_at:
            raise ValidationError(
                {
                    "ends_at": (
                        "End date/time must be after "
                        "the start date/time."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.percentage}%"