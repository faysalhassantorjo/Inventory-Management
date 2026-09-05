"""
Inventory service layer.

All stock-changing operations must go through this module so that:
  - Every change is logged to InventoryMovement.
  - Stock validation happens server-side.
  - Operations are wrapped in atomic transactions.
"""

from django.db import transaction
from .models import InventoryMovement
from apps.products.models import ProductSpecification


class InsufficientStockError(Exception):
    """Raised when an operation would result in negative stock."""


@transaction.atomic
def record_production(spec: ProductSpecification, *, quantity: int, reference: str = "", user=None) -> InventoryMovement:
    """Record finished-goods production for a SKU, increasing stock."""
    if quantity <= 0:
        raise ValueError("Production quantity must be a positive integer.")

    # Use select_for_update to serialize writes (effective on PostgreSQL;
    # on SQLite the transaction-level lock achieves the same result).
    spec = ProductSpecification.objects.select_for_update().get(pk=spec.pk)
    spec.stock += quantity
    spec.save(update_fields=['stock', 'updated_at'])

    return InventoryMovement.objects.create(
        sku=spec,
        quantity_change=quantity,
        movement_type='PRODUCTION',
        reference_id=reference,
        reason="Production batch",
        user=user,
    )


@transaction.atomic
def record_adjustment(spec: ProductSpecification, *, quantity_change: int, reason: str, user=None) -> InventoryMovement:
    """Apply a manual stock adjustment (positive or negative)."""
    if quantity_change == 0:
        raise ValueError("Adjustment quantity cannot be zero.")

    spec = ProductSpecification.objects.select_for_update().get(pk=spec.pk)
    new_stock = spec.stock + quantity_change
    if new_stock < 0:
        raise InsufficientStockError(
            f"Adjustment would result in negative stock for {spec.sku}. "
            f"Current: {spec.stock}, change: {quantity_change}."
        )

    spec.stock = new_stock
    spec.save(update_fields=['stock', 'updated_at'])

    return InventoryMovement.objects.create(
        sku=spec,
        quantity_change=quantity_change,
        movement_type='ADJUSTMENT',
        reason=reason,
        user=user,
    )
