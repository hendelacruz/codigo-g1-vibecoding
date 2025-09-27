"""
Filtros personalizados para el módulo de entidades.
Implementa búsquedas avanzadas para clientes, proveedores y unidades.
"""

import django_filters
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Cliente, Proveedor, Unidad


class ClienteFilter(django_filters.FilterSet):
    """
    Filtro avanzado para clientes con búsquedas por múltiples campos.
    """
    # Filtros básicos
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    ruc = django_filters.CharFilter(lookup_expr='icontains')
    contacto = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por rango de fecha
    fecha_registro_desde = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte',
        help_text='Fecha de registro desde (YYYY-MM-DD)'
    )
    fecha_registro_hasta = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte',
        help_text='Fecha de registro hasta (YYYY-MM-DD)'
    )
    
    # Búsqueda avanzada por texto
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en nombre, documento, email, teléfono, dirección'
    )
    
    # Filtros especiales
    con_unidades = django_filters.BooleanFilter(
        method='filter_con_unidades',
        help_text='Clientes que tienen unidades registradas'
    )
    
    con_servicios = django_filters.BooleanFilter(
        method='filter_con_servicios',
        help_text='Clientes que tienen servicios registrados'
    )
    
    registrados_reciente = django_filters.BooleanFilter(
        method='filter_registrados_reciente',
        help_text='Clientes registrados en los últimos 30 días'
    )
    


    class Meta:
        model = Cliente
        fields = [
            'nombre', 'ruc', 'contacto', 'is_active',
            'fecha_registro_desde', 'fecha_registro_hasta', 'search',
            'con_unidades', 'con_servicios', 'registrados_reciente'
        ]

    def filter_search(self, queryset, name, value):
        """
        Búsqueda avanzada en múltiples campos.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(ruc__icontains=value) |
            Q(correo__icontains=value) |
            Q(celular__icontains=value) |
            Q(direccion__icontains=value) |
            Q(contacto__icontains=value)
        )

    def filter_con_unidades(self, queryset, name, value):
        """
        Filtrar clientes que tienen unidades registradas.
        """
        if not value:
            return queryset
        
        return queryset.filter(unidades__isnull=False).distinct()

    def filter_con_servicios(self, queryset, name, value):
        """
        Filtrar clientes que tienen servicios registrados.
        """
        if not value:
            return queryset
        
        return queryset.filter(servicios__isnull=False).distinct()

    def filter_registrados_reciente(self, queryset, name, value):
        """
        Filtrar clientes registrados recientemente (últimos 30 días).
        """
        if not value:
            return queryset
        
        fecha_limite = timezone.now() - timedelta(days=30)
        return queryset.filter(created_at__gte=fecha_limite)




class ProveedorFilter(django_filters.FilterSet):
    """
    Filtro avanzado para proveedores con búsquedas por múltiples campos.
    """
    # Filtros básicos
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    ruc = django_filters.CharFilter(lookup_expr='icontains')
    contacto = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por rango de fecha
    fecha_registro_desde = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte'
    )
    fecha_registro_hasta = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte'
    )
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en nombre, documento, email, teléfono, categoría'
    )
    
    # Filtros especiales
    con_productos = django_filters.BooleanFilter(
        method='filter_con_productos',
        help_text='Proveedores que tienen productos en inventario'
    )
    
    activos_reciente = django_filters.BooleanFilter(
        method='filter_activos_reciente',
        help_text='Proveedores con actividad en los últimos 60 días'
    )

    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'ruc', 'contacto', 'is_active',
            'fecha_registro_desde', 'fecha_registro_hasta', 'search',
            'con_productos', 'activos_reciente'
        ]

    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(ruc__icontains=value) |
            Q(correo__icontains=value) |
            Q(celular__icontains=value) |
            Q(contacto__icontains=value) |
            Q(direccion__icontains=value)
        )

    def filter_con_productos(self, queryset, name, value):
        """Filtrar proveedores que tienen productos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(gps_proveedor__isnull=False) |
            Q(simcard_proveedor__isnull=False) |
            Q(otros_proveedor__isnull=False)
        ).distinct()

    def filter_activos_reciente(self, queryset, name, value):
        """Filtrar proveedores con actividad reciente."""
        if not value:
            return queryset
        
        fecha_limite = timezone.now() - timedelta(days=60)
        return queryset.filter(
            Q(gps_proveedor__created_at__gte=fecha_limite) |
            Q(simcard_proveedor__created_at__gte=fecha_limite) |
            Q(otros_proveedor__created_at__gte=fecha_limite)
        ).distinct()


class UnidadFilter(django_filters.FilterSet):
    """
    Filtro avanzado para unidades con búsquedas por múltiples campos.
    """
    # Filtros básicos
    placa = django_filters.CharFilter(lookup_expr='icontains')
    marca = django_filters.CharFilter(lookup_expr='icontains')
    modelo = django_filters.CharFilter(lookup_expr='icontains')
    tipo = django_filters.ChoiceFilter(choices=[('bus', 'Bus'), ('camion', 'Camión'), ('otro', 'Otro')])
    cliente = django_filters.NumberFilter(field_name='cliente__id')
    
    # Filtros por rango de fecha
    fecha_registro_desde = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte'
    )
    fecha_registro_hasta = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte'
    )
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en placa, marca, modelo, serie, cliente'
    )
    
    # Filtros personalizados
    registrados_reciente = django_filters.BooleanFilter(
        method='filter_registrados_reciente',
        help_text='Unidades registradas en los últimos 30 días'
    )

    class Meta:
        model = Unidad
        fields = [
            'placa', 'marca', 'modelo', 'tipo', 'cliente', 'is_active',
            'fecha_registro_desde', 'fecha_registro_hasta', 'search',
            'registrados_reciente'
        ]



    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(placa__icontains=value) |
            Q(marca__icontains=value) |
            Q(modelo__icontains=value) |
            Q(serie__icontains=value) |
            Q(cliente__nombre__icontains=value)
        )

    def filter_registrados_reciente(self, queryset, name, value):
        """Filtrar unidades registradas recientemente."""
        if not value:
            return queryset
        
        fecha_limite = timezone.now() - timedelta(days=30)
        return queryset.filter(created_at__gte=fecha_limite)