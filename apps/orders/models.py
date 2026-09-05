from django.db import models
from django.conf import settings
from apps.products.models import ProductSpecification

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True)
    total_price = models.PositiveIntegerField(default=0)  # Total price of the order
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku = models.ForeignKey(ProductSpecification, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    sold_price = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"{self.quantity} x {self.sku.sku} for Order #{self.order.id}"
    
    def save(self, *args, **kwargs):
        if not self.sold_price:
            self.sold_price = self.sku.product.price
        super().save(*args, **kwargs)
