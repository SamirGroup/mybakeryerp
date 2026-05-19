from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('branch-dashboard/', views.branch_dashboard, name='branch_dashboard'),
    path('settings/telegram/', views.save_telegram_settings, name='save_telegram_settings'),
    path('settings/telegram/test/', views.test_telegram, name='test_telegram'),
]
