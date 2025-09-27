"""
Tests for viewsets in todoapi.utils.viewsets
"""

import csv
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.http import HttpResponse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.response import Response
from rest_framework import serializers

from todoapi.utils.viewsets import (
    AdvancedSearchViewSet,
    BusinessIntelligenceViewSet
)

User = get_user_model()


# Mock model for testing
class MockModel(models.Model):
    """Mock model for testing viewsets"""
    name = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cantidad = models.IntegerField(null=True)
    stock_actual = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    fecha_venta = models.DateField(null=True)
    
    class Meta:
        app_label = 'test'


class MockSerializer(serializers.ModelSerializer):
    """Mock serializer for testing"""
    class Meta:
        model = MockModel
        fields = '__all__'


class AdvancedSearchViewSetTest(APITestCase):
    """Test AdvancedSearchViewSet functionality"""
    
    def setUp(self):
        """Set up test data"""
        from authentication.models import Role
        
        self.factory = APIRequestFactory()
        
        # Crear rol para el usuario
        self.user_role = Role.objects.create(
            nombre='admin',
            descripcion='Administrador del sistema'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='30000010',
            celular='3000000010',
            rol=self.user_role
        )
        
        # Create test viewset class
        class TestViewSet(AdvancedSearchViewSet):
            queryset = MockModel.objects.all()
            serializer_class = MockSerializer
            search_config_key = 'test.model'
            
            def get_queryset(self):
                # Mock queryset for testing
                mock_queryset = Mock()
                mock_queryset.model = MockModel
                mock_queryset.count.return_value = 10
                mock_queryset.filter.return_value = mock_queryset
                mock_queryset.values_list.return_value.distinct.return_value = ['test1', 'test2']
                mock_queryset.aggregate.return_value = {
                    'avg': 100.0, 'min': 50.0, 'max': 150.0, 'sum': 1000.0
                }
                mock_queryset.exists.return_value = True
                mock_queryset.__iter__ = lambda x: iter([])
                return mock_queryset
        
        self.viewset_class = TestViewSet
    
    def test_get_search_config(self):
        """Test search configuration retrieval"""
        viewset = self.viewset_class()
        viewset.search_config_key = 'test.model'
        
        # Mock SEARCH_CONFIGURATIONS
        with patch('todoapi.utils.viewsets.SEARCH_CONFIGURATIONS', {
            'test': {'model': {'search_fields': ['name', 'description']}}
        }):
            config = viewset.get_search_config()
            self.assertEqual(config, {'search_fields': ['name', 'description']})
    
    def test_get_search_config_no_key(self):
        """Test search configuration when no key is set"""
        viewset = self.viewset_class()
        viewset.search_config_key = None
        
        config = viewset.get_search_config()
        self.assertEqual(config, {})
    
    def test_filter_queryset_with_advanced_search(self):
        """Test queryset filtering with advanced search"""
        request = self.factory.get('/test/', {'advanced_search': 'test query'})
        
        viewset = self.viewset_class()
        viewset.request = request
        viewset.apply_advanced_search = Mock(return_value=Mock())
        
        mock_queryset = Mock()
        result = viewset.filter_queryset(mock_queryset)
        
        viewset.apply_advanced_search.assert_called_once_with(mock_queryset, 'test query')
    
    def test_apply_advanced_search(self):
        """Test advanced search application"""
        viewset = self.viewset_class()
        viewset.get_search_config = Mock(return_value={
            'search_fields': ['name', 'description']
        })
        viewset.build_search_query = Mock(return_value=Mock())
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        result = viewset.apply_advanced_search(mock_queryset, 'test')
        
        viewset.build_search_query.assert_called_once_with(['name', 'description'], 'test')
        mock_queryset.filter.assert_called_once()
    
    def test_apply_numeric_range_filters(self):
        """Test numeric range filters application"""
        request = self.factory.get('/test/', {
            'precio_min': '10.0',
            'precio_max': '100.0',
            'cantidad_min': '5'
        })
        
        viewset = self.viewset_class()
        viewset.request = request
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        with patch('todoapi.utils.viewsets.NumericRangeFilter') as mock_filter:
            mock_filter.validate_range.return_value = True
            mock_filter.build_range_query.return_value = Mock()
            
            result = viewset.apply_numeric_range_filters(mock_queryset)
            
            # Should validate and build range queries
            mock_filter.validate_range.assert_called()
            mock_filter.build_range_query.assert_called()
    
    def test_apply_numeric_range_filters_invalid_values(self):
        """Test numeric range filters with invalid values"""
        request = self.factory.get('/test/', {
            'precio_min': 'invalid',
            'precio_max': 'also_invalid'
        })
        
        viewset = self.viewset_class()
        viewset.request = request
        
        mock_queryset = Mock()
        
        # Should not raise error with invalid values
        result = viewset.apply_numeric_range_filters(mock_queryset)
        self.assertEqual(result, mock_queryset)
    
    def test_apply_date_range_filters(self):
        """Test date range filters application"""
        request = self.factory.get('/test/', {
            'fecha_desde': '2023-01-01',
            'fecha_hasta': '2023-12-31'
        })
        
        viewset = self.viewset_class()
        viewset.request = request
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        
        with patch('todoapi.utils.viewsets.DateRangeFilter') as mock_filter:
            mock_filter.build_date_range_query.return_value = Mock()
            
            result = viewset.apply_date_range_filters(mock_queryset)
            
            mock_filter.build_date_range_query.assert_called()
            mock_queryset.filter.assert_called()
    
    def test_apply_date_range_filters_invalid_dates(self):
        """Test date range filters with invalid dates"""
        request = self.factory.get('/test/', {
            'fecha_desde': 'invalid-date',
            'fecha_hasta': '2023-13-45'  # Invalid date
        })
        
        viewset = self.viewset_class()
        viewset.request = request
        
        mock_queryset = Mock()
        
        # Should not raise error with invalid dates
        result = viewset.apply_date_range_filters(mock_queryset)
        self.assertEqual(result, mock_queryset)
    
    def test_search_suggestions_action(self):
        """Test search suggestions action"""
        request = self.factory.get('/test/search_suggestions/', {'q': 'test'})
        
        viewset = self.viewset_class()
        viewset.request = request
        viewset.get_search_config = Mock(return_value={
            'search_fields': ['name', 'description']
        })
        
        # Mock queryset for suggestions
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.values_list.return_value.distinct.return_value = ['test1', 'test2']
        viewset.get_queryset = Mock(return_value=mock_queryset)
        
        response = viewset.search_suggestions(request)
        
        self.assertIsInstance(response, Response)
        self.assertIn('suggestions', response.data)
    
    def test_search_suggestions_short_query(self):
        """Test search suggestions with short query"""
        request = self.factory.get('/test/search_suggestions/', {'q': 't'})
        
        viewset = self.viewset_class()
        viewset.request = request
        
        response = viewset.search_suggestions(request)
        
        self.assertEqual(response.data['suggestions'], [])
    
    def test_advanced_stats_action(self):
        """Test advanced stats action"""
        request = self.factory.get('/test/advanced_stats/')
        
        viewset = self.viewset_class()
        viewset.request = request
        viewset.filter_queryset = Mock(return_value=viewset.get_queryset())
        
        with patch('todoapi.utils.viewsets.timezone') as mock_timezone:
            mock_timezone.now.return_value.date.return_value = datetime(2023, 6, 15).date()
            
            response = viewset.advanced_stats(request)
            
            self.assertIsInstance(response, Response)
            self.assertIn('total_count', response.data)
            self.assertIn('created_today', response.data)
            self.assertIn('created_this_week', response.data)
            self.assertIn('created_this_month', response.data)
    
    def test_export_filtered_action(self):
        """Test export filtered action"""
        request = self.factory.get('/test/export_filtered/')
        
        viewset = self.viewset_class()
        viewset.request = request
        
        # Mock queryset with data
        mock_obj = Mock()
        mock_obj.name = 'Test Object'
        mock_obj.precio = 100.0
        
        mock_queryset = Mock()
        mock_queryset.model = MockModel
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__ = lambda x: iter([mock_obj])
        
        viewset.filter_queryset = Mock(return_value=mock_queryset)
        viewset.get_queryset = Mock(return_value=mock_queryset)
        
        response = viewset.export_filtered(request)
        
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_list_with_additional_info(self):
        """Test list method with additional information"""
        request = self.factory.get('/test/', {
            'search': 'test query',
            'filter1': 'value1',
            'page': '1'
        })
        
        viewset = self.viewset_class()
        viewset.request = request
        
        # Mock parent list method
        mock_response = Response({
            'results': [],
            'count': 0
        })
        
        with patch.object(AdvancedSearchViewSet.__bases__[0], 'list', return_value=mock_response):
            response = viewset.list(request)
            
            self.assertIn('applied_filters', response.data)
            self.assertIn('filter_count', response.data)
            self.assertIn('search_term', response.data)
            self.assertIn('search_applied', response.data)
            self.assertTrue(response.data['search_applied'])


class BusinessIntelligenceViewSetTest(APITestCase):
    """Test BusinessIntelligenceViewSet functionality"""
    
    def setUp(self):
        """Set up test data"""
        from authentication.models import Role
        
        self.factory = APIRequestFactory()
        
        # Crear rol para el usuario
        self.user_role = Role.objects.create(
            nombre='admin',
            descripcion='Administrador del sistema'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='30000011',
            celular='3000000011',
            rol=self.user_role
        )
        
        class TestBIViewSet(BusinessIntelligenceViewSet):
            queryset = MockModel.objects.all()
            serializer_class = MockSerializer
            
            def get_queryset(self):
                mock_queryset = Mock()
                mock_queryset.count.return_value = 10
                mock_queryset.filter.return_value = mock_queryset
                mock_queryset.annotate.return_value = mock_queryset
                mock_queryset.values.return_value = mock_queryset
                mock_queryset.order_by.return_value = [
                    {'date': datetime(2023, 6, 1).date(), 'count': 5},
                    {'date': datetime(2023, 6, 2).date(), 'count': 3}
                ]
                return mock_queryset
        
        self.viewset_class = TestBIViewSet
    
    def test_dashboard_stats_action(self):
        """Test dashboard stats action"""
        request = self.factory.get('/test/dashboard_stats/')
        
        viewset = self.viewset_class()
        viewset.request = request
        
        with patch('todoapi.utils.viewsets.timezone') as mock_timezone:
            mock_now = datetime(2023, 6, 15, 12, 0, 0)
            mock_timezone.now.return_value = mock_now
            mock_timezone.now.return_value.date.return_value = mock_now.date()
            
            response = viewset.dashboard_stats(request)
            
            self.assertIsInstance(response, Response)
            self.assertIn('today', response.data)
            self.assertIn('yesterday', response.data)
            self.assertIn('this_week', response.data)
            self.assertIn('this_month', response.data)
            self.assertIn('total', response.data)
            self.assertIn('trends', response.data)
            
            # Check trends structure
            trends = response.data['trends']
            self.assertIn('week_change', trends)
            self.assertIn('month_change', trends)
            self.assertIn('week_change_percent', trends)
            self.assertIn('month_change_percent', trends)
    
    def test_time_series_action(self):
        """Test time series action"""
        request = self.factory.get('/test/time_series/', {'days': '7'})
        
        viewset = self.viewset_class()
        viewset.request = request
        
        with patch('todoapi.utils.viewsets.timezone') as mock_timezone:
            mock_timezone.now.return_value = datetime(2023, 6, 15, 12, 0, 0)
            
            response = viewset.time_series(request)
            
            self.assertIsInstance(response, Response)
            self.assertIsInstance(response.data, list)
    
    def test_time_series_default_days(self):
        """Test time series action with default days parameter"""
        request = self.factory.get('/test/time_series/')
        
        viewset = self.viewset_class()
        viewset.request = request
        
        with patch('todoapi.utils.viewsets.timezone') as mock_timezone:
            mock_timezone.now.return_value = datetime(2023, 6, 15, 12, 0, 0)
            
            response = viewset.time_series(request)
            
            self.assertIsInstance(response, Response)
            # Should use default 30 days
            viewset.get_queryset().filter.assert_called()


class ViewSetIntegrationTest(APITestCase):
    """Integration tests for viewset functionality"""
    
    def setUp(self):
        """Set up test data"""
        from authentication.models import Role
        
        self.factory = APIRequestFactory()
        
        # Crear rol para el usuario
        self.user_role = Role.objects.create(
            nombre='admin',
            descripcion='Administrador del sistema'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='30000012',
            celular='3000000012',
            rol=self.user_role
        )
    
    def test_viewset_inheritance_chain(self):
        """Test that viewset inheritance works correctly"""
        class TestViewSet(BusinessIntelligenceViewSet):
            queryset = MockModel.objects.all()
            serializer_class = MockSerializer
        
        viewset = TestViewSet()
        
        # Should have methods from both parent classes
        self.assertTrue(hasattr(viewset, 'dashboard_stats'))
        self.assertTrue(hasattr(viewset, 'time_series'))
        self.assertTrue(hasattr(viewset, 'search_suggestions'))
        self.assertTrue(hasattr(viewset, 'advanced_stats'))
        self.assertTrue(hasattr(viewset, 'export_filtered'))
    
    def test_error_handling_in_stats(self):
        """Test error handling in statistical methods"""
        class TestViewSet(BusinessIntelligenceViewSet):
            def get_queryset(self):
                # Mock queryset that raises errors
                mock_queryset = Mock()
                mock_queryset.count.side_effect = Exception("Database error")
                mock_queryset.filter.return_value = mock_queryset
                return mock_queryset
        
        viewset = TestViewSet()
        request = self.factory.get('/test/dashboard_stats/')
        viewset.request = request
        
        # Should handle errors gracefully
        try:
            response = viewset.dashboard_stats(request)
            # If no exception is raised, the error handling worked
        except Exception as e:
            self.fail(f"Error handling failed: {e}")
    
    def test_empty_queryset_handling(self):
        """Test handling of empty querysets"""
        class TestViewSet(AdvancedSearchViewSet):
            def get_queryset(self):
                mock_queryset = Mock()
                mock_queryset.exists.return_value = False
                mock_queryset.count.return_value = 0
                mock_queryset.filter.return_value = mock_queryset
                mock_queryset.__iter__ = lambda x: iter([])
                return mock_queryset
        
        viewset = TestViewSet()
        request = self.factory.get('/test/export_filtered/')
        viewset.request = request
        viewset.filter_queryset = Mock(return_value=viewset.get_queryset())
        
        response = viewset.export_filtered(request)
        
        # Should handle empty queryset without errors
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')