"""
Filtros personalizados para el módulo de ventas.
Implementa búsquedas avanzadas para ventas y detalles de venta.
"""

import django_filters
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from .models import Ventas, ESTADO_VENTA_CHOICES, TIPO_PAGO_CHOICES
from entities.models import Cliente


class VentaFilter(django_filters.FilterSet):
    """
    Filtro avanzado para ventas con análisis de negocio.
    """
    # Filtros básicos
    estado = django_filters.ChoiceFilter(choices=ESTADO_VENTA_CHOICES)
    metodo_pago = django_filters.ChoiceFilter(
        field_name='tipo_pago',
        choices=TIPO_PAGO_CHOICES
    )
    cliente = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los clientes"
    )

    
    # Filtros por rango de fechas
    fecha_desde = django_filters.DateFilter(
        field_name='fecha_generacion_factura', 
        lookup_expr='gte',
        help_text='Fecha de factura desde (YYYY-MM-DD)'
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='fecha_generacion_factura', 
        lookup_expr='lte',
        help_text='Fecha de factura hasta (YYYY-MM-DD)'
    )
    
    # Filtros por rango de monto
    monto_min = django_filters.NumberFilter(
        field_name='total', 
        lookup_expr='gte',
        help_text='Monto mínimo de venta'
    )
    monto_max = django_filters.NumberFilter(
        field_name='total', 
        lookup_expr='lte',
        help_text='Monto máximo de venta'
    )
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en número de venta, cliente, vendedor, observaciones'
    )
    
    # Filtros especiales de negocio
    ventas_grandes = django_filters.BooleanFilter(
        method='filter_ventas_grandes',
        help_text='Ventas mayores a S/. 1000'
    )
    
    ventas_recientes = django_filters.BooleanFilter(
        method='filter_ventas_recientes',
        help_text='Ventas de los últimos 7 días'
    )
    
    ventas_mes_actual = django_filters.BooleanFilter(
        method='filter_ventas_mes_actual',
        help_text='Ventas del mes actual'
    )
    
    con_descuento = django_filters.BooleanFilter(
        method='filter_con_descuento',
        help_text='Ventas que tienen descuento aplicado'
    )
    
    # Filtros por período
    periodo = django_filters.ChoiceFilter(
        method='filter_periodo',
        choices=[
            ('hoy', 'Hoy'),
            ('ayer', 'Ayer'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
            ('trimestre', 'Este trimestre'),
            ('año', 'Este año'),
        ],
        help_text='Filtrar por período predefinido'
    )

    class Meta:
        model = Ventas
        fields = [
            'estado', 'metodo_pago', 'cliente',
            'fecha_desde', 'fecha_hasta', 'monto_min', 'monto_max',
            'search', 'ventas_grandes', 'ventas_recientes', 'ventas_mes_actual',
            'con_descuento', 'periodo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar querysets dinámicamente
        self.filters['cliente'].queryset = Cliente.objects.filter(is_active=True)

    def filter_search(self, queryset, name, value):
        """Búsqueda avanzada en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(numero_factura__icontains=value) |
            Q(numero_operacion__icontains=value) |
            Q(cliente__nombre__icontains=value) |
            Q(cliente__ruc__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(banco__icontains=value)
        )

    def filter_ventas_grandes(self, queryset, name, value):
        """Filtrar ventas mayores a S/. 1000."""
        if not value:
            return queryset
        
        return queryset.filter(total__gt=Decimal('1000.00'))

    def filter_ventas_recientes(self, queryset, name, value):
        """Filtrar ventas de los últimos 7 días."""
        if not value:
            return queryset
        
        fecha_limite = timezone.now().date() - timedelta(days=7)
        return queryset.filter(fecha_generacion_factura__date__gte=fecha_limite)

    def filter_ventas_mes_actual(self, queryset, name, value):
        """Filtrar ventas del mes actual."""
        if not value:
            return queryset
        
        hoy = timezone.now().date()
        primer_dia_mes = hoy.replace(day=1)
        return queryset.filter(fecha_generacion_factura__date__gte=primer_dia_mes)

    def filter_con_descuento(self, queryset, name, value):
        """Filtrar ventas con IGV aplicado."""
        if not value:
            return queryset
        
        return queryset.filter(igv__gt=Decimal('0.00'))

    def filter_periodo(self, queryset, name, value):
        """Filtrar por períodos predefinidos."""
        if not value:
            return queryset
        
        hoy = timezone.now().date()
        
        if value == 'hoy':
            return queryset.filter(fecha_generacion_factura__date=hoy)
        elif value == 'ayer':
            ayer = hoy - timedelta(days=1)
            return queryset.filter(fecha_generacion_factura__date=ayer)
        elif value == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            return queryset.filter(fecha_generacion_factura__date__gte=inicio_semana)
        elif value == 'mes':
            inicio_mes = hoy.replace(day=1)
            return queryset.filter(fecha_generacion_factura__date__gte=inicio_mes)
        elif value == 'trimestre':
            mes_actual = hoy.month
            inicio_trimestre = hoy.replace(month=((mes_actual - 1) // 3) * 3 + 1, day=1)
            return queryset.filter(fecha_generacion_factura__date__gte=inicio_trimestre)
        elif value == 'año':
            inicio_año = hoy.replace(month=1, day=1)
            return queryset.filter(fecha_generacion_factura__date__gte=inicio_año)
        
        return queryset