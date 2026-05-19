from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_dashboard, name='sales_dashboard'),
    path('quick/', views.quick_sale_view, name='quick_sale'),
    path('customer-display/', views.customer_display_view, name='customer_display'),
    path('receipt/<int:sale_id>/', views.print_receipt_view, name='print_receipt'),
]
