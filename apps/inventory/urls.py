from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('movements/', views.movement_list, name='movement_list'),
    path('production/create/', views.production_create, name='production_create'),
    path('adjustments/create/', views.adjustment_create, name='adjustment_create'),
]
