from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import InventoryMovement
from apps.products.models import ProductSpecification
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages

@login_required
def movement_list(request):
    movements = InventoryMovement.objects.all().order_by('-created_at')
    
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/movement_list.html', {
        'page_obj': page_obj
    })

@login_required
@transaction.atomic
def production_create(request):
    if request.method == 'POST':
        sku_id = request.POST.get('sku')
        quantity = int(request.POST.get('quantity', 0))
        reference = request.POST.get('reference', '')
        
        if quantity > 0 and sku_id:
            spec = ProductSpecification.objects.select_for_update().get(id=sku_id)
            spec.stock += quantity
            spec.save()
            
            InventoryMovement.objects.create(
                sku=spec,
                quantity_change=quantity,
                movement_type='PRODUCTION',
                reference_id=reference,
                reason="Production batch",
                user=request.user
            )
            messages.success(request, f'Successfully recorded production of {quantity} for {spec.sku}.')
            return redirect('inventory:movement_list')
            
    skus = ProductSpecification.objects.filter(product__is_active=True)
    return render(request, 'inventory/production_form.html', {'skus': skus})

@login_required
@transaction.atomic
def adjustment_create(request):
    if request.method == 'POST':
        sku_id = request.POST.get('sku')
        quantity_change = int(request.POST.get('quantity_change', 0))
        reason = request.POST.get('reason', '')
        
        if quantity_change != 0 and sku_id:
            spec = ProductSpecification.objects.select_for_update().get(id=sku_id)
            if spec.stock + quantity_change < 0:
                messages.error(request, 'Adjustment would result in negative stock.')
            else:
                spec.stock += quantity_change
                spec.save()
                
                InventoryMovement.objects.create(
                    sku=spec,
                    quantity_change=quantity_change,
                    movement_type='ADJUSTMENT',
                    reason=reason,
                    user=request.user
                )
                messages.success(request, f'Successfully adjusted stock for {spec.sku}.')
                return redirect('inventory:movement_list')

    skus = ProductSpecification.objects.filter(product__is_active=True)
    return render(request, 'inventory/adjustment_form.html', {'skus': skus})
