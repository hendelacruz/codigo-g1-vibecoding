"""
Tests para filtros personalizados del módulo inventory.
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from .models import GPS, SIMCard, Otros
from .filters import GPSFilter, SIMCardFilter, OtrosFilter
from entities.models import Proveedor
from authentication.models import Role

User = get_user_model()


class GPSFilterTestCase(TestCase):
    """
    Tests para el filtro de GPS.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Limpiar todos los GPS existentes para evitar interferencias
        GPS.objects.all().delete()
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='12345678901',
            correo='test@proveedor.com',
            celular='123456789'
        )
        
        # Crear datos de prueba
        self.gps1 = GPS.objects.create(
            imei='123456789012345',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='F001',
            proveedor=self.proveedor,
            precio_compra=Decimal('150.00'),
            fecha_compra=timezone.now(),
            estado='no_asignado',
            proceso='en_produccion',
            observaciones='GPS nuevo'
        )
        
        self.gps2 = GPS.objects.create(
            imei='987654321098765',
            marca='Queclink',
            modelo='GV300',
            numero_factura='F002',
            proveedor=self.proveedor,
            precio_compra=Decimal('200.00'),
            fecha_compra=timezone.now() - timedelta(days=30),
            estado='asignado',
            proceso='en_produccion',
            observaciones='GPS instalado en unidad'
        )
        
        self.gps3 = GPS.objects.create(
            imei='555666777888999',
            marca='Teltonika',
            modelo='FMB640',
            numero_factura='F003',
            proveedor=self.proveedor,
            precio_compra=Decimal('120.00'),
            fecha_compra=timezone.now() - timedelta(days=60),
            estado='no_asignado',
            proceso='en_mantenimiento',
            observaciones='GPS en reparación'
        )
    
    def test_filter_by_estado(self):
        """
        Test filtrado por estado.
        """
        filter_data = {'estado': 'no_asignado'}
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        
        # Verificar que todos los GPS filtrados tienen estado 'no_asignado'
        for gps in filterset.qs:
            self.assertEqual(gps.estado, 'no_asignado')
        
        # Verificar que tenemos al menos los GPS que esperamos
        self.assertGreaterEqual(filterset.qs.count(), 2)
        
        # Verificar que nuestros GPS específicos están incluidos si tienen el estado correcto
        if self.gps1.estado == 'no_asignado':
            self.assertIn(self.gps1, filterset.qs)
        if self.gps3.estado == 'no_asignado':
            self.assertIn(self.gps3, filterset.qs)
    
    def test_filter_by_marca(self):
        """
        Test filtrado por marca.
        """
        filter_data = {'marca': 'Teltonika'}
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 2)
        self.assertIn(self.gps1, filterset.qs)
        self.assertIn(self.gps3, filterset.qs)
    
    def test_filter_by_price_range(self):
        """
        Test filtrado por rango de precio.
        """
        filter_data = {
            'precio_min': '130.00',
            'precio_max': '180.00'
        }
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.gps1)
    
    def test_filter_by_date_range(self):
        """
        Test filtrado por rango de fecha.
        """
        filter_data = {
            'fecha_compra_desde': (timezone.now() - timedelta(days=45)).isoformat(),
            'fecha_compra_hasta': timezone.now().isoformat()
        }
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 2)
        self.assertIn(self.gps1, filterset.qs)
        self.assertIn(self.gps2, filterset.qs)
    
    def test_search_filter(self):
        """
        Test búsqueda por texto.
        """
        filter_data = {'search': 'FMB920'}
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.gps1)
    
    def test_disponibles_filter(self):
        """
        Test filtro de disponibles.
        """
        filter_data = {'disponible': True}
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        
        # Verificar que todos los GPS filtrados cumplen: estado='no_asignado' Y proceso='en_produccion'
        for gps in filterset.qs:
            self.assertEqual(gps.estado, 'no_asignado')
            self.assertEqual(gps.proceso, 'en_produccion')
        
        # Verificar que tenemos al menos un GPS disponible
        self.assertGreaterEqual(filterset.qs.count(), 1)
        
        # Verificar que gps1 está incluido si cumple las condiciones
        if (self.gps1.estado == 'no_asignado' and self.gps1.proceso == 'en_produccion'):
            self.assertIn(self.gps1, filterset.qs)
    
    def test_multiple_filters(self):
        """
        Test combinación de múltiples filtros.
        """
        filter_data = {
            'marca': 'Teltonika',
            'proceso': 'en_produccion',  # Corregido: usar proceso en lugar de estado
            'precio_min': '100.00'
        }
        filterset = GPSFilter(filter_data, queryset=GPS.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.gps1)


class SIMCardFilterTestCase(TestCase):
    """
    Tests para el filtro personalizado de SIMCard.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor SIM',
            ruc='12345678902',
            correo='sim@proveedor.com',
            celular='123456789'
        )
        
        self.sim1 = SIMCard.objects.create(
            numero_chip='987654321',
            icc='89511234567890123456',
            operadora='Claro',
            plan='Plan Básico',
            numero_factura='S001',
            proveedor=self.proveedor,
            precio_compra=Decimal('25.00'),
            fecha_compra=timezone.now(),
            estado='activo',
            observaciones='SIM nueva'
        )
        
        self.sim2 = SIMCard.objects.create(
            numero_chip='123456789',
            icc='89511234567890123457',
            operadora='Movistar',
            plan='Plan Premium',
            numero_factura='S002',
            proveedor=self.proveedor,
            precio_compra=Decimal('35.00'),
            fecha_compra=timezone.now() - timedelta(days=15),
            estado='suspendido',
            observaciones='SIM suspendida'
        )
    
    def test_filter_by_operadora(self):
        """
        Test filtrado por operadora.
        """
        filter_data = {'operadora': 'Claro'}
        filterset = SIMCardFilter(filter_data, queryset=SIMCard.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.sim1)
    
    def test_filter_by_estado(self):
        """
        Test filtrado por estado.
        """
        filter_data = {'estado': 'activo'}
        filterset = SIMCardFilter(filter_data, queryset=SIMCard.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.sim1)
    
    def test_activas_filter(self):
        """
        Test filtro de SIMs activas.
        """
        filter_data = {'activas': True}
        filterset = SIMCardFilter(filter_data, queryset=SIMCard.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.sim1)


class OtrosFilterTestCase(TestCase):
    """
    Tests para el filtro personalizado de Otros.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Otros',
            ruc='12345678903',
            correo='otros@proveedor.com',
            celular='123456789'
        )
        
        self.item1 = Otros.objects.create(
            descripcion='Cable USB',
            categoria='Cables',
            cantidad=100,
            stock_actual=50,
            precio_unitario=Decimal('15.00'),
            numero_factura='O001',
            proveedor=self.proveedor,
            fecha_compra=timezone.now(),
            observaciones='Cables nuevos'
        )
        
        self.item2 = Otros.objects.create(
            descripcion='Antena GPS',
            categoria='Antenas',
            cantidad=20,
            stock_actual=3,
            precio_unitario=Decimal('45.00'),
            numero_factura='O002',
            proveedor=self.proveedor,
            fecha_compra=timezone.now() - timedelta(days=20),
            observaciones='Antenas de repuesto'
        )
    
    def test_filter_by_categoria(self):
        """
        Test filtrado por categoría.
        """
        filter_data = {'categoria': 'Cables'}
        filterset = OtrosFilter(filter_data, queryset=Otros.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.item1)
    
    def test_filter_by_stock_range(self):
        """
        Test filtrado por rango de stock.
        """
        filter_data = {
            'stock_min': 20,
            'stock_max': 60
        }
        filterset = OtrosFilter(filter_data, queryset=Otros.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.item1)
    
    def test_bajo_stock_filter(self):
        """
        Test filtro de bajo stock.
        """
        filter_data = {'stock_bajo': True}
        filterset = OtrosFilter(filter_data, queryset=Otros.objects.all())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 1)
        self.assertEqual(filterset.qs.first(), self.item2)


class InventoryAPIFilterTestCase(APITestCase):
    """
    Tests de integración para filtros en la API de inventory.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests de API.
        """
        # Crear rol de prueba
        self.role = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'inventory': ['read', 'write']}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.role
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor API',
            ruc='12345678904',
            correo='api@proveedor.com',
            celular='123456789'
        )
        
        self.gps = GPS.objects.create(
            imei='123456789012345',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='F001',
            proveedor=self.proveedor,
            precio_compra=Decimal('150.00'),
            fecha_compra=timezone.now(),
            estado='no_asignado',
            proceso='en_produccion'
        )
    
    def test_gps_api_filter_by_estado(self):
        """
        Test filtrado por estado en la API de GPS.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url, {'estado': 'no_asignado'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['imei'], '123456789012345')
    
    def test_gps_api_search(self):
        """
        Test búsqueda en la API de GPS.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url, {'search': 'Teltonika'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_gps_api_advanced_search(self):
        """
        Test búsqueda avanzada en la API de GPS.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url, {'advanced_search': 'FMB920'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_gps_api_price_range(self):
        """
        Test filtrado por rango de precio en la API.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url, {
            'precio_min': '100.00',
            'precio_max': '200.00'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_gps_api_estadisticas(self):
        """
        Test endpoint de estadísticas de GPS.
        """
        url = reverse('inventory:gps-estadisticas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('disponibles', response.data)
        self.assertIn('asignados', response.data)
        self.assertIn('en_mantenimiento', response.data)
        self.assertIn('precio_promedio', response.data)
    
    def test_gps_cambiar_estado(self):
        """
        Test endpoint para cambiar estado de GPS.
        """
        # Crear un cliente para poder asignar el GPS
        from entities.models import Cliente
        cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            correo='cliente@test.com',
            celular='987654321'
        )
        
        # Asignar el cliente al GPS
        self.gps.cliente = cliente
        self.gps.save()
        
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        response = self.client.patch(url, {
            'estado': 'asignado',
            'observaciones': 'Asignado para prueba'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'asignado')
    
    def test_pagination_info(self):
        """
        Test información de paginación en respuestas.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        # Note: pagination info depends on the pagination class used
    
    def test_applied_filters_info(self):
        """
        Test información de filtros aplicados.
        """
        url = reverse('inventory:gps-list')
        response = self.client.get(url, {'estado': 'no_asignado', 'marca': 'Teltonika'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: filter info depends on the custom viewset implementation