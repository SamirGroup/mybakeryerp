from django.urls import path
from . import views

urlpatterns = [
    path('', views.hr_dashboard, name='hr_dashboard'),
    path('positions-export-json/', views.positions_export_json, name='positions_export_json'),
    path('positions-import-json/', views.positions_import_json, name='positions_import_json'),
    path('employee/<int:emp_id>/report/', views.employee_report, name='employee_report'),
    
    # Face ID URLs
    path('face-id/check-in/', views.face_id_check_in, name='face_id_check_in'),
    path('face-id/check-out/', views.face_id_check_out, name='face_id_check_out'),
    path('face-id/enroll/', views.face_id_enroll, name='face_id_enroll'),
    path('face-id/dashboard/', views.face_dashboard, name='face_dashboard'),
    path('face-id/camera/', views.face_id_camera, name='face_id_camera'),
    
    # API for check-in/check-out
    path('api/check-in/', views.api_check_in, name='api_check_in'),
    
    # Kunlik nagruzka API
    path('employee/<int:emp_id>/daily-target/', views.daily_target_api, name='daily_target_api'),
]
