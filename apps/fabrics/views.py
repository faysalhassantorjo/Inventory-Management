from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FabricPurchase
from .forms import FabricPurchaseForm
from django.core.paginator import Paginator

@login_required
def fabric_purchase_list(request):
    purchases = FabricPurchase.objects.all().order_by('-purchase_date', '-id')
    
    paginator = Paginator(purchases, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'fabrics/fabric_purchase_list.html', {'page_obj': page_obj})

@login_required
def fabric_purchase_add(request):
    if request.method == 'POST':
        form = FabricPurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            messages.success(request, 'Fabric purchase added successfully.')
            return redirect('purchasing:fabric_purchase_list')
    else:
        form = FabricPurchaseForm()
    
    return render(request, 'fabrics/fabric_purchase_form.html', {
        'form': form,
        'title': 'Add Fabric Purchase'
    })

@login_required
def fabric_purchase_edit(request, pk):
    purchase = get_object_or_404(FabricPurchase, pk=pk)
    if request.method == 'POST':
        form = FabricPurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fabric purchase updated successfully.')
            return redirect('purchasing:fabric_purchase_list')
    else:
        form = FabricPurchaseForm(instance=purchase)
    
    return render(request, 'fabrics/fabric_purchase_form.html', {
        'form': form,
        'title': 'Edit Fabric Purchase',
        'purchase': purchase
    })
