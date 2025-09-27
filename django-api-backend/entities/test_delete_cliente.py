"""
Tests específicos para el endpoint DELETE de clientes.
Verifica el comportamiento de soft delete y manejo de errores.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Cliente
from authentication.models import Role

User = get_user_model()


class ClienteDeleteEndpointTestCase(APITestCase):
    """
    Tests específicos para el endpoint DELETE /api/entities/clientes/{id}/
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear rol de administrador (que tiene permisos de eliminación)
        self.rol = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador para tests',
            permisos={'read': True, 'write': True, 'delete': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='admin123',
            dni='87654321',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear cliente de prueba
        self.cliente_activo = Cliente.objects.create(
            nombre='Cliente Test DELETE',
            ruc='98765432101',
            correo='delete@test.com',
            celular='987654321',
            direccion='Dirección Test DELETE',
            contacto='Contacto Test DELETE',
            is_active=True
        )
        
        # Crear cliente ya inactivo
        self.cliente_inactivo = Cliente.objects.create(
            nombre='Cliente Inactivo',
            ruc='11111111111',
            correo='inactivo@test.com',
            celular='111111111',
            direccion='Dirección Inactivo',
            contacto='Contacto Inactivo',
            is_active=False
        )

    def test_delete_cliente_existente_activo(self):
        """
        Test: DELETE de cliente existente y activo debe hacer soft delete
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Verificar estado inicial
        self.assertTrue(self.cliente_activo.is_active)
        
        # Realizar DELETE
        response = self.client.delete(url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que el cliente sigue existiendo pero inactivo
        self.cliente_activo.refresh_from_db()
        self.assertFalse(self.cliente_activo.is_active)
        
        # Verificar que el cliente aún existe en la base de datos
        self.assertTrue(Cliente.objects.filter(id=self.cliente_activo.id).exists())

    def test_delete_cliente_ya_inactivo(self):
        """
        Test: DELETE de cliente ya inactivo debe funcionar sin problemas
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_inactivo.id})
        
        # Verificar estado inicial
        self.assertFalse(self.cliente_inactivo.is_active)
        
        # Realizar DELETE
        response = self.client.delete(url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que sigue inactivo
        self.cliente_inactivo.refresh_from_db()
        self.assertFalse(self.cliente_inactivo.is_active)

    def test_delete_cliente_inexistente(self):
        """
        Test: DELETE de cliente inexistente debe retornar 404
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': 99999})
        
        # Realizar DELETE
        response = self.client.delete(url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_sin_autenticacion(self):
        """
        Test: DELETE sin autenticación debe retornar 401
        """
        # Desautenticar cliente
        self.client.force_authenticate(user=None)
        
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Realizar DELETE
        response = self.client.delete(url)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el cliente no fue modificado
        self.cliente_activo.refresh_from_db()
        self.assertTrue(self.cliente_activo.is_active)

    def test_delete_con_usuario_sin_permisos(self):
        """
        Test: DELETE con usuario sin permisos debe retornar 403
        """
        # Crear usuario sin permisos de eliminación
        rol_limitado = Role.objects.create(
            nombre='operador_limitado',
            descripcion='Operador sin permisos de eliminación',
            permisos={'read': True, 'write': True, 'delete': False}
        )
        
        usuario_limitado = User.objects.create_user(
            username='operador_limitado',
            email='operador@test.com',
            password='operador123',
            dni='11111111',
            celular='+51111111111',
            rol=rol_limitado
        )
        
        # Autenticar con usuario limitado
        self.client.force_authenticate(user=usuario_limitado)
        
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Realizar DELETE
        response = self.client.delete(url)
        
        # Verificar respuesta (puede ser 403 o 401 dependiendo de la implementación de permisos)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Verificar que el cliente no fue modificado
        self.cliente_activo.refresh_from_db()
        self.assertTrue(self.cliente_activo.is_active)

    def test_delete_multiple_veces(self):
        """
        Test: DELETE múltiples veces del mismo cliente debe ser idempotente
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Primer DELETE
        response1 = self.client.delete(url)
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que está inactivo
        self.cliente_activo.refresh_from_db()
        self.assertFalse(self.cliente_activo.is_active)
        
        # Segundo DELETE del mismo cliente
        response2 = self.client.delete(url)
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que sigue inactivo
        self.cliente_activo.refresh_from_db()
        self.assertFalse(self.cliente_activo.is_active)

    def test_delete_preserva_datos(self):
        """
        Test: DELETE debe preservar todos los datos del cliente, solo cambiar is_active
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Guardar datos originales
        datos_originales = {
            'nombre': self.cliente_activo.nombre,
            'ruc': self.cliente_activo.ruc,
            'correo': self.cliente_activo.correo,
            'celular': self.cliente_activo.celular,
            'direccion': self.cliente_activo.direccion,
            'contacto': self.cliente_activo.contacto,
        }
        
        # Realizar DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que todos los datos se preservaron
        self.cliente_activo.refresh_from_db()
        self.assertEqual(self.cliente_activo.nombre, datos_originales['nombre'])
        self.assertEqual(self.cliente_activo.ruc, datos_originales['ruc'])
        self.assertEqual(self.cliente_activo.correo, datos_originales['correo'])
        self.assertEqual(self.cliente_activo.celular, datos_originales['celular'])
        self.assertEqual(self.cliente_activo.direccion, datos_originales['direccion'])
        self.assertEqual(self.cliente_activo.contacto, datos_originales['contacto'])
        
        # Solo is_active debe haber cambiado
        self.assertFalse(self.cliente_activo.is_active)

    def test_delete_actualiza_updated_at(self):
        """
        Test: DELETE debe actualizar el campo updated_at
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # Guardar timestamp original
        updated_at_original = self.cliente_activo.updated_at
        
        # Esperar un momento para asegurar diferencia en timestamp
        import time
        time.sleep(0.1)
        
        # Realizar DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que updated_at cambió
        self.cliente_activo.refresh_from_db()
        self.assertGreater(self.cliente_activo.updated_at, updated_at_original)

    def test_delete_con_metodo_incorrecto(self):
        """
        Test: Otros métodos HTTP en el endpoint de detalle deben funcionar correctamente
        """
        url = reverse('entities:cliente-detail', kwargs={'pk': self.cliente_activo.id})
        
        # GET debe funcionar
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        
        # PATCH debe funcionar (actualización parcial)
        response_patch = self.client.patch(url, {'nombre': 'Nombre PATCH'}, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        
        # Verificar que el cliente sigue activo después de otras operaciones
        self.cliente_activo.refresh_from_db()
        self.assertTrue(self.cliente_activo.is_active)