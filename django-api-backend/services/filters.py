"""
Filtros personalizados para el módulo de servicios.
Implementa búsquedas avanzadas para tipos de trabajo y servicios.
"""

import django_filters
from django.db.models import Q, Avg, Count, Sum
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from .models import TipoTrabajo, Servicio, ESTADO_SERVICIO_CHOICES
from entities.models import Cliente, Unidad
from authentication.models import CustomUser


class TipoTrabajoFilter(django_filters.FilterSet):
    """
    Filtro avanzado para TipoTrabajo con múltiples opciones de búsqueda.
    """
    # Filtros básicos
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en nombre y descripción'
    )
    
    # Filtros especiales de negocio
    mas_solicitados = django_filters.BooleanFilter(
        method='filter_mas_solicitados',
        help_text='Tipos de trabajo más solicitados (más de 5 servicios)'
    )

    class Meta:
        model = TipoTrabajo
        fields = [
            'nombre', 'is_active', 'search', 'mas_solicitados'
        ]

    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )

    def filter_mas_solicitados(self, queryset, name, value):
        """Filtrar tipos de trabajo más solicitados."""
        if not value:
            return queryset
        
        return queryset.annotate(
            num_servicios=Count('servicios')
        ).filter(num_servicios__gt=5)


class ServicioFilter(django_filters.FilterSet):
    """
    Filtro avanzado para servicios con análisis de negocio.
    """
    # Filtros básicos
    estado_servicio = django_filters.ChoiceFilter(choices=ESTADO_SERVICIO_CHOICES)
    tipo_trabajo = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los tipos"
    )
    cliente = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los clientes"
    )
    unidad = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todas las unidades"
    )
    tecnico = django_filters.ModelChoiceFilter(
        queryset=None,  # Se define en __init__
        empty_label="Todos los técnicos"
    )
    
    # Filtros por fecha
    fecha_desde = django_filters.DateFilter(
        field_name='fecha', 
        lookup_expr='gte',
        help_text='Fecha desde (YYYY-MM-DD)'
    )
    fecha_hasta = django_filters.DateFilter(
        method='filter_fecha_hasta',
        help_text='Fecha hasta (YYYY-MM-DD)'
    )
    
    # Filtros por precio
    precio_min = django_filters.NumberFilter(
        field_name='precio', 
        lookup_expr='gte'
    )
    precio_max = django_filters.NumberFilter(
        field_name='precio', 
        lookup_expr='lte'
    )
    
    # Búsqueda avanzada
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Buscar en cliente, unidad, tipo de trabajo, observaciones'
    )
    
    # Filtros especiales de negocio
    servicios_pendientes = django_filters.BooleanFilter(
        method='filter_servicios_pendientes',
        help_text='Servicios pendientes o en proceso'
    )
    
    servicios_hoy = django_filters.BooleanFilter(
        method='filter_servicios_hoy',
        help_text='Servicios de hoy'
    )
    
    servicios_semana = django_filters.BooleanFilter(
        method='filter_servicios_semana',
        help_text='Servicios de esta semana'
    )
    
    con_gps = django_filters.BooleanFilter(
        method='filter_con_gps',
        help_text='Servicios que incluyen GPS'
    )
    
    # Filtro por período
    periodo = django_filters.ChoiceFilter(
        method='filter_periodo',
        choices=[
            ('hoy', 'Hoy'),
            ('mañana', 'Mañana'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
        ],
        help_text='Filtrar por período de fecha programada'
    )

    class Meta:
        model = Servicio
        fields = [
            'estado_servicio', 'tipo_trabajo', 'cliente', 'unidad', 'tecnico',
            'fecha_desde', 'fecha_hasta',
            'precio_min', 'precio_max', 'search',
            'servicios_pendientes', 'servicios_hoy',
            'servicios_semana', 'con_gps', 'periodo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar querysets dinámicamente
        self.filters['tipo_trabajo'].queryset = TipoTrabajo.objects.filter(is_active=True)
        self.filters['cliente'].queryset = Cliente.objects.filter(is_active=True)
        self.filters['unidad'].queryset = Unidad.objects.filter(is_active=True)
        self.filters['tecnico'].queryset = CustomUser.objects.filter(
            is_active=True,
            rol__nombre__in=['tecnico', 'administrador']
        )

    def filter_search(self, queryset, name, value):
        """Búsqueda avanzada en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(cliente__contacto__icontains=value) |
            Q(cliente__ruc__icontains=value) |
            Q(unidad__placa__icontains=value) |
            Q(unidad__marca__icontains=value) |
            Q(unidad__modelo__icontains=value) |
            Q(tipo_trabajo__nombre__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(observaciones__icontains=value) |
            Q(tecnico__first_name__icontains=value) |
            Q(tecnico__last_name__icontains=value)
        )



    def filter_servicios_pendientes(self, queryset, name, value):
        """Filtrar servicios pendientes o en proceso."""
        if not value:
            return queryset
        
        return queryset.filter(estado_servicio__in=['pendiente', 'en_proceso'])



    def filter_servicios_hoy(self, queryset, name, value):
        """Filtrar servicios de hoy."""
        if not value:
            return queryset
        
        hoy = timezone.now().date()
        return queryset.filter(fecha__date=hoy)

    def filter_servicios_semana(self, queryset, name, value):
        """Filtrar servicios de esta semana."""
        if not value:
            return queryset
        
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        return queryset.filter(
            fecha__date__gte=inicio_semana,
            fecha__date__lte=fin_semana
        )

    def filter_con_gps(self, queryset, name, value):
        """Filtrar servicios que incluyen GPS."""
        if not value:
            return queryset
        
        return queryset.filter(gps__isnull=False)

    def filter_periodo(self, queryset, name, value):
        """Filtrar por períodos predefinidos."""
        if not value:
            return queryset
        
        hoy = timezone.now().date()
        
        if value == 'hoy':
            return queryset.filter(fecha__date=hoy)
        elif value == 'mañana':
            mañana = hoy + timedelta(days=1)
            return queryset.filter(fecha__date=mañana)
        elif value == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            return queryset.filter(
                fecha__date__gte=inicio_semana,
                fecha__date__lte=fin_semana
            )
        elif value == 'mes':
            inicio_mes = hoy.replace(day=1)
            if hoy.month == 12:
                fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                fin_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
            return queryset.filter(
                fecha__date__gte=inicio_mes,
                fecha__date__lte=fin_mes
            )
        
        return queryset
    
    def filter_fecha_hasta(self, queryset, name, value):
        """
        Filtrar servicios hasta una fecha específica (incluye todo el día).
        Convierte la fecha al final del día para incluir servicios con hora.
        """
        if not value:
            return queryset
        
        # Convertir la fecha al final del día (23:59:59)
        from datetime import datetime, time
        fecha_fin = datetime.combine(value, time.max)
        
        # Si tenemos timezone activado, hacer la fecha timezone-aware
        if timezone.is_aware(timezone.now()):
            fecha_fin = timezone.make_aware(fecha_fin)
        
        return queryset.filter(fecha__lte=fecha_fin)