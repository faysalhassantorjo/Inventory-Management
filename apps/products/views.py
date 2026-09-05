from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction

from .models import Category, Product, ProductSpecification, ProductImage, Discount
from .forms import CategoryForm, ProductForm, DiscountForm


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@login_required
def product_list(request):
    qs = Product.objects.select_related('category').prefetch_related('specifications')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(specifications__sku__icontains=query)
        ).distinct()
    if category_id:
        qs = qs.filter(category_id=category_id)
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.filter(is_active=True).order_by('name')

    template = 'products/partials/product_table.html' if request.headers.get('HX-Request') else 'products/product_list.html'
    return render(request, template, {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'status': status,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('specifications', 'images'),
        pk=pk
    )
    specs = product.specifications.all()
    images = product.images.all()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'specs': specs,
        'images': images,
    })


@login_required
def product_create(request):

    if request.method == "POST":

        product_form = ProductForm(
            request.POST,
            request.FILES,
        )

        discount_form = DiscountForm(
            request.POST,
            prefix="discount",
        )

        # -------------------------------------------------
        # The discount section is optional. Whether the user
        # wants a discount is decided from whether they typed
        # anything into the percentage field at all - we never
        # call int() on a value that might be blank, and we
        # never require discount_form to validate when no
        # discount was requested.
        # -------------------------------------------------

        discount_percentage_raw = request.POST.get("discount-percentage", "").strip()
        wants_discount = bool(discount_percentage_raw)

        discount_valid = True
        if wants_discount:
            discount_valid = discount_form.is_valid()

        if product_form.is_valid() and discount_valid:

            with transaction.atomic():

                # -----------------------------------------
                # Product
                # -----------------------------------------

                product = product_form.save()

                # -----------------------------------------
                # Specifications / Sizes
                # -----------------------------------------

                sizes = request.POST.getlist("size[]")

                for i, size in enumerate(sizes):

                    size = size.strip()

                    if not size:
                        continue

                    m_keys = request.POST.getlist(f"mkey_{i}[]")
                    m_vals = request.POST.getlist(f"mval_{i}[]")

                    measurements = {}

                    for key, value in zip(m_keys, m_vals):
                        key = key.strip()
                        value = value.strip()
                        if key:
                            measurements[key] = value

                    ProductSpecification.objects.create(
                        product=product,
                        size=size,
                        measurements=measurements,
                    )

                # -----------------------------------------
                # Additional Images
                # -----------------------------------------

                for image_file in request.FILES.getlist("additional_images"):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                    )

                # -----------------------------------------
                # Discount
                # -----------------------------------------

                if wants_discount:
                    discount = discount_form.save(commit=False)
                    discount.product = product
                    discount.save()

            messages.success(
                request,
                f'Product "{product.name}" created successfully.'
            )

            return redirect("products:product_detail", pk=product.pk)

    else:

        product_form = ProductForm()
        discount_form = DiscountForm(prefix="discount")

    return render(
        request,
        "products/product_form.html",
        {
            "form": product_form,
            "discount_form": discount_form,
            "title": "Create Product",
        },
    )


@login_required
def product_edit(request, pk):

    product = get_object_or_404(Product, pk=pk)

    try:
        existing_discount = product.discount
    except Discount.DoesNotExist:
        existing_discount = None

    if request.method == "POST":

        product_form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        discount_form = DiscountForm(
            request.POST,
            instance=existing_discount,
            prefix="discount",
        )

        discount_percentage_raw = request.POST.get("discount-percentage", "").strip()
        wants_discount = bool(discount_percentage_raw)

        discount_valid = True
        if wants_discount:
            discount_valid = discount_form.is_valid()

        if product_form.is_valid() and discount_valid:

            with transaction.atomic():

                # -----------------------------------------
                # Product
                # -----------------------------------------

                product = product_form.save()

                # -----------------------------------------
                # Additional Images
                # -----------------------------------------

                for image_file in request.FILES.getlist("additional_images"):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                    )

                # -----------------------------------------
                # Discount
                # -----------------------------------------

                if wants_discount:
                    discount = discount_form.save(commit=False)
                    discount.product = product
                    discount.save()
                elif existing_discount:
                    # Percentage left blank -> user wants the
                    # existing discount removed.
                    existing_discount.delete()

            messages.success(request, "Product updated successfully.")

            return redirect("products:product_detail", pk=product.pk)

    else:

        product_form = ProductForm(instance=product)
        discount_form = DiscountForm(instance=existing_discount, prefix="discount")

    return render(
        request,
        "products/product_form.html",
        {
            "form": product_form,
            "discount_form": discount_form,
            "title": "Edit Product",
            "product": product,
        },
    )


@login_required
def product_archive(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        state = 'activated' if product.is_active else 'archived'
        messages.success(request, f'Product "{product.name}" {state}.')
    return redirect('products:product_detail', pk=product.pk)


# ---------------------------------------------------------------------------
# HTMX helpers – specification form row
# ---------------------------------------------------------------------------

@login_required
@require_GET
def htmx_spec_row(request):
    """Return an empty specification form row (for 'Add Another Size')."""
    index = int(request.GET.get('index', 0))
    return render(request, 'products/partials/spec_row.html', {'index': index})