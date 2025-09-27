from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoTrabajoViewSet, ServicioViewSet, ServicioFlexibleViewSet

app_name = 'services'

# Router para registrar los ViewSets
router = DefaultRouter()
router.register(r'tipos-trabajo', TipoTrabajoViewSet, basename='tipotrabajo')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'servicios-flexibles', ServicioFlexibleViewSet, basename='servicio-flexible')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs generadas automáticamente por el router:
# 
# TIPOS DE TRABAJO:
# GET    /api/services/tipos-trabajo/                    - Listar tipos de trabajo
# POST   /api/services/tipos-trabajo/                    - Crear tipo de trabajo
# GET    /api/services/tipos-trabajo/{id}/               - Obtener tipo específico
# PUT    /api/services/tipos-trabajo/{id}/               - Actualizar tipo completo
# PATCH  /api/services/tipos-trabajo/{id}/               - Actualizar tipo parcial
# DELETE /api/services/tipos-trabajo/{id}/               - Desactivar tipo
# GET    /api/services/tipos-trabajo/{id}/servicios/     - Servicios del tipo
# PATCH  /api/services/tipos-trabajo/{id}/toggle_active/ - Activar/desactivar tipo
# GET    /api/services/tipos-trabajo/estadisticas/       - Estadísticas de tipos
#
# SERVICIOS:
# GET    /api/services/servicios/                    - Listar servicios
# POST   /api/services/servicios/                    - Crear servicio
# GET    /api/services/servicios/{id}/               - Obtener servicio específico
# PUT    /api/services/servicios/{id}/               - Actualizar servicio completo
# PATCH  /api/services/servicios/{id}/               - Actualizar servicio parcial
# DELETE /api/services/servicios/{id}/               - Desactivar servicio
# PATCH  /api/services/servicios/{id}/cambiar_estado/ - Cambiar estado del servicio
# PATCH  /api/services/servicios/{id}/toggle_active/ - Activar/desactivar servicio
# GET    /api/services/servicios/estadisticas/       - Estadísticas de servicios
# GET    /api/services/servicios/dashboard/          - Dashboard de servicios
#
# SERVICIOS FLEXIBLES:
# GET    /api/services/servicios-flexibles/                    - Listar servicios flexibles
# POST   /api/services/servicios-flexibles/                    - Crear servicio flexible
# GET    /api/services/servicios-flexibles/{id}/               - Obtener servicio flexible específico
# PUT    /api/services/servicios-flexibles/{id}/               - Actualizar servicio flexible completo
# PATCH  /api/services/servicios-flexibles/{id}/               - Actualizar servicio flexible parcial
# DELETE /api/services/servicios-flexibles/{id}/               - Desactivar servicio flexible
# GET    /api/services/servicios-flexibles/validar_requerimientos/ - Validar requerimientos por tipo
# GET    /api/services/servicios-flexibles/estadisticas_flexibles/ - Estadísticas de servicios flexibles
#
# FILTROS DISPONIBLES:
# - Servicios: ?estado_servicio=pendiente&tipo_trabajo=1&tecnico=2&cliente=3
# - Servicios: ?fecha_desde=2024-01-01&fecha_hasta=2024-12-31
# - Servicios flexibles: ?sin_equipos=true&tipo_trabajo=1
# - Búsqueda: ?search=instalacion
# - Ordenamiento: ?ordering=-fecha,precio