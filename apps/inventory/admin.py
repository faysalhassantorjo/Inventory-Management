from django.contrib import admin
from .models import InventoryMovement

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('sku', 'quantity_change', 'movement_type', 'reference_id', 'created_at')
