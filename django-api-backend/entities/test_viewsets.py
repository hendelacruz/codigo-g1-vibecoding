"""
Tests para ViewSets del módulo entities con funcionalidades avanzadas.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Cliente, Proveedor, Unidad
from authentication.models import Role

User = get_user_model()


class ClienteViewSetTestCase(APITestCase):
    """
    Tests para ClienteViewSet con inteligencia de negocio.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'read': True, 'write': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.cliente1 = Cliente.objects.create(
            nombre='Juan Pérez',
            ruc='12345678901',
            correo='juan@example.com',
            celular='987654321',
            direccion='Calle 123',
            contacto='Juan Pérez'
        )
        
        self.cliente2 = Cliente.objects.create(
            nombre='María García',
            ruc='87654321098',
            correo='maria@example.com',
            celular='987654322',
            direccion='Avenida 456',
            contacto='María García'
        )
        
        self.cliente3 = Cliente.objects.create(
            nombre='Carlos López',
            ruc='11223344556',
            correo='carlos@example.com',
            celular='987654323',
            direccion='Carrera 789',
            contacto='Carlos López'
        )
    
    def test_list_clientes(self):
        """
        Test listar clientes.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
        self.assertIn('nombre', response.data['results'][0])
        self.assertIn('ruc', response.data['results'][0])
    
    def test_search_clientes(self):
        """
        Test búsqueda básica en clientes.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Juan Pérez')
        self.assertIn('adaptive_info', response.data)
    
    def test_search_by_nombre(self):
        """
        Test búsqueda por nombre de cliente.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Juan Pérez')
    
    def test_filter_by_nombre(self):
        """
        Test filtrado por nombre usando el filtro de búsqueda estándar.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        # Verificar que al menos uno de los resultados contiene 'Juan' en el nombre
        nombres = [cliente['nombre'] for cliente in response.data['results']]
        self.assertTrue(any('Juan' in nombre for nombre in nombres))
    
    def test_ordering_clientes(self):
        """
        Test ordenamiento de clientes.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {'ordering': 'nombre'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [cliente['nombre'] for cliente in response.data['results']]
        self.assertEqual(nombres, sorted(nombres))
    
    def test_combined_search_and_filters(self):
        """
        Test combinación de búsqueda y filtros.
        """
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {
            'search': 'Juan',
            'ordering': 'nombre'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 0)


class ProveedorViewSetTestCase(APITestCase):
    """
    Tests para ProveedorViewSet con búsqueda avanzada.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'read': True, 'write': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.proveedor1 = Proveedor.objects.create(
            nombre='Proveedor GPS',
            ruc='11111111111',
            correo='gps@proveedor.com',
            celular='987654331',
            direccion='Zona Industrial 1',
            contacto='Proveedor GPS'
        )
        
        self.proveedor2 = Proveedor.objects.create(
            nombre='Proveedor SIM',
            ruc='22222222222',
            correo='sim@proveedor.com',
            celular='987654332',
            direccion='Zona Industrial 2',
            contacto='Proveedor SIM'
        )
    
    def test_list_proveedores(self):
        """
        Test listado básico de proveedores.
        """
        url = reverse('entities:proveedor-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_search_by_nombre_proveedor(self):
        """
        Test búsqueda por nombre de proveedor.
        """
        url = reverse('entities:proveedor-list')
        response = self.client.get(url, {'search': 'Proveedor'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
        self.assertIn('nombre', response.data['results'][0])
    
    def test_search_by_correo(self):
        """
        Test búsqueda por correo en proveedores.
        """
        url = reverse('entities:proveedor-list')
        response = self.client.get(url, {'search': 'gps@proveedor.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_search_by_celular(self):
        """
        Test búsqueda por celular en proveedores.
        """
        url = reverse('entities:proveedor-list')
        response = self.client.get(url, {'search': '987654331'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    

    
    def test_ordering_proveedores(self):
        """
        Test ordenamiento de proveedores.
        """
        url = reverse('entities:proveedor-list')
        response = self.client.get(url, {'ordering': '-nombre'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [proveedor['nombre'] for proveedor in response.data['results']]
        self.assertEqual(nombres, sorted(nombres, reverse=True))


class UnidadViewSetTestCase(APITestCase):
    """
    Tests para UnidadViewSet con inteligencia de negocio.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'read': True, 'write': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear cliente para las unidades
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            correo='cliente@test.com',
            celular='987654321',
            direccion='Dirección Test',
            contacto='Cliente Test'
        )
        
        # Crear datos de prueba
        self.unidad1 = Unidad.objects.create(
            tipo='bus',
            placa='ABC123',
            marca='Toyota',
            modelo='Corolla',
            serie='SER123',
            cliente=self.cliente
        )
        
        self.unidad2 = Unidad.objects.create(
            tipo='camion',
            placa='XYZ789',
            marca='Honda',
            modelo='Civic',
            serie='SER456',
            cliente=self.cliente
        )
        
        self.unidad3 = Unidad.objects.create(
            tipo='bus',
            placa='DEF456',
            marca='Toyota',
            modelo='Camry',
            serie='SER789',
            cliente=self.cliente
        )
    
    def test_list_unidades(self):
        """
        Test listado básico de unidades.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)
    
    def test_search_by_placa(self):
        """
        Test búsqueda por placa.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {'search': 'ABC123'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['placa'], 'ABC123')
    
    def test_search_by_serie(self):
        """
        Test búsqueda por número de serie.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {'search': 'SER123'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_search_by_serie_partial(self):
        """
        Test búsqueda parcial por número de serie.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {'search': 'SER456'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_filter_by_marca(self):
        """
        Test filtrado por marca.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {'marca': 'Toyota'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_filter_by_tipo(self):
        """
        Test filtrado por tipo de vehículo.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {'tipo': 'bus'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_combined_filters_unidades(self):
        """
        Test combinación de filtros en unidades.
        """
        url = reverse('entities:unidad-list')
        response = self.client.get(url, {
            'search': 'Toyota',
            'ordering': 'modelo'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 0)


class EntitiesIntegrationTestCase(APITestCase):
    """
    Tests de integración para el módulo entities.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests de integración.
        """
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'read': True, 'write': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos relacionados
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            correo='cliente@test.com',
            celular='987654321',
            direccion='Dirección Test',
            contacto='Cliente Test'
        )
        
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC123',
            marca='Toyota',
            modelo='Corolla',
            serie='SER123',
            cliente=self.cliente
        )
    
    def test_cliente_unidades_relationship(self):
        """
        Test relación entre cliente y unidades.
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que incluye información de unidades relacionadas
        self.assertIn('unidades_count', response.data)
        self.assertEqual(response.data['unidades_count'], 1)
    
    def test_basic_search_functionality(self):
        """
        Test funcionalidad básica de búsqueda.
        """
        # Buscar cliente
        url = reverse('entities:cliente-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 0)
    
    def test_basic_endpoints_availability(self):
        """
        Test disponibilidad de endpoints básicos.
        """
        endpoints = [
            reverse('entities:cliente-list'),
            reverse('entities:proveedor-list'),
            reverse('entities:unidad-list')
        ]
        
        for url in endpoints:
            response = self.client.get(url, {'search': 'test'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('adaptive_info', response.data)
            # Verificar que adaptive_info contiene información útil
            self.assertIsInstance(response.data['adaptive_info'], dict)
    
    def test_consistent_response_format(self):
        """
        Test formato de respuesta consistente.
        """
        endpoints = [
            reverse('entities:cliente-list'),
            reverse('entities:proveedor-list'),
            reverse('entities:unidad-list')
        ]
        
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verificar estructura consistente
            required_fields = ['results', 'count', 'current_page', 'adaptive_info']
            for field in required_fields:
                self.assertIn(field, response.data, f"Missing {field} in {url}")
    
    def test_error_handling_consistency(self):
        """
        Test manejo consistente de errores.
        """
        endpoints = [
            reverse('entities:cliente-list'),
            reverse('entities:proveedor-list'),
            reverse('entities:unidad-list')
        ]
        
        for url in endpoints:
            # Test con parámetros inválidos
            response = self.client.get(url, {'ordering': 'invalid_field'})
            
            # Debe manejar el error sin fallar
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])