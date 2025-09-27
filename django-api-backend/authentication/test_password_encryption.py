"""
Tests específicos para verificar el cifrado de contraseñas en operaciones CRUD
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import CustomUser, Role


class PasswordEncryptionTest(APITestCase):
    """
    Test cases para verificar que las contraseñas se cifren correctamente
    en operaciones CREATE y UPDATE
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Crear rol de administrador
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Rol administrativo',
            permisos=['create', 'read', 'update', 'delete']
        )
        
        # Crear rol de usuario
        self.user_role = Role.objects.create(
            nombre='usuario',
            descripcion='Rol básico',
            permisos=['read']
        )
        
        # Crear usuario administrador
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            dni='12345678',
            password='adminpass123',
            rol=self.admin_role,
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        # Autenticar usuario administrador
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh.access_token)
        
        # URLs
        self.users_url = reverse('authentication:user_list_create')
    
    def test_create_user_password_is_encrypted(self):
        """
        Test que verifica que la contraseña se cifre correctamente al crear un usuario
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'dni': '98765432',
            'celular': '987654321',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'rol': self.user_role.id
        }
        
        response = self.client.post(self.users_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el usuario fue creado
        created_user = CustomUser.objects.get(username='testuser')
        
        # Verificar que la contraseña NO está en texto plano
        self.assertNotEqual(created_user.password, 'testpassword123')
        
        # Verificar que la contraseña está cifrada correctamente
        self.assertTrue(check_password('testpassword123', created_user.password))
        
        # Verificar que la contraseña cifrada tiene el formato correcto de Django
        self.assertTrue(created_user.password.startswith('pbkdf2_sha256$'))
    
    def test_update_user_password_is_encrypted(self):
        """
        Test que verifica que la contraseña se cifre correctamente al actualizar un usuario
        """
        # Crear usuario de prueba
        test_user = CustomUser.objects.create_user(
            username='updateuser',
            email='updateuser@example.com',
            dni='11111111',
            password='oldpassword123',
            rol=self.user_role,
            first_name='Update',
            last_name='User'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        # Datos para actualizar (incluyendo nueva contraseña)
        update_data = {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'first_name': 'Updated'
        }
        
        url = reverse('authentication:user_detail', kwargs={'pk': test_user.pk})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refrescar el usuario desde la base de datos
        test_user.refresh_from_db()
        
        # Verificar que la contraseña NO está en texto plano
        self.assertNotEqual(test_user.password, 'newpassword123')
        
        # Verificar que la nueva contraseña está cifrada correctamente
        self.assertTrue(check_password('newpassword123', test_user.password))
        
        # Verificar que la contraseña antigua ya no funciona
        self.assertFalse(check_password('oldpassword123', test_user.password))
        
        # Verificar que la contraseña cifrada tiene el formato correcto de Django
        self.assertTrue(test_user.password.startswith('pbkdf2_sha256$'))
        
        # Verificar que otros campos se actualizaron correctamente
        self.assertEqual(test_user.first_name, 'Updated')
    
    def test_update_user_without_password_keeps_old_password(self):
        """
        Test que verifica que al actualizar un usuario sin incluir contraseña,
        la contraseña anterior se mantiene
        """
        # Crear usuario de prueba
        test_user = CustomUser.objects.create_user(
            username='keeppassuser',
            email='keeppassuser@example.com',
            dni='22222222',
            password='keepthispassword123',
            rol=self.user_role,
            first_name='Keep',
            last_name='Password'
        )
        
        # Guardar la contraseña original
        original_password = test_user.password
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        # Actualizar solo el nombre (sin contraseña)
        update_data = {
            'first_name': 'KeepUpdated'
        }
        
        url = reverse('authentication:user_detail', kwargs={'pk': test_user.pk})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refrescar el usuario desde la base de datos
        test_user.refresh_from_db()
        
        # Verificar que la contraseña no cambió
        self.assertEqual(test_user.password, original_password)
        
        # Verificar que la contraseña original sigue funcionando
        self.assertTrue(check_password('keepthispassword123', test_user.password))
        
        # Verificar que el nombre se actualizó
        self.assertEqual(test_user.first_name, 'KeepUpdated')
    
    def test_partial_update_with_password_encryption(self):
        """
        Test que verifica el cifrado de contraseñas en actualizaciones parciales (PATCH)
        """
        # Crear usuario de prueba
        test_user = CustomUser.objects.create_user(
            username='patchuser',
            email='patchuser@example.com',
            dni='33333333',
            password='patcholdpass123',
            rol=self.user_role,
            first_name='Patch',
            last_name='User'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        # Actualización parcial solo de contraseña
        patch_data = {
            'password': 'patchnewpass123',
            'password_confirm': 'patchnewpass123'
        }
        
        url = reverse('authentication:user_detail', kwargs={'pk': test_user.pk})
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refrescar el usuario desde la base de datos
        test_user.refresh_from_db()
        
        # Verificar cifrado correcto
        self.assertNotEqual(test_user.password, 'patchnewpass123')
        self.assertTrue(check_password('patchnewpass123', test_user.password))
        self.assertTrue(test_user.password.startswith('pbkdf2_sha256$'))
        
        # Verificar que otros campos no cambiaron
        self.assertEqual(test_user.first_name, 'Patch')
        self.assertEqual(test_user.last_name, 'User')


class PasswordEncryptionModelTest(TestCase):
    """
    Test cases para verificar el cifrado de contraseñas a nivel de modelo
    """
    
    def setUp(self):
        """Set up test data"""
        self.user_role = Role.objects.create(
            nombre='usuario',
            descripcion='Rol básico',
            permisos=['read']
        )
    
    def test_set_password_method_encrypts_correctly(self):
        """
        Test que verifica que el método set_password cifre correctamente
        """
        user = CustomUser.objects.create(
            username='testsetpass',
            email='testsetpass@example.com',
            dni='44444444',
            rol=self.user_role,
            first_name='Test',
            last_name='SetPass'
        )
        
        # Establecer contraseña usando set_password
        user.set_password('testpassword123')
        user.save()
        
        # Verificar cifrado
        self.assertNotEqual(user.password, 'testpassword123')
        self.assertTrue(check_password('testpassword123', user.password))
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_create_user_method_encrypts_correctly(self):
        """
        Test que verifica que create_user cifre correctamente
        """
        user = CustomUser.objects.create_user(
            username='testcreateuser',
            email='testcreateuser@example.com',
            dni='55555555',
            password='createuserpass123',
            rol=self.user_role,
            first_name='Test',
            last_name='CreateUser'
        )
        
        # Verificar cifrado
        self.assertNotEqual(user.password, 'createuserpass123')
        self.assertTrue(check_password('createuserpass123', user.password))
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))