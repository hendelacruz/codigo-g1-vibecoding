"""
Configuración de paginación optimizada para la API.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar para la mayoría de endpoints.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Respuesta paginada con información adicional.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Paginación para conjuntos de datos grandes (reportes, exportaciones).
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
    
    def get_paginated_response(self, data):
        """
        Respuesta paginada optimizada para grandes volúmenes.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('performance_info', {
                'items_per_page': len(data),
                'is_large_dataset': self.page.paginator.count > 1000,
                'suggested_page_size': min(100, max(20, self.page.paginator.count // 20))
            })
        ]))


class SmallResultsSetPagination(PageNumberPagination):
    """
    Paginación para conjuntos de datos pequeños (configuraciones, catálogos).
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        """
        Respuesta paginada simple para datos pequeños.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class DashboardPagination(PageNumberPagination):
    """
    Paginación optimizada para dashboards y vistas de resumen.
    """
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 30
    
    def get_paginated_response(self, data):
        """
        Respuesta paginada con métricas para dashboard.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('dashboard_info', {
                'items_shown': len(data),
                'total_items': self.page.paginator.count,
                'percentage_shown': round((len(data) / max(self.page.paginator.count, 1)) * 100, 2),
                'is_first_page': self.page.number == 1,
                'is_last_page': not self.page.has_next()
            })
        ]))


class NoPagination:
    """
    Clase para deshabilitar paginación en endpoints específicos.
    """
    def paginate_queryset(self, queryset, request, view=None):
        return None
    
    def get_paginated_response(self, data):
        return Response(data)


# Configuración de paginación por módulo
PAGINATION_CONFIG = {
    'inventory': {
        'default': StandardResultsSetPagination,
        'reports': LargeResultsSetPagination,
        'dashboard': DashboardPagination,
    },
    'entities': {
        'default': StandardResultsSetPagination,
        'clientes': StandardResultsSetPagination,
        'proveedores': SmallResultsSetPagination,
        'unidades': StandardResultsSetPagination,
        'dashboard': DashboardPagination,
    },
    'sales': {
        'default': StandardResultsSetPagination,
        'ventas': StandardResultsSetPagination,
        'detalles': LargeResultsSetPagination,
        'reports': LargeResultsSetPagination,
        'dashboard': DashboardPagination,
    },
    'services': {
        'default': StandardResultsSetPagination,
        'servicios': StandardResultsSetPagination,
        'tipos_trabajo': SmallResultsSetPagination,
        'dashboard': DashboardPagination,
    },
    'authentication': {
        'default': SmallResultsSetPagination,
        'users': StandardResultsSetPagination,
    }
}


def get_pagination_class(module_name, view_type='default'):
    """
    Obtiene la clase de paginación apropiada para un módulo y tipo de vista.
    
    Args:
        module_name (str): Nombre del módulo (inventory, entities, etc.)
        view_type (str): Tipo de vista (default, reports, dashboard, etc.)
    
    Returns:
        class: Clase de paginación apropiada
    """
    module_config = PAGINATION_CONFIG.get(module_name, {})
    return module_config.get(view_type, StandardResultsSetPagination)


class AdaptivePagination(PageNumberPagination):
    """
    Paginación adaptiva que ajusta el tamaño de página según el contenido.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_page_size(self, request):
        """
        Calcula el tamaño de página óptimo basado en el contexto.
        """
        # Obtener tamaño solicitado
        requested_size = super().get_page_size(request)
        
        # Ajustar según el tipo de dispositivo (si está disponible)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            # Reducir tamaño para móviles
            return min(requested_size, 10)
        elif 'tablet' in user_agent:
            # Tamaño medio para tablets
            return min(requested_size, 15)
        
        # Ajustar según parámetros de consulta
        if request.query_params.get('search'):
            # Más resultados para búsquedas
            return min(requested_size * 2, self.max_page_size)
        
        return requested_size
    
    def get_paginated_response(self, data):
        """
        Respuesta con información adaptiva.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('adaptive_info', {
                'is_search_result': bool(self.request.query_params.get('search')),
                'is_filtered': len(self.request.query_params) > 1,
                'optimal_page_size': self._calculate_optimal_size(),
                'performance_score': self._calculate_performance_score()
            })
        ]))
    
    def _calculate_optimal_size(self):
        """
        Calcula el tamaño de página óptimo basado en el total de elementos.
        """
        total_count = self.page.paginator.count
        
        if total_count <= 50:
            return min(total_count, 25)
        elif total_count <= 200:
            return 20
        elif total_count <= 1000:
            return 30
        else:
            return 50
    
    def _calculate_performance_score(self):
        """
        Calcula un score de performance basado en varios factores.
        """
        page_size = self.get_page_size(self.request)
        total_count = self.page.paginator.count
        
        # Score base
        score = 100
        
        # Penalizar páginas muy grandes
        if page_size > 50:
            score -= (page_size - 50) * 2
        
        # Penalizar conjuntos de datos muy grandes sin filtros
        if total_count > 1000 and len(self.request.query_params) <= 1:
            score -= 20
        
        # Bonificar búsquedas y filtros
        if self.request.query_params.get('search'):
            score += 10
        
        if len(self.request.query_params) > 2:
            score += 5
        
        return max(0, min(100, score))