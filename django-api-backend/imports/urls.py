"""
URLs para el sistema de importación de Excel.
Define las rutas para los endpoints de importación.
"""
from django.urls import path
from . import views

app_name = 'imports'

urlpatterns = [
    # Endpoint principal para importar archivos Excel
    path('excel/', views.import_excel, name='import_excel'),
    
    # Endpoint para obtener plantillas de importación
    path('template/<str:module>/', views.import_template, name='import_template'),
    
    # Endpoint para obtener información sobre módulos disponibles
    path('status/', views.import_status, name='import_status'),
]