from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Order, Customer, OrderItem
from .services import confirm_order, cancel_order, InsufficientStockError, OrderStatusError
from apps.products.models import ProductSpecification


@login_required
def order_list(request):
    qs = Order.objects.select_related('customer').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    if query:
        qs = qs.filter(
            Q(customer__name__icontains=query) |
            Q(customer__phone__icontains=query) |
            Q(id__icontains=query)
        )
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'orders/order_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'created_by').prefetch_related('items__sku__product'),
        pk=pk
    )
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_confirm_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        try:
            confirm_order(order, user=request.user)
            messages.success(request, f'Order #{order.pk} confirmed and stock deducted.')
        except InsufficientStockError as e:
            messages.error(request, str(e))
        except OrderStatusError as e:
            messages.error(request, str(e))
    return redirect('orders:order_detail', pk=pk)


@login_required
def order_cancel_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Order cancelled')
        try:
            cancel_order(order, user=request.user, reason=reason)
            messages.success(request, f'Order #{order.pk} cancelled.')
        except OrderStatusError as e:
            messages.error(request, str(e))
    return redirect('orders:order_detail', pk=pk)


@login_required
def order_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        notes = request.POST.get('notes', '').strip()

        # Get customer or create new
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_email = request.POST.get('customer_phone', '').strip()
        customer_address = request.POST.get('customer_phone', '').strip()

        if customer_id:
            customer = get_object_or_404(Customer, pk=customer_id)
        elif customer_name:
            customer = Customer.objects.create(name=customer_name, phone=customer_phone)
            customer.email = customer_email
            customer.address = customer_address
            customer.save()
        else:
            messages.error(request, 'Please select or enter a customer.')
            return redirect('orders:order_create')

        order = Order.objects.create(
            customer=customer,
            status='DRAFT',
            notes=notes,
            created_by=request.user,
        )

        # Parse order items
        sku_ids = request.POST.getlist('sku_id[]')
        quantities = request.POST.getlist('quantity[]')
        for sku_id, qty in zip(sku_ids, quantities):
            try:
                qty = int(qty)
                spec = ProductSpecification.objects.get(pk=sku_id)
                if qty > 0:
                    OrderItem.objects.create(order=order, sku=spec, quantity=qty)
            except (ValueError, ProductSpecification.DoesNotExist):
                continue

        messages.success(request, f'Order #{order.pk} created as Draft.')
        return redirect('orders:order_detail', pk=order.pk)

    customers = Customer.objects.order_by('name')
    skus = ProductSpecification.objects.select_related('product').filter(product__is_active=True).order_by('product__name', 'size')
    return render(request, 'orders/order_form.html', {
        'customers': customers,
        'skus': skus,
    })

from django.db.models import Count
@login_required
def customer_list(request):
    query = request.GET.get('q', '').strip()
    qs = Customer.objects.annotate(
        order_count=Count('orders')
    ).order_by('name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'orders/customer_list.html', {
        'page_obj': page_obj,
        'query': query,
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.order_by('-created_at')
    return render(request, 'orders/customer_details.html', {
        'customer': customer,
        'orders': orders,
    })
