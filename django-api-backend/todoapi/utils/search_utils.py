"""
Utilidades para búsquedas avanzadas y filtrado.
Proporciona funciones comunes para mejorar las capacidades de búsqueda.
"""

import re
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.conf import settings


class AdvancedSearchMixin:
    """
    Mixin para agregar capacidades de búsqueda avanzada a los filtros.
    """
    
    def get_search_terms(self, value):
        """
        Procesa el término de búsqueda y devuelve una lista de términos.
        Maneja búsquedas con comillas, operadores AND/OR, etc.
        """
        if not value:
            return []
        
        # Buscar términos entre comillas
        quoted_terms = re.findall(r'"([^"]*)"', value)
        
        # Remover términos entre comillas del valor original
        remaining_value = re.sub(r'"[^"]*"', '', value)
        
        # Dividir el resto por espacios
        other_terms = [term.strip() for term in remaining_value.split() if term.strip()]
        
        return quoted_terms + other_terms
    
    def build_search_query(self, fields, value):
        """
        Construye una consulta Q compleja para búsqueda en múltiples campos.
        """
        if not value or not fields:
            return Q()
        
        terms = self.get_search_terms(value)
        if not terms:
            return Q()
        
        # Construir consulta para cada término
        query = Q()
        
        for term in terms:
            term_query = Q()
            for field in fields:
                term_query |= Q(**{f"{field}__icontains": term})
            query &= term_query
        
        return query
    
    def build_exact_search_query(self, fields, value):
        """
        Construye una consulta Q para búsqueda exacta en múltiples campos.
        """
        if not value or not fields:
            return Q()
        
        query = Q()
        for field in fields:
            query |= Q(**{f"{field}__iexact": value})
        
        return query


class NumericRangeFilter:
    """
    Utilidad para crear filtros de rango numérico con validación.
    """
    
    @staticmethod
    def validate_range(min_value, max_value):
        """
        Valida que el rango sea coherente.
        """
        if min_value is not None and max_value is not None:
            return min_value <= max_value
        return True
    
    @staticmethod
    def build_range_query(field_name, min_value, max_value):
        """
        Construye una consulta Q para filtro de rango.
        """
        query = Q()
        
        if min_value is not None:
            query &= Q(**{f"{field_name}__gte": min_value})
        
        if max_value is not None:
            query &= Q(**{f"{field_name}__lte": max_value})
        
        return query


class DateRangeFilter:
    """
    Utilidad para crear filtros de rango de fechas con opciones predefinidas.
    """
    
    @staticmethod
    def get_predefined_ranges():
        """
        Devuelve rangos de fecha predefinidos.
        """
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        today = now.date()
        
        return {
            'hoy': (today, today),
            'ayer': (today - timedelta(days=1), today - timedelta(days=1)),
            'ultima_semana': (today - timedelta(days=7), today),
            'ultimo_mes': (today - timedelta(days=30), today),
            'ultimo_trimestre': (today - timedelta(days=90), today),
            'ultimo_año': (today - timedelta(days=365), today),
        }
    
    @staticmethod
    def build_date_range_query(field_name, start_date, end_date):
        """
        Construye una consulta Q para filtro de rango de fechas.
        """
        query = Q()
        
        if start_date:
            query &= Q(**{f"{field_name}__gte": start_date})
        
        if end_date:
            query &= Q(**{f"{field_name}__lte": end_date})
        
        return query


class SearchHighlighter:
    """
    Utilidad para resaltar términos de búsqueda en los resultados.
    """
    
    @staticmethod
    def highlight_terms(text, terms, highlight_class="highlight"):
        """
        Resalta los términos de búsqueda en el texto.
        """
        if not text or not terms:
            return text
        
        highlighted_text = str(text)
        
        for term in terms:
            if term:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_text = pattern.sub(
                    f'<span class="{highlight_class}">{term}</span>',
                    highlighted_text
                )
        
        return highlighted_text


class FilterValidation:
    """
    Utilidades para validar parámetros de filtro.
    """
    
    @staticmethod
    def validate_choice_field(value, choices):
        """
        Valida que el valor esté en las opciones permitidas.
        """
        if not value:
            return True
        
        valid_choices = [choice[0] for choice in choices]
        return value in valid_choices
    
    @staticmethod
    def validate_numeric_field(value, min_value=None, max_value=None):
        """
        Valida que el valor numérico esté en el rango permitido.
        """
        if value is None:
            return True
        
        try:
            numeric_value = float(value)
            
            if min_value is not None and numeric_value < min_value:
                return False
            
            if max_value is not None and numeric_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_field(value):
        """
        Valida que el valor sea una fecha válida.
        """
        if not value:
            return True
        
        try:
            from datetime import datetime
            if isinstance(value, str):
                datetime.strptime(value, '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False


class PaginationHelper:
    """
    Utilidades para mejorar la paginación.
    """
    
    @staticmethod
    def get_pagination_info(paginator, page_number):
        """
        Devuelve información detallada de paginación.
        """
        try:
            page = paginator.page(page_number)
            return {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'items_per_page': paginator.per_page,
                'has_previous': page.has_previous(),
                'has_next': page.has_next(),
                'previous_page': page.previous_page_number() if page.has_previous() else None,
                'next_page': page.next_page_number() if page.has_next() else None,
                'start_index': page.start_index(),
                'end_index': page.end_index(),
            }
        except Exception:
            return None
    
    @staticmethod
    def get_page_range(paginator, current_page, window=5):
        """
        Devuelve un rango de páginas para mostrar en la navegación.
        """
        total_pages = paginator.num_pages
        
        if total_pages <= window:
            return list(range(1, total_pages + 1))
        
        start = max(1, current_page - window // 2)
        end = min(total_pages, start + window - 1)
        
        # Ajustar si estamos cerca del final
        if end == total_pages:
            start = max(1, end - window + 1)
        
        return list(range(start, end + 1))


# Configuraciones globales para búsqueda
SEARCH_CONFIGURATIONS = {
    'inventory': {
        'gps': {
            'search_fields': ['modelo', 'marca', 'imei'],
            'exact_fields': ['imei'],
            'highlight_fields': ['modelo', 'marca'],
        },
        'simcard': {
            'search_fields': ['numero', 'operadora', 'icc'],
            'exact_fields': ['numero', 'icc'],
            'highlight_fields': ['numero', 'operadora'],
        },
        'otros': {
            'search_fields': ['nombre', 'descripcion', 'categoria'],
            'exact_fields': ['nombre'],
            'highlight_fields': ['nombre', 'descripcion'],
        },
    },
    'entities': {
        'cliente': {
            'search_fields': ['nombre', 'numero_documento', 'email', 'telefono', 'direccion'],
            'exact_fields': ['numero_documento', 'email'],
            'highlight_fields': ['nombre', 'email'],
        },
        'proveedor': {
            'search_fields': ['nombre', 'numero_documento', 'email', 'telefono', 'categoria'],
            'exact_fields': ['numero_documento', 'email'],
            'highlight_fields': ['nombre', 'categoria'],
        },
        'unidad': {
            'search_fields': ['placa', 'marca', 'modelo', 'vin', 'numero_motor'],
            'exact_fields': ['placa', 'vin', 'numero_motor'],
            'highlight_fields': ['placa', 'marca', 'modelo'],
        },
    },
    'sales': {
        'venta': {
            'search_fields': ['numero_venta', 'cliente__nombre', 'observaciones'],
            'exact_fields': ['numero_venta'],
            'highlight_fields': ['numero_venta', 'observaciones'],
        },
    },
    'services': {
        'servicio': {
            'search_fields': ['cliente__nombre', 'unidad__placa', 'tipo_trabajo__nombre', 'observaciones'],
            'exact_fields': ['unidad__placa'],
            'highlight_fields': ['observaciones'],
        },
    },
}