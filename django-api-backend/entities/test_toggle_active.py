"""
Test específico para verificar el endpoint toggle_active de clientes.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser as User, Role
from entities.models import Cliente


class ClienteToggleActiveTestCase(TestCase):
    """
    Test específico para el endpoint PATCH /api/entities/clientes/{id}/toggle_active/
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
            celular='987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear cliente de prueba (activo por defecto)
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            correo='cliente@test.com',
            celular='987654321',
            direccion='Dirección Test',
            contacto='Contacto Test'
        )
        
        # URL del endpoint
        self.url = reverse('entities:cliente-toggle-active', kwargs={'pk': self.cliente.pk})
    
    def test_toggle_active_endpoint_exists(self):
        """
        Test que verifica que el endpoint existe y es accesible.
        """
        # Verificar que el cliente está activo inicialmente
        self.assertTrue(self.cliente.is_active)
        
        # Hacer request al endpoint
        response = self.client.patch(self.url, {'is_active': False}, format='json')
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el cliente fue desactivado
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_active)
    
    def test_toggle_active_desactivar_cliente(self):
        """
        Test para desactivar un cliente activo.
        """
        # Verificar estado inicial
        self.assertTrue(self.cliente.is_active)
        
        # Desactivar cliente
        response = self.client.patch(self.url, {'is_active': False}, format='json')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)
        self.assertFalse(response.data['is_active'])
        
        # Verificar en base de datos
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_active)
    
    def test_toggle_active_activar_cliente(self):
        """
        Test para activar un cliente inactivo.
        """
        # Desactivar cliente primero
        self.cliente.is_active = False
        self.cliente.save()
        
        # Activar cliente
        response = self.client.patch(self.url, {'is_active': True}, format='json')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)
        self.assertTrue(response.data['is_active'])
        
        # Verificar en base de datos
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.is_active)
    
    def test_toggle_active_sin_parametro_is_active(self):
        """
        Test que verifica el manejo de error cuando no se envía is_active.
        """
        response = self.client.patch(self.url, {}, format='json')
        
        # Verificar error 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'El campo is_active es requerido')
        
        # Verificar que el cliente no cambió
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.is_active)  # Debe seguir activo
    
    def test_toggle_active_con_valores_diversos(self):
        """
        Test que verifica el manejo de diferentes valores para is_active.
        Nota: La implementación usa bool() que convierte cualquier string no vacío a True.
        """
        test_cases = [
            (True, True),
            (False, False),
            ('true', True),  # Cualquier string no vacío es True
            ('false', True),  # Cualquier string no vacío es True
            (1, True),
            (0, False),
            ('1', True),  # Cualquier string no vacío es True
            ('0', True),  # Cualquier string no vacío es True
            ('', False),  # String vacío es False
            (None, False),  # None es False (pero este caso se maneja antes)
        ]
        
        for input_value, expected_result in test_cases:
            with self.subTest(input_value=input_value, expected=expected_result):
                # Caso especial para None que se maneja diferente
                if input_value is None:
                    response = self.client.patch(
                        self.url, 
                        {}, 
                        format='json'
                    )
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    continue
                
                response = self.client.patch(
                    self.url, 
                    {'is_active': input_value}, 
                    format='json'
                )
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['is_active'], expected_result)
                
                # Verificar en base de datos
                self.cliente.refresh_from_db()
                self.assertEqual(self.cliente.is_active, expected_result)
    
    def test_toggle_active_cliente_inexistente(self):
        """
        Test que verifica el manejo de error para cliente inexistente.
        """
        url_inexistente = reverse('entities:cliente-toggle-active', kwargs={'pk': 99999})
        response = self.client.patch(url_inexistente, {'is_active': False}, format='json')
        
        # Verificar error 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_toggle_active_metodo_incorrecto(self):
        """
        Test que verifica que solo se acepta método PATCH.
        """
        # Probar con GET
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Probar con POST
        response = self.client.post(self.url, {'is_active': False})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Probar con PUT
        response = self.client.put(self.url, {'is_active': False})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_toggle_active_sin_autenticacion(self):
        """
        Test que verifica que se requiere autenticación.
        """
        # Crear cliente sin autenticación
        client_no_auth = APIClient()
        response = client_no_auth.patch(self.url, {'is_active': False}, format='json')
        
        # Verificar que se requiere autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_toggle_active_respuesta_completa(self):
        """
        Test que verifica que la respuesta contiene todos los campos del cliente.
        """
        response = self.client.patch(self.url, {'is_active': False}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la respuesta contiene los campos esperados
        expected_fields = ['id', 'nombre', 'ruc', 'correo', 'celular', 'direccion', 'contacto', 'is_active']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verificar valores específicos
        self.assertEqual(response.data['nombre'], self.cliente.nombre)
        self.assertEqual(response.data['ruc'], self.cliente.ruc)
        self.assertFalse(response.data['is_active'])