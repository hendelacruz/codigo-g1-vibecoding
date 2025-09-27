from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .equipment_assignment_service import (
    available_equipment_view,
    assign_equipment_view,
    unassign_equipment_view
)

app_name = 'inventory'

# Router para ViewSets
router = DefaultRouter()
router.register(r'gps', views.GPSViewSet, basename='gps')
router.register(r'simcards', views.SIMCardViewSet, basename='simcard')
router.register(r'otros', views.OtrosViewSet, basename='otros')

urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
    
    # Equipment Assignment Service URLs
    path('equipment/available/', available_equipment_view, name='available-equipment'),
    path('equipment/assign/', assign_equipment_view, name='assign-equipment'),
    path('equipment/unassign/', unassign_equipment_view, name='unassign-equipment'),
]

# Las URLs generadas automáticamente por el router serán:
# /api/inventory/gps/ - Lista y creación de GPS
# /api/inventory/gps/{id}/ - Detalle, actualización y eliminación de GPS
# /api/inventory/gps/{id}/cambiar_estado/ - Cambiar estado de GPS
# /api/inventory/gps/estadisticas/ - Estadísticas de GPS
# /api/inventory/simcards/ - Lista y creación de SIM
# /api/inventory/simcards/{id}/ - Detalle, actualización y eliminación de SIM
# /api/inventory/simcards/{id}/cambiar_estado/ - Cambiar estado de SIM
# /api/inventory/simcards/estadisticas/ - Estadísticas de SIM
# /api/inventory/otros/ - Lista y creación de otros productos
# /api/inventory/otros/{id}/ - Detalle, actualización y eliminación de otros
# /api/inventory/otros/{id}/ajustar_stock/ - Ajustar stock de producto
# /api/inventory/otros/stock_bajo/ - Productos con stock bajo
# /api/inventory/otros/estadisticas/ - Estadísticas de otros productos