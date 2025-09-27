from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from django.db.models import Count, Sum, Q, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta

from .models import TipoTrabajo, Servicio, ESTADO_SERVICIO_CHOICES
from .serializers import (
    TipoTrabajoSerializer, 
    ServicioSerializer, 
    ServicioListSerializer,
    ServicioCreateSerializer,
    ServicioFlexibleSerializer
)
from .filters import TipoTrabajoFilter, ServicioFilter
from todoapi.utils.permissions import IsAdminOrSupervisor
from todoapi.utils.viewsets import AdvancedSearchViewSet, BusinessIntelligenceViewSet


@extend_schema_view(
    list=extend_schema(
        summary="Listar tipos de trabajo",
        description="Lista todos los tipos de trabajo con filtros opcionales",
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en nombre y descripción'),
        ]
    ),
    create=extend_schema(
        summary="Crear tipo de trabajo",
        description="Crea un nuevo tipo de trabajo en el sistema"
    ),
    retrieve=extend_schema(
        summary="Obtener tipo de trabajo",
        description="Obtiene los detalles de un tipo de trabajo específico"
    ),
    update=extend_schema(
        summary="Actualizar tipo de trabajo",
        description="Actualiza completamente un tipo de trabajo"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente tipo de trabajo",
        description="Actualiza parcialmente un tipo de trabajo"
    ),
    destroy=extend_schema(
        summary="Eliminar tipo de trabajo",
        description="Desactiva un tipo de trabajo del sistema"
    )
)
class TipoTrabajoViewSet(AdvancedSearchViewSet):
    """
    ViewSet para gestionar tipos de trabajo con búsqueda avanzada.
    """
    queryset = TipoTrabajo.objects.all()
    serializer_class = TipoTrabajoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TipoTrabajoFilter
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['created_at', 'nombre', 'precio_base']
    ordering = ['-created_at']
    search_config_key = 'services.tipo_trabajo'

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva el tipo de trabajo en lugar de eliminarlo
        """
        instance.is_active = False
        instance.save()

    @extend_schema(
        summary="Servicios del tipo de trabajo",
        description="Lista todos los servicios de un tipo de trabajo específico"
    )
    @action(detail=True, methods=['get'])
    def servicios(self, request, pk=None):
        """
        Acción para obtener los servicios de un tipo de trabajo
        """
        tipo_trabajo = self.get_object()
        servicios = tipo_trabajo.servicios.filter(is_active=True)
        
        # Estadísticas básicas
        total_servicios = servicios.count()
        servicios_completados = servicios.filter(estado_servicio='completado').count()
        ingresos_totales = servicios.filter(estado_servicio='completado').aggregate(
            total=Sum('precio')
        )['total'] or 0
        
        return Response({
            'tipo_trabajo': tipo_trabajo.get_nombre_display(),
            'total_servicios': total_servicios,
            'servicios_completados': servicios_completados,
            'servicios_pendientes': servicios.filter(estado_servicio='pendiente').count(),
            'ingresos_totales': float(ingresos_totales),
            'porcentaje_completados': round(
                (servicios_completados / total_servicios * 100) if total_servicios > 0 else 0, 2
            )
        })

    @extend_schema(
        summary="Activar/Desactivar tipo de trabajo",
        description="Cambia el estado activo de un tipo de trabajo",
        request={
            'type': 'object',
            'properties': {
                'is_active': {'type': 'boolean', 'description': 'Estado activo del tipo de trabajo'}
            },
            'required': ['is_active']
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Acción para activar/desactivar un tipo de trabajo
        """
        tipo_trabajo = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tipo_trabajo.is_active = bool(is_active)
        tipo_trabajo.save()
        
        serializer = self.get_serializer(tipo_trabajo)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas de tipos de trabajo",
        description="Obtiene estadísticas generales de los tipos de trabajo"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de tipos de trabajo
        """
        total = self.queryset.count()
        activos = self.queryset.filter(is_active=True).count()
        inactivos = total - activos
        
        # Tipos más utilizados
        tipos_mas_usados = self.queryset.annotate(
            servicios_count=Count('servicios', filter=Q(servicios__is_active=True))
        ).order_by('-servicios_count')[:5]
        
        top_tipos = []
        for tipo in tipos_mas_usados:
            top_tipos.append({
                'nombre': tipo.get_nombre_display(),
                'servicios': tipo.servicios_count
            })
        
        return Response({
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'porcentaje_activos': round((activos / total * 100) if total > 0 else 0, 2),
            'tipos_mas_utilizados': top_tipos
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar servicios",
        description="Lista todos los servicios con filtros opcionales",
        parameters=[
            OpenApiParameter('estado_servicio', OpenApiTypes.STR, description='Filtrar por estado del servicio'),
            OpenApiParameter('tipo_trabajo', OpenApiTypes.INT, description='Filtrar por tipo de trabajo'),
            OpenApiParameter('tecnico', OpenApiTypes.INT, description='Filtrar por técnico'),
            OpenApiParameter('cliente', OpenApiTypes.INT, description='Filtrar por cliente'),
            OpenApiParameter('fecha_desde', OpenApiTypes.DATE, description='Filtrar desde fecha (YYYY-MM-DD)'),
            OpenApiParameter('fecha_hasta', OpenApiTypes.DATE, description='Filtrar hasta fecha (YYYY-MM-DD)'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en descripción y observaciones'),
        ]
    ),
    create=extend_schema(
        summary="Crear servicio",
        description="Crea un nuevo servicio en el sistema"
    ),
    retrieve=extend_schema(
        summary="Obtener servicio",
        description="Obtiene los detalles de un servicio específico"
    ),
    update=extend_schema(
        summary="Actualizar servicio",
        description="Actualiza completamente un servicio"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente servicio",
        description="Actualiza parcialmente un servicio"
    ),
    destroy=extend_schema(
        summary="Eliminar servicio",
        description="Desactiva un servicio del sistema"
    )
)
class ServicioViewSet(BusinessIntelligenceViewSet):
    """
    ViewSet para gestionar servicios con inteligencia de negocio.
    """
    queryset = Servicio.objects.select_related(
        'tipo_trabajo', 'tecnico', 'cliente', 'unidad', 'gps', 'sim_card'
    ).all()
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServicioFilter
    search_fields = ['descripcion', 'observaciones', 'unidad__placa', 'cliente__nombre', 'numero_orden']
    ordering_fields = ['fecha', 'precio', 'estado_servicio', 'created_at', 'fecha_solicitud', 'fecha_programada', 'costo_total']
    ordering = ['-fecha']
    search_config_key = 'services.servicio'

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == 'list':
            return ServicioListSerializer
        elif self.action == 'create':
            return ServicioCreateSerializer
        return ServicioSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha__date__gte=fecha_desde)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha__date__lte=fecha_hasta)
            except ValueError:
                pass
        
        return queryset

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva el servicio en lugar de eliminarlo
        """
        instance.is_active = False
        instance.save()

    @extend_schema(
        summary="Cambiar estado del servicio",
        description="Cambia el estado de un servicio específico",
        request={
            'type': 'object',
            'properties': {
                'estado_servicio': {
                    'type': 'string', 
                    'enum': [choice[0] for choice in ESTADO_SERVICIO_CHOICES],
                    'description': 'Nuevo estado del servicio'
                },
                'observaciones': {
                    'type': 'string',
                    'description': 'Observaciones adicionales sobre el cambio de estado'
                }
            },
            'required': ['estado_servicio']
        }
    )
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Acción para cambiar el estado de un servicio
        """
        servicio = self.get_object()
        nuevo_estado = request.data.get('estado_servicio')
        observaciones_adicionales = request.data.get('observaciones', '')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado_servicio es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el estado sea válido
        estados_validos = [choice[0] for choice in ESTADO_SERVICIO_CHOICES]
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Estados válidos: {estados_validos}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado y observaciones
        servicio.estado_servicio = nuevo_estado
        if observaciones_adicionales:
            if servicio.observaciones:
                servicio.observaciones += f"\n\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {observaciones_adicionales}"
            else:
                servicio.observaciones = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {observaciones_adicionales}"
        
        servicio.save()
        
        serializer = self.get_serializer(servicio)
        return Response(serializer.data)

    @extend_schema(
        summary="Activar/Desactivar servicio",
        description="Cambia el estado activo de un servicio",
        request={
            'type': 'object',
            'properties': {
                'is_active': {'type': 'boolean', 'description': 'Estado activo del servicio'}
            },
            'required': ['is_active']
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Acción para activar/desactivar un servicio
        """
        servicio = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicio.is_active = bool(is_active)
        servicio.save()
        
        serializer = self.get_serializer(servicio)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas de servicios",
        description="Obtiene estadísticas generales de los servicios"
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Acción para obtener estadísticas de servicios
        """
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total = queryset.count()
        activos = queryset.filter(is_active=True).count()
        
        # Estadísticas por estado
        stats_por_estado = {}
        for estado, nombre in ESTADO_SERVICIO_CHOICES:
            count = queryset.filter(estado_servicio=estado).count()
            stats_por_estado[estado] = {
                'nombre': nombre,
                'cantidad': count,
                'porcentaje': round((count / total * 100) if total > 0 else 0, 2)
            }
        
        # Ingresos totales y promedio
        servicios_completados = queryset.filter(estado_servicio='completado')
        ingresos_totales = servicios_completados.aggregate(total=Sum('precio'))['total'] or 0
        precio_promedio = servicios_completados.aggregate(promedio=Avg('precio'))['promedio'] or 0
        
        # Servicios por mes (últimos 6 meses)
        from django.utils import timezone
        hoy = timezone.now().date()
        hace_6_meses = hoy - timedelta(days=180)
        
        servicios_por_mes = queryset.filter(
            fecha__date__gte=hace_6_meses
        ).extra(
            select={'mes': "DATE_FORMAT(fecha, '%%Y-%%m')"}
        ).values('mes').annotate(
            cantidad=Count('id'),
            ingresos=Sum('precio', filter=Q(estado_servicio='completado'))
        ).order_by('mes')
        
        return Response({
            'total': total,
            'activos': activos,
            'inactivos': total - activos,
            'por_estado': stats_por_estado,
            'ingresos_totales': float(ingresos_totales),
            'precio_promedio': float(precio_promedio),
            'servicios_por_mes': list(servicios_por_mes)
        })

    @extend_schema(
        summary="Dashboard de servicios",
        description="Obtiene datos para el dashboard de servicios (últimos 30 días)"
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Acción para obtener datos del dashboard de servicios
        """
        from django.utils import timezone
        
        # Últimos 30 días
        hoy = timezone.now().date()
        hace_30_dias = hoy - timedelta(days=30)
        
        servicios_recientes = self.get_queryset().filter(
            fecha__date__gte=hace_30_dias
        )
        
        # Métricas principales
        total_servicios = servicios_recientes.count()
        servicios_completados = servicios_recientes.filter(estado_servicio='completado').count()
        servicios_pendientes = servicios_recientes.filter(estado_servicio='pendiente').count()
        ingresos_mes = servicios_recientes.filter(
            estado_servicio='completado'
        ).aggregate(total=Sum('precio'))['total'] or 0
        
        # Top técnicos
        top_tecnicos = servicios_recientes.values(
            'tecnico__first_name', 'tecnico__last_name'
        ).annotate(
            servicios_count=Count('id'),
            servicios_completados=Count('id', filter=Q(estado_servicio='completado'))
        ).order_by('-servicios_count')[:5]
        
        # Top clientes
        top_clientes = servicios_recientes.values(
            'cliente__nombre', 'cliente__ruc'
        ).annotate(
            servicios_count=Count('id'),
            total_gastado=Sum('precio', filter=Q(estado_servicio='completado'))
        ).order_by('-servicios_count')[:5]
        
        return Response({
            'periodo': f'{hace_30_dias} a {hoy}',
            'metricas_principales': {
                'total_servicios': total_servicios,
                'servicios_completados': servicios_completados,
                'servicios_pendientes': servicios_pendientes,
                'tasa_completados': round(
                    (servicios_completados / total_servicios * 100) if total_servicios > 0 else 0, 2
                ),
                'ingresos_mes': float(ingresos_mes)
            },
            'top_tecnicos': list(top_tecnicos),
            'top_clientes': list(top_clientes)
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar servicios flexibles",
        description="Lista servicios con validaciones flexibles según el tipo de trabajo",
        parameters=[
            OpenApiParameter('estado_servicio', OpenApiTypes.STR, description='Filtrar por estado del servicio'),
            OpenApiParameter('tipo_trabajo', OpenApiTypes.INT, description='Filtrar por tipo de trabajo'),
            OpenApiParameter('tecnico', OpenApiTypes.INT, description='Filtrar por técnico'),
            OpenApiParameter('cliente', OpenApiTypes.INT, description='Filtrar por cliente'),
            OpenApiParameter('sin_equipos', OpenApiTypes.BOOL, description='Filtrar servicios sin equipos asignados'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en descripción y observaciones'),
        ]
    ),
    create=extend_schema(
        summary="Crear servicio flexible",
        description="Crea un servicio con validaciones flexibles según el tipo de trabajo",
        request=ServicioFlexibleSerializer,
        examples=[
            OpenApiExample(
                name='Mantenimiento sin equipos (tipo otro)',
                summary='Servicio de mantenimiento que no requiere cambio de equipos usando tipo "otro"',
                value={
                    'fecha': '2024-01-15T10:00:00Z',
                    'tipo_trabajo': 4,  # Tipo "otro"
                    'tecnico_dni': '12345678',
                    'cliente': 1,
                    'unidad': 1,
                    'descripcion': 'Mantenimiento preventivo del sistema GPS existente',
                    'observaciones': 'Mantenimiento sin cambio de equipos - Revisión completa del GPS instalado, limpieza de conexiones, verificación de antena y calibración de señal. No requiere equipos nuevos.',
                    'precio': 150.00,
                    'requiere_gps': False,
                    'requiere_sim_card': False,
                    'motivo_sin_equipos': 'Mantenimiento de GPS ya instalado, no requiere cambio de equipos'
                },
                request_only=True
            ),
            OpenApiExample(
                name='Instalación de accesorio (tipo otro)',
                summary='Instalación de accesorio sin GPS ni SIM usando tipo "otro"',
                value={
                    'fecha': '2024-01-16T14:00:00Z',
                    'tipo_trabajo': 4,  # Tipo "otro"
                    'tecnico_dni': '87654321',
                    'cliente': 2,
                    'unidad': 2,
                    'descripcion': 'Instalación de cámara de seguridad adicional',
                    'observaciones': 'Instalación de cámara de seguridad adicional en vehículo - Sistema independiente que no requiere GPS ni SIM Card. Incluye cableado, montaje y configuración básica.',
                    'precio': 200.00,
                    'requiere_gps': False,
                    'requiere_sim_card': False,
                    'motivo_sin_equipos': 'Instalación de accesorio independiente, no requiere GPS ni SIM'
                },
                request_only=True
            ),
            OpenApiExample(
                name='Instalación nueva completa',
                summary='Instalación nueva con todos los equipos',
                value={
                    'fecha': '2024-01-17T09:00:00Z',
                    'tipo_trabajo': 1,  # Instalación nueva
                    'tecnico_dni': '11223344',
                    'cliente': 3,
                    'unidad': 3,
                    'gps': 1,
                    'sim_card': 1,
                    'descripcion': 'Instalación completa de sistema GPS con rastreo satelital',
                    'observaciones': 'Instalación completa con GPS y SIM Card nuevos, configuración de plataforma de monitoreo y pruebas de funcionamiento.',
                    'precio': 500.00,
                    'requiere_gps': True,
                    'requiere_sim_card': True
                },
                request_only=True
            ),
            OpenApiExample(
                name='Revisión técnica (tipo otro)',
                summary='Diagnóstico técnico sin cambio de equipos',
                value={
                    'fecha': '2024-01-18T11:00:00Z',
                    'tipo_trabajo': 4,  # Tipo "otro"
                    'tecnico_dni': '55667788',
                    'cliente': 4,
                    'unidad': 4,
                    'descripcion': 'Diagnóstico de fallas en el sistema de rastreo',
                    'observaciones': 'Revisión técnica para diagnóstico de fallas - Análisis de conectividad, verificación de señal GPS, pruebas de transmisión de datos. Servicio de diagnóstico sin instalación de equipos.',
                    'precio': 100.00,
                    'requiere_gps': False,
                    'requiere_sim_card': False,
                    'motivo_sin_equipos': 'Servicio de diagnóstico técnico, no requiere equipos nuevos'
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Obtener servicio flexible",
        description="Obtiene los detalles de un servicio flexible específico"
    ),
    update=extend_schema(
        summary="Actualizar servicio flexible",
        description="Actualiza completamente un servicio flexible"
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente servicio flexible",
        description="Actualiza parcialmente un servicio flexible"
    )
)
class ServicioFlexibleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar servicios con validaciones flexibles según el tipo de trabajo.
    
    Este ViewSet permite crear servicios con diferentes requerimientos de equipos:
    - Mantenimiento sin cambio de equipos: No requiere GPS ni SIM Card
    - Instalación de accesorios: No requiere GPS ni SIM Card  
    - Revisión técnica: Solo requiere descripción detallada
    - Configuración de software: Puede requerir GPS pero no SIM Card
    - Instalación nueva: Requiere validación de equipos según necesidad
    """
    
    queryset = Servicio.objects.select_related(
        'tipo_trabajo', 'tecnico', 'cliente', 'unidad', 'gps', 'sim_card'
    ).all()
    serializer_class = ServicioFlexibleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServicioFilter
    search_fields = ['descripcion', 'observaciones', 'unidad__placa', 'cliente__nombre']
    ordering_fields = ['fecha', 'precio', 'estado_servicio', 'created_at']
    ordering = ['-fecha']
    
    def get_queryset(self):
        """
        Optionally filter services by equipment assignment.
        """
        queryset = super().get_queryset()
        
        # Filter by services without equipment if requested
        sin_equipos = self.request.query_params.get('sin_equipos', None)
        if sin_equipos is not None:
            if sin_equipos.lower() in ['true', '1']:
                queryset = queryset.filter(gps__isnull=True, sim_card__isnull=True)
            elif sin_equipos.lower() in ['false', '0']:
                queryset = queryset.filter(Q(gps__isnull=False) | Q(sim_card__isnull=False))
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create service with additional logging for flexible services.
        """
        # Log the type of service being created
        tipo_trabajo = serializer.validated_data.get('tipo_trabajo')
        has_gps = bool(serializer.validated_data.get('gps'))
        has_sim_card = bool(serializer.validated_data.get('sim_card'))
        
        # Additional validation for business rules
        if tipo_trabajo and tipo_trabajo.nombre == 'instalacion_nueva':
            if not has_gps and not has_sim_card:
                # This is allowed but should be logged for review
                pass
        
        serializer.save()
    
    @extend_schema(
        summary="Validar requerimientos de equipos",
        description="Valida si un tipo de trabajo requiere equipos específicos",
        parameters=[
            OpenApiParameter('tipo_trabajo_id', OpenApiTypes.INT, description='ID del tipo de trabajo a validar')
        ]
    )
    @action(detail=False, methods=['get'])
    def validar_requerimientos(self, request):
        """
        Endpoint para validar requerimientos de equipos según el tipo de trabajo.
        """
        tipo_trabajo_id = request.query_params.get('tipo_trabajo_id')
        
        if not tipo_trabajo_id:
            return Response(
                {'error': 'Se requiere el parámetro tipo_trabajo_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tipo_trabajo = TipoTrabajo.objects.get(id=tipo_trabajo_id, is_active=True)
        except TipoTrabajo.DoesNotExist:
            return Response(
                {'error': 'Tipo de trabajo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Define requirements based on service type
        requerimientos = {
            'instalacion_nueva': {
                'gps_requerido': True,
                'sim_card_requerido': True,
                'puede_omitir_gps': True,
                'puede_omitir_sim': True,
                'requiere_justificacion': True,
                'descripcion': 'Instalación nueva típicamente requiere GPS y SIM Card, pero puede omitirse con justificación'
            },
            'mantenimiento_preventivo': {
                'gps_requerido': False,
                'sim_card_requerido': False,
                'puede_omitir_gps': True,
                'puede_omitir_sim': True,
                'requiere_justificacion': False,
                'descripcion': 'Mantenimiento preventivo no requiere equipos nuevos por defecto'
            },
            'mantenimiento_correctivo': {
                'gps_requerido': False,
                'sim_card_requerido': False,
                'puede_omitir_gps': True,
                'puede_omitir_sim': True,
                'requiere_justificacion': False,
                'descripcion': 'Mantenimiento correctivo puede requerir equipos según el problema'
            },
            'otro': {
                'gps_requerido': False,
                'sim_card_requerido': False,
                'puede_omitir_gps': True,
                'puede_omitir_sim': True,
                'requiere_justificacion': True,
                'requiere_observaciones_detalladas': True,
                'observaciones_minimas': 10,
                'descripcion': 'Tipo de trabajo personalizado. Use observaciones para especificar: mantenimiento sin equipos, instalación de accesorios, revisión técnica, configuración de software, etc.',
                'ejemplos_observaciones': [
                    'Mantenimiento preventivo sin cambio de equipos - Revisión y limpieza del GPS existente',
                    'Instalación de cámara de seguridad adicional - No requiere GPS ni SIM Card',
                    'Revisión técnica para diagnóstico de fallas en el sistema de rastreo',
                    'Configuración de software del GPS - Actualización de parámetros de reporte',
                    'Reparación menor de cableado - Mantenimiento correctivo sin cambio de equipos'
                ]
            }
        }
        
        requerimiento = requerimientos.get(
            tipo_trabajo.nombre, 
            requerimientos['otro']
        )
        
        return Response({
            'tipo_trabajo': {
                'id': tipo_trabajo.id,
                'nombre': tipo_trabajo.nombre,
                'nombre_display': tipo_trabajo.get_nombre_display(),
                'descripcion': tipo_trabajo.descripcion
            },
            'requerimientos': requerimiento,
            'campos_flexibles': [
                'gps',
                'sim_card',
                'motivo_sin_equipos',
                'requiere_gps',
                'requiere_sim_card'
            ]
        })
    
    @extend_schema(
        summary="Estadísticas de servicios flexibles",
        description="Obtiene estadísticas de servicios agrupados por tipo y requerimientos de equipos"
    )
    @action(detail=False, methods=['get'])
    def estadisticas_flexibles(self, request):
        """
        Estadísticas específicas para servicios flexibles.
        """
        queryset = self.get_queryset()
        
        # Estadísticas por tipo de trabajo
        stats_por_tipo = queryset.values(
            'tipo_trabajo__nombre'
        ).annotate(
            total_servicios=Count('id'),
            con_gps=Count('id', filter=Q(gps__isnull=False)),
            con_sim_card=Count('id', filter=Q(sim_card__isnull=False)),
            sin_equipos=Count('id', filter=Q(gps__isnull=True, sim_card__isnull=True)),
            precio_promedio=Avg('precio')
        ).order_by('-total_servicios')
        
        # Servicios sin equipos por mes (últimos 6 meses)
        from django.utils import timezone
        hace_6_meses = timezone.now().date() - timedelta(days=180)
        
        # Usar función compatible con SQLite para tests
        from django.conf import settings
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            servicios_sin_equipos_mes = queryset.filter(
                fecha__date__gte=hace_6_meses,
                gps__isnull=True,
                sim_card__isnull=True
            ).extra(
                select={'mes': "strftime('%%Y-%%m', fecha)"}
            ).values('mes').annotate(
                count=Count('id')
            ).order_by('mes')
        else:
            servicios_sin_equipos_mes = queryset.filter(
                fecha__date__gte=hace_6_meses,
                gps__isnull=True,
                sim_card__isnull=True
            ).extra(
                select={'mes': "DATE_FORMAT(fecha, '%%Y-%%m')"}
            ).values('mes').annotate(
                count=Count('id')
            ).order_by('mes')
        
        # Agregar nombre_display a las estadísticas por tipo
        tipos_trabajo = {tipo.nombre: tipo for tipo in TipoTrabajo.objects.all()}
        stats_por_tipo_con_display = []
        for stat in stats_por_tipo:
            tipo_nombre = stat['tipo_trabajo__nombre']
            tipo_obj = tipos_trabajo.get(tipo_nombre)
            stat_con_display = dict(stat)
            stat_con_display['nombre_display'] = tipo_obj.get_nombre_display() if tipo_obj else tipo_nombre
            stats_por_tipo_con_display.append(stat_con_display)

        return Response({
            'resumen_general': {
                'total_servicios': queryset.count(),
                'servicios_con_gps': queryset.filter(gps__isnull=False).count(),
                'servicios_con_sim': queryset.filter(sim_card__isnull=False).count(),
                'servicios_sin_equipos': queryset.filter(gps__isnull=True, sim_card__isnull=True).count(),
                'servicios_completos': queryset.filter(gps__isnull=False, sim_card__isnull=False).count()
            },
            'estadisticas_por_tipo': stats_por_tipo_con_display,
            'servicios_sin_equipos_por_mes': list(servicios_sin_equipos_mes)
        })
