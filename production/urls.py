from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_dashboard, name='production_dashboard'),
    path('manage/', views.manage_products, name='manage_products'),
]
