"""
Tests para ViewSets avanzados con búsqueda e inteligencia de negocio.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from entities.models import Cliente, Proveedor, Unidad
from sales.models import Ventas
from services.models import TipoTrabajo, Servicio
from inventory.models import GPS

User = get_user_model()


class AdvancedSearchViewSetTestCase(APITestCase):
    """
    Tests para funcionalidades de búsqueda avanzada.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='555-1234',
            direccion='Calle 123'
        )
        
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            documento='87654321',
            email='proveedor@example.com',
            telefono='555-5678',
            direccion='Avenida 456'
        )
        
        self.tipo_trabajo = TipoTrabajo.objects.create(
            nombre='Instalación GPS',
            descripcion='Instalación de dispositivo GPS',
            precio_base=Decimal('100.00')
        )
    
    def test_advanced_search_cliente(self):
        """
        Test búsqueda avanzada en clientes.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'advanced_search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Juan Pérez')
    
    def test_search_suggestions_cliente(self):
        """
        Test sugerencias de búsqueda para clientes.
        """
        url = reverse('cliente-search-suggestions')
        response = self.client.get(url, {'q': 'Ju'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        self.assertTrue(len(response.data['suggestions']) > 0)
    
    def test_search_history_cliente(self):
        """
        Test historial de búsquedas para clientes.
        """
        # Realizar algunas búsquedas primero
        url = reverse('cliente-list')
        self.client.get(url, {'search': 'Juan'})
        self.client.get(url, {'search': 'Pérez'})
        
        # Obtener historial
        history_url = reverse('cliente-search-history')
        response = self.client.get(history_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('history', response.data)
    
    def test_advanced_search_proveedor(self):
        """
        Test búsqueda avanzada en proveedores.
        """
        url = reverse('proveedor-list')
        response = self.client.get(url, {'advanced_search': 'Proveedor'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_with_filters_proveedor(self):
        """
        Test búsqueda combinada con filtros en proveedores.
        """
        url = reverse('proveedor-list')
        response = self.client.get(url, {
            'search': 'Test',
            'documento': '87654321'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_performance_metrics(self):
        """
        Test métricas de rendimiento de búsqueda.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_info', response.data)
        self.assertIn('query_time', response.data['search_info'])
        self.assertIn('total_results', response.data['search_info'])
    
    def test_empty_search_handling(self):
        """
        Test manejo de búsquedas vacías.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': ''})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe devolver todos los resultados cuando la búsqueda está vacía
        self.assertEqual(len(response.data['results']), 1)
    
    def test_special_characters_search(self):
        """
        Test búsqueda con caracteres especiales.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': 'Juan@#$%'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe manejar caracteres especiales sin errores
    
    def test_case_insensitive_search(self):
        """
        Test búsqueda insensible a mayúsculas/minúsculas.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': 'JUAN'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_partial_match_search(self):
        """
        Test búsqueda con coincidencias parciales.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': 'Jua'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class BusinessIntelligenceViewSetTestCase(APITestCase):
    """
    Tests para funcionalidades de inteligencia de negocio.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='555-1234',
            direccion='Calle 123'
        )
        
        self.unidad = Unidad.objects.create(
            placa='ABC123',
            marca='Toyota',
            modelo='Corolla',
            año=2020,
            numero_motor='MOT123',
            numero_chasis='CHA123',
            cliente=self.cliente
        )
        
        # Crear ventas de prueba
        from datetime import datetime, time
        self.venta1 = Ventas.objects.create(
            mes=date.today(),
            fecha_pago=time(14, 30),
            numero_operacion='OP001',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='V001',
            fecha_generacion_factura=datetime.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba 1',
            unidad=self.unidad,
            precio=Decimal('1180.00'),
            importe=Decimal('1000.00'),
            igv=Decimal('180.00'),
            total=Decimal('1180.00'),
            estado='pagado'
        )
        
        self.venta2 = Ventas.objects.create(
            mes=date.today() - timedelta(days=30),
            fecha_pago=time(16, 45),
            numero_operacion='OP002',
            tipo_pago='transferencia',
            banco='Interbank',
            numero_factura='V002',
            fecha_generacion_factura=datetime.now() - timedelta(days=30),
            cliente=self.cliente,
            descripcion='Venta de prueba 2',
            unidad=self.unidad,
            precio=Decimal('1770.00'),
            importe=Decimal('1500.00'),
            igv=Decimal('270.00'),
            total=Decimal('1770.00'),
            estado='pagado'
        )
    
    def test_advanced_stats_cliente(self):
        """
        Test estadísticas avanzadas para clientes.
        """
        url = reverse('cliente-advanced-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_count', response.data)
        self.assertIn('created_today', response.data)
        self.assertIn('created_this_week', response.data)
        self.assertIn('created_this_month', response.data)
        self.assertIn('growth_rate', response.data)
    
    def test_trends_analysis_cliente(self):
        """
        Test análisis de tendencias para clientes.
        """
        url = reverse('cliente-trends-analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('trends', response.data)
        self.assertIn('period', response.data)
        self.assertIn('data_points', response.data)
    
    def test_performance_metrics_cliente(self):
        """
        Test métricas de rendimiento para clientes.
        """
        url = reverse('cliente-performance-metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', response.data)
        self.assertIn('query_performance', response.data)
    
    def test_advanced_stats_unidad(self):
        """
        Test estadísticas avanzadas para unidades.
        """
        url = reverse('unidad-advanced-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_count', response.data)
        self.assertIn('by_marca', response.data)
        self.assertIn('by_year', response.data)
    
    def test_trends_analysis_venta(self):
        """
        Test análisis de tendencias para ventas.
        """
        url = reverse('venta-trends-analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('trends', response.data)
        self.assertIn('revenue_trends', response.data)
        self.assertIn('volume_trends', response.data)
    
    def test_performance_metrics_venta(self):
        """
        Test métricas de rendimiento para ventas.
        """
        url = reverse('venta-performance-metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', response.data)
        self.assertIn('average_sale_value', response.data)
        self.assertIn('total_revenue', response.data)
    
    def test_stats_with_date_range(self):
        """
        Test estadísticas con rango de fechas.
        """
        url = reverse('venta-advanced-stats')
        response = self.client.get(url, {
            'start_date': (date.today() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'end_date': date.today().strftime('%Y-%m-%d')
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_count', response.data)
        self.assertIn('date_range', response.data)
    
    def test_trends_with_period(self):
        """
        Test análisis de tendencias con período específico.
        """
        url = reverse('cliente-trends-analysis')
        response = self.client.get(url, {'period': 'monthly'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'monthly')
    
    def test_performance_metrics_caching(self):
        """
        Test caché de métricas de rendimiento.
        """
        url = reverse('cliente-performance-metrics')
        
        # Primera llamada
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Segunda llamada (debería usar caché)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verificar que las respuestas son consistentes
        self.assertEqual(response1.data['metrics'], response2.data['metrics'])
    
    def test_stats_error_handling(self):
        """
        Test manejo de errores en estadísticas.
        """
        url = reverse('cliente-advanced-stats')
        
        # Test con parámetros inválidos
        response = self.client.get(url, {'start_date': 'invalid-date'})
        
        # Debe manejar el error graciosamente
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


class ViewSetIntegrationTestCase(APITestCase):
    """
    Tests de integración para ViewSets avanzados.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests de integración.
        """
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento='12345678',
            email='juan@example.com'
        )
        
        self.gps = GPS.objects.create(
            imei='123456789012345',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='F001',
            precio_compra=Decimal('150.00'),
            fecha_compra=date.today(),
            estado='disponible'
        )
    
    def test_combined_search_and_filters(self):
        """
        Test combinación de búsqueda avanzada y filtros.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {
            'advanced_search': 'Juan',
            'documento': '12345678',
            'ordering': 'nombre'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('search_info', response.data)
        self.assertIn('applied_filters', response.data)
    
    def test_pagination_with_advanced_features(self):
        """
        Test paginación con funcionalidades avanzadas.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'page_size': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('adaptive_info', response.data)
        self.assertIn('current_page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_ordering_with_search(self):
        """
        Test ordenamiento combinado con búsqueda.
        """
        url = reverse('gps-list')
        response = self.client.get(url, {
            'search': 'Teltonika',
            'ordering': '-fecha_compra'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ordering_info', response.data)
    
    def test_response_format_consistency(self):
        """
        Test consistencia del formato de respuesta.
        """
        endpoints = [
            reverse('cliente-list'),
            reverse('gps-list'),
            reverse('proveedor-list')
        ]
        
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verificar estructura de respuesta consistente
            self.assertIn('results', response.data)
            self.assertIn('count', response.data)
            self.assertIn('current_page', response.data)
            self.assertIn('adaptive_info', response.data)
    
    def test_error_handling_consistency(self):
        """
        Test manejo consistente de errores.
        """
        url = reverse('cliente-list')
        
        # Test con parámetros inválidos
        response = self.client.get(url, {'ordering': 'invalid_field'})
        
        # Debe manejar el error sin fallar
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    @patch('todoapi.utils.viewsets.cache')
    def test_caching_integration(self, mock_cache):
        """
        Test integración del sistema de caché.
        """
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        url = reverse('cliente-performance-metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que se intentó usar el caché
        mock_cache.get.assert_called()
    
    def test_search_config_loading(self):
        """
        Test carga de configuración de búsqueda.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'advanced_search': 'test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que la configuración se aplicó correctamente
        self.assertIn('search_info', response.data)
    
    def test_performance_monitoring(self):
        """
        Test monitoreo de rendimiento.
        """
        url = reverse('cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_info', response.data)
        self.assertIn('query_time', response.data['search_info'])
        
        # Verificar que el tiempo de consulta es razonable
        query_time = response.data['search_info']['query_time']
        self.assertIsInstance(query_time, (int, float))
        self.assertGreater(query_time, 0)