from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.products.models import Product, ProductSpecification
from apps.orders.models import Order
from apps.inventory.models import InventoryMovement
from apps.fabrics.models import FabricPurchase


@login_required
def dashboard_view(request):

    total_products = Product.objects.count()

    total_skus = ProductSpecification.objects.count()

    total_units_in_stock = (
        ProductSpecification.objects.aggregate(
            total=Sum('stock')
        )['total'] or 0
    )

    out_of_stock = ProductSpecification.objects.filter(
        stock__lte=5
    ).count()

    pending_orders_count = Order.objects.filter(
        status='PENDING'
    ).count()

    recent_orders = Order.objects.order_by('-created_at')[:5]

    recent_movements = InventoryMovement.objects.order_by(
        '-created_at'
    )[:5]

    recent_fabric = FabricPurchase.objects.order_by(
        '-purchase_date'
    )[:5]

    # -----------------------------
    # Last 7 days sales
    # -----------------------------

    today = timezone.localdate()
    start_date = today - timezone.timedelta(days=6)

    sales_by_day = (
        Order.objects
        .filter(
            status='CONFIRMED',
            created_at__date__gte=start_date,
            created_at__date__lte=today,
        )
        .annotate(
            date=TruncDate('created_at')
        )
        .values('date')
        .annotate(
            sales=Sum('total_price')
        )
        .order_by('date')
    )

    # Convert queryset into dictionary
    sales_dict = {
        item['date']: item['sales'] or 0
        for item in sales_by_day
    }

    # Create all 7 days, including days with no sales
    sales_chart = []

    for i in range(7):
        date = start_date + timezone.timedelta(days=i)

        sales_chart.append({
            'date': date.strftime('%b %d'),
            'sales': float(sales_dict.get(date, 0)),
        })

    context = {
        'total_products': total_products,
        'total_skus': total_skus,
        'total_units_in_stock': total_units_in_stock,
        'out_of_stock': out_of_stock,
        'pending_orders_count': pending_orders_count,
        'recent_orders': recent_orders,
        'recent_movements': recent_movements,
        'recent_fabric': recent_fabric,

        # Chart data
        'sales_chart': sales_chart,
    }

    return render(request, 'dashboard/index.html', context)