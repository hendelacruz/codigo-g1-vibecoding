"""
Tests para el CRUD de Unidades Vehiculares
Incluye tests para crear, leer, actualizar y eliminar unidades
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from authentication.models import Role
from entities.models import Cliente, Unidad

User = get_user_model()


class UnidadCRUDTestCase(TestCase):
    """
    Test case para operaciones CRUD de Unidades Vehiculares
    """
    
    def setUp(self):
        """
        Configuración inicial para cada test
        """
        # Crear rol de administrador
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            dni='12345678',
            licencia='A1234567',
            celular='987654321',
            rol=self.admin_role
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear cliente de prueba
        self.test_cliente = Cliente.objects.create(
            nombre='Cliente Test S.A.C.',
            ruc='20987654326',  # RUC válido
            direccion='Av. Test 123, Lima',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com',
            is_active=True
        )
        
        # Datos válidos para crear unidad
        self.valid_unidad_data = {
            'tipo': 'bus',
            'placa': 'ABC-123',
            'marca': 'Mercedes',
            'modelo': 'Sprinter',
            'serie': 'VIN123456789',
            'cliente': self.test_cliente.id,
            'is_active': True
        }
        
        # URL base para unidades
        self.unidades_url = reverse('entities:unidad-list')
    
    def test_create_unidad_valid_data(self):
        """
        Test: Crear unidad con datos válidos
        """
        response = self.client.post(
            self.unidades_url, 
            self.valid_unidad_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Unidad.objects.count(), 1)
        
        # Verificar datos de la unidad creada
        unidad = Unidad.objects.first()
        self.assertEqual(unidad.tipo, 'bus')
        self.assertEqual(unidad.placa, 'ABC-123')
        self.assertEqual(unidad.marca, 'Mercedes')
        self.assertEqual(unidad.modelo, 'Sprinter')
        self.assertEqual(unidad.serie, 'VIN123456789')
        self.assertEqual(unidad.cliente, self.test_cliente)
        self.assertTrue(unidad.is_active)
        
        # Verificar respuesta
        self.assertIn('id', response.data)
        self.assertEqual(response.data['tipo'], 'bus')
        self.assertEqual(response.data['placa'], 'ABC-123')
        self.assertEqual(response.data['cliente'], self.test_cliente.id)
    
    def test_create_unidad_invalid_tipo(self):
        """
        Test: Crear unidad con tipo inválido
        """
        invalid_data = self.valid_unidad_data.copy()
        invalid_data['tipo'] = 'automovil'  # Tipo no válido
        
        response = self.client.post(
            self.unidades_url, 
            invalid_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Unidad.objects.count(), 0)
        self.assertIn('tipo', response.data)
    
    def test_create_unidad_invalid_placa(self):
        """
        Test: Crear unidad con placa inválida
        """
        invalid_data = self.valid_unidad_data.copy()
        invalid_data['placa'] = '123'  # Placa muy corta
        
        response = self.client.post(
            self.unidades_url, 
            invalid_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Unidad.objects.count(), 0)
        self.assertIn('placa', response.data)
    
    def test_create_unidad_duplicate_placa(self):
        """
        Test: Crear unidad con placa duplicada
        """
        # Crear primera unidad
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        
        # Intentar crear segunda unidad con misma placa
        response = self.client.post(
            self.unidades_url, 
            self.valid_unidad_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Unidad.objects.count(), 1)
        self.assertIn('placa', response.data)
    
    def test_create_unidad_duplicate_serie(self):
        """
        Test: Crear unidad con número de serie duplicado
        """
        # Crear primera unidad
        Unidad.objects.create(
            tipo='bus',
            placa='XYZ-789',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN123456789',
            cliente=self.test_cliente
        )
        
        # Intentar crear segunda unidad con mismo número de serie
        response = self.client.post(
            self.unidades_url, 
            self.valid_unidad_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Unidad.objects.count(), 1)
        self.assertIn('serie', response.data)
    
    def test_create_unidad_cliente_inactive(self):
        """
        Test: Crear unidad con cliente inactivo
        """
        # Desactivar cliente
        self.test_cliente.is_active = False
        self.test_cliente.save()
        
        response = self.client.post(
            self.unidades_url, 
            self.valid_unidad_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Unidad.objects.count(), 0)
        self.assertIn('cliente', response.data)
    
    def test_list_unidades(self):
        """
        Test: Listar unidades
        """
        # Crear varias unidades
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN222222222',
            cliente=self.test_cliente
        )
        
        response = self.client.get(self.unidades_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_unidad(self):
        """
        Test: Obtener una unidad específica
        """
        unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        
        url = reverse('entities:unidad-detail', kwargs={'pk': unidad.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], unidad.id)
        self.assertEqual(response.data['placa'], 'ABC-123')
        self.assertIn('cliente_info', response.data)
        self.assertEqual(response.data['cliente_info']['nombre'], self.test_cliente.nombre)
    
    def test_update_unidad(self):
        """
        Test: Actualizar unidad completa
        """
        unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        
        updated_data = {
            'tipo': 'camion',
            'placa': 'XYZ-789',
            'marca': 'Volvo',
            'modelo': 'FH',
            'serie': 'VIN999999999',
            'cliente': self.test_cliente.id,
            'is_active': True
        }
        
        url = reverse('entities:unidad-detail', kwargs={'pk': unidad.pk})
        response = self.client.put(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        unidad.refresh_from_db()
        self.assertEqual(unidad.tipo, 'camion')
        self.assertEqual(unidad.placa, 'XYZ-789')
        self.assertEqual(unidad.marca, 'Volvo')
        self.assertEqual(unidad.modelo, 'Fh')
    
    def test_partial_update_unidad(self):
        """
        Test: Actualización parcial de unidad
        """
        unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        
        partial_data = {
            'marca': 'Scania',
            'modelo': 'K320'
        }
        
        url = reverse('entities:unidad-detail', kwargs={'pk': unidad.pk})
        response = self.client.patch(url, partial_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización parcial
        unidad.refresh_from_db()
        self.assertEqual(unidad.marca, 'Scania')
        self.assertEqual(unidad.modelo, 'K320')
        self.assertEqual(unidad.tipo, 'bus')  # No cambió
        self.assertEqual(unidad.placa, 'ABC-123')  # No cambió
    
    def test_delete_unidad(self):
        """
        Test: Eliminar unidad (soft delete)
        """
        unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        
        url = reverse('entities:unidad-detail', kwargs={'pk': unidad.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar soft delete
        unidad.refresh_from_db()
        self.assertFalse(unidad.is_active)
        self.assertEqual(Unidad.objects.count(), 1)  # Sigue existiendo
    
    def test_toggle_active_unidad(self):
        """
        Test: Activar/desactivar unidad
        """
        unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente,
            is_active=True
        )
        
        # Desactivar
        url = reverse('entities:unidad-toggle-active', kwargs={'pk': unidad.pk})
        response = self.client.patch(url, {'is_active': False}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unidad.refresh_from_db()
        self.assertFalse(unidad.is_active)
        
        # Activar nuevamente
        response = self.client.patch(url, {'is_active': True}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unidad.refresh_from_db()
        self.assertTrue(unidad.is_active)
    
    def test_filter_unidades_by_tipo(self):
        """
        Test: Filtrar unidades por tipo
        """
        # Crear unidades de diferentes tipos
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN222222222',
            cliente=self.test_cliente
        )
        
        # Filtrar por tipo bus
        response = self.client.get(self.unidades_url, {'tipo': 'bus'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['tipo'], 'bus')
    
    def test_filter_unidades_by_cliente(self):
        """
        Test: Filtrar unidades por cliente
        """
        # Crear segundo cliente
        cliente2 = Cliente.objects.create(
            nombre='Cliente 2 S.A.C.',
            ruc='20123456786',  # RUC válido diferente
            direccion='Av. Test 456, Lima',
            contacto='María García',
            celular='987654322',
            correo='cliente2@test.com'
        )
        
        # Crear unidades para diferentes clientes
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN222222222',
            cliente=cliente2
        )
        
        # Filtrar por cliente
        response = self.client.get(self.unidades_url, {'cliente': self.test_cliente.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['cliente'], self.test_cliente.id)
    
    def test_search_unidades(self):
        """
        Test: Buscar unidades por placa, marca, modelo
        """
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente
        )
        Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN222222222',
            cliente=self.test_cliente
        )
        
        # Buscar por placa
        response = self.client.get(self.unidades_url, {'search': 'ABC'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Buscar por marca
        response = self.client.get(self.unidades_url, {'search': 'Mercedes'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Buscar por modelo
        response = self.client.get(self.unidades_url, {'search': 'Sprinter'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_estadisticas_unidades(self):
        """
        Test: Obtener estadísticas de unidades
        """
        # Crear unidades de prueba
        Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN111111111',
            cliente=self.test_cliente,
            is_active=True
        )
        Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN222222222',
            cliente=self.test_cliente,
            is_active=False
        )
        
        url = reverse('entities:unidad-estadisticas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('activas', response.data)
        self.assertIn('inactivas', response.data)
        self.assertIn('porcentaje_activas', response.data)
        self.assertIn('por_tipo', response.data)
        
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['activas'], 1)
        self.assertEqual(response.data['inactivas'], 1)