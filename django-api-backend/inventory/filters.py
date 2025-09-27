"""
Filtros personalizados para el módulo de inventario.
Implementa búsquedas avanzadas y filtros específicos según la tarea 3.4.
"""

import django_filters
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

from .models import GPS, SIMCard, Otros


class GPSFilter(django_filters.FilterSet):
    """
    Filtro avanzado para GPS con búsquedas por múltiples campos.
    Incluye filtros separados para estado de asignación y proceso operativo.
    """
    # Filtros básicos - separados en estado y proceso
    estado = django_filters.ChoiceFilter(choices=GPS.ESTADO_CHOICES)
    proceso = django_filters.ChoiceFilter(choices=GPS.PROCESO_CHOICES)
    marca = django_filters.CharFilter(lookup_expr='icontains')
    modelo = django_filters.CharFilter(lookup_expr='icontains')
    proveedor = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los proveedores"
    )
    cliente = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los clientes"
    )
    
    # Filtros por rango de fecha
    fecha_compra_desde = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='gte',
        help_text='Fecha desde (YYYY-MM-DD)'
    )
    fecha_compra_hasta = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='lte',
        help_text='Fecha hasta (YYYY-MM-DD)'
    )
    
    # Filtros por rango de precio
    precio_min = django_filters.NumberFilter(
        field_name='precio_compra', 
        lookup_expr='gte',
        help_text='Precio mínimo'
    )
    precio_max = django_filters.NumberFilter(
        field_name='precio_compra', 
        lookup_expr='lte',
        help_text='Precio máximo'
    )
    
    # Búsqueda avanzada por texto
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en IMEI, marca, modelo, proveedor'
    )
    
    # Filtros de tiempo relativo
    agregado_reciente = django_filters.BooleanFilter(
        method='filter_agregado_reciente',
        help_text='GPS agregados en los últimos 7 días'
    )
    
    # Filtro por disponibilidad
    disponible = django_filters.BooleanFilter(
        method='filter_disponible',
        help_text='Solo GPS disponibles para asignar'
    )
    
    # Filtros específicos para cliente
    sin_cliente = django_filters.BooleanFilter(
        method='filter_sin_cliente',
        help_text='GPS sin cliente asignado'
    )
    
    con_cliente = django_filters.BooleanFilter(
        method='filter_con_cliente',
        help_text='GPS con cliente asignado'
    )

    class Meta:
        model = GPS
        fields = {
            'estado': ['exact'],
            'proceso': ['exact'],
            'marca': ['icontains'],
            'modelo': ['icontains'],
            'proveedor': ['exact'],
            'cliente': ['exact', 'isnull'],
            'fecha_compra': ['gte', 'lte'],
            'precio_compra': ['gte', 'lte'],
        }
        # Campos adicionales personalizados
        extra_fields = [
            'search', 'agregado_reciente', 'disponible',
            'sin_cliente', 'con_cliente'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar queryset para proveedor y cliente dinámicamente
        from entities.models import Proveedor, Cliente
        self.filters['proveedor'].queryset = Proveedor.objects.filter(is_active=True)
        self.filters['cliente'].queryset = Cliente.objects.filter(is_active=True)

    def filter_search(self, queryset, name, value):
        """
        Búsqueda avanzada en múltiples campos.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(imei__icontains=value) |
            Q(marca__icontains=value) |
            Q(modelo__icontains=value) |
            Q(proveedor__nombre__icontains=value)
        )

    def filter_agregado_reciente(self, queryset, name, value):
        """
        Filtrar GPS agregados recientemente (últimos 7 días).
        """
        if not value:
            return queryset
        
        fecha_limite = timezone.now() - timedelta(days=7)
        return queryset.filter(created_at__gte=fecha_limite)

    def filter_disponible(self, queryset, name, value):
        """
        Filtrar GPS disponibles para asignar a servicios.
        Un GPS está disponible si no está asignado a un cliente y tiene proceso 'en_produccion'.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            estado='no_asignado',
            proceso='en_produccion'
        )

    def filter_sin_cliente(self, queryset, name, value):
        """
        Filtrar GPS sin cliente asignado.
        """
        if not value:
            return queryset
        
        return queryset.filter(cliente__isnull=True)

    def filter_con_cliente(self, queryset, name, value):
        """
        Filtrar GPS con cliente asignado.
        """
        if not value:
            return queryset
        
        return queryset.filter(cliente__isnull=False)


class SIMCardFilter(django_filters.FilterSet):
    """
    Filtro avanzado para SIM Cards.
    """
    # Filtros básicos
    from .models import ESTADO_CHOICES
    estado = django_filters.ChoiceFilter(choices=ESTADO_CHOICES)
    operadora = django_filters.CharFilter(lookup_expr='icontains')
    proveedor = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los proveedores"
    )
    
    # Filtros por rango de fecha
    fecha_compra_desde = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='gte'
    )
    fecha_compra_hasta = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='lte'
    )
    
    # Filtros por rango de precio
    precio_min = django_filters.NumberFilter(field_name='precio_compra', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio_compra', lookup_expr='lte')
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en número, operadora, ICCID'
    )
    
    # Filtros especiales
    disponible = django_filters.BooleanFilter(
        method='filter_disponible',
        help_text='Solo SIM Cards disponibles'
    )
    
    activas = django_filters.BooleanFilter(
        method='filter_activas',
        help_text='Solo SIM Cards activas'
    )
    
    vence_pronto = django_filters.BooleanFilter(
        method='filter_vence_pronto',
        help_text='SIM Cards que vencen en los próximos 30 días'
    )
    
    # Filtros específicos para cliente
    sin_cliente = django_filters.BooleanFilter(
        method='filter_sin_cliente',
        help_text='SIM Cards sin cliente asignado'
    )
    
    con_cliente = django_filters.BooleanFilter(
        method='filter_con_cliente',
        help_text='SIM Cards con cliente asignado'
    )

    class Meta:
        model = SIMCard
        fields = [
            'estado', 'operadora', 'proveedor',
            'fecha_compra_desde', 'fecha_compra_hasta',
            'precio_min', 'precio_max', 'search', 'disponible', 'activas', 'vence_pronto',
            'sin_cliente', 'con_cliente'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from entities.models import Proveedor
        self.filters['proveedor'].queryset = Proveedor.objects.filter(is_active=True)

    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(numero__icontains=value) |
            Q(operadora__icontains=value) |
            Q(iccid__icontains=value) |
            Q(proveedor__nombre__icontains=value)
        )

    def filter_disponible(self, queryset, name, value):
        """Filtrar SIM Cards disponibles."""
        if not value:
            return queryset
        
        return queryset.filter(estado='disponible')

    def filter_activas(self, queryset, name, value):
        """Filtrar SIM Cards activas."""
        if not value:
            return queryset
        
        return queryset.filter(estado='activo')

    def filter_vence_pronto(self, queryset, name, value):
        """Filtrar SIM Cards que vencen pronto."""
        if not value:
            return queryset
        
        fecha_limite = timezone.now() + timedelta(days=30)
        return queryset.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now()
        )

    def filter_sin_cliente(self, queryset, name, value):
        """
        Filtrar SIM Cards sin cliente asignado.
        """
        if not value:
            return queryset
        
        return queryset.filter(cliente__isnull=True)

    def filter_con_cliente(self, queryset, name, value):
        """
        Filtrar SIM Cards con cliente asignado.
        """
        if not value:
            return queryset
        
        return queryset.filter(cliente__isnull=False)


class OtrosFilter(django_filters.FilterSet):
    """
    Filtro avanzado para otros productos de inventario.
    """
    # Filtros básicos
    categoria = django_filters.CharFilter(lookup_expr='icontains')
    marca = django_filters.CharFilter(lookup_expr='icontains')
    proveedor = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los proveedores"
    )
    
    # Filtros por rango de fecha
    fecha_compra_desde = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='gte'
    )
    fecha_compra_hasta = django_filters.DateTimeFilter(
        field_name='fecha_compra', 
        lookup_expr='lte'
    )
    
    # Filtros por rango de precio
    precio_min = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='lte')
    
    # Filtros por stock
    stock_min = django_filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_max = django_filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en nombre, descripción, categoría, marca'
    )
    
    # Filtros especiales
    stock_bajo = django_filters.BooleanFilter(
        method='filter_stock_bajo',
        help_text='Productos con stock bajo (menos de 5 unidades)'
    )
    
    sin_stock = django_filters.BooleanFilter(
        method='filter_sin_stock',
        help_text='Productos sin stock'
    )

    class Meta:
        model = Otros
        fields = [
            'categoria', 'proveedor',
            'fecha_compra_desde', 'fecha_compra_hasta',
            'precio_min', 'precio_max', 'stock_min', 'stock_max',
            'search', 'stock_bajo', 'sin_stock'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from entities.models import Proveedor
        self.filters['proveedor'].queryset = Proveedor.objects.filter(is_active=True)

    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(categoria__icontains=value) |
            Q(marca__icontains=value) |
            Q(proveedor__nombre__icontains=value)
        )

    def filter_stock_bajo(self, queryset, name, value):
        """Filtrar productos con stock bajo."""
        if not value:
            return queryset
        return queryset.filter(stock_actual__lt=5, stock_actual__gt=0)

    def filter_sin_stock(self, queryset, name, value):
        """Filtrar productos sin stock."""
        if not value:
            return queryset
        return queryset.filter(stock_actual=0)