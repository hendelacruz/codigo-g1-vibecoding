"""
ViewSets base con funcionalidades avanzadas de búsqueda y filtrado.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta

from .search_utils import (
    AdvancedSearchMixin, 
    NumericRangeFilter, 
    DateRangeFilter,
    SearchHighlighter,
    FilterValidation,
    PaginationHelper,
    SEARCH_CONFIGURATIONS
)


class AdvancedSearchViewSet(viewsets.ModelViewSet, AdvancedSearchMixin):
    """
    ViewSet base con capacidades avanzadas de búsqueda y filtrado.
    """
    
    # Configuración de búsqueda específica del modelo
    search_config_key = None  # Debe ser definido en las subclases
    
    def get_search_config(self):
        """
        Obtiene la configuración de búsqueda para el modelo actual.
        """
        if not self.search_config_key:
            return {}
        
        parts = self.search_config_key.split('.')
        config = SEARCH_CONFIGURATIONS
        
        for part in parts:
            config = config.get(part, {})
        
        return config
    
    def filter_queryset(self, queryset):
        """
        Aplica filtros avanzados al queryset.
        """
        queryset = super().filter_queryset(queryset)
        
        # Aplicar búsqueda avanzada si está disponible
        search_term = self.request.query_params.get('advanced_search')
        if search_term:
            queryset = self.apply_advanced_search(queryset, search_term)
        
        # Aplicar filtros de rango numérico
        queryset = self.apply_numeric_range_filters(queryset)
        
        # Aplicar filtros de rango de fecha
        queryset = self.apply_date_range_filters(queryset)
        
        return queryset
    
    def apply_advanced_search(self, queryset, search_term):
        """
        Aplica búsqueda avanzada usando la configuración del modelo.
        """
        config = self.get_search_config()
        search_fields = config.get('search_fields', [])
        
        if search_fields:
            search_query = self.build_search_query(search_fields, search_term)
            queryset = queryset.filter(search_query)
        
        return queryset
    
    def apply_numeric_range_filters(self, queryset):
        """
        Aplica filtros de rango numérico basados en parámetros de consulta.
        """
        numeric_filters = [
            ('precio_min', 'precio_max', 'precio_compra'),
            ('total_min', 'total_max', 'total'),
            ('cantidad_min', 'cantidad_max', 'cantidad'),
            ('stock_min', 'stock_max', 'stock_actual'),
        ]
        
        for min_param, max_param, field_name in numeric_filters:
            min_value = self.request.query_params.get(min_param)
            max_value = self.request.query_params.get(max_param)
            
            if min_value or max_value:
                try:
                    min_val = float(min_value) if min_value else None
                    max_val = float(max_value) if max_value else None
                    
                    if NumericRangeFilter.validate_range(min_val, max_val):
                        range_query = NumericRangeFilter.build_range_query(
                            field_name, min_val, max_val
                        )
                        queryset = queryset.filter(range_query)
                except (ValueError, TypeError):
                    continue
        
        return queryset
    
    def apply_date_range_filters(self, queryset):
        """
        Aplica filtros de rango de fecha basados en parámetros de consulta.
        """
        date_filters = [
            ('fecha_desde', 'fecha_hasta', 'created_at'),
            ('fecha_venta_desde', 'fecha_venta_hasta', 'fecha_venta'),
            ('fecha_solicitud_desde', 'fecha_solicitud_hasta', 'fecha_solicitud'),
            ('fecha_programada_desde', 'fecha_programada_hasta', 'fecha_programada'),
        ]
        
        for start_param, end_param, field_name in date_filters:
            start_date = self.request.query_params.get(start_param)
            end_date = self.request.query_params.get(end_param)
            
            if start_date or end_date:
                try:
                    start_val = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
                    end_val = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
                    
                    date_query = DateRangeFilter.build_date_range_query(
                        field_name, start_val, end_val
                    )
                    queryset = queryset.filter(date_query)
                except (ValueError, TypeError):
                    continue
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """
        Proporciona sugerencias de búsqueda basadas en el contenido existente.
        """
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'suggestions': []})
        
        config = self.get_search_config()
        search_fields = config.get('search_fields', [])
        
        suggestions = []
        
        for field in search_fields[:3]:  # Limitar a 3 campos para performance
            try:
                field_suggestions = self.get_queryset().filter(
                    **{f"{field}__icontains": query}
                ).values_list(field, flat=True).distinct()[:5]
                
                suggestions.extend([
                    {'field': field, 'value': suggestion}
                    for suggestion in field_suggestions if suggestion
                ])
            except:
                continue
        
        return Response({'suggestions': suggestions[:10]})
    
    @action(detail=False, methods=['get'])
    def advanced_stats(self, request):
        """
        Proporciona estadísticas avanzadas del modelo.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total_count': queryset.count(),
            'created_today': queryset.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'created_this_week': queryset.filter(
                created_at__gte=timezone.now().date() - timedelta(days=7)
            ).count(),
            'created_this_month': queryset.filter(
                created_at__gte=timezone.now().date() - timedelta(days=30)
            ).count(),
        }
        
        # Agregar estadísticas específicas si hay campos numéricos
        numeric_fields = ['precio', 'total', 'cantidad', 'stock_actual']
        for field in numeric_fields:
            if hasattr(self.get_queryset().model, field):
                try:
                    field_stats = queryset.aggregate(
                        avg=Avg(field),
                        min=Min(field),
                        max=Max(field),
                        sum=Sum(field)
                    )
                    stats[f'{field}_stats'] = field_stats
                except:
                    continue
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def export_filtered(self, request):
        """
        Exporta los datos filtrados en formato CSV.
        """
        import csv
        from django.http import HttpResponse
        
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_queryset().model._meta.model_name}_export.csv"'
        
        writer = csv.writer(response)
        
        # Escribir encabezados
        if queryset.exists():
            model = queryset.model
            field_names = [field.name for field in model._meta.fields]
            writer.writerow(field_names)
            
            # Escribir datos
            for obj in queryset[:1000]:  # Limitar a 1000 registros
                row = []
                for field_name in field_names:
                    value = getattr(obj, field_name, '')
                    if value is None:
                        value = ''
                    row.append(str(value))
                writer.writerow(row)
        
        return response
    
    def list(self, request, *args, **kwargs):
        """
        Lista con información adicional de paginación y filtros aplicados.
        """
        response = super().list(request, *args, **kwargs)
        
        # Agregar información adicional
        if hasattr(response, 'data') and isinstance(response.data, dict):
            # Información de filtros aplicados
            applied_filters = {}
            for key, value in request.query_params.items():
                if value and key not in ['page', 'page_size', 'ordering']:
                    applied_filters[key] = value
            
            response.data['applied_filters'] = applied_filters
            response.data['filter_count'] = len(applied_filters)
            
            # Información de búsqueda
            search_term = request.query_params.get('search') or request.query_params.get('advanced_search')
            if search_term:
                response.data['search_term'] = search_term
                response.data['search_applied'] = True
            else:
                response.data['search_applied'] = False
        
        return response


class BusinessIntelligenceViewSet(AdvancedSearchViewSet):
    """
    ViewSet con capacidades de inteligencia de negocio.
    """
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Estadísticas para dashboard de negocio.
        """
        queryset = self.get_queryset()
        now = timezone.now()
        
        # Estadísticas temporales
        stats = {
            'today': queryset.filter(created_at__date=now.date()).count(),
            'yesterday': queryset.filter(
                created_at__date=now.date() - timedelta(days=1)
            ).count(),
            'this_week': queryset.filter(
                created_at__gte=now.date() - timedelta(days=7)
            ).count(),
            'this_month': queryset.filter(
                created_at__gte=now.date() - timedelta(days=30)
            ).count(),
            'total': queryset.count(),
        }
        
        # Calcular tendencias
        last_week = queryset.filter(
            created_at__gte=now.date() - timedelta(days=14),
            created_at__lt=now.date() - timedelta(days=7)
        ).count()
        
        last_month = queryset.filter(
            created_at__gte=now.date() - timedelta(days=60),
            created_at__lt=now.date() - timedelta(days=30)
        ).count()
        
        stats['trends'] = {
            'week_change': stats['this_week'] - last_week,
            'month_change': stats['this_month'] - last_month,
            'week_change_percent': ((stats['this_week'] - last_week) / max(last_week, 1)) * 100,
            'month_change_percent': ((stats['this_month'] - last_month) / max(last_month, 1)) * 100,
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def time_series(self, request):
        """
        Datos de serie temporal para gráficos.
        """
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        days = int(request.query_params.get('days', 30))
        queryset = self.get_queryset().filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )
        
        time_series = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return Response(list(time_series))