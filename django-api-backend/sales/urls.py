from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentasViewSet

app_name = 'sales'

# Router para registrar los ViewSets
router = DefaultRouter()
router.register(r'ventas', VentasViewSet, basename='ventas')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs generadas automáticamente por el router:
# 
# VENTAS:
# GET    /api/sales/ventas/                    - Listar ventas
# POST   /api/sales/ventas/                    - Crear venta
# GET    /api/sales/ventas/{id}/               - Obtener venta específica
# PUT    /api/sales/ventas/{id}/               - Actualizar venta completa
# PATCH  /api/sales/ventas/{id}/               - Actualizar venta parcial
# DELETE /api/sales/ventas/{id}/               - Desactivar venta
# PATCH  /api/sales/ventas/{id}/cambiar_estado/ - Cambiar estado de venta
# PATCH  /api/sales/ventas/{id}/anular_venta/  - Anular venta específica
# PATCH  /api/sales/ventas/{id}/toggle_active/ - Activar/desactivar venta
# GET    /api/sales/ventas/estadisticas/       - Estadísticas de ventas
# GET    /api/sales/ventas/dashboard/          - Dashboard de ventas
# GET    /api/sales/ventas/reporte/            - Reporte detallado de ventas
#
# FILTROS DISPONIBLES:
# - Ventas: ?estado=pagado&tipo_pago=efectivo&cliente=1&unidad=2
# - Ventas: ?mes=2024-01-01&fecha_generacion_factura__gte=2024-01-01
# - Ventas: ?precio__gte=100&total__lte=1000&is_active=true
# - Búsqueda: ?search=FAC001 (busca en número de factura, cliente, RUC, placa, descripción)
# - Ordenamiento: ?ordering=-fecha_generacion_factura,precio
#
# EJEMPLOS DE USO:
# - Ventas pendientes: ?estado=pendiente
# - Ventas del mes: ?mes=2024-01-01
# - Ventas por cliente: ?cliente=5
# - Ventas por rango de precio: ?precio__gte=500&precio__lte=2000
# - Buscar por factura: ?search=FAC001
# - Estadísticas del mes: /estadisticas/?mes=2024-01-01
# - Cambiar estado: /{id}/cambiar_estado/?nuevo_estado=pagado