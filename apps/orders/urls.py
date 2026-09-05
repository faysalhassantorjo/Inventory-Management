from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/confirm/', views.order_confirm_view, name='order_confirm'),
    path('<int:pk>/cancel/', views.order_cancel_view, name='order_cancel'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
]
