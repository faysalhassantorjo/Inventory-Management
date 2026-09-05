from django.db import models
from django.conf import settings
from apps.products.models import ProductSpecification

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = (
        ('PRODUCTION', 'Production'),
        ('ORDER', 'Order'),
        ('RETURN', 'Return'),
        ('ADJUSTMENT', 'Adjustment'),
    )
    
    sku = models.ForeignKey(ProductSpecification, on_delete=models.PROTECT, related_name='movements')
    quantity_change = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference_id = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Order # or Production #")
    reason = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.quantity_change > 0 else ""
        return f"{self.sku.sku} {sign}{self.quantity_change} ({self.movement_type})"
