from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification, Discount

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    inlines = [ProductSpecificationInline, ProductImageInline, DiscountInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'thumbnail', 'base_price', 'is_active')
        }),
        # ('Timestamps', {
        #     'fields': ('created_at', 'updated_at'),
        #     'classes': ('collapse',),
        # }),
    )
