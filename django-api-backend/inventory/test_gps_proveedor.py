from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from authentication.models import Role
from entities.models import Proveedor, Cliente
from inventory.models import GPS
from decimal import Decimal
from datetime import datetime
from decimal import Decimal

User = get_user_model()


class GPSProveedorTestCase(APITestCase):
    """
    Test suite para validar la relación entre GPS y Proveedor
    Verifica que se pueda identificar correctamente el proveedor (Movistar, Claro, Entel, etc.)
    """
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Limpiar datos existentes
        GPS.objects.all().delete()
        Cliente.objects.all().delete()
        Proveedor.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()
        # Crear rol de administrador
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Rol de administrador del sistema'
        )
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.admin_role
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear proveedores de telecomunicaciones
        self.proveedor_movistar = Proveedor.objects.create(
            nombre='Movistar Perú',
            ruc='20100017491',
            direccion='Av. Arequipa 1155, Lima',
            contacto='Juan Pérez',
            celular='987654321',
            correo='contacto@movistar.pe'
        )
        
        self.proveedor_claro = Proveedor.objects.create(
            nombre='Claro Perú',
            ruc='20467534026',
            direccion='Av. República de Panamá 3505, Lima',
            contacto='María García',
            celular='987654322',
            correo='contacto@claro.pe'
        )
        
        self.proveedor_entel = Proveedor.objects.create(
            nombre='Entel Perú',
            ruc='20600258681',
            direccion='Av. Víctor Andrés Belaúnde 147, Lima',
            contacto='Carlos López',
            celular='987654323',
            correo='contacto@entel.pe'
        )
        
        # Crear clientes de prueba
        self.cliente1 = Cliente.objects.create(
            nombre="Transportes Lima SAC",
            ruc="20111222333",
            direccion="Av. Principal 789",
            contacto="Carlos Mendoza",
            celular="+51999888777",
            correo="contacto@transporteslima.com"
        )
        
        self.cliente2 = Cliente.objects.create(
            nombre="Logística del Sur EIRL",
            ruc="20444555666",
            direccion="Jr. Comercio 321",
            contacto="Ana Torres",
            celular="+51888777666",
            correo="info@logisticasur.com"
        )
        
        # URL para endpoints de GPS
        self.gps_url = reverse('inventory:gps-list')
        
        # Datos válidos para crear GPS
        self.valid_gps_data = {
            'fecha_compra': '2024-01-15T10:00:00Z',
            'imei': '123456789012347',  # IMEI válido según algoritmo de Luhn
            'marca': 'Teltonika',
            'modelo': 'FMB920',
            'numero_factura': 'FAC-001',
            'proveedor': self.proveedor_movistar.id,
            'estado': 'no_asignado',
            'proceso': 'en_produccion',
            'precio_compra': '250.00',
            'observaciones': 'GPS para pruebas con Movistar'
        }
    
    def test_create_gps_with_movistar_provider(self):
        """Test: Crear GPS con proveedor Movistar"""
        response = self.client.post(self.gps_url, self.valid_gps_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GPS.objects.count(), 1)
        
        gps = GPS.objects.first()
        self.assertEqual(gps.proveedor.id, self.proveedor_movistar.id)
        self.assertEqual(gps.proveedor.nombre, 'Movistar Perú')
        
        # Verificar que la respuesta incluye información del proveedor
        self.assertIn('proveedor_info', response.data)
        self.assertEqual(response.data['proveedor_info']['nombre'], 'Movistar Perú')
        self.assertEqual(response.data['proveedor_info']['ruc'], '20100017491')
    
    def test_create_gps_with_claro_provider(self):
        """Test: Crear GPS con proveedor Claro"""
        gps_data = self.valid_gps_data.copy()
        gps_data['proveedor'] = self.proveedor_claro.id
        gps_data['imei'] = '123456789012354'  # IMEI diferente y válido
        gps_data['numero_factura'] = 'FAC-002'
        gps_data['observaciones'] = 'GPS para pruebas con Claro'
        
        response = self.client.post(self.gps_url, gps_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Error: {response.data}")
        
        gps = GPS.objects.get(imei='123456789012354')
        self.assertEqual(gps.proveedor.id, self.proveedor_claro.id)
        self.assertEqual(gps.proveedor.nombre, 'Claro Perú')
        
        # Verificar información del proveedor en la respuesta
        self.assertEqual(response.data['proveedor_info']['nombre'], 'Claro Perú')
        self.assertEqual(response.data['proveedor_info']['ruc'], '20467534026')
    
    def test_create_gps_with_entel_provider(self):
        """Test: Crear GPS con proveedor Entel"""
        gps_data = self.valid_gps_data.copy()
        gps_data['proveedor'] = self.proveedor_entel.id
        gps_data['imei'] = '351234567890124'  # IMEI válido que pasa algoritmo de Luhn
        gps_data['numero_factura'] = 'FAC-003'
        gps_data['observaciones'] = 'GPS para pruebas con Entel'
        
        response = self.client.post(self.gps_url, gps_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Error: {response.data}")
        
        gps = GPS.objects.get(imei='351234567890124')
        self.assertEqual(gps.proveedor.id, self.proveedor_entel.id)
        self.assertEqual(gps.proveedor.nombre, 'Entel Perú')
        
        # Verificar información del proveedor en la respuesta
        self.assertEqual(response.data['proveedor_info']['nombre'], 'Entel Perú')
        self.assertEqual(response.data['proveedor_info']['ruc'], '20600258681')
    
    def test_list_gps_with_provider_info(self):
        """Test: Listar GPS mostrando información del proveedor"""
        # Crear GPS con diferentes proveedores
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='555666777888991',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('250.00')
        )
        
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='111222333444556',
            marca='Queclink',
            modelo='GV300',
            numero_factura='FAC-002',
            proveedor=self.proveedor_claro,
            precio_compra=Decimal('180.00')
        )
        
        response = self.client.get(self.gps_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verificar que cada GPS incluye información del proveedor
        for gps_data in response.data['results']:
            self.assertIn('proveedor_info', gps_data)
            self.assertIn('nombre', gps_data['proveedor_info'])
            self.assertIn('ruc', gps_data['proveedor_info'])
    
    def test_filter_gps_by_provider(self):
        """Test: Filtrar GPS por proveedor"""
        # Crear GPS con diferentes proveedores
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='222333444555667',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('250.00')
        )
        
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='333444555666778',
            marca='Queclink',
            modelo='GV300',
            numero_factura='FAC-002',
            proveedor=self.proveedor_claro,
            precio_compra=Decimal('180.00')
        )
        
        # Filtrar por proveedor Movistar
        response = self.client.get(f'{self.gps_url}?proveedor={self.proveedor_movistar.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['proveedor_info']['nombre'], 'Movistar Perú')
    
    def test_update_gps_provider(self):
        """Test: Actualizar proveedor de un GPS"""
        # Crear GPS con Movistar
        gps = GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='444555666777889',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('250.00')
        )
        
        # Actualizar a Claro
        update_data = {
            'proveedor': self.proveedor_claro.id,
            'numero_factura': 'FAC-001-UPD'  # Cambiar factura para evitar duplicados
        }
        
        response = self.client.patch(f'{self.gps_url}{gps.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        gps.refresh_from_db()
        self.assertEqual(gps.proveedor.id, self.proveedor_claro.id)
        self.assertEqual(gps.proveedor.nombre, 'Claro Perú')
        
        # Verificar respuesta
        self.assertEqual(response.data['proveedor_info']['nombre'], 'Claro Perú')
    
    def test_create_gps_with_inactive_provider(self):
        """Test: No permitir crear GPS con proveedor inactivo"""
        # Desactivar proveedor
        self.proveedor_movistar.is_active = False
        self.proveedor_movistar.save()
        
        response = self.client.post(self.gps_url, self.valid_gps_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('proveedor', response.data)
    
    def test_gps_provider_relationship_integrity(self):
        """Test: Verificar integridad de la relación GPS-Proveedor"""
        # Crear GPS
        gps = GPS.objects.create(
            fecha_compra=datetime.now(),
            imei='666777888999001',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('250.00')
        )
        
        # Verificar que no se puede eliminar proveedor con GPS asociados
        with self.assertRaises(Exception):  # models.ProtectedError
            self.proveedor_movistar.delete()
        
        # Verificar que el GPS sigue existiendo
        self.assertTrue(GPS.objects.filter(id=gps.id).exists())
        self.assertTrue(Proveedor.objects.filter(id=self.proveedor_movistar.id).exists())

    def test_create_gps_with_client(self):
        """
        Test: Crear GPS con cliente asignado
        """
        data = {
            'fecha_compra': '2024-01-15T10:00:00Z',
            'imei': '123456789012347',  # IMEI válido según algoritmo de Luhn
            'marca': 'Garmin',
            'modelo': 'GPS-2024',
            'numero_factura': 'FAC-CLIENT-001',
            'proveedor': self.proveedor_movistar.id,
            'cliente': self.cliente1.id,
            'estado': 'asignado',
            'precio_compra': '350.00'
        }
        
        response = self.client.post(self.gps_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se creó correctamente con cliente
        gps = GPS.objects.get(imei='123456789012347')
        self.assertEqual(gps.cliente.id, self.cliente1.id)
        self.assertEqual(gps.estado, 'asignado')
        
        # Verificar que la respuesta incluye información del cliente
        self.assertIn('cliente_info', response.data)
        self.assertEqual(response.data['cliente_info']['nombre'], 'Transportes Lima SAC')

    def test_assign_client_to_existing_gps(self):
        """
        Test: Asignar cliente a GPS existente
        """
        # Crear GPS sin cliente
        gps = GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="777888999000118",
            marca="TomTom",
            modelo="Pro-2024",
            numero_factura="FAC-002",
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('299.99'),
            proceso='en_produccion'
        )
        
        # Asignar cliente
        url = reverse('inventory:gps-detail', kwargs={'pk': gps.id})
        data = {
            'cliente': self.cliente2.id,
            'estado': 'asignado'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar asignación
        gps.refresh_from_db()
        self.assertEqual(gps.cliente.id, self.cliente2.id)
        self.assertEqual(gps.estado, 'asignado')

    def test_unassign_client_from_gps(self):
        """
        Test: Desasignar cliente de GPS
        """
        # Crear GPS con cliente asignado
        gps = GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="888999000111223",
            marca="Magellan",
            modelo="Explorer",
            numero_factura="FAC-003",
            proveedor=self.proveedor_claro,
            cliente=self.cliente1,
            estado='asignado',
            precio_compra=Decimal('399.99')
        )
        
        # Desasignar cliente
        url = reverse('inventory:gps-detail', kwargs={'pk': gps.id})
        data = {
            'cliente': None,
            'estado': 'no_asignado',
            'proceso': 'en_produccion'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar desasignación
        gps.refresh_from_db()
        self.assertIsNone(gps.cliente)
        self.assertEqual(gps.estado, 'no_asignado')
        self.assertEqual(gps.proceso, 'en_produccion')

    def test_filter_gps_by_client(self):
        """
        Test: Filtrar GPS por cliente
        """
        # Crear GPS con diferentes clientes
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="999000111222334",
            marca="Garmin",
            modelo="Client1-GPS",
            numero_factura="FAC-CLIENT1",
            proveedor=self.proveedor_movistar,
            cliente=self.cliente1,
            precio_compra=Decimal('300.00')
        )
        
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="000111222333445",
            marca="TomTom",
            modelo="Client2-GPS",
            numero_factura="FAC-CLIENT2",
            proveedor=self.proveedor_claro,
            cliente=self.cliente2,
            precio_compra=Decimal('350.00')
        )
        
        GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="111222333444556",
            marca="Magellan",
            modelo="No-Client-GPS",
            numero_factura="FAC-NO-CLIENT",
            proveedor=self.proveedor_movistar,
            precio_compra=Decimal('250.00')
        )
        
        # Filtrar por cliente 1
        response = self.client.get(f'{self.gps_url}?cliente={self.cliente1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['modelo'], 'Client1-GPS')
        
        # Filtrar GPS sin cliente asignado
        response = self.client.get(f'{self.gps_url}?cliente__isnull=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['modelo'], 'No-Client-GPS')

    def test_client_deletion_sets_gps_client_to_null(self):
        """
        Test: Verificar que al eliminar cliente, el GPS queda sin cliente asignado
        """
        # Crear GPS con cliente
        gps = GPS.objects.create(
            fecha_compra=datetime.now(),
            imei="222333444555667",
            marca="Garmin",
            modelo="Delete-Test",
            numero_factura="FAC-DELETE",
            proveedor=self.proveedor_movistar,
            cliente=self.cliente1,
            precio_compra=Decimal('400.00')
        )
        
        # Eliminar cliente
        cliente_id = self.cliente1.id
        self.cliente1.delete()
        
        # Verificar que GPS existe pero sin cliente
        gps.refresh_from_db()
        self.assertIsNone(gps.cliente)
        self.assertFalse(Cliente.objects.filter(id=cliente_id).exists())