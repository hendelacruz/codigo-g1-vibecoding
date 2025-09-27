"""
Tests para el servicio de asignación de equipos.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from entities.models import Cliente, Proveedor
from authentication.models import Role
from .models import GPS, SIMCard
from .equipment_assignment_service import EquipmentAssignmentService

User = get_user_model()


class EquipmentAssignmentServiceTestCase(TestCase):
    """
    Test case for Equipment Assignment Service functionality.
    """
    
    def setUp(self):
        """Set up test data"""
        # Create test role
        self.role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de prueba',
            permisos={'read': True, 'write': True}
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.role
        )
        
        # Create test client for API calls
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Test Proveedor',
            ruc='12345678901',
            correo='proveedor@test.com',
            celular='123456789'
        )
        
        # Create test cliente
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='98765432109',
            direccion='Test Address',
            contacto='Test Contact',
            correo='cliente@test.com',
            celular='987654321'
        )
        
        # Create test GPS devices
        self.gps_available = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='TestMarca',
            modelo='TestModelo',
            numero_factura='FAC001',
            proveedor=self.proveedor,
            estado='no_asignado',
            precio_compra=100.00
        )
        
        self.gps_assigned = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012346',
            marca='TestMarca',
            modelo='TestModelo',
            numero_factura='FAC002',
            proveedor=self.proveedor,
            cliente=self.cliente,
            estado='asignado',
            precio_compra=100.00
        )
        
        # Create test SIM cards
        self.simcard_available = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC003',
            numero_chip='123456789',
            icc='ICC001',
            proveedor=self.proveedor,
            estado='no_asignado',
            precio_compra=50.00
        )
        
        self.simcard_assigned = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC004',
            numero_chip='987654321',
            icc='ICC002',
            proveedor=self.proveedor,
            cliente=self.cliente,
            estado='asignado',
            precio_compra=50.00
        )
    
    def test_get_available_equipment(self):
        """Test getting available equipment"""
        result = EquipmentAssignmentService.get_available_equipment()
        
        # Check structure
        self.assertIn('gps_devices', result)
        self.assertIn('sim_cards', result)
        self.assertIn('summary', result)
        
        # Check counts
        self.assertEqual(result['summary']['total_gps'], 1)
        self.assertEqual(result['summary']['total_simcards'], 1)
        
        # Check that only available equipment is returned
        gps_ids = [gps['id'] for gps in result['gps_devices']]
        simcard_ids = [sim['id'] for sim in result['sim_cards']]
        
        self.assertIn(self.gps_available.id, gps_ids)
        self.assertNotIn(self.gps_assigned.id, gps_ids)
        self.assertIn(self.simcard_available.id, simcard_ids)
        self.assertNotIn(self.simcard_assigned.id, simcard_ids)
    
    def test_assign_gps_to_client(self):
        """Test assigning GPS to client"""
        result = EquipmentAssignmentService.assign_equipment_to_client(
            'gps', self.gps_available.id, self.cliente.id, self.user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('asignado exitosamente', result['message'])
        self.assertIsNotNone(result['equipment'])
        self.assertIsNotNone(result['client'])
        
        # Verify database changes
        self.gps_available.refresh_from_db()
        self.assertEqual(self.gps_available.estado, 'asignado')
        self.assertEqual(self.gps_available.cliente, self.cliente)
    
    def test_assign_simcard_to_client(self):
        """Test assigning SIM card to client"""
        result = EquipmentAssignmentService.assign_equipment_to_client(
            'simcard', self.simcard_available.id, self.cliente.id, self.user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('asignado exitosamente', result['message'])
        self.assertIsNotNone(result['equipment'])
        self.assertIsNotNone(result['client'])
        
        # Verify database changes
        self.simcard_available.refresh_from_db()
        self.assertEqual(self.simcard_available.estado, 'asignado')
        self.assertEqual(self.simcard_available.cliente, self.cliente)
    
    def test_assign_invalid_equipment_type(self):
        """Test assigning with invalid equipment type"""
        result = EquipmentAssignmentService.assign_equipment_to_client(
            'invalid', 1, self.cliente.id, self.user
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Tipo de equipo no válido', result['message'])
    
    def test_assign_nonexistent_equipment(self):
        """Test assigning nonexistent equipment"""
        result = EquipmentAssignmentService.assign_equipment_to_client(
            'gps', 99999, self.cliente.id, self.user
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Error al asignar equipo', result['message'])
    
    def test_unassign_gps_from_client(self):
        """Test unassigning GPS from client"""
        result = EquipmentAssignmentService.unassign_equipment(
            'gps', self.gps_assigned.id, self.user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('desasignado exitosamente', result['message'])
        self.assertIsNotNone(result['equipment'])
        
        # Verify database changes
        self.gps_assigned.refresh_from_db()
        self.assertEqual(self.gps_assigned.estado, 'no_asignado')
        self.assertIsNone(self.gps_assigned.cliente)
    
    def test_unassign_simcard_from_client(self):
        """Test unassigning SIM card from client"""
        result = EquipmentAssignmentService.unassign_equipment(
            'simcard', self.simcard_assigned.id, self.user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('desasignado exitosamente', result['message'])
        self.assertIsNotNone(result['equipment'])
        
        # Verify database changes
        self.simcard_assigned.refresh_from_db()
        self.assertEqual(self.simcard_assigned.estado, 'no_asignado')
        self.assertIsNone(self.simcard_assigned.cliente)


class EquipmentAssignmentAPITestCase(TestCase):
    """
    Test case for Equipment Assignment API endpoints.
    """
    
    def setUp(self):
        """Set up test data"""
        # Create test role
        self.role = Role.objects.create(
            nombre='operador',
            descripcion='Operador de prueba',
            permisos={'read': True, 'write': True}
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='87654321',
            celular='+51987654322',
            rol=self.role
        )
        
        # Create test client for API calls
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Test Proveedor',
            ruc='12345678902',
            correo='proveedor@test.com',
            celular='123456789'
        )
        
        # Create test cliente
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='98765432108',
            direccion='Test Address',
            contacto='Test Contact',
            correo='cliente@test.com',
            celular='987654321'
        )
        
        # Create test equipment
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='TestMarca',
            modelo='TestModelo',
            numero_factura='FAC001',
            proveedor=self.proveedor,
            estado='no_asignado',
            precio_compra=100.00
        )
        
        self.simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC002',
            numero_chip='123456789',
            icc='ICC001',
            proveedor=self.proveedor,
            estado='no_asignado',
            precio_compra=50.00
        )
    
    def test_available_equipment_endpoint(self):
        """Test the available equipment API endpoint"""
        url = reverse('inventory:available-equipment')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('gps_devices', response.data)
        self.assertIn('sim_cards', response.data)
        self.assertIn('summary', response.data)
    
    def test_assign_equipment_endpoint(self):
        """Test the assign equipment API endpoint"""
        url = reverse('inventory:assign-equipment')
        data = {
            'equipment_type': 'gps',
            'equipment_id': self.gps.id,
            'client_id': self.cliente.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify database changes
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'asignado')
        self.assertEqual(self.gps.cliente, self.cliente)
    
    def test_assign_equipment_missing_data(self):
        """Test assign equipment endpoint with missing data"""
        url = reverse('inventory:assign-equipment')
        data = {
            'equipment_type': 'gps',
            # Missing equipment_id and client_id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_unassign_equipment_endpoint(self):
        """Test the unassign equipment API endpoint"""
        # First assign the equipment
        self.gps.cliente = self.cliente
        self.gps.estado = 'asignado'
        self.gps.save()
        
        url = reverse('inventory:unassign-equipment')
        data = {
            'equipment_type': 'gps',
            'equipment_id': self.gps.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify database changes
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'no_asignado')
        self.assertIsNone(self.gps.cliente)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the endpoints"""
        # Create unauthenticated client
        client = APIClient()
        
        urls = [
            reverse('inventory:available-equipment'),
            reverse('inventory:assign-equipment'),
            reverse('inventory:unassign-equipment'),
        ]
        
        for url in urls:
            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)