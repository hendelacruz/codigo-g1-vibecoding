"""
Tests for GPS State Management System.

This module tests the state validation, transitions, and business logic
for GPS devices in the inventory system.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

from entities.models import Proveedor, Cliente
from authentication.models import Role
from .models import GPS
from .state_manager import GPSStateManager, GPSStateValidator


class GPSStateManagerTest(TestCase):
    """Test GPS State Manager functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.proveedor = Proveedor.objects.create(
            nombre="Test Provider",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="123456789",
            correo="test@provider.com"
        )
        
        self.cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="98765432109",
            direccion="Client Address",
            contacto="Client Contact",
            celular="987654321",
            correo="test@client.com"
        )
        
        self.gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion",
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
    
    def test_valid_state_transitions(self):
        """Test valid state transitions."""
        # no_asignado -> asignado (with client)
        is_valid, _ = GPSStateManager.validate_state_transition(
            'no_asignado', 'asignado', has_client=True
        )
        self.assertTrue(is_valid)
        
        # asignado -> no_asignado (without client)
        is_valid, _ = GPSStateManager.validate_state_transition(
            'asignado', 'no_asignado', has_client=False
        )
        self.assertTrue(is_valid)
    
    def test_invalid_state_transitions(self):
        """Test invalid state transitions."""
        # asignado without client
        is_valid, error = GPSStateManager.validate_state_transition(
            'no_asignado', 'asignado', has_client=False
        )
        self.assertFalse(is_valid)
        self.assertIn("cliente", error.lower())
        
        # no_asignado with client (inconsistent)
        is_valid, error = GPSStateManager.validate_state_transition(
            'asignado', 'no_asignado', has_client=True
        )
        self.assertFalse(is_valid)
        self.assertIn("cliente", error.lower())
    
    def test_auto_state_update_on_client_assignment(self):
        """Test automatic state update when client is assigned."""
        # Assign client to available GPS
        new_state = GPSStateManager.auto_update_state_on_client_change(
            self.gps, old_client=None, new_client=self.cliente
        )
        self.assertEqual(new_state, 'asignado')
        
        # Remove client from assigned GPS
        self.gps.estado = 'asignado'
        new_state = GPSStateManager.auto_update_state_on_client_change(
            self.gps, old_client=self.cliente, new_client=None
        )
        self.assertEqual(new_state, 'no_asignado')
    
    def test_can_assign_client(self):
        """Test client assignment validation."""
        # Can assign to available GPS with disponible process
        self.assertTrue(GPSStateManager.can_assign_client('en_produccion'))
        
        # Can assign to GPS in transit
        self.assertTrue(GPSStateManager.can_assign_client('en_transito'))
        
        # Cannot assign to damaged GPS
        self.assertFalse(GPSStateManager.can_assign_client('dañado'))
        
        # Cannot assign to GPS in maintenance
        self.assertFalse(GPSStateManager.can_assign_client('en_mantenimiento'))
    
    def test_get_valid_next_states(self):
        """Test getting valid next states."""
        # Available GPS without client
        valid_states = GPSStateManager.get_valid_next_states('no_asignado', has_client=False)
        self.assertNotIn('asignado', valid_states)  # Needs client
        
        # Available GPS with potential client
        valid_states = GPSStateManager.get_valid_next_states('no_asignado', has_client=True)
        self.assertIn('asignado', valid_states)
        
        # Assigned GPS with client
        valid_states = GPSStateManager.get_valid_next_states('asignado', has_client=True)
        self.assertIn('no_asignado', valid_states)


class GPSStateValidatorTest(TestCase):
    """Test GPS State Validator functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.proveedor = Proveedor.objects.create(
            nombre="Test Provider",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="123456789",
            correo="test@provider.com"
        )
        
        self.cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="98765432109",
            direccion="Client Address",
            contacto="Client Contact",
            celular="987654321",
            correo="test@client.com"
        )
    
    def test_validate_consistent_state(self):
        """Test validation of consistent GPS state."""
        # Valid: assigned GPS with client
        gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="asignado",
            proceso="en_produccion",
            cliente=self.cliente,
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
        
        is_valid, errors = GPSStateValidator.validate_gps_state(gps)
        self.assertEqual(len(errors), 0)
        self.assertTrue(is_valid)
    
    def test_validate_inconsistent_state(self):
        """Test validation of inconsistent GPS state."""
        # Create GPS with valid state first, then modify to invalid state
        gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion",
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
        
        # Manually set invalid state (bypass validation)
        GPS.objects.filter(pk=gps.pk).update(estado="asignado")
        gps.refresh_from_db()
        
        is_valid, errors = GPSStateValidator.validate_gps_state(gps)
        self.assertGreater(len(errors), 0)
        self.assertFalse(is_valid)
        self.assertTrue(any("cliente" in error.lower() for error in errors))
    
    def test_suggest_state_fix(self):
        """Test state fix suggestions."""
        # Create GPS with valid state first, then modify to invalid state
        gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="no_asignado",
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
        
        # Manually set invalid state (bypass validation)
        GPS.objects.filter(pk=gps.pk).update(estado="asignado")
        gps.refresh_from_db()
        
        suggestion = GPSStateValidator.suggest_estado_fix(gps)
        self.assertIsNotNone(suggestion)
        self.assertIn("no_asignado", suggestion.lower())


class GPSModelStateTest(TestCase):
    """Test GPS model state management methods."""
    
    def setUp(self):
        """Set up test data."""
        self.proveedor = Proveedor.objects.create(
            nombre="Test Provider",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="123456789",
            correo="test@provider.com"
        )
        
        self.cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="98765432109",
            direccion="Client Address",
            contacto="Client Contact",
            celular="987654321",
            correo="test@client.com"
        )
        
        self.gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion",
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
    
    def test_change_state_valid(self):
        """Test valid state change."""
        # Assign GPS to a client (estado change)
        cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="987654321",
            correo="test@client.com"
        )
        self.gps.cliente = cliente
        result = self.gps.change_state('asignado', 'Asignado a cliente')
        self.assertTrue(result)
        self.assertEqual(self.gps.estado, 'asignado')
        self.assertIn('Asignado a cliente', self.gps.observaciones)
    
    def test_change_state_invalid(self):
        """Test invalid state change."""
        # Try to assign without client
        with self.assertRaises(ValidationError):
            self.gps.change_state('asignado', 'Invalid assignment')
    
    def test_get_valid_next_states(self):
        """Test getting valid next states from model."""
        # Test GPS without client - should not be able to assign
        valid_states = self.gps.get_valid_next_states()
        self.assertIsInstance(valid_states, list)
        # GPS without client cannot change to 'asignado'
        self.assertNotIn('asignado', valid_states)
        
        # Test GPS with client - should be able to assign
        cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="987654321",
            correo="test@client.com"
        )
        self.gps.cliente = cliente
        valid_states_with_client = self.gps.get_valid_next_states()
        self.assertIn('asignado', valid_states_with_client)
    
    def test_estado_info_property(self):
        """Test estado_info property."""
        info = self.gps.estado_info
        self.assertIsInstance(info, dict)
        self.assertIn('current_state', info)
        self.assertIn('has_client', info)
        self.assertIn('valid_next_states', info)
        self.assertIn('is_consistent', info)
        
        self.assertEqual(info['current_state'], 'no_asignado')
        self.assertFalse(info['has_client'])
        self.assertTrue(info['is_consistent'])
    
    def test_auto_state_update_on_save(self):
        """Test automatic state update when saving GPS with client change."""
        # Assign client
        self.gps.cliente = self.cliente
        self.gps.save()
        
        # State should automatically change to 'asignado'
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'asignado')
        
        # Remove client
        self.gps.cliente = None
        self.gps.save()
        
        # State should automatically change to 'no_asignado'
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'no_asignado')


class GPSStateAPITest(APITestCase):
    """Test GPS state management through API endpoints."""
    
    def setUp(self):
        """Set up test data and authentication."""
        # Create test role
        self.role = Role.objects.create(
            nombre='operador',
            descripcion='Operador de prueba',
            permisos={'read': True, 'write': True}
        )
        
        # Create user and get token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.role
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up test data
        self.proveedor = Proveedor.objects.create(
            nombre="Test Provider",
            ruc="12345678901",
            direccion="Test Address",
            contacto="Test Contact",
            celular="123456789",
            correo="test@provider.com"
        )
        
        self.cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="98765432109",
            direccion="Client Address",
            contacto="Client Contact",
            celular="987654321",
            correo="test@client.com"
        )
        
        self.gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestBrand",
            modelo="TestModel",
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion",
            numero_factura="FAC-001",
            fecha_compra="2024-01-01",
            precio_compra=100.00
        )
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_cambiar_estado_valid(self):
        """Test valid state change through API."""
        url = f'/api/inventory/gps/{self.gps.id}/cambiar_estado/'
        data = {
            'proceso': 'en_mantenimiento',
            'observaciones': 'Mantenimiento programado'
        }
        
        response = self.client.patch(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.proceso, 'en_mantenimiento')
    
    def test_cambiar_estado_invalid(self):
        """Test invalid state change through API."""
        url = f'/api/inventory/gps/{self.gps.id}/cambiar_estado/'
        data = {
            'estado': 'asignado',  # Invalid without client
            'observaciones': 'Invalid assignment'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check error response includes helpful information
        self.assertIn('error', response.data)
        self.assertIn('valid_next_states', response.data)
        self.assertIn('has_client', response.data)
    
    def test_estado_info_endpoint(self):
        """Test estado_info endpoint."""
        url = f'/api/inventory/gps/{self.gps.id}/estado_info/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('current_state', response.data)
        self.assertIn('has_client', response.data)
        self.assertIn('valid_next_states', response.data)
        self.assertIn('is_consistent', response.data)
    
    def test_asignar_cliente_with_state_validation(self):
        """Test client assignment with state validation."""
        url = f'/api/inventory/gps/{self.gps.id}/asignar_cliente/'
        data = {
            'cliente_id': self.cliente.id,
            'observaciones': 'Asignación de prueba'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'asignado')
        self.assertEqual(self.gps.cliente, self.cliente)
    
    def test_asignar_cliente_invalid_state(self):
        """Test client assignment to GPS in invalid state."""
        # Set GPS to damaged process (not assignable)
        self.gps.proceso = 'dañado'
        self.gps.save()
        
        url = f'/api/inventory/gps/{self.gps.id}/asignar_cliente/'
        data = {
            'cliente_id': self.cliente.id,
            'observaciones': 'Invalid assignment'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check error message includes valid processes
        self.assertIn('error', response.data)
        self.assertIn('valid_processes_for_assignment', response.data)