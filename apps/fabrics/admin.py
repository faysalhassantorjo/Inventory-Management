from django.contrib import admin
from .models import FabricPurchase

@admin.register(FabricPurchase)
class FabricPurchaseAdmin(admin.ModelAdmin):
    list_display = ('fabric_name', 'supplier', 'quantity', 'unit_price', 'total_price', 'purchase_date')
