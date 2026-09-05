from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),

    # Products
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/archive/', views.product_archive, name='product_archive'),

    # HTMX helpers
    path('htmx/spec-row/', views.htmx_spec_row, name='htmx_spec_row'),
]
