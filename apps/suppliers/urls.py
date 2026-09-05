from django.urls import path
from apps.suppliers import views as supplier_views
from apps.fabrics import views as fabric_views

app_name = 'purchasing'
urlpatterns = [
    path('suppliers/', supplier_views.supplier_list, name='supplier_list'),
    path('suppliers/add/', supplier_views.supplier_add, name='supplier_add'),
    path('suppliers/<int:pk>/edit/', supplier_views.supplier_edit, name='supplier_edit'),
    
    path('fabric-purchases/', fabric_views.fabric_purchase_list, name='fabric_purchase_list'),
    path('fabric-purchases/add/', fabric_views.fabric_purchase_add, name='fabric_purchase_add'),
    path('fabric-purchases/<int:pk>/edit/', fabric_views.fabric_purchase_edit, name='fabric_purchase_edit'),
]
