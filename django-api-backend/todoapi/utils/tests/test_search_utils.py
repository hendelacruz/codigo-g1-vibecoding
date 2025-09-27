"""
Tests comprehensivos para las utilidades de búsqueda en todoapi.utils.search_utils
"""

from datetime import datetime, date, timedelta
from django.test import TestCase
from django.db.models import Q
from django.core.paginator import Paginator
from unittest.mock import Mock, patch

from todoapi.utils.search_utils import (
    AdvancedSearchMixin, NumericRangeFilter, DateRangeFilter,
    SearchHighlighter, FilterValidation, PaginationHelper,
    SEARCH_CONFIGURATIONS
)


class AdvancedSearchMixinTest(TestCase):
    """Tests para AdvancedSearchMixin"""
    
    def setUp(self):
        self.mixin = AdvancedSearchMixin()
    
    def test_get_search_terms_empty_value(self):
        """Test get_search_terms con valor vacío"""
        result = self.mixin.get_search_terms("")
        self.assertEqual(result, [])
        
        result = self.mixin.get_search_terms(None)
        self.assertEqual(result, [])
    
    def test_get_search_terms_simple_words(self):
        """Test get_search_terms con palabras simples"""
        result = self.mixin.get_search_terms("hello world")
        self.assertEqual(result, ["hello", "world"])
    
    def test_get_search_terms_quoted_phrases(self):
        """Test get_search_terms con frases entre comillas"""
        result = self.mixin.get_search_terms('"hello world" test')
        self.assertEqual(result, ["hello world", "test"])
    
    def test_get_search_terms_multiple_quotes(self):
        """Test get_search_terms con múltiples frases entre comillas"""
        result = self.mixin.get_search_terms('"first phrase" "second phrase" word')
        self.assertEqual(result, ["first phrase", "second phrase", "word"])
    
    def test_get_search_terms_mixed_content(self):
        """Test get_search_terms con contenido mixto"""
        result = self.mixin.get_search_terms('word1 "quoted phrase" word2')
        self.assertEqual(set(result), {"quoted phrase", "word1", "word2"})
    
    def test_build_search_query_empty_inputs(self):
        """Test build_search_query con inputs vacíos"""
        result = self.mixin.build_search_query([], "test")
        self.assertEqual(result, Q())
        
        result = self.mixin.build_search_query(["field1"], "")
        self.assertEqual(result, Q())
    
    def test_build_search_query_single_term_single_field(self):
        """Test build_search_query con un término y un campo"""
        result = self.mixin.build_search_query(["name"], "john")
        expected = Q(name__icontains="john")
        self.assertEqual(result, expected)
    
    def test_build_search_query_single_term_multiple_fields(self):
        """Test build_search_query con un término y múltiples campos"""
        result = self.mixin.build_search_query(["name", "email"], "john")
        expected = Q(name__icontains="john") | Q(email__icontains="john")
        self.assertEqual(result, expected)
    
    def test_build_search_query_multiple_terms_single_field(self):
        """Test build_search_query con múltiples términos y un campo"""
        result = self.mixin.build_search_query(["name"], "john doe")
        expected = Q(name__icontains="john") & Q(name__icontains="doe")
        self.assertEqual(result, expected)
    
    def test_build_search_query_multiple_terms_multiple_fields(self):
        """Test build_search_query con múltiples términos y campos"""
        result = self.mixin.build_search_query(["name", "email"], "john doe")
        expected = (
            (Q(name__icontains="john") | Q(email__icontains="john")) &
            (Q(name__icontains="doe") | Q(email__icontains="doe"))
        )
        self.assertEqual(result, expected)
    
    def test_build_exact_search_query_empty_inputs(self):
        """Test build_exact_search_query con inputs vacíos"""
        result = self.mixin.build_exact_search_query([], "test")
        self.assertEqual(result, Q())
        
        result = self.mixin.build_exact_search_query(["field1"], "")
        self.assertEqual(result, Q())
    
    def test_build_exact_search_query_single_field(self):
        """Test build_exact_search_query con un campo"""
        result = self.mixin.build_exact_search_query(["name"], "john")
        expected = Q(name__iexact="john")
        self.assertEqual(result, expected)
    
    def test_build_exact_search_query_multiple_fields(self):
        """Test build_exact_search_query con múltiples campos"""
        result = self.mixin.build_exact_search_query(["name", "email"], "john")
        expected = Q(name__iexact="john") | Q(email__iexact="john")
        self.assertEqual(result, expected)


class NumericRangeFilterTest(TestCase):
    """Tests para NumericRangeFilter"""
    
    def test_validate_range_valid_range(self):
        """Test validate_range con rango válido"""
        result = NumericRangeFilter.validate_range(10, 20)
        self.assertTrue(result)
    
    def test_validate_range_equal_values(self):
        """Test validate_range con valores iguales"""
        result = NumericRangeFilter.validate_range(10, 10)
        self.assertTrue(result)
    
    def test_validate_range_invalid_range(self):
        """Test validate_range con rango inválido"""
        result = NumericRangeFilter.validate_range(20, 10)
        self.assertFalse(result)
    
    def test_validate_range_none_values(self):
        """Test validate_range con valores None"""
        result = NumericRangeFilter.validate_range(None, 20)
        self.assertTrue(result)
        
        result = NumericRangeFilter.validate_range(10, None)
        self.assertTrue(result)
        
        result = NumericRangeFilter.validate_range(None, None)
        self.assertTrue(result)
    
    def test_build_range_query_both_values(self):
        """Test build_range_query con ambos valores"""
        result = NumericRangeFilter.build_range_query("price", 10, 20)
        expected = Q(price__gte=10) & Q(price__lte=20)
        self.assertEqual(result, expected)
    
    def test_build_range_query_min_only(self):
        """Test build_range_query solo con valor mínimo"""
        result = NumericRangeFilter.build_range_query("price", 10, None)
        expected = Q(price__gte=10)
        self.assertEqual(result, expected)
    
    def test_build_range_query_max_only(self):
        """Test build_range_query solo con valor máximo"""
        result = NumericRangeFilter.build_range_query("price", None, 20)
        expected = Q(price__lte=20)
        self.assertEqual(result, expected)
    
    def test_build_range_query_no_values(self):
        """Test build_range_query sin valores"""
        result = NumericRangeFilter.build_range_query("price", None, None)
        self.assertEqual(result, Q())


class DateRangeFilterTest(TestCase):
    """Tests para DateRangeFilter"""
    
    def test_get_predefined_ranges_returns_dict(self):
        """Test que get_predefined_ranges retorna un diccionario"""
        ranges = DateRangeFilter.get_predefined_ranges()
        self.assertIsInstance(ranges, dict)
        
        # Verificar que contiene las claves esperadas
        expected_keys = ['today', 'yesterday', 'this_week', 'last_week', 
                        'this_month', 'last_month', 'this_year']
        for key in expected_keys:
            self.assertIn(key, ranges)
    
    def test_get_predefined_ranges_today(self):
        """Test rango predefinido 'today'"""
        ranges = DateRangeFilter.get_predefined_ranges()
        today_range = ranges['today']
        
        self.assertEqual(today_range['start'], date.today())
        self.assertEqual(today_range['end'], date.today())
    
    def test_get_predefined_ranges_yesterday(self):
        """Test rango predefinido 'yesterday'"""
        ranges = DateRangeFilter.get_predefined_ranges()
        yesterday_range = ranges['yesterday']
        yesterday = date.today() - timedelta(days=1)
        
        self.assertEqual(yesterday_range['start'], yesterday)
        self.assertEqual(yesterday_range['end'], yesterday)
    
    def test_build_date_range_query_both_dates(self):
        """Test build_date_range_query con ambas fechas"""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        
        result = DateRangeFilter.build_date_range_query("created_at", start_date, end_date)
        expected = Q(created_at__gte=start_date) & Q(created_at__lte=end_date)
        self.assertEqual(result, expected)
    
    def test_build_date_range_query_start_only(self):
        """Test build_date_range_query solo con fecha de inicio"""
        start_date = date(2023, 1, 1)
        
        result = DateRangeFilter.build_date_range_query("created_at", start_date, None)
        expected = Q(created_at__gte=start_date)
        self.assertEqual(result, expected)
    
    def test_build_date_range_query_end_only(self):
        """Test build_date_range_query solo con fecha de fin"""
        end_date = date(2023, 12, 31)
        
        result = DateRangeFilter.build_date_range_query("created_at", None, end_date)
        expected = Q(created_at__lte=end_date)
        self.assertEqual(result, expected)
    
    def test_build_date_range_query_no_dates(self):
        """Test build_date_range_query sin fechas"""
        result = DateRangeFilter.build_date_range_query("created_at", None, None)
        self.assertEqual(result, Q())


class SearchHighlighterTest(TestCase):
    """Tests para SearchHighlighter"""
    
    def test_highlight_terms_single_term(self):
        """Test highlight_terms con un término"""
        text = "Hello world"
        terms = ["world"]
        result = SearchHighlighter.highlight_terms(text, terms)
        expected = 'Hello <span class="highlight">world</span>'
        self.assertEqual(result, expected)
    
    def test_highlight_terms_multiple_terms(self):
        """Test highlight_terms con múltiples términos"""
        text = "Hello beautiful world"
        terms = ["Hello", "world"]
        result = SearchHighlighter.highlight_terms(text, terms)
        
        self.assertIn('<span class="highlight">Hello</span>', result)
        self.assertIn('<span class="highlight">world</span>', result)
        self.assertIn('beautiful', result)
    
    def test_highlight_terms_custom_class(self):
        """Test highlight_terms con clase CSS personalizada"""
        text = "Hello world"
        terms = ["world"]
        result = SearchHighlighter.highlight_terms(text, terms, "custom-highlight")
        expected = 'Hello <span class="custom-highlight">world</span>'
        self.assertEqual(result, expected)
    
    def test_highlight_terms_case_insensitive(self):
        """Test highlight_terms es case insensitive"""
        text = "Hello WORLD"
        terms = ["world"]
        result = SearchHighlighter.highlight_terms(text, terms)
        expected = 'Hello <span class="highlight">WORLD</span>'
        self.assertEqual(result, expected)
    
    def test_highlight_terms_no_matches(self):
        """Test highlight_terms sin coincidencias"""
        text = "Hello world"
        terms = ["python"]
        result = SearchHighlighter.highlight_terms(text, terms)
        self.assertEqual(result, text)
    
    def test_highlight_terms_empty_inputs(self):
        """Test highlight_terms con inputs vacíos"""
        result = SearchHighlighter.highlight_terms("", ["term"])
        self.assertEqual(result, "")
        
        result = SearchHighlighter.highlight_terms("text", [])
        self.assertEqual(result, "text")


class FilterValidationTest(TestCase):
    """Tests para FilterValidation"""
    
    def test_validate_choice_field_valid_choice(self):
        """Test validate_choice_field con opción válida"""
        choices = [('active', 'Active'), ('inactive', 'Inactive')]
        result = FilterValidation.validate_choice_field('active', choices)
        self.assertTrue(result)
    
    def test_validate_choice_field_invalid_choice(self):
        """Test validate_choice_field con opción inválida"""
        choices = [('active', 'Active'), ('inactive', 'Inactive')]
        result = FilterValidation.validate_choice_field('pending', choices)
        self.assertFalse(result)
    
    def test_validate_choice_field_empty_value(self):
        """Test validate_choice_field con valor vacío"""
        choices = [('active', 'Active'), ('inactive', 'Inactive')]
        result = FilterValidation.validate_choice_field('', choices)
        self.assertTrue(result)  # Valores vacíos son válidos
        
        result = FilterValidation.validate_choice_field(None, choices)
        self.assertTrue(result)
    
    def test_validate_numeric_field_valid_number(self):
        """Test validate_numeric_field con número válido"""
        result = FilterValidation.validate_numeric_field(10)
        self.assertTrue(result)
    
    def test_validate_numeric_field_with_range(self):
        """Test validate_numeric_field con rango"""
        result = FilterValidation.validate_numeric_field(15, min_value=10, max_value=20)
        self.assertTrue(result)
    
    def test_validate_numeric_field_below_min(self):
        """Test validate_numeric_field por debajo del mínimo"""
        result = FilterValidation.validate_numeric_field(5, min_value=10)
        self.assertFalse(result)
    
    def test_validate_numeric_field_above_max(self):
        """Test validate_numeric_field por encima del máximo"""
        result = FilterValidation.validate_numeric_field(25, max_value=20)
        self.assertFalse(result)
    
    def test_validate_numeric_field_non_numeric(self):
        """Test validate_numeric_field con valor no numérico"""
        result = FilterValidation.validate_numeric_field("not_a_number")
        self.assertFalse(result)
    
    def test_validate_numeric_field_none_value(self):
        """Test validate_numeric_field con valor None"""
        result = FilterValidation.validate_numeric_field(None)
        self.assertTrue(result)  # None es válido
    
    def test_validate_date_field_valid_date_string(self):
        """Test validate_date_field con string de fecha válido"""
        result = FilterValidation.validate_date_field("2023-12-25")
        self.assertTrue(result)
    
    def test_validate_date_field_valid_date_object(self):
        """Test validate_date_field con objeto date válido"""
        result = FilterValidation.validate_date_field(date(2023, 12, 25))
        self.assertTrue(result)
    
    def test_validate_date_field_invalid_date_string(self):
        """Test validate_date_field con string de fecha inválido"""
        result = FilterValidation.validate_date_field("invalid-date")
        self.assertFalse(result)
    
    def test_validate_date_field_none_value(self):
        """Test validate_date_field con valor None"""
        result = FilterValidation.validate_date_field(None)
        self.assertTrue(result)  # None es válido


class PaginationHelperTest(TestCase):
    """Tests para PaginationHelper"""
    
    def setUp(self):
        # Crear datos de prueba
        self.items = list(range(1, 101))  # 100 items
        self.paginator = Paginator(self.items, 10)  # 10 items por página
    
    def test_get_pagination_info_valid_page(self):
        """Test get_pagination_info con página válida"""
        result = PaginationHelper.get_pagination_info(self.paginator, 1)
        
        self.assertIn('current_page', result)
        self.assertIn('total_pages', result)
        self.assertIn('total_items', result)
        self.assertIn('items_per_page', result)
        self.assertIn('has_previous', result)
        self.assertIn('has_next', result)
        
        self.assertEqual(result['current_page'], 1)
        self.assertEqual(result['total_pages'], 10)
        self.assertEqual(result['total_items'], 100)
        self.assertEqual(result['items_per_page'], 10)
        self.assertFalse(result['has_previous'])
        self.assertTrue(result['has_next'])
    
    def test_get_pagination_info_middle_page(self):
        """Test get_pagination_info con página del medio"""
        result = PaginationHelper.get_pagination_info(self.paginator, 5)
        
        self.assertEqual(result['current_page'], 5)
        self.assertTrue(result['has_previous'])
        self.assertTrue(result['has_next'])
        self.assertIn('previous_page', result)
        self.assertIn('next_page', result)
        self.assertEqual(result['previous_page'], 4)
        self.assertEqual(result['next_page'], 6)
    
    def test_get_pagination_info_last_page(self):
        """Test get_pagination_info con última página"""
        result = PaginationHelper.get_pagination_info(self.paginator, 10)
        
        self.assertEqual(result['current_page'], 10)
        self.assertTrue(result['has_previous'])
        self.assertFalse(result['has_next'])
        self.assertIn('previous_page', result)
        self.assertNotIn('next_page', result)
    
    def test_get_pagination_info_invalid_page(self):
        """Test get_pagination_info con página inválida"""
        result = PaginationHelper.get_pagination_info(self.paginator, 999)
        
        # Debe retornar información de la última página válida
        self.assertEqual(result['current_page'], 10)
    
    def test_get_page_range_beginning(self):
        """Test get_page_range al inicio"""
        result = PaginationHelper.get_page_range(self.paginator, 1, window=3)
        expected = [1, 2, 3, 4]  # window=3 significa 3 a cada lado + actual
        self.assertEqual(result, expected)
    
    def test_get_page_range_middle(self):
        """Test get_page_range en el medio"""
        result = PaginationHelper.get_page_range(self.paginator, 5, window=2)
        expected = [3, 4, 5, 6, 7]  # window=2 significa 2 a cada lado + actual
        self.assertEqual(result, expected)
    
    def test_get_page_range_end(self):
        """Test get_page_range al final"""
        result = PaginationHelper.get_page_range(self.paginator, 10, window=3)
        expected = [7, 8, 9, 10]  # Limitado por el final
        self.assertEqual(result, expected)
    
    def test_get_page_range_small_paginator(self):
        """Test get_page_range con paginador pequeño"""
        small_paginator = Paginator(self.items[:25], 10)  # Solo 3 páginas
        result = PaginationHelper.get_page_range(small_paginator, 2, window=5)
        expected = [1, 2, 3]  # Todas las páginas disponibles
        self.assertEqual(result, expected)


class SearchConfigurationsTest(TestCase):
    """Tests para SEARCH_CONFIGURATIONS"""
    
    def test_search_configurations_structure(self):
        """Test que SEARCH_CONFIGURATIONS tiene la estructura correcta"""
        self.assertIsInstance(SEARCH_CONFIGURATIONS, dict)
        
        # Verificar que contiene las apps esperadas
        expected_apps = ['inventory', 'entities', 'sales', 'services']
        for app in expected_apps:
            self.assertIn(app, SEARCH_CONFIGURATIONS)
    
    def test_inventory_configurations(self):
        """Test configuraciones de inventory"""
        inventory_config = SEARCH_CONFIGURATIONS['inventory']
        
        # Verificar que contiene los modelos esperados
        expected_models = ['gps', 'simcard', 'otros']
        for model in expected_models:
            self.assertIn(model, inventory_config)
            
            # Verificar estructura de cada modelo
            model_config = inventory_config[model]
            self.assertIn('search_fields', model_config)
            self.assertIn('exact_fields', model_config)
            self.assertIn('highlight_fields', model_config)
            
            # Verificar que son listas
            self.assertIsInstance(model_config['search_fields'], list)
            self.assertIsInstance(model_config['exact_fields'], list)
            self.assertIsInstance(model_config['highlight_fields'], list)
    
    def test_entities_configurations(self):
        """Test configuraciones de entities"""
        entities_config = SEARCH_CONFIGURATIONS['entities']
        
        expected_models = ['cliente', 'proveedor', 'unidad']
        for model in expected_models:
            self.assertIn(model, entities_config)
            
            model_config = entities_config[model]
            self.assertIn('search_fields', model_config)
            self.assertIn('exact_fields', model_config)
            self.assertIn('highlight_fields', model_config)
    
    def test_sales_configurations(self):
        """Test configuraciones de sales"""
        sales_config = SEARCH_CONFIGURATIONS['sales']
        
        self.assertIn('venta', sales_config)
        venta_config = sales_config['venta']
        
        # Verificar que incluye búsqueda por relaciones
        self.assertIn('cliente__nombre', venta_config['search_fields'])
        self.assertIn('numero_venta', venta_config['exact_fields'])
    
    def test_services_configurations(self):
        """Test configuraciones de services"""
        services_config = SEARCH_CONFIGURATIONS['services']
        
        self.assertIn('servicio', services_config)
        servicio_config = services_config['servicio']
        
        # Verificar que incluye búsqueda por relaciones múltiples
        self.assertIn('cliente__nombre', servicio_config['search_fields'])
        self.assertIn('unidad__placa', servicio_config['search_fields'])
        self.assertIn('tipo_trabajo__nombre', servicio_config['search_fields'])
    
    def test_all_configurations_have_required_fields(self):
        """Test que todas las configuraciones tienen los campos requeridos"""
        required_fields = ['search_fields', 'exact_fields', 'highlight_fields']
        
        for app_name, app_config in SEARCH_CONFIGURATIONS.items():
            for model_name, model_config in app_config.items():
                for field in required_fields:
                    self.assertIn(field, model_config, 
                                f"Missing {field} in {app_name}.{model_name}")
                    self.assertIsInstance(model_config[field], list,
                                        f"{field} should be a list in {app_name}.{model_name}")
    
    def test_exact_fields_subset_of_search_fields(self):
        """Test que exact_fields es un subconjunto de search_fields donde sea lógico"""
        for app_name, app_config in SEARCH_CONFIGURATIONS.items():
            for model_name, model_config in app_config.items():
                search_fields = set(model_config['search_fields'])
                exact_fields = set(model_config['exact_fields'])
                
                # Los exact_fields deberían estar relacionados con search_fields
                # (aunque no necesariamente ser un subconjunto exacto debido a relaciones)
                for exact_field in exact_fields:
                    # Verificar que el campo exacto tiene sentido
                    self.assertTrue(
                        exact_field in search_fields or 
                        any(exact_field in search_field for search_field in search_fields),
                        f"Exact field {exact_field} not related to search fields in {app_name}.{model_name}"
                    )