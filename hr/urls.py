from django.urls import path
from . import views

urlpatterns = [
    path('', views.hr_dashboard, name='hr_dashboard'),
    path('positions-export-json/', views.positions_export_json, name='positions_export_json'),
    path('positions-import-json/', views.positions_import_json, name='positions_import_json'),
    path('employee/<int:emp_id>/report/', views.employee_report, name='employee_report'),
]
