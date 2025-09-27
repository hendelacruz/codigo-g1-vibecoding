from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from django.db.models import Q, Count

from .models import Cliente, Proveedor, Unidad
from .serializers import ClienteSerializer, ProveedorSerializer, UnidadSerializer
from .filters import ClienteFilter, ProveedorFilter, UnidadFilter
from todoapi.utils.permissions import IsAdminOrSupervisor
from todoapi.utils.viewsets import AdvancedSearchViewSet, BusinessIntelligenceViewSet


@extend_schema_view(
    list=extend_schema(
        summary="Listar clientes",
        description="Lista todos los clientes con filtros opcionales",
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en nombre, RUC, contacto'),
        ]
    ),
    create=extend_schema(
        summary="Crear cliente",
        description="Crea un nuevo cliente en el sistema"
    ),
    retrieve=extend_schema(
        summary="Obtener cliente",
        description="Obtiene los detalles de un cliente específico"
    ),
    update=extend_schema(
        summary="Actualizar cliente",
        description="Actualiza completamente un cliente"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente cliente",
        description="Actualiza parcialmente un cliente"
    ),
    destroy=extend_schema(
        summary="Eliminar cliente",
        description="Desactiva un cliente del sistema"
    )
)
class ClienteViewSet(BusinessIntelligenceViewSet):
    """
    ViewSet para gestionar clientes del sistema con inteligencia de negocio.
    
    Proporciona operaciones CRUD completas con filtros avanzados:
    - Filtrado por estado activo
    - Búsqueda por nombre, RUC, contacto
    - Ordenamiento por nombre, fecha de creación
    - Acciones personalizadas para gestión de unidades
    - Capacidades de inteligencia de negocio
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClienteFilter
    search_fields = ['nombre', 'ruc', 'correo', 'celular']
    ordering_fields = ['nombre', 'created_at', 'ruc']
    ordering = ['-created_at']
    search_config_key = 'entities.cliente'

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva el cliente en lugar de eliminarlo
        """
        instance.is_active = False
        instance.save()

    @extend_schema(
        summary="Unidades del cliente",
        description="Lista todas las unidades vehiculares de un cliente específico"
    )
    @action(detail=True, methods=['get'])
    def unidades(self, request, pk=None):
        """
        Acción para obtener las unidades de un cliente
        """
        cliente = self.get_object()
        unidades = cliente.unidades.filter(is_active=True)
        
        # Importar aquí para evitar importación circular
        from .serializers import UnidadBasicSerializer
        serializer = UnidadBasicSerializer(unidades, many=True)
        
        return Response({
            'cliente': cliente.nombre,
            'total_unidades': unidades.count(),
            'unidades': serializer.data
        })

    @extend_schema(
        summary="Activar/Desactivar cliente",
        description="Cambia el estado activo de un cliente",
        request={
            'type': 'object',
            'properties': {
                'is_active': {'type': 'boolean', 'description': 'Estado activo del cliente'}
            },
            'required': ['is_active']
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Acción para activar/desactivar un cliente
        """
        cliente = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cliente.is_active = bool(is_active)
        cliente.save()
        
        serializer = self.get_serializer(cliente)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas de clientes",
        description="Obtiene estadísticas generales de los clientes"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de clientes
        """
        total = self.queryset.count()
        activos = self.queryset.filter(is_active=True).count()
        inactivos = total - activos
        
        # Clientes con más unidades
        from django.db.models import Count
        clientes_con_unidades = self.queryset.annotate(
            unidades_count=Count('unidades', filter=models.Q(unidades__is_active=True))
        ).filter(unidades_count__gt=0).order_by('-unidades_count')[:5]
        
        top_clientes = []
        for cliente in clientes_con_unidades:
            top_clientes.append({
                'nombre': cliente.nombre,
                'ruc': cliente.ruc,
                'unidades': cliente.unidades_count
            })
        
        return Response({
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'porcentaje_activos': round((activos / total * 100) if total > 0 else 0, 2),
            'top_clientes_por_unidades': top_clientes
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar proveedores",
        description="Lista todos los proveedores con filtros opcionales",
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en nombre, RUC, contacto'),
        ]
    ),
    create=extend_schema(
        summary="Crear proveedor",
        description="Crea un nuevo proveedor en el sistema"
    ),
    retrieve=extend_schema(
        summary="Obtener proveedor",
        description="Obtiene los detalles de un proveedor específico"
    ),
    update=extend_schema(
        summary="Actualizar proveedor",
        description="Actualiza completamente un proveedor"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente proveedor",
        description="Actualiza parcialmente un proveedor"
    ),
    destroy=extend_schema(
        summary="Eliminar proveedor",
        description="Desactiva un proveedor del sistema"
    )
)
class ProveedorViewSet(AdvancedSearchViewSet):
    """
    ViewSet para gestionar proveedores con búsqueda avanzada.
    """
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProveedorFilter
    search_fields = ['nombre', 'correo', 'celular', 'direccion', 'ruc']
    ordering_fields = ['created_at', 'nombre', 'ruc']
    ordering = ['-created_at']
    search_config_key = 'entities.proveedor'

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva el proveedor en lugar de eliminarlo
        """
        instance.is_active = False
        instance.save()

    @extend_schema(
        summary="Productos del proveedor",
        description="Lista todos los productos de inventario de un proveedor específico"
    )
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """
        Acción para obtener los productos de un proveedor
        """
        proveedor = self.get_object()
        
        # Contar productos por tipo
        gps_count = proveedor.gps_set.count()
        sim_count = proveedor.simcard_set.count()
        otros_count = proveedor.otros_set.count()
        
        return Response({
            'proveedor': proveedor.nombre,
            'total_productos': gps_count + sim_count + otros_count,
            'productos_por_tipo': {
                'gps': gps_count,
                'simcards': sim_count,
                'otros': otros_count
            }
        })

    @extend_schema(
        summary="Activar/Desactivar proveedor",
        description="Cambia el estado activo de un proveedor",
        request={
            'type': 'object',
            'properties': {
                'is_active': {'type': 'boolean', 'description': 'Estado activo del proveedor'}
            },
            'required': ['is_active']
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Acción para activar/desactivar un proveedor
        """
        proveedor = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        proveedor.is_active = bool(is_active)
        proveedor.save()
        
        serializer = self.get_serializer(proveedor)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas de proveedores",
        description="Obtiene estadísticas generales de los proveedores"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de proveedores
        """
        total = self.queryset.count()
        activos = self.queryset.filter(is_active=True).count()
        inactivos = total - activos
        
        return Response({
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'porcentaje_activos': round((activos / total * 100) if total > 0 else 0, 2)
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar unidades vehiculares",
        description="Lista todas las unidades vehiculares con filtros opcionales",
        parameters=[
            OpenApiParameter('tipo', OpenApiTypes.STR, description='Filtrar por tipo de vehículo'),
            OpenApiParameter('cliente', OpenApiTypes.INT, description='Filtrar por cliente'),
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en placa, marca, modelo'),
        ]
    ),
    create=extend_schema(
        summary="Crear unidad vehicular",
        description="Crea una nueva unidad vehicular en el sistema"
    ),
    retrieve=extend_schema(
        summary="Obtener unidad vehicular",
        description="Obtiene los detalles de una unidad vehicular específica"
    ),
    update=extend_schema(
        summary="Actualizar unidad vehicular",
        description="Actualiza completamente una unidad vehicular"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente unidad vehicular",
        description="Actualiza parcialmente una unidad vehicular"
    ),
    destroy=extend_schema(
        summary="Eliminar unidad vehicular",
        description="Desactiva una unidad vehicular del sistema"
    )
)
class UnidadViewSet(BusinessIntelligenceViewSet):
    """
    ViewSet para gestionar unidades vehiculares con búsquedas avanzadas.
    
    Proporciona operaciones CRUD completas con filtros avanzados:
    - Filtrado por tipo, cliente, marca, modelo
    - Búsqueda por placa, marca, modelo, serie
    - Ordenamiento por fecha de creación, placa, marca
    - Acciones personalizadas para gestión de unidades
    """
    # Optimized queryset with select_related for Cliente relationship
    queryset = Unidad.objects.select_related('cliente').all()
    serializer_class = UnidadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UnidadFilter
    search_fields = ['placa', 'marca', 'modelo', 'serie']
    ordering_fields = ['created_at', 'placa', 'marca', 'modelo']
    ordering = ['-created_at']
    search_config_key = 'entities.unidad'

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva la unidad en lugar de eliminarla
        """
        instance.is_active = False
        instance.save()

    @extend_schema(
        summary="Servicios de la unidad",
        description="Lista todos los servicios de una unidad vehicular específica"
    )
    @action(detail=True, methods=['get'])
    def servicios(self, request, pk=None):
        """
        Acción para obtener los servicios de una unidad
        """
        unidad = self.get_object()
        
        # Contar servicios (esto requerirá que el modelo Servicio esté implementado)
        try:
            servicios_count = unidad.servicios.count()
            servicios_activos = unidad.servicios.filter(is_active=True).count()
        except AttributeError:
            # Si el modelo Servicio no está implementado aún
            servicios_count = 0
            servicios_activos = 0
        
        return Response({
            'unidad': f"{unidad.placa} - {unidad.marca} {unidad.modelo}",
            'cliente': unidad.cliente.nombre,
            'total_servicios': servicios_count,
            'servicios_activos': servicios_activos
        })

    @extend_schema(
        summary="Activar/Desactivar unidad",
        description="Cambia el estado activo de una unidad vehicular",
        request={
            'type': 'object',
            'properties': {
                'is_active': {'type': 'boolean', 'description': 'Estado activo de la unidad'}
            },
            'required': ['is_active']
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Acción para activar/desactivar una unidad
        """
        unidad = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unidad.is_active = bool(is_active)
        unidad.save()
        
        serializer = self.get_serializer(unidad)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas de unidades",
        description="Obtiene estadísticas generales de las unidades vehiculares"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de unidades vehiculares
        """
        from django.db.models import Count
        
        total = self.queryset.count()
        activas = self.queryset.filter(is_active=True).count()
        inactivas = total - activas
        
        # Estadísticas por tipo
        stats_por_tipo = self.queryset.values('tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Estadísticas por cliente (top 5)
        stats_por_cliente = self.queryset.values(
            'cliente__nombre', 'cliente__ruc'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        return Response({
            'total': total,
            'activas': activas,
            'inactivas': inactivas,
            'porcentaje_activas': round((activas / total * 100) if total > 0 else 0, 2),
            'por_tipo': list(stats_por_tipo),
            'top_clientes': list(stats_por_cliente)
        })
