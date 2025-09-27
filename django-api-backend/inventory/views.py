from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import GPS, SIMCard, Otros
from .serializers import GPSSerializer, SIMCardSerializer, OtrosSerializer
from .filters import GPSFilter, SIMCardFilter, OtrosFilter
from todoapi.utils.permissions import IsAdminOrSupervisor
from todoapi.utils.viewsets import AdvancedSearchViewSet
from todoapi.utils.rate_limiting import APIRateLimitMixin


@extend_schema_view(
    list=extend_schema(
        summary="Listar dispositivos GPS",
        description="Lista todos los dispositivos GPS con filtros opcionales",
        parameters=[
            OpenApiParameter('estado', OpenApiTypes.STR, description='Filtrar por estado de asignación (asignado/no_asignado)'),
            OpenApiParameter('proceso', OpenApiTypes.STR, description='Filtrar por proceso operativo (disponible/operativo/en_transito/etc)'),
            OpenApiParameter('marca', OpenApiTypes.STR, description='Filtrar por marca'),
            OpenApiParameter('proveedor', OpenApiTypes.INT, description='Filtrar por proveedor'),
            OpenApiParameter('cliente', OpenApiTypes.INT, description='Filtrar por cliente asignado'),
            OpenApiParameter('cliente__isnull', OpenApiTypes.BOOL, description='Filtrar GPS sin cliente asignado'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en IMEI, marca, modelo'),
        ]
    ),
    create=extend_schema(
        summary="Crear dispositivo GPS",
        description="Crea un nuevo dispositivo GPS en el inventario"
    ),
    retrieve=extend_schema(
        summary="Obtener dispositivo GPS",
        description="Obtiene los detalles de un dispositivo GPS específico"
    ),
    update=extend_schema(
        summary="Actualizar dispositivo GPS",
        description="Actualiza completamente un dispositivo GPS"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente dispositivo GPS",
        description="Actualiza parcialmente un dispositivo GPS"
    ),
    destroy=extend_schema(
        summary="Eliminar dispositivo GPS",
        description="Elimina un dispositivo GPS del inventario"
    )
)
class GPSViewSet(APIRateLimitMixin, AdvancedSearchViewSet):
    """
    ViewSet para gestionar dispositivos GPS con búsquedas avanzadas.
    
    Proporciona operaciones CRUD completas con filtros avanzados:
    - Filtrado por estado, marca, proveedor
    - Búsqueda por IMEI, marca, modelo
    - Ordenamiento por fecha de compra, marca, estado
    - Acciones personalizadas para cambio de estado
    """
    # Optimized queryset with select_related for Proveedor and Cliente relationships
    queryset = GPS.objects.select_related('proveedor', 'cliente').all()
    serializer_class = GPSSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GPSFilter
    search_fields = ['imei', 'marca', 'modelo', 'numero_factura', 'observaciones']
    ordering_fields = ['fecha_compra', 'marca', 'estado', 'precio_compra']
    ordering = ['-fecha_compra']
    search_config_key = 'inventory.gps'
    
    # Rate limiting configuration for GPS endpoints
    rate_limit_scope = 'inventory'
    rate_limit_config = {'requests': 500, 'window': 3600}  # 500 requests per hour

    @extend_schema(
        summary="Cambiar estado/proceso de GPS",
        description="Cambia el estado de asignación, proceso operativo y/o estado activo de un dispositivo GPS",
        request={
            'type': 'object',
            'properties': {
                'estado': {
                    'type': 'string',
                    'enum': ['asignado', 'no_asignado'],
                    'description': 'Estado de asignación del GPS'
                },
                'proceso': {
                    'type': 'string',
                    'enum': ['disponible', 'operativo', 'en_transito', 'en_mantenimiento', 'dañado', 'perdido', 'en_reparacion', 'dado_de_baja'],
                    'description': 'Proceso operativo del GPS'
                },
                'is_active': {
                    'type': 'boolean',
                    'description': 'Estado activo del dispositivo (true=activo, false=inactivo)'
                },
                'observaciones': {'type': 'string', 'description': 'Observaciones del cambio'}
            }
        }
    )
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de asignación y/o proceso operativo de un GPS.
        
        La nueva estructura separa:
        - Estado: asignado/no_asignado (relacionado con cliente)
        - Proceso: disponible, operativo, en_transito, etc. (estado operativo)
        """
        from .state_manager import GPSStateManager, GPSStateValidator
        from django.core.exceptions import ValidationError
        
        gps = self.get_object()
        nuevo_estado = request.data.get('estado')
        nuevo_proceso = request.data.get('proceso')
        nuevo_is_active = request.data.get('is_active')
        observaciones = request.data.get('observaciones', '')
        
        if not nuevo_estado and not nuevo_proceso and nuevo_is_active is None:
            return Response(
                {'error': 'Debe proporcionar al menos "estado", "proceso" o "is_active"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar campos individualmente
        if nuevo_estado:
            estados_validos = [choice[0] for choice in gps._meta.get_field('estado').choices]
            if nuevo_estado not in estados_validos:
                return Response(
                    {'error': f'Estado inválido. Estados válidos: {estados_validos}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if nuevo_proceso:
            procesos_validos = [choice[0] for choice in gps._meta.get_field('proceso').choices]
            if nuevo_proceso not in procesos_validos:
                return Response(
                    {'error': f'Proceso inválido. Procesos válidos: {procesos_validos}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar valores de is_active
        if nuevo_is_active is not None and not isinstance(nuevo_is_active, bool):
            return Response(
                {'error': 'is_active debe ser un valor booleano (true/false)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Actualizar campos
            if nuevo_estado:
                gps.estado = nuevo_estado
            if nuevo_proceso:
                gps.proceso = nuevo_proceso
            if nuevo_is_active is not None:
                gps.is_active = nuevo_is_active
            if observaciones:
                gps.observaciones = observaciones
            
            # Validar la combinación usando GPSStateValidator
            validator = GPSStateValidator()
            is_valid, errors = validator.validate_gps_state(gps)
            
            if not is_valid:
                from .state_manager import GPSStateManager
                return Response({
                    'error': 'Combinación de estado y proceso inválida',
                    'validation_errors': errors,
                    'current_estado': gps.estado,
                    'current_proceso': gps.proceso,
                    'has_client': bool(gps.cliente),
                    'valid_next_states': GPSStateManager.get_valid_proceso_transitions(gps.proceso)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            gps.save()
            serializer = self.get_serializer(gps)
            return Response(serializer.data)
            
        except ValidationError as e:
            from .state_manager import GPSStateManager
            return Response({
                'error': str(e),
                'current_estado': gps.estado,
                'current_proceso': gps.proceso,
                'requested_estado': nuevo_estado,
                'requested_proceso': nuevo_proceso,
                'has_client': bool(gps.cliente),
                'client_name': gps.cliente.nombre if gps.cliente else None,
                'valid_next_states': GPSStateManager.get_valid_proceso_transitions(gps.proceso)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Información de estado y proceso del GPS",
        description="Obtiene información detallada del estado de asignación y proceso operativo del GPS"
    )
    @action(detail=True, methods=['get'])
    def estado_info(self, request, pk=None):
        """
        Obtiene información detallada del estado de asignación y proceso operativo del GPS.
        
        Returns:
            dict: Información completa del estado y proceso del GPS
        """
        gps = self.get_object()
        estado_info = gps.estado_info
        
        return Response(estado_info)

    @extend_schema(
        summary="Asignar/Desasignar cliente a GPS",
        description="Asigna o desasigna un cliente a un dispositivo GPS específico",
        request={
            'type': 'object',
            'properties': {
                'cliente_id': {
                    'type': 'integer',
                    'description': 'ID del cliente a asignar (null para desasignar)'
                },
                'observaciones': {
                    'type': 'string',
                    'description': 'Observaciones de la asignación'
                }
            }
        }
    )
    @action(detail=True, methods=['patch'])
    def asignar_cliente(self, request, pk=None):
        """
        Endpoint para asignar o desasignar cliente a GPS usando el sistema de gestión de estados.
        """
        from .state_manager import GPSStateManager
        from django.core.exceptions import ValidationError
        
        gps = self.get_object()
        cliente_id = request.data.get('cliente_id')
        observaciones = request.data.get('observaciones', '')
        
        try:
            if cliente_id:
                # Asignar cliente
                from entities.models import Cliente
                cliente = Cliente.objects.get(id=cliente_id, is_active=True)
                
                # Validate if GPS can be assigned
                if not GPSStateManager.can_assign_client(gps.proceso):
                    return Response({
                        'error': f'No se puede asignar cliente. GPS está en proceso "{gps.proceso}"',
                        'valid_processes_for_assignment': list(GPSStateManager.ASSIGNABLE_PROCESSES)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Assign client and update state
                old_cliente = gps.cliente
                gps.cliente = cliente
                gps.estado = GPSStateManager.auto_update_state_on_client_change(
                    gps, old_cliente, cliente
                )
                action_message = f"GPS asignado al cliente {cliente.nombre}"
            else:
                # Desasignar cliente
                if not gps.cliente:
                    return Response({
                        'error': 'El GPS no tiene cliente asignado'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                old_cliente = gps.cliente
                cliente_anterior = old_cliente.nombre
                gps.cliente = None
                gps.estado = GPSStateManager.auto_update_state_on_client_change(
                    gps, old_cliente, None
                )
                action_message = f"GPS desasignado del cliente {cliente_anterior}"
            
            # Agregar observaciones si se proporcionan
            if observaciones:
                if gps.observaciones:
                    gps.observaciones += f"\n{action_message}: {observaciones}"
                else:
                    gps.observaciones = f"{action_message}: {observaciones}"
            
            gps.save()
            
            serializer = self.get_serializer(gps)
            return Response({
                'message': action_message,
                'gps': serializer.data
            })
            
        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado o inactivo'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({
                'error': 'Error de validación',
                'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Error al procesar la asignación: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Estadísticas de GPS",
        description="Obtiene estadísticas generales de los dispositivos GPS"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de GPS.
        """
        from django.db.models import Count, Avg, Q
        
        stats = self.get_queryset().aggregate(
            total=Count('id'),
            disponibles=Count('id', filter=Q(estado='disponible')),
            asignados=Count('id', filter=Q(estado='asignado')),
            en_mantenimiento=Count('id', filter=Q(estado='en_mantenimiento')),
            precio_promedio=Avg('precio_compra'),
            con_cliente=Count('id', filter=Q(cliente__isnull=False)),
            sin_cliente=Count('id', filter=Q(cliente__isnull=True))
        )
        
        return Response(stats)


@extend_schema_view(
    list=extend_schema(
        summary="Listar tarjetas SIM",
        description="Lista todas las tarjetas SIM con filtros opcionales",
        parameters=[
            OpenApiParameter('estado', OpenApiTypes.STR, description='Filtrar por estado'),
            OpenApiParameter('operadora', OpenApiTypes.STR, description='Filtrar por operadora'),
            OpenApiParameter('proveedor', OpenApiTypes.INT, description='Filtrar por proveedor'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en número chip, ICC'),
        ]
    ),
    create=extend_schema(
        summary="Crear tarjeta SIM",
        description="Crea una nueva tarjeta SIM en el inventario"
    ),
    retrieve=extend_schema(
        summary="Obtener tarjeta SIM",
        description="Obtiene los detalles de una tarjeta SIM específica"
    ),
    update=extend_schema(
        summary="Actualizar tarjeta SIM",
        description="Actualiza completamente una tarjeta SIM"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente tarjeta SIM",
        description="Actualiza parcialmente una tarjeta SIM"
    ),
    destroy=extend_schema(
        summary="Eliminar tarjeta SIM",
        description="Elimina una tarjeta SIM del inventario"
    )
)
class SIMCardViewSet(APIRateLimitMixin, AdvancedSearchViewSet):
    """
    ViewSet para gestionar tarjetas SIM con búsquedas avanzadas.
    
    Proporciona operaciones CRUD completas con filtros avanzados:
    - Filtrado por estado, operadora, proveedor
    - Búsqueda por número, ICCID, operadora
    - Ordenamiento por fecha de compra, operadora, estado
    - Acciones personalizadas para cambio de estado
    """
    # Optimized queryset with select_related for Proveedor relationship
    queryset = SIMCard.objects.select_related('proveedor', 'cliente').all()
    serializer_class = SIMCardSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SIMCardFilter
    search_fields = ['numero_chip', 'icc', 'numero_factura', 'observaciones', 'cliente__nombre']
    ordering_fields = ['fecha_compra', 'estado', 'proceso', 'precio_compra']
    ordering = ['-fecha_compra']
    search_config_key = 'inventory.simcard'
    
    # Rate limiting configuration for SIMCard endpoints
    rate_limit_scope = 'inventory'
    rate_limit_config = {'requests': 500, 'window': 3600}  # 500 requests per hour

    @extend_schema(
        summary="Cambiar estado/proceso de SIM",
        description="Cambia el estado de asignación, proceso operativo y/o estado activo de una tarjeta SIM",
        request={
            'type': 'object',
            'properties': {
                'estado': {
                    'type': 'string',
                    'enum': ['asignado', 'no_asignado'],
                    'description': 'Estado de asignación de la SIM'
                },
                'proceso': {
                    'type': 'string',
                    'enum': ['disponible', 'operativo', 'en_transito', 'en_mantenimiento', 'dañado', 'perdido', 'en_reparacion', 'dado_de_baja'],
                    'description': 'Proceso operativo de la SIM'
                },
                'is_active': {
                    'type': 'boolean',
                    'description': 'Estado activo de la SIM (true=activo, false=inactivo)'
                },
                'observaciones': {'type': 'string', 'description': 'Observaciones del cambio'}
            }
        }
    )
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de asignación y/o proceso operativo de una SIM.
        
        La nueva estructura separa:
        - Estado: asignado/no_asignado (relacionado con cliente)
        - Proceso: disponible, operativo, en_transito, etc. (estado operativo)
        """
        from django.core.exceptions import ValidationError
        
        sim = self.get_object()
        nuevo_estado = request.data.get('estado')
        nuevo_proceso = request.data.get('proceso')
        nuevo_is_active = request.data.get('is_active')
        observaciones = request.data.get('observaciones', '')
        
        if not nuevo_estado and not nuevo_proceso and nuevo_is_active is None:
            return Response(
                {'error': 'Debe proporcionar al menos "estado", "proceso" o "is_active"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar campos individualmente
        if nuevo_estado:
            estados_validos = [choice[0] for choice in sim._meta.get_field('estado').choices]
            if nuevo_estado not in estados_validos:
                return Response(
                    {'error': f'Estado inválido. Estados válidos: {estados_validos}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if nuevo_proceso:
            procesos_validos = [choice[0] for choice in sim._meta.get_field('proceso').choices]
            if nuevo_proceso not in procesos_validos:
                return Response(
                    {'error': f'Proceso inválido. Procesos válidos: {procesos_validos}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar valores de is_active
        if nuevo_is_active is not None and not isinstance(nuevo_is_active, bool):
            return Response(
                {'error': 'is_active debe ser un valor booleano (true/false)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Actualizar campos
            if nuevo_estado:
                sim.estado = nuevo_estado
            if nuevo_proceso:
                sim.proceso = nuevo_proceso
            if nuevo_is_active is not None:
                sim.is_active = nuevo_is_active
            if observaciones:
                sim.observaciones = observaciones
            
            # Validar la combinación usando el método clean del modelo
            sim.clean()
            sim.save()
            
            serializer = self.get_serializer(sim)
            return Response(serializer.data)
            
        except ValidationError as e:
            return Response({
                'error': str(e),
                'current_estado': sim.estado,
                'current_proceso': sim.proceso,
                'requested_estado': nuevo_estado,
                'requested_proceso': nuevo_proceso,
                'has_client': bool(sim.cliente),
                'client_name': sim.cliente.nombre if sim.cliente else None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Estadísticas de SIM",
        description="Obtiene estadísticas generales de las tarjetas SIM"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de tarjetas SIM
        """
        total = self.queryset.count()
        disponibles = self.queryset.filter(estado='disponible').count()
        asignados = self.queryset.filter(estado='asignado').count()
        
        # Estadísticas por operadora
        operadoras = self.queryset.values('operadora').distinct()
        stats_operadoras = {}
        for op in operadoras:
            if op['operadora']:
                stats_operadoras[op['operadora']] = self.queryset.filter(operadora=op['operadora']).count()
        
        return Response({
            'total': total,
            'disponibles': disponibles,
            'asignados': asignados,
            'porcentaje_disponibles': round((disponibles / total * 100) if total > 0 else 0, 2),
            'por_operadora': stats_operadoras
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar otros productos",
        description="Lista todos los otros productos con filtros opcionales",
        parameters=[
            OpenApiParameter('categoria', OpenApiTypes.STR, description='Filtrar por categoría'),
            OpenApiParameter('proveedor', OpenApiTypes.INT, description='Filtrar por proveedor'),
            OpenApiParameter('stock_bajo', OpenApiTypes.BOOL, description='Filtrar productos con stock bajo'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en descripción, categoría'),
        ]
    ),
    create=extend_schema(
        summary="Crear otro producto",
        description="Crea un nuevo producto en el inventario"
    ),
    retrieve=extend_schema(
        summary="Obtener otro producto",
        description="Obtiene los detalles de un producto específico"
    ),
    update=extend_schema(
        summary="Actualizar otro producto",
        description="Actualiza completamente un producto"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente otro producto",
        description="Actualiza parcialmente un producto"
    ),
    destroy=extend_schema(
        summary="Eliminar otro producto",
        description="Elimina un producto del inventario"
    )
)
class OtrosViewSet(APIRateLimitMixin, AdvancedSearchViewSet):
    """
    ViewSet para gestionar otros productos del inventario con búsquedas avanzadas.
    
    Proporciona operaciones CRUD completas con filtros avanzados:
    - Filtrado por categoría, proveedor, stock bajo
    - Búsqueda por descripción, categoría
    - Ordenamiento por fecha de compra, categoría, stock
    - Acciones personalizadas para gestión de stock
    """
    # Optimized queryset with select_related for Proveedor relationship
    queryset = Otros.objects.select_related('proveedor').all()
    serializer_class = OtrosSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OtrosFilter
    search_fields = ['descripcion', 'categoria', 'numero_factura', 'observaciones']
    ordering_fields = ['fecha_compra', 'categoria', 'stock_actual', 'precio_unitario']
    ordering = ['-fecha_compra']
    search_config_key = 'inventory.otros'
    
    # Rate limiting configuration for Otros endpoints
    rate_limit_scope = 'inventory'
    rate_limit_config = {'requests': 500, 'window': 3600}  # 500 requests per hour

    def get_queryset(self):
        """
        Personaliza el queryset para incluir filtro de stock bajo
        """
        queryset = super().get_queryset()
        stock_bajo = self.request.query_params.get('stock_bajo', None)
        
        if stock_bajo and stock_bajo.lower() == 'true':
            # Filtrar productos donde stock_actual <= stock_minimo
            queryset = queryset.filter(stock_actual__lte=models.F('stock_minimo'))
        
        return queryset

    @extend_schema(
        summary="Ajustar stock",
        description="Ajusta el stock de un producto específico",
        request={
            'type': 'object',
            'properties': {
                'cantidad': {'type': 'integer', 'description': 'Cantidad a ajustar (positiva o negativa)'},
                'motivo': {'type': 'string', 'description': 'Motivo del ajuste'}
            },
            'required': ['cantidad']
        }
    )
    @action(detail=True, methods=['patch'])
    def ajustar_stock(self, request, pk=None):
        """
        Acción personalizada para ajustar el stock de un producto
        """
        producto = self.get_object()
        cantidad = request.data.get('cantidad')
        motivo = request.data.get('motivo', '')
        
        if cantidad is None:
            return Response(
                {'error': 'El campo cantidad es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cantidad = int(cantidad)
        except ValueError:
            return Response(
                {'error': 'La cantidad debe ser un número entero'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nuevo_stock = producto.stock_actual + cantidad
        
        if nuevo_stock < 0:
            return Response(
                {'error': 'El stock no puede ser negativo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        producto.stock_actual = nuevo_stock
        if motivo:
            observacion = f"Ajuste de stock: {cantidad:+d} unidades. Motivo: {motivo}"
            producto.observaciones = f"{producto.observaciones}\n{observacion}" if producto.observaciones else observacion
        producto.save()
        
        serializer = self.get_serializer(producto)
        return Response(serializer.data)

    @extend_schema(
        summary="Productos con stock bajo",
        description="Lista productos con stock actual menor o igual al stock mínimo"
    )
    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        """
        Acción para obtener productos con stock bajo
        """
        from django.db import models
        productos_stock_bajo = self.queryset.filter(stock_actual__lte=models.F('stock_minimo'))
        serializer = self.get_serializer(productos_stock_bajo, many=True)
        return Response({
            'count': productos_stock_bajo.count(),
            'productos': serializer.data
        })

    @extend_schema(
        summary="Estadísticas de inventario",
        description="Obtiene estadísticas generales del inventario de otros productos"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de otros productos
        """
        from django.db import models
        from django.db.models import Sum, Avg, Count
        
        total_productos = self.queryset.count()
        total_stock = self.queryset.aggregate(Sum('stock_actual'))['stock_actual__sum'] or 0
        valor_total = self.queryset.aggregate(
            total=Sum(models.F('precio_unitario') * models.F('stock_actual'))
        )['total'] or 0
        
        productos_stock_bajo = self.queryset.filter(stock_actual__lte=models.F('stock_minimo')).count()
        
        # Estadísticas por categoría
        stats_categorias = self.queryset.values('categoria').annotate(
            total=Count('id'),
            stock_total=Sum('stock_actual')
        ).order_by('-total')
        
        return Response({
            'total_productos': total_productos,
            'total_stock': total_stock,
            'valor_total_inventario': float(valor_total),
            'productos_stock_bajo': productos_stock_bajo,
            'porcentaje_stock_bajo': round((productos_stock_bajo / total_productos * 100) if total_productos > 0 else 0, 2),
            'por_categoria': list(stats_categorias)
        })
