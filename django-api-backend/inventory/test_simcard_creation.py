"""
Test cases for SIMCard creation and editing without mandatory assignment.
Tests the scenario where 10 SIM cards arrive and initially are not assigned to clients.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from inventory.models import SIMCard
from entities.models import Proveedor, Cliente
from authentication.models import Role


class SIMCardCreationModelTest(TestCase):
    """Test SIMCard model creation without mandatory client assignment."""
    
    def setUp(self):
        """Set up test data."""
        self.proveedor = Proveedor.objects.create(
            nombre="TechSIM Provider",
            ruc="20123456789",
            celular="987654321",
            contacto="Juan Pérez",
            direccion="Av. Test 123",
            correo="contacto@techsim.com"
        )
        
        self.cliente = Cliente.objects.create(
            nombre="Test Client",
            ruc="20987654321",
            direccion="Calle Test 456",
            contacto="María García",
            celular="123456789",
            correo="maria@testclient.com"
        )
    
    def test_create_simcard_without_client_assignment(self):
        """Test creating a SIM card without assigning it to a client."""
        simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura="F001-001",
            numero_chip="123456789",
            icc="8951123456789012345",
            proveedor=self.proveedor
            # Note: cliente is not provided (should be None)
            # Note: estado and proceso should use default values
        )
        
        # Verify the SIM card was created successfully
        self.assertIsNotNone(simcard.id)
        self.assertEqual(simcard.numero_chip, "123456789")
        self.assertEqual(simcard.icc, "8951123456789012345")
        self.assertEqual(simcard.proveedor, self.proveedor)
        
        # Verify default values are set correctly
        self.assertIsNone(simcard.cliente)  # Should be None (not assigned)
        self.assertEqual(simcard.estado, 'no_asignado')  # Default value
        self.assertEqual(simcard.proceso, 'en_produccion')  # Default value
        self.assertTrue(simcard.is_active)  # Default value
        
        # Verify optional fields can be empty
        self.assertEqual(simcard.plan, '')  # blank=True
        self.assertIsNone(simcard.precio_compra)  # null=True
        self.assertEqual(simcard.observaciones, '')  # blank=True
    
    def test_create_multiple_simcards_batch_scenario(self):
        """Test creating multiple SIM cards as they would arrive in a batch."""
        simcards_data = [
            {
                'numero_chip': f'12345678{i:01d}' if i < 10 else f'12345679{i-10:01d}',
                'icc': f'895112345678901234{i:02d}',
                'numero_factura': f'F001-00{i}'
            }
            for i in range(1, 11)  # 10 SIM cards
        ]
        
        created_simcards = []
        for data in simcards_data:
            simcard = SIMCard.objects.create(
                fecha_compra=timezone.now(),
                numero_factura=data['numero_factura'],
                numero_chip=data['numero_chip'],
                icc=data['icc'],
                proveedor=self.proveedor
                # No client assignment - they arrive unassigned
            )
            created_simcards.append(simcard)
        
        # Verify all 10 SIM cards were created
        self.assertEqual(len(created_simcards), 10)
        self.assertEqual(SIMCard.objects.count(), 10)
        
        # Verify all are unassigned by default
        unassigned_count = SIMCard.objects.filter(
            cliente__isnull=True,
            estado='no_asignado'
        ).count()
        self.assertEqual(unassigned_count, 10)
    
    def test_edit_simcard_without_changing_assignment(self):
        """Test editing SIM card properties without changing client assignment."""
        simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura="F001-001",
            numero_chip="123456789",
            icc="8951123456789012345",
            proveedor=self.proveedor
        )
        
        # Edit non-assignment fields
        simcard.plan = "Plan Datos 10GB"
        simcard.precio_compra = 25.00
        simcard.observaciones = "SIM card actualizada con nuevo plan"
        simcard.save()
        
        # Verify changes were saved
        updated_simcard = SIMCard.objects.get(id=simcard.id)
        self.assertEqual(updated_simcard.plan, "Plan Datos 10GB")
        self.assertEqual(float(updated_simcard.precio_compra), 25.00)
        self.assertEqual(updated_simcard.observaciones, "SIM card actualizada con nuevo plan")
        
        # Verify assignment status remains unchanged
        self.assertIsNone(updated_simcard.cliente)
        self.assertEqual(updated_simcard.estado, 'no_asignado')
    
    def test_change_proceso_without_client_assignment(self):
        """Test changing proceso field without requiring client assignment."""
        simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura="F001-001",
            numero_chip="123456789",
            icc="8951123456789012345",
            proveedor=self.proveedor
        )
        
        # Change proceso to 'en_almacen'
        simcard.proceso = 'en_almacen'
        simcard.save()
        
        # Verify proceso changed but client assignment remains None
        updated_simcard = SIMCard.objects.get(id=simcard.id)
        self.assertEqual(updated_simcard.proceso, 'en_almacen')
        self.assertIsNone(updated_simcard.cliente)
        self.assertEqual(updated_simcard.estado, 'no_asignado')
    
    def test_required_fields_validation(self):
        """Test that only truly required fields are enforced."""
        # Test missing required fields
        with self.assertRaises(Exception):  # Should fail without fecha_compra
            SIMCard.objects.create(
                numero_factura="F001-001",
                numero_chip="987654321",
                icc="89511234567890123456",
                proveedor=self.proveedor
            )
        
        with self.assertRaises(Exception):  # Should fail without numero_chip
            SIMCard.objects.create(
                fecha_compra=timezone.now(),
                numero_factura="F001-001",
                icc="89511234567890123456",
                proveedor=self.proveedor
            )
        
        with self.assertRaises(Exception):  # Should fail without proveedor
            SIMCard.objects.create(
                fecha_compra=timezone.now(),
                numero_factura="F001-001",
                numero_chip="987654321",
                icc="89511234567890123456"
            )


class SIMCardCreationAPITest(APITestCase):
    """Test SIMCard creation via API without mandatory client assignment."""
    
    def setUp(self):
        """Set up test data and authentication."""
        # Create test role
        self.role = Role.objects.create(
            nombre='operador',
            descripcion='Operador de prueba',
            permisos={'read': True, 'write': True}
        )
        
        # Create user for authentication
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.role
        )
        
        # Create access token
        self.access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test proveedor
        self.proveedor = Proveedor.objects.create(
            nombre="TechSIM Provider",
            ruc="20123456789",
            celular="987654321",
            contacto="Juan Pérez",
            direccion="Av. Test 123",
            correo="contacto@techsim.com"
        )
    
    def test_create_simcard_via_api_minimal_data(self):
        """Test creating SIM card via API with minimal required data."""
        data = {
            'fecha_compra': timezone.now().isoformat(),
            'numero_factura': 'F001-001',
            'numero_chip': '123456789',
            'icc': '89511234567890123456',
            'proveedor': self.proveedor.id
            # Note: No cliente, estado, or proceso provided
        }
        
        response = self.client.post('/api/inventory/simcards/', data, format='json')
        
        # Debug: Print error if not 201
        if response.status_code != 201:
            print(f"Error response: {response.json()}")
        
        # Verify successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response data
        response_data = response.json()
        self.assertEqual(response_data['numero_chip'], '123456789')
        self.assertEqual(response_data['icc'], '89511234567890123456')
        self.assertEqual(response_data['proveedor'], self.proveedor.id)
        
        # Verify default values are applied
        self.assertIsNone(response_data['cliente'])
        self.assertEqual(response_data['estado'], 'no_asignado')
        self.assertEqual(response_data['proceso'], 'en_produccion')
        self.assertTrue(response_data['is_active'])
    
    def test_create_multiple_simcards_via_api(self):
        """Test creating multiple SIM cards via API (batch scenario)."""
        simcards_data = [
            {
                'fecha_compra': timezone.now().isoformat(),
                'numero_factura': f'F001-00{i}',
                'numero_chip': f'12345678{i:01d}' if i < 10 else f'12345679{i-10:01d}',
                'icc': f'8951123456789012345{i:01d}',
                'proveedor': self.proveedor.id
            }
            for i in range(1, 6)  # 5 SIM cards for testing
        ]
        
        created_simcards = []
        for data in simcards_data:
            response = self.client.post('/api/inventory/simcards/', data, format='json')
            if response.status_code != status.HTTP_201_CREATED:
                print(f"Error response: {response.data}")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_simcards.append(response.json())
        
        # Verify all were created with correct defaults
        self.assertEqual(len(created_simcards), 5)
        for simcard in created_simcards:
            self.assertIsNone(simcard['cliente'])
            self.assertEqual(simcard['estado'], 'no_asignado')
            self.assertEqual(simcard['proceso'], 'en_produccion')
    
    def test_edit_simcard_via_api_without_assignment(self):
        """Test editing SIM card via API without changing assignment."""
        # First create a SIM card
        create_data = {
            'fecha_compra': timezone.now().isoformat(),
            'numero_factura': 'F001-001',
            'numero_chip': '123456789',
            'icc': '89511234567890123456',
            'proveedor': self.proveedor.id
        }
        
        create_response = self.client.post('/api/inventory/simcards/', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        simcard_id = create_response.json()['id']
        
        # Edit the SIM card without changing assignment
        edit_data = {
            'plan': 'Plan Datos 15GB',
            'precio_compra': '30.00',
            'observaciones': 'Plan actualizado via API'
        }
        
        response = self.client.patch(f'/api/inventory/simcards/{simcard_id}/', edit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify changes were applied
        response_data = response.json()
        self.assertEqual(response_data['plan'], 'Plan Datos 15GB')
        self.assertEqual(response_data['precio_compra'], '30.00')
        self.assertEqual(response_data['observaciones'], 'Plan actualizado via API')
        
        # Verify assignment status unchanged
        self.assertIsNone(response_data['cliente'])
        self.assertEqual(response_data['estado'], 'no_asignado')
    
    def test_change_proceso_via_api_without_assignment(self):
        """Test changing proceso via API without requiring client assignment."""
        # Create SIM card
        create_data = {
            'fecha_compra': timezone.now().isoformat(),
            'numero_factura': 'F001-001',
            'numero_chip': '123456789',
            'icc': '89511234567890123456',
            'proveedor': self.proveedor.id
        }
        
        create_response = self.client.post('/api/inventory/simcards/', create_data, format='json')
        simcard_id = create_response.json()['id']
        
        # Change proceso to 'en_almacen'
        edit_data = {'proceso': 'en_almacen'}
        
        response = self.client.patch(f'/api/inventory/simcards/{simcard_id}/', edit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify proceso changed
        response_data = response.json()
        self.assertEqual(response_data['proceso'], 'en_almacen')
        self.assertEqual(response_data['proceso_display'], 'En Almacén')
        
        # Verify assignment status unchanged
        self.assertIsNone(response_data['cliente'])
        self.assertEqual(response_data['estado'], 'no_asignado')