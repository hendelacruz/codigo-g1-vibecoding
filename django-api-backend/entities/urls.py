from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, ProveedorViewSet, UnidadViewSet

app_name = 'entities'

# Router para registrar los ViewSets
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'unidades', UnidadViewSet, basename='unidad')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs generadas automáticamente por el router:
# 
# CLIENTES:
# GET    /api/entities/clientes/                    - Listar clientes
# POST   /api/entities/clientes/                    - Crear cliente
# GET    /api/entities/clientes/{id}/               - Obtener cliente específico
# PUT    /api/entities/clientes/{id}/               - Actualizar cliente completo
# PATCH  /api/entities/clientes/{id}/               - Actualizar cliente parcial
# DELETE /api/entities/clientes/{id}/               - Desactivar cliente
# GET    /api/entities/clientes/{id}/unidades/      - Unidades del cliente
# PATCH  /api/entities/clientes/{id}/toggle_active/ - Activar/desactivar cliente
# GET    /api/entities/clientes/estadisticas/       - Estadísticas de clientes
#
# PROVEEDORES:
# GET    /api/entities/proveedores/                    - Listar proveedores
# POST   /api/entities/proveedores/                    - Crear proveedor
# GET    /api/entities/proveedores/{id}/               - Obtener proveedor específico
# PUT    /api/entities/proveedores/{id}/               - Actualizar proveedor completo
# PATCH  /api/entities/proveedores/{id}/               - Actualizar proveedor parcial
# DELETE /api/entities/proveedores/{id}/               - Desactivar proveedor
# GET    /api/entities/proveedores/{id}/productos/     - Productos del proveedor
# PATCH  /api/entities/proveedores/{id}/toggle_active/ - Activar/desactivar proveedor
# GET    /api/entities/proveedores/estadisticas/       - Estadísticas de proveedores
#
# UNIDADES:
# GET    /api/entities/unidades/                    - Listar unidades vehiculares
# POST   /api/entities/unidades/                    - Crear unidad vehicular
# GET    /api/entities/unidades/{id}/               - Obtener unidad específica
# PUT    /api/entities/unidades/{id}/               - Actualizar unidad completa
# PATCH  /api/entities/unidades/{id}/               - Actualizar unidad parcial
# DELETE /api/entities/unidades/{id}/               - Desactivar unidad
# GET    /api/entities/unidades/{id}/servicios/     - Servicios de la unidad
# PATCH  /api/entities/unidades/{id}/toggle_active/ - Activar/desactivar unidad
# GET    /api/entities/unidades/estadisticas/       - Estadísticas de unidades