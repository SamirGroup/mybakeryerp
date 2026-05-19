from django.urls import path
from . import views

urlpatterns = [
    path('', views.branches_dashboard, name='branches_dashboard'),
    path('<int:branch_id>/', views.branch_detail, name='branch_detail'),
]
