from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_dashboard, name='production_dashboard'),
    path('manage/', views.manage_products, name='manage_products'),
    path('done/<int:log_id>/', views.mark_production_done, name='mark_production_done'),
    path('recipe/<int:recipe_id>/print/', views.recipe_print, name='recipe_print'),
    path('recipe/<int:recipe_id>/json/', views.recipe_json, name='recipe_json'),

    # Retsept
    path('recipe-import/', views.recipe_import, name='recipe_import'),
    path('recipe-import-template/', views.recipe_import_template, name='recipe_import_template'),
    path('recipe-export-json/', views.recipe_export_json, name='recipe_export_json'),
    path('recipe-import-json/', views.recipe_import_json, name='recipe_import_json'),

    # Mahsulotlar
    path('products-export-excel/', views.products_export_excel, name='products_export_excel'),
    path('products-export-json/', views.products_export_json, name='products_export_json'),
    path('products-import-excel/', views.products_import_excel, name='products_import_excel'),
    path('products-import-json/', views.products_import_json, name='products_import_json'),

    # Xom ashyo
    path('materials-export-excel/', views.materials_export_excel, name='materials_export_excel'),
    path('materials-export-json/', views.materials_export_json, name='materials_export_json'),
    path('materials-import-excel/', views.materials_import_excel, name='materials_import_excel'),
    path('materials-import-json/', views.materials_import_json, name='materials_import_json'),
]
