"""
Tests comprehensivos para el CRUD de proveedores con validaciones específicas.
Incluye tests para RUC peruano, celular peruano y validaciones de correo único.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.exceptions import ValidationError

from .models import Proveedor
from authentication.models import Role

User = get_user_model()


class ProveedorCRUDTestCase(APITestCase):
    """
    Tests comprehensivos para el CRUD de proveedores con validaciones específicas.
    """
    
    def setUp(self):
        """
        Configuración inicial para los tests.
        """
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='ADMIN',
            descripcion='Rol de administrador para tests',
            permisos={
                'usuarios': ['create', 'read', 'update', 'delete'],
                'roles': ['create', 'read', 'update', 'delete'],
                'gps': ['create', 'read', 'update', 'delete'],
                'reportes': ['create', 'read', 'update', 'delete'],
                'configuracion': ['create', 'read', 'update', 'delete']
            }
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='admin',
            email='admin@todoapi.com',
            password='admin123',
            dni='12345678',
            celular='987654321',
            rol=self.rol
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs para los tests
        self.list_url = reverse('entities:proveedor-list')
        
        # Datos válidos para crear proveedor
        self.valid_proveedor_data = {
            'nombre': 'Proveedor Test SA',
            'ruc': '20123456786',  # RUC válido calculado
            'direccion': 'Av. Test 123, Lima',
            'contacto': 'Juan Pérez',
            'celular': '987654321',  # Celular peruano válido
            'correo': 'test@proveedor.com',
            'is_active': True  # Explícitamente activo
        }

    def test_create_proveedor_valid_data(self):
        """
        Test crear proveedor con datos válidos.
        """
        response = self.client.post(self.list_url, self.valid_proveedor_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], self.valid_proveedor_data['nombre'])
        self.assertEqual(response.data['ruc'], self.valid_proveedor_data['ruc'])
        self.assertEqual(response.data['celular'], self.valid_proveedor_data['celular'])
        self.assertEqual(response.data['correo'], self.valid_proveedor_data['correo'])
        # Verificar que is_active tiene un valor booleano válido (por defecto debería ser True)
        self.assertIsInstance(response.data['is_active'], bool)
        # Si no se especifica is_active, debería ser True por defecto del modelo
        self.assertTrue(response.data['is_active'])

    def test_create_proveedor_invalid_ruc_format(self):
        """
        Test crear proveedor con RUC de formato inválido.
        """
        invalid_data = self.valid_proveedor_data.copy()
        invalid_data['ruc'] = '123456789'  # RUC con menos de 11 dígitos
        
        response = self.client.post(self.list_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ruc', response.data)

    def test_create_proveedor_invalid_ruc_check_digit(self):
        """
        Test crear proveedor con RUC con dígito verificador inválido.
        """
        invalid_data = self.valid_proveedor_data.copy()
        invalid_data['ruc'] = '20123456789'  # RUC con dígito verificador incorrecto
        
        response = self.client.post(self.list_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ruc', response.data)

    def test_create_proveedor_duplicate_ruc(self):
        """
        Test crear proveedor con RUC duplicado.
        """
        # Crear primer proveedor
        self.client.post(self.list_url, self.valid_proveedor_data)
        
        # Intentar crear segundo proveedor con mismo RUC
        duplicate_data = self.valid_proveedor_data.copy()
        duplicate_data['nombre'] = 'Otro Proveedor'
        duplicate_data['correo'] = 'otro@proveedor.com'
        
        response = self.client.post(self.list_url, duplicate_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ruc', response.data)

    def test_create_proveedor_invalid_celular_format(self):
        """
        Test crear proveedor con celular de formato inválido.
        """
        invalid_data = self.valid_proveedor_data.copy()
        invalid_data['celular'] = '123456789'  # Celular que no empieza con 9
        
        response = self.client.post(self.list_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('celular', response.data)

    def test_create_proveedor_invalid_celular_length(self):
        """
        Test crear proveedor con celular de longitud inválida.
        """
        invalid_data = self.valid_proveedor_data.copy()
        invalid_data['celular'] = '98765432'  # Celular con menos de 9 dígitos
        
        response = self.client.post(self.list_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('celular', response.data)

    def test_create_proveedor_duplicate_correo(self):
        """
        Test crear proveedor con correo duplicado.
        """
        # Crear primer proveedor
        self.client.post(self.list_url, self.valid_proveedor_data)
        
        # Intentar crear segundo proveedor con mismo correo
        duplicate_data = self.valid_proveedor_data.copy()
        duplicate_data['nombre'] = 'Otro Proveedor'
        duplicate_data['ruc'] = '20987654326'  # RUC diferente pero válido
        
        response = self.client.post(self.list_url, duplicate_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('correo', response.data)

    def test_list_proveedores(self):
        """
        Test listar proveedores.
        """
        # Crear algunos proveedores
        self.client.post(self.list_url, self.valid_proveedor_data)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_proveedor(self):
        """
        Test obtener un proveedor específico.
        """
        # Crear proveedor
        create_response = self.client.post(self.list_url, self.valid_proveedor_data)
        proveedor_id = create_response.data['id']
        
        # Obtener proveedor
        detail_url = reverse('entities:proveedor-detail', kwargs={'pk': proveedor_id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], proveedor_id)
        self.assertEqual(response.data['nombre'], self.valid_proveedor_data['nombre'])

    def test_update_proveedor_put(self):
        """
        Test actualizar proveedor completo con PUT.
        """
        # Crear proveedor
        create_response = self.client.post(self.list_url, self.valid_proveedor_data)
        proveedor_id = create_response.data['id']
        
        # Datos actualizados - necesitamos calcular un RUC válido diferente
        updated_data = {
            'nombre': 'Proveedor Actualizado SA',
            'ruc': '20987654326',  # RUC válido calculado
            'direccion': 'Av. Actualizada 456, Lima',
            'contacto': 'María García',
            'celular': '987654322',
            'correo': 'actualizado@proveedor.com'
        }
        
        # Actualizar proveedor
        detail_url = reverse('entities:proveedor-detail', kwargs={'pk': proveedor_id})
        response = self.client.put(detail_url, updated_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], updated_data['nombre'])
        self.assertEqual(response.data['ruc'], updated_data['ruc'])
        self.assertEqual(response.data['celular'], updated_data['celular'])

    def test_update_proveedor_patch(self):
        """
        Test actualizar proveedor parcial con PATCH.
        """
        # Crear proveedor
        create_response = self.client.post(self.list_url, self.valid_proveedor_data)
        proveedor_id = create_response.data['id']
        
        # Datos parciales para actualizar
        partial_data = {
            'nombre': 'Proveedor PATCH Update',
            'celular': '987654323'
        }
        
        # Actualizar proveedor parcialmente
        detail_url = reverse('entities:proveedor-detail', kwargs={'pk': proveedor_id})
        response = self.client.patch(detail_url, partial_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], partial_data['nombre'])
        self.assertEqual(response.data['celular'], partial_data['celular'])
        # Verificar que otros campos no cambiaron
        self.assertEqual(response.data['ruc'], self.valid_proveedor_data['ruc'])

    def test_toggle_active_proveedor(self):
        """
        Test activar/desactivar proveedor.
        """
        # Crear proveedor
        create_response = self.client.post(self.list_url, self.valid_proveedor_data)
        proveedor_id = create_response.data['id']
        
        # Desactivar proveedor
        toggle_url = reverse('entities:proveedor-toggle-active', kwargs={'pk': proveedor_id})
        response = self.client.patch(toggle_url, {'is_active': False}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        
        # Reactivar proveedor
        response = self.client.patch(toggle_url, {'is_active': True}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])

    def test_search_proveedores(self):
        """
        Test búsqueda de proveedores.
        """
        # Crear proveedor
        self.client.post(self.list_url, self.valid_proveedor_data)
        
        # Buscar por nombre
        response = self.client.get(self.list_url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_proveedores_by_active(self):
        """
        Test filtrar proveedores por estado activo.
        """
        # Crear dos proveedores
        self.client.post(self.list_url, self.valid_proveedor_data)
        
        proveedor_data_2 = self.valid_proveedor_data.copy()
        proveedor_data_2['nombre'] = 'Proveedor Inactivo SA'
        proveedor_data_2['ruc'] = '20987654326'
        proveedor_data_2['correo'] = 'inactivo@proveedor.com'
        create_response = self.client.post(self.list_url, proveedor_data_2)
        
        # Desactivar el segundo proveedor
        proveedor_id = create_response.data['id']
        toggle_url = reverse('entities:proveedor-toggle-active', kwargs={'pk': proveedor_id})
        self.client.patch(toggle_url, {'is_active': False}, format='json')
        
        # Filtrar solo activos
        response = self.client.get(self.list_url, {'is_active': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Solo el proveedor activo
        
        # Filtrar solo inactivos
        response = self.client.get(self.list_url, {'is_active': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Solo el proveedor inactivo

    def test_validation_error_messages(self):
        """
        Test que los mensajes de error de validación sean claros.
        """
        invalid_data = {
            'nombre': 'Test',
            'ruc': '123',  # RUC inválido
            'celular': '123',  # Celular inválido
            'correo': 'invalid-email'  # Email inválido
        }
        
        response = self.client.post(self.list_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ruc', response.data)
        self.assertIn('celular', response.data)
        self.assertIn('correo', response.data)


class ProveedorModelTestCase(TestCase):
    """
    Tests para el modelo Proveedor y sus validaciones.
    """
    
    def test_str_representation(self):
        """
        Test representación string del modelo.
        """
        proveedor = Proveedor(nombre='Test Proveedor', ruc='20123456786')
        self.assertEqual(str(proveedor), 'Test Proveedor (20123456786)')

    def test_ruc_validation_in_model(self):
        """
        Test validación de RUC a nivel de modelo.
        """
        proveedor = Proveedor(
            nombre='Test',
            ruc='123',  # RUC inválido
            celular='987654321',
            correo='test@example.com'
        )
        
        with self.assertRaises(ValidationError):
            proveedor.full_clean()

    def test_celular_validation_in_model(self):
        """
        Test validación de celular a nivel de modelo.
        """
        proveedor = Proveedor(
            nombre='Test',
            ruc='20123456786',
            celular='123',  # Celular inválido
            correo='test@example.com'
        )
        
        with self.assertRaises(ValidationError):
            proveedor.full_clean()

    def test_unique_ruc_constraint(self):
        """
        Test restricción de unicidad para RUC.
        """
        # Crear primer proveedor
        Proveedor.objects.create(
            nombre='Proveedor 1',
            ruc='20123456786',
            celular='987654321',
            correo='test1@example.com'
        )
        
        # Intentar crear segundo proveedor con mismo RUC
        proveedor2 = Proveedor(
            nombre='Proveedor 2',
            ruc='20123456786',  # RUC duplicado
            celular='987654322',
            correo='test2@example.com'
        )
        
        with self.assertRaises(ValidationError):
            proveedor2.full_clean()

    def test_unique_correo_constraint(self):
        """
        Test restricción de unicidad para correo a través del serializer.
        """
        from .serializers import ProveedorSerializer
        
        # Crear primer proveedor
        Proveedor.objects.create(
            nombre='Proveedor 1',
            ruc='20123456786',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Intentar crear segundo proveedor con mismo correo usando serializer
        data = {
            'nombre': 'Proveedor 2',
            'ruc': '20987654327',
            'celular': '987654322',
            'correo': 'test@example.com'  # Correo duplicado
        }
        
        serializer = ProveedorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('correo', serializer.errors)