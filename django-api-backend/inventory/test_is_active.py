"""
Tests para la funcionalidad is_active del modelo GPS
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import GPS, Proveedor
from authentication.models import Role

User = get_user_model()


class GPSIsActiveModelTestCase(TestCase):
    """Tests para los métodos de activación/desactivación del modelo GPS"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor Test",
            ruc="12345678901",
            contacto="Contacto Test",
            celular="987654321",
            correo="test@test.com"
        )
        
        from datetime import datetime
        self.gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestMarca",
            modelo="TestModelo",
            numero_factura="FAC-001",
            fecha_compra=datetime.now(),
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion"
        )
    
    def test_gps_created_active_by_default(self):
        """Test que verifica que un GPS se crea activo por defecto"""
        self.assertTrue(self.gps.is_active)
    
    def test_activate_method(self):
        """Test del método activate()"""
        # Desactivar primero
        self.gps.is_active = False
        self.gps.save()
        
        # Activar usando el método
        result = self.gps.activate("Activado por test")
        
        self.assertTrue(result)
        self.assertTrue(self.gps.is_active)
        self.assertIn("Activado por test", self.gps.observaciones)
    
    def test_deactivate_method(self):
        """Test del método deactivate()"""
        # Asegurar que está activo
        self.assertTrue(self.gps.is_active)
        
        # Desactivar usando el método
        result = self.gps.deactivate("Desactivado por test")
        
        self.assertTrue(result)
        self.assertFalse(self.gps.is_active)
        self.assertIn("Desactivado por test", self.gps.observaciones)
    
    def test_toggle_active_method(self):
        """Test del método toggle_active()"""
        # Inicialmente activo
        self.assertTrue(self.gps.is_active)
        
        # Toggle a inactivo
        self.gps.toggle_active("Toggle a inactivo")
        self.assertFalse(self.gps.is_active)
        
        # Toggle a activo
        self.gps.toggle_active("Toggle a activo")
        self.assertTrue(self.gps.is_active)
    
    def test_estado_info_includes_is_active(self):
        """Test que verifica que estado_info incluye is_active"""
        estado_info = self.gps.estado_info
        
        self.assertIn('is_active', estado_info)
        self.assertEqual(estado_info['is_active'], self.gps.is_active)


class GPSIsActiveAPITestCase(APITestCase):
    """Tests para la API con el campo is_active"""
    
    def setUp(self):
        """Configuración inicial para los tests de API"""
        # Crear rol para el usuario
        self.role = Role.objects.create(
            nombre='administrador',
            descripcion='Rol de administrador para tests',
            permisos={'create': True, 'read': True, 'update': True, 'delete': True}
        )
        
        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            dni='12345678',
            password='testpass123',
            rol=self.role
        )
        self.client.force_authenticate(user=self.user)
        
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor Test",
            ruc="12345678902",
            contacto="Contacto Test",
            celular="987654321",
            correo="test@test.com"
        )
        
        from datetime import datetime
        self.gps = GPS.objects.create(
            imei="123456789012345",
            marca="TestMarca",
            modelo="TestModelo",
            numero_factura="FAC-002",
            fecha_compra=datetime.now(),
            proveedor=self.proveedor,
            estado="no_asignado",
            proceso="en_produccion"
        )
    
    def test_cambiar_estado_with_is_active_true(self):
        """Test cambiar estado con is_active=True"""
        # Desactivar primero
        self.gps.is_active = False
        self.gps.save()
        
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        data = {
            'is_active': True,
            'observaciones': 'Activado via API'
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Debug temporal
        if response.status_code != status.HTTP_200_OK:
            print(f"Error response: {response.data}")
            print(f"Status code: {response.status_code}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        self.gps.refresh_from_db()
        self.assertTrue(self.gps.is_active)
        self.assertIn('Activado via API', self.gps.observaciones)
    
    def test_cambiar_estado_with_is_active_false(self):
        """Test cambiar estado con is_active=False"""
        # Asegurar que está activo
        self.assertTrue(self.gps.is_active)
        
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        data = {
            'is_active': False,
            'observaciones': 'Desactivado via API'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        self.gps.refresh_from_db()
        self.assertFalse(self.gps.is_active)
        self.assertIn('Desactivado via API', self.gps.observaciones)
    
    def test_cambiar_estado_combined_fields(self):
        """Test cambiar estado, proceso e is_active juntos"""
        # Asignar un cliente al GPS para poder cambiar a estado 'asignado'
        from entities.models import Cliente
        cliente = Cliente.objects.create(
            nombre="Cliente Test",
            ruc="12345678901",
            direccion="Dirección Test",
            contacto="Contacto Test",
            celular="987654321",
            correo="cliente@test.com"
        )
        self.gps.cliente = cliente
        self.gps.save()
        
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        data = {
            'estado': 'asignado',
            'proceso': 'en_transito',  # Proceso válido para GPS asignado
            'is_active': True,
            'observaciones': 'Asignando GPS y activando'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.gps.refresh_from_db()
        self.assertEqual(self.gps.estado, 'asignado')
        self.assertEqual(self.gps.proceso, 'en_transito')
        self.assertTrue(self.gps.is_active)
    
    def test_cambiar_estado_invalid_is_active_type(self):
        """Test con tipo inválido para is_active"""
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        data = {
            'is_active': 'invalid_string'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is_active debe ser un valor booleano', response.data['error'])
    
    def test_cambiar_estado_only_is_active(self):
        """Test cambiar solo el campo is_active"""
        url = reverse('inventory:gps-cambiar-estado', kwargs={'pk': self.gps.pk})
        data = {
            'is_active': False
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que solo se cambió is_active
        self.gps.refresh_from_db()
        self.assertFalse(self.gps.is_active)
        self.assertEqual(self.gps.estado, 'no_asignado')  # Sin cambios
        self.assertEqual(self.gps.proceso, 'en_produccion')  # Sin cambios
    
    def test_gps_list_includes_is_active(self):
        """Test que la lista de GPS incluye el campo is_active"""
        url = reverse('inventory:gps-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que is_active está en la respuesta
        gps_data = response.data['results'][0]
        self.assertIn('is_active', gps_data)
        self.assertEqual(gps_data['is_active'], self.gps.is_active)
    
    def test_gps_detail_includes_is_active(self):
        """Test que el detalle de GPS incluye el campo is_active"""
        url = reverse('inventory:gps-detail', kwargs={'pk': self.gps.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que is_active está en la respuesta
        self.assertIn('is_active', response.data)
        self.assertEqual(response.data['is_active'], self.gps.is_active)