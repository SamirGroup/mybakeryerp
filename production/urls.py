from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_dashboard, name='production_dashboard'),
    path('manage/', views.manage_products, name='manage_products'),
    path('done/<int:log_id>/', views.mark_production_done, name='mark_production_done'),
    path('recipe/<int:recipe_id>/print/', views.recipe_print, name='recipe_print'),
    path('recipe/<int:recipe_id>/json/', views.recipe_json, name='recipe_json'),
]
