"""
ViewSets para la aplicación de ventas.
Maneja las operaciones CRUD y acciones personalizadas para Ventas.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Ventas, ESTADO_VENTA_CHOICES, TIPO_PAGO_CHOICES
from .serializers import (
    VentasSerializer, VentasListSerializer, VentasCreateSerializer,
    VentasReportSerializer, VentasStatsSerializer
)
from .filters import VentaFilter
from todoapi.utils.permissions import IsAdminOrSupervisor
from todoapi.utils.viewsets import AdvancedSearchViewSet, BusinessIntelligenceViewSet
from todoapi.utils.cache import cache_response, CacheManager
from todoapi.utils.rate_limiting import APIRateLimitMixin, rate_limit


class VentasViewSet(APIRateLimitMixin, BusinessIntelligenceViewSet):
    """
    ViewSet para gestionar las ventas del sistema con inteligencia de negocio.
    
    Proporciona operaciones CRUD completas para ventas con:
    - Cálculos automáticos de IGV
    - Filtros por estado, cliente, fecha, tipo de pago
    - Búsqueda por número de factura, cliente, descripción
    - Acciones para cambiar estado y generar reportes
    - Estadísticas y dashboard de ventas
    """
    # Optimized queryset with select_related for ForeignKey relationships
    queryset = Ventas.objects.select_related(
        'cliente',  # Cliente relationship
        'unidad'    # Unidad relationship
    ).all()
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Configuración de filtros
    filterset_class = VentaFilter
    
    # Campos de búsqueda
    search_fields = ['numero_factura', 'cliente__nombre', 'cliente__ruc', 
                    'unidad__placa', 'descripcion', 'numero_operacion']
    
    # Campos de ordenamiento
    ordering_fields = ['fecha_generacion_factura', 'mes', 'precio', 'total', 'estado']
    ordering = ['-fecha_generacion_factura']
    
    # Rate limiting configuration
    rate_limit_scope = 'sales'
    rate_limit_config = {'requests': 200, 'window': 3600}  # 200 requests per hour
    search_config_key = 'sales.ventas'

    def _invalidate_sales_cache(self):
        """Invalidate sales-related cache entries."""
        try:
            CacheManager.invalidate_model_cache('sales.ventas')
            # Also invalidate specific cache patterns
            from todoapi.utils.cache import invalidate_cache_pattern
            invalidate_cache_pattern('sales_stats')
            invalidate_cache_pattern('sales_dashboard')
            invalidate_cache_pattern('sales_list')
        except (NotImplementedError, Exception) as e:
            # Cache not available (e.g., in tests), continue without caching
            pass

    @rate_limit(requests_per_hour=50, requests_per_minute=5)
    def create(self, request, *args, **kwargs):
        """
        Create a new sale with rate limiting.
        Limited to 50 sales per hour and 5 per minute per user.
        """
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Override to invalidate cache after creating a sale."""
        super().perform_create(serializer)
        self._invalidate_sales_cache()

    def perform_update(self, serializer):
        """Override to invalidate cache after updating a sale."""
        super().perform_update(serializer)
        self._invalidate_sales_cache()

    def perform_destroy(self, instance):
        """
        Soft delete: desactiva la venta en lugar de eliminarla físicamente.
        """
        instance.is_active = False
        instance.save()
        self._invalidate_sales_cache()

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'list':
            return VentasListSerializer
        elif self.action == 'create':
            return VentasCreateSerializer
        elif self.action in ['reporte', 'exportar']:
            return VentasReportSerializer
        elif self.action in ['estadisticas', 'dashboard']:
            return VentasStatsSerializer
        return VentasSerializer

    def get_permissions(self):
        """
        Permisos específicos por acción.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 
                          'cambiar_estado', 'anular_venta']:
            permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Cambiar estado de venta",
        description="Permite cambiar el estado de una venta específica",
        parameters=[
            OpenApiParameter(
                name='nuevo_estado',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=[choice[0] for choice in ESTADO_VENTA_CHOICES],
                description="Nuevo estado para la venta"
            )
        ],
        examples=[
            OpenApiExample(
                'Marcar como pagado',
                value={'nuevo_estado': 'pagado'},
                request_only=True,
            ),
            OpenApiExample(
                'Marcar como vencido',
                value={'nuevo_estado': 'vencido'},
                request_only=True,
            ),
        ]
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOrSupervisor])
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de una venta específica.
        """
        venta = self.get_object()
        nuevo_estado = request.query_params.get('nuevo_estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Debe proporcionar el parámetro nuevo_estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estados_validos = [choice[0] for choice in ESTADO_VENTA_CHOICES]
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Estados válidos: {estados_validos}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estado_anterior = venta.estado
        venta.estado = nuevo_estado
        venta.save()
        
        # Invalidate cache after state change
        self._invalidate_sales_cache()
        
        return Response({
            'message': f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            'venta_id': venta.id,
            'estado_anterior': estado_anterior,
            'estado_actual': nuevo_estado
        })

    @extend_schema(
        summary="Anular venta",
        description="Anula una venta y la marca como inactiva",
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOrSupervisor])
    def anular_venta(self, request, pk=None):
        """
        Anula una venta específica.
        """
        venta = self.get_object()
        
        if venta.estado == 'anulado':
            return Response(
                {'error': 'La venta ya está anulada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        venta.estado = 'anulado'
        venta.is_active = False
        venta.save()
        
        # Invalidate cache after cancellation
        self._invalidate_sales_cache()
        
        return Response({
            'message': 'Venta anulada exitosamente',
            'venta_id': venta.id,
            'numero_factura': venta.numero_factura
        })

    @extend_schema(
        summary="Activar/desactivar venta",
        description="Alterna el estado activo/inactivo de una venta",
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOrSupervisor])
    def toggle_active(self, request, pk=None):
        """
        Activa o desactiva una venta.
        """
        venta = self.get_object()
        venta.is_active = not venta.is_active
        venta.save()
        
        # Invalidate cache after status change
        self._invalidate_sales_cache()
        
        estado = "activada" if venta.is_active else "desactivada"
        return Response({
            'message': f'Venta {estado} exitosamente',
            'venta_id': venta.id,
            'is_active': venta.is_active
        })

    @extend_schema(
        summary="Estadísticas de ventas",
        description="Obtiene estadísticas generales de ventas con filtros opcionales",
        parameters=[
            OpenApiParameter(
                name='mes',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filtrar por mes específico (YYYY-MM-DD)"
            ),
            OpenApiParameter(
                name='cliente',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar por cliente específico (ID)"
            ),
            OpenApiParameter(
                name='estado',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por estado específico"
            ),
        ]
    )
    @cache_response(timeout=600, key_prefix='sales_stats')  # Cache for 10 minutes
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas de ventas con filtros opcionales.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Aplicar filtros adicionales
        mes = request.query_params.get('mes')
        cliente = request.query_params.get('cliente')
        estado = request.query_params.get('estado')
        
        if mes:
            try:
                fecha_mes = datetime.strptime(mes, '%Y-%m-%d').date()
                queryset = queryset.filter(mes=fecha_mes)
            except ValueError:
                pass
        
        if cliente:
            queryset = queryset.filter(cliente_id=cliente)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Calcular estadísticas
        stats = queryset.aggregate(
            total_ventas=Sum('total'),
            total_igv=Sum('igv'),
            total_importe=Sum('importe'),
            cantidad_ventas=Count('id'),
            promedio_venta=Avg('total')
        )
        
        # Ventas por estado
        ventas_por_estado = {}
        for estado_choice in ESTADO_VENTA_CHOICES:
            estado_key = estado_choice[0]
            count = queryset.filter(estado=estado_key).count()
            ventas_por_estado[estado_key] = count
        
        # Ventas por tipo de pago
        ventas_por_tipo_pago = {}
        for tipo_choice in TIPO_PAGO_CHOICES:
            tipo_key = tipo_choice[0]
            count = queryset.filter(tipo_pago=tipo_key).count()
            ventas_por_tipo_pago[tipo_key] = count
        
        # Preparar respuesta
        stats_data = {
            'total_ventas': stats['total_ventas'] or Decimal('0.00'),
            'total_igv': stats['total_igv'] or Decimal('0.00'),
            'total_importe': stats['total_importe'] or Decimal('0.00'),
            'cantidad_ventas': stats['cantidad_ventas'] or 0,
            'promedio_venta': stats['promedio_venta'] or Decimal('0.00'),
            'ventas_por_estado': ventas_por_estado,
            'ventas_por_tipo_pago': ventas_por_tipo_pago,
        }
        
        if mes:
            stats_data['mes'] = fecha_mes
        if cliente:
            stats_data['cliente'] = cliente
        
        return Response(stats_data)

    @extend_schema(
        summary="Dashboard de ventas",
        description="Obtiene datos para el dashboard de ventas con métricas clave",
    )
    @cache_response(timeout=300, key_prefix='sales_dashboard')  # Cache for 5 minutes
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Obtiene datos para el dashboard de ventas.
        """
        # Ventas del mes actual
        mes_actual = timezone.now().date().replace(day=1)
        ventas_mes = self.get_queryset().filter(mes=mes_actual)
        
        # Ventas pendientes
        ventas_pendientes = self.get_queryset().filter(estado='pendiente')
        
        # Ventas vencidas
        ventas_vencidas = self.get_queryset().filter(estado='vencido')
        
        # Top 5 clientes por ventas
        top_clientes = (
            self.get_queryset()
            .values('cliente__nombre', 'cliente__id')
            .annotate(
                total_ventas=Sum('total'),
                cantidad_ventas=Count('id')
            )
            .order_by('-total_ventas')[:5]
        )
        
        # Ventas por mes (últimos 6 meses)
        ventas_por_mes = []
        for i in range(6):
            fecha = timezone.now().date().replace(day=1)
            if i > 0:
                if fecha.month > i:
                    fecha = fecha.replace(month=fecha.month - i)
                else:
                    year = fecha.year - 1
                    month = 12 - (i - fecha.month)
                    fecha = fecha.replace(year=year, month=month)
            
            ventas_mes_data = self.get_queryset().filter(mes=fecha).aggregate(
                total=Sum('total'),
                cantidad=Count('id')
            )
            
            ventas_por_mes.append({
                'mes': fecha.strftime('%Y-%m'),
                'total': ventas_mes_data['total'] or Decimal('0.00'),
                'cantidad': ventas_mes_data['cantidad'] or 0
            })
        
        dashboard_data = {
            'ventas_mes_actual': {
                'total': ventas_mes.aggregate(Sum('total'))['total__sum'] or Decimal('0.00'),
                'cantidad': ventas_mes.count()
            },
            'ventas_pendientes': {
                'total': ventas_pendientes.aggregate(Sum('total'))['total__sum'] or Decimal('0.00'),
                'cantidad': ventas_pendientes.count()
            },
            'ventas_vencidas': {
                'total': ventas_vencidas.aggregate(Sum('total'))['total__sum'] or Decimal('0.00'),
                'cantidad': ventas_vencidas.count()
            },
            'top_clientes': list(top_clientes),
            'ventas_por_mes': ventas_por_mes
        }
        
        return Response(dashboard_data)

    @extend_schema(
        summary="Reporte de ventas",
        description="Genera un reporte detallado de ventas con filtros",
    )
    @rate_limit(requests_per_hour=20, requests_per_minute=3)
    @action(detail=False, methods=['get'])
    def reporte(self, request):
        """
        Genera un reporte detallado de ventas.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = VentasReportSerializer(queryset, many=True)
        
        # Calcular totales del reporte
        totales = queryset.aggregate(
            total_ventas=Sum('total'),
            total_igv=Sum('igv'),
            total_importe=Sum('importe'),
            cantidad_ventas=Count('id')
        )
        
        return Response({
            'ventas': serializer.data,
            'totales': totales,
            'fecha_generacion': timezone.now(),
            'filtros_aplicados': dict(request.query_params)
        })
