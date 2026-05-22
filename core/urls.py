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
    path('settings/branch-telegram/', views.save_branch_telegram, name='save_branch_telegram'),
    path('settings/branch-telegram/test/', views.test_branch_telegram, name='test_branch_telegram'),
    path('settings/branch-telegram/get-chat-id/', views.get_telegram_chat_id, name='get_telegram_chat_id'),
    # Face ID Kamera va Sessiya boshqaruvi
    path('face-id/cameras/', views.camera_management, name='camera_management'),
    path('face-id/session/', views.face_id_session_control, name='face_id_session_control'),
]
