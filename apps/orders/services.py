"""
Orders service layer.

Handles order confirmation (stock deduction) and cancellation (stock restoration).
All operations are atomic and auditable.
"""

from django.db import transaction
from apps.inventory.models import InventoryMovement
from apps.products.models import ProductSpecification


class InsufficientStockError(Exception):
    """Raised when an order item requires more stock than available."""


class OrderStatusError(Exception):
    """Raised when an operation is attempted on an order in an incompatible status."""


@transaction.atomic
def confirm_order(order, *, user=None):
    """
    Confirm an order: validate stock across all items, deduct from each SKU,
    and write inventory movement records.  Rolls back atomically on any failure.
    """
    from .models import Order  # avoid circular at module level

    if order.status not in ('DRAFT', 'PENDING'):
        raise OrderStatusError(
            f"Cannot confirm an order with status '{order.status}'. "
            "Only DRAFT or PENDING orders can be confirmed."
        )

    items = list(order.items.select_related('sku').all())

    total = 0
    # --- Validate all items first (no writes yet) ---
    for item in items:
        spec = ProductSpecification.objects.select_for_update().get(pk=item.sku_id)
        if spec.stock < item.quantity:
            raise InsufficientStockError(
                f"Not enough stock for {spec.sku}. "
                f"Available: {spec.stock}, requested: {item.quantity}."
            )

    # --- All OK: deduct stock and write movements ---
    for item in items:
        spec = ProductSpecification.objects.select_for_update().get(pk=item.sku_id)
        spec.stock -= item.quantity
        spec.save(update_fields=['stock', 'updated_at'])

        item_total = item.quantity * item.sold_price
        total += item_total
        
        InventoryMovement.objects.create(
            sku=spec,
            quantity_change=-item.quantity,
            movement_type='ORDER',
            reference_id=f"Order #{order.pk}",
            reason="Order confirmed",
            user=user,
        )

    order.status = 'CONFIRMED'
    order.total_price = total
    order.save(update_fields=['status', 'total_price', 'updated_at'])
    return order


@transaction.atomic
def cancel_order(order, *, user=None, reason: str = "Order cancelled"):
    """
    Cancel a confirmed order and restore its inventory movements.
    Only confirmed orders trigger stock restoration.
    """
    from .models import Order

    if order.status == 'CANCELLED':
        raise OrderStatusError("Order is already cancelled.")

    stock_was_deducted = order.status in ('CONFIRMED', 'PROCESSING', 'SHIPPED')

    if stock_was_deducted:
        items = list(order.items.select_related('sku').all())
        for item in items:
            spec = ProductSpecification.objects.select_for_update().get(pk=item.sku_id)
            spec.stock += item.quantity
            spec.save(update_fields=['stock', 'updated_at'])

            InventoryMovement.objects.create(
                sku=spec,
                quantity_change=item.quantity,
                movement_type='RETURN',
                reference_id=f"Order #{order.pk} cancelled",
                reason=reason,
                user=user,
            )

    order.status = 'CANCELLED'
    order.save(update_fields=['status', 'updated_at'])
    return order
