from django.db import models
from django.conf import settings
from apps.suppliers.models import Supplier

class FabricPurchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='fabric_purchases')
    fabric_name = models.CharField(max_length=255)
    color = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fabric_name} from {self.supplier.name}"
