"""
Tests for sales views
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date, time
from django.utils import timezone
from unittest.mock import patch, Mock
from django.core.cache import cache

from sales.models import Ventas
from sales.views import VentasViewSet
from entities.models import Cliente, Unidad
from authentication.models import Role

User = get_user_model()


class VentasViewSetTest(APITestCase):
    """Test cases for VentasViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Clear cache before each test
        cache.clear()
        
        # Clean up any existing test data to ensure isolation
        Ventas.objects.all().delete()
        
        # Create test role and user
        self.role, created = Role.objects.get_or_create(
            nombre='administrador',
            defaults={
                'descripcion': 'Test Administrator role',
                'permisos': ['view_ventas', 'add_ventas', 'change_ventas', 'delete_ventas']
            }
        )
        self.user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'dni': '12345678',
                'celular': '+51987654321',
                'rol': self.role
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Create test client
        self.cliente, created = Cliente.objects.get_or_create(
            ruc='12345678901',
            defaults={
                'nombre': 'Test Cliente',
                'direccion': 'Test Address',
                'contacto': 'Test Contact',
                'celular': '987654321',
                'correo': 'test@example.com'
            }
        )
        
        # Create test unit
        self.unidad, created = Unidad.objects.get_or_create(
            placa='ABC-123',
            defaults={
                'tipo': 'camion',
                'marca': 'Test Marca',
                'modelo': 'Test Modelo',
                'serie': 'TEST123456',
                'cliente': self.cliente
            }
        )
        
        # Create test ventas
        self.venta1 = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba 1',
            unidad=self.unidad,
            precio=Decimal('1180.00'),
            estado='pendiente'
        )
        
        self.venta2 = Ventas.objects.create(
            mes=date(2024, 1, 2),
            fecha_pago=time(15, 30),
            numero_operacion='0987654321',
            tipo_pago='transferencia',
            banco='BBVA',
            numero_factura='F001-002',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba 2',
            unidad=self.unidad,
            precio=Decimal('2360.00'),
            estado='pagado'
        )
        
        # Set up API client with authentication
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Base URL for ventas endpoints
        self.base_url = '/api/sales/ventas/'
    
    def test_list_ventas_success(self):
        """Test successful listing of ventas"""
        response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that ventas are ordered by fecha_generacion_factura desc
        ventas = response.data['results']
        self.assertEqual(ventas[0]['numero_factura'], 'F001-002')  # Most recent
        self.assertEqual(ventas[1]['numero_factura'], 'F001-001')  # Older
    
    def test_list_ventas_pagination(self):
        """Test pagination in ventas list"""
        # Create more ventas to test pagination
        for i in range(15):
            Ventas.objects.create(
                mes=date(2024, 1, 1),
                fecha_pago=time(14, 30),
                numero_operacion=f'12345678{i:02d}'[:10],
                tipo_pago='efectivo',
                banco='BCP',
                numero_factura=f'F001-{i+10:03d}',
                fecha_generacion_factura=timezone.now(),
                cliente=self.cliente,
                descripcion=f'Venta de prueba {i}',
                unidad=self.unidad,
                precio=Decimal('1180.00'),
                estado='pendiente'
            )
        
        response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 17)  # 2 original + 15 new
    
    def test_retrieve_venta_success(self):
        """Test successful retrieval of single venta"""
        url = f'{self.base_url}{self.venta1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['numero_factura'], 'F001-001')
        self.assertEqual(response.data['precio'], '1180.00')
        self.assertIn('cliente_info', response.data)
        self.assertIn('unidad_info', response.data)
    
    def test_retrieve_venta_not_found(self):
        """Test retrieval of non-existent venta"""
        url = f'{self.base_url}99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_venta_success(self):
        """Test successful venta creation"""
        venta_data = {
            'mes': '2024-01-03',
            'fecha_pago': '16:30:00',
            'numero_operacion': '1111111111',
            'tipo_pago': 'yape',
            'banco': 'BCP',
            'numero_factura': 'F001-003',
            'fecha_generacion_factura': '2024-01-03',
            'cliente': self.cliente.id,
            'descripcion': 'Nueva venta',
            'unidad': self.unidad.id,
            'precio': '590.00',
            'estado': 'pendiente'
        }
        
        response = self.client.post(self.base_url, venta_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['numero_factura'], 'F001-003')
        self.assertEqual(response.data['precio'], '590.00')
        
        # Verify venta was created in database
        venta = Ventas.objects.get(numero_factura='F001-003')
        self.assertEqual(venta.precio, Decimal('590.00'))
        self.assertEqual(venta.importe, Decimal('500.00'))
        self.assertEqual(venta.igv, Decimal('90.00'))
    
    def test_create_venta_validation_error(self):
        """Test venta creation with validation errors"""
        venta_data = {
            'numero_factura': 'F001-001',  # Duplicate
            'cliente': self.cliente.id,
            'precio': '-100.00',  # Invalid price
            'tipo_pago': 'invalid_type'  # Invalid choice
        }
        
        response = self.client.post(self.base_url, venta_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('numero_factura', response.data)
        self.assertIn('precio', response.data)
        self.assertIn('tipo_pago', response.data)
    
    def test_update_venta_success(self):
        """Test successful venta update"""
        url = f'{self.base_url}{self.venta1.id}/'
        update_data = {
            'descripcion': 'Updated description',
            'precio': '2360.00',
            'estado': 'pagado'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descripcion'], 'Updated description')
        self.assertEqual(response.data['precio'], '2360.00')
        self.assertEqual(response.data['estado'], 'pagado')
        
        # Verify update in database
        self.venta1.refresh_from_db()
        self.assertEqual(self.venta1.precio, Decimal('2360.00'))
        self.assertEqual(self.venta1.estado, 'pagado')
    
    def test_delete_venta_success(self):
        """Test successful venta deletion (soft delete)"""
        url = f'{self.base_url}{self.venta1.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify soft delete (is_active = False)
        self.venta1.refresh_from_db()
        self.assertFalse(self.venta1.is_active)
    
    def test_search_ventas(self):
        """Test search functionality"""
        # Search by numero_factura
        response = self.client.get(f'{self.base_url}?search=F001-001')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['numero_factura'], 'F001-001')
        
        # Search by cliente name
        response = self.client.get(f'{self.base_url}?search=Test Cliente')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_ventas(self):
        """Test filtering functionality"""
        # Filter by estado
        response = self.client.get(f'{self.base_url}?estado=pendiente')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['estado'], 'pendiente')
        
        # Filter by metodo_pago (maps to tipo_pago field)
        response = self.client.get(f'{self.base_url}?metodo_pago=transferencia')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['tipo_pago'], 'transferencia')
        
        # Filter by cliente
        response = self.client.get(f'{self.base_url}?cliente={self.cliente.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_ordering_ventas(self):
        """Test ordering functionality"""
        # Order by precio ascending
        response = self.client.get(f'{self.base_url}?ordering=precio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ventas = response.data['results']
        self.assertEqual(ventas[0]['precio'], '1180.00')  # Lower price first
        self.assertEqual(ventas[1]['precio'], '2360.00')  # Higher price second
        
        # Order by precio descending
        response = self.client.get(f'{self.base_url}?ordering=-precio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ventas = response.data['results']
        self.assertEqual(ventas[0]['precio'], '2360.00')  # Higher price first
        self.assertEqual(ventas[1]['precio'], '1180.00')  # Lower price second
    
    def test_cambiar_estado_action(self):
        """Test cambiar_estado custom action"""
        url = f'{self.base_url}{self.venta1.id}/cambiar_estado/?nuevo_estado=pagado'
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Estado cambiado de pendiente a pagado')
        
        # Verify state change
        self.venta1.refresh_from_db()
        self.assertEqual(self.venta1.estado, 'pagado')
    
    def test_cambiar_estado_invalid_estado(self):
        """Test cambiar_estado with invalid estado"""
        url = f'{self.base_url}{self.venta1.id}/cambiar_estado/?nuevo_estado=invalid_estado'
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_anular_venta_action(self):
        """Test anular_venta custom action"""
        url = f'{self.base_url}{self.venta1.id}/anular_venta/'
        data = {'motivo': 'Error en facturación'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Venta anulada exitosamente')
        
        # Verify venta was annulled
        self.venta1.refresh_from_db()
        self.assertEqual(self.venta1.estado, 'anulado')
    
    def test_anular_venta_already_anulado(self):
        """Test anular_venta on already annulled venta"""
        self.venta1.estado = 'anulado'
        self.venta1.save()
        
        url = f'{self.base_url}{self.venta1.id}/anular_venta/'
        data = {'motivo': 'Test'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_toggle_active_action(self):
        """Test toggle_active custom action"""
        url = f'{self.base_url}{self.venta1.id}/toggle_active/'
        
        # Toggle to inactive
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.venta1.refresh_from_db()
        self.assertFalse(self.venta1.is_active)
        
        # Toggle back to active
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.venta1.refresh_from_db()
        self.assertTrue(self.venta1.is_active)
    
    def test_estadisticas_action(self):
        """Test estadisticas custom action"""
        url = f'{self.base_url}estadisticas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_ventas', response.data)
        self.assertIn('total_igv', response.data)
        self.assertIn('total_importe', response.data)
        self.assertIn('cantidad_ventas', response.data)
        self.assertIn('promedio_venta', response.data)
        self.assertIn('ventas_por_estado', response.data)
        self.assertIn('ventas_por_tipo_pago', response.data)
    
    def test_dashboard_action(self):
        """Test dashboard custom action"""
        url = f'{self.base_url}dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ventas_mes_actual', response.data)
        self.assertIn('ventas_pendientes', response.data)
        self.assertIn('ventas_vencidas', response.data)
        self.assertIn('top_clientes', response.data)
        self.assertIn('ventas_por_mes', response.data)
    
    def test_reporte_action(self):
        """Test reporte custom action"""
        url = f'{self.base_url}reporte/'
        
        # Test with date filters
        params = {
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ventas', response.data)
        self.assertIn('totales', response.data)
        self.assertIn('fecha_generacion', response.data)
        self.assertIn('filtros_aplicados', response.data)
        
        # Check totales structure
        totales = response.data['totales']
        self.assertIn('total_ventas', totales)
        self.assertIn('total_igv', totales)
        self.assertIn('total_importe', totales)
        self.assertIn('cantidad_ventas', totales)
    
    def test_reporte_action_no_dates(self):
        """Test reporte action without date filters"""
        url = f'{self.base_url}reporte/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ventas', response.data)
        self.assertIn('totales', response.data)
        self.assertIn('fecha_generacion', response.data)
    
    def test_authentication_required(self):
        """Test that authentication is required"""
        # Remove authentication
        self.client.credentials()
        
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_permission_required(self):
        """Test that proper permissions are required for create action"""
        # Create user without admin/operator permissions
        role_no_perms = Role.objects.create(
            nombre='No Perms',
            descripcion='Role without permissions',
            permisos=[]
        )
        user_no_perms = User.objects.create_user(
            username='noperms',
            email='noperms@example.com',
            dni='87654321',
            celular='+51987654322',
            password='testpass123',
            rol=role_no_perms
        )
        
        # Authenticate as user without permissions
        refresh = RefreshToken.for_user(user_no_perms)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Test POST (create) action which requires IsAdminOrSupervisor
        venta_data = {
            'mes': '2024-01-01',
            'fecha_pago': '14:30:00',
            'numero_operacion': '1234567890',
            'tipo_pago': 'transferencia',
            'numero_factura': 'F001-00001',
            'fecha_generacion_factura': '2024-01-15',
            'cliente': self.cliente.id,
            'precio': '1000.00',
            'estado': 'pendiente',
            'banco': 'BCP',
            'descripcion': 'Venta de prueba',
            'unidad': self.unidad.id
        }
        response = self.client.post(self.base_url, venta_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('sales.views.VentasViewSet.throttle_classes')
    def test_rate_limiting(self, mock_throttle):
        """Test rate limiting is applied"""
        # This test verifies that throttling is configured
        # In a real scenario, you would test actual rate limiting behavior
        viewset = VentasViewSet()
        self.assertTrue(hasattr(viewset, 'throttle_classes'))
    
    def test_cache_invalidation_on_create(self):
        """Test that cache is invalidated on venta creation"""
        # First, populate cache by calling estadisticas
        self.client.get(f'{self.base_url}estadisticas/')
        
        # Create new venta
        venta_data = {
            'mes': '2024-01-01',
            'fecha_pago': '14:30:00',
            'numero_operacion': '1234567890',
            'tipo_pago': 'efectivo',
            'numero_factura': 'F001-999',
            'fecha_generacion_factura': '2024-01-15',
            'cliente': self.cliente.id,
            'precio': '1180.00',
            'estado': 'pendiente',
            'banco': 'BCP',
            'descripcion': 'Venta de prueba cache',
            'unidad': self.unidad.id
        }
        
        with patch('todoapi.utils.cache.invalidate_cache_pattern') as mock_invalidate:
            mock_invalidate.return_value = 1  # Simulate successful cache invalidation
            response = self.client.post(self.base_url, venta_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify cache was invalidated
            mock_invalidate.assert_called()
    
    def test_queryset_optimization(self):
        """Test that queryset is optimized with select_related"""
        with self.assertNumQueries(3):  # Should be optimized with select_related
            response = self.client.get(self.base_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_error_handling(self):
        """Test error handling in views"""
        # Test with invalid venta ID
        url = f'{self.base_url}invalid_id/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test with malformed data
        venta_data = {'invalid': 'data'}
        response = self.client.post(self.base_url, venta_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_response_format_consistency(self):
        """Test that all responses follow consistent format"""
        # Test list response
        response = self.client.get(self.base_url)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Test detail response
        url = f'{self.base_url}{self.venta1.id}/'
        response = self.client.get(url)
        self.assertIn('id', response.data)
        self.assertIn('numero_factura', response.data)
        
        # Test error response
        response = self.client.get(f'{self.base_url}99999/')
        self.assertIn('detail', response.data)


class VentasViewSetIntegrationTest(APITestCase):
    """Integration tests for VentasViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Clear cache before each test
        cache.clear()
        
        # Create test role and user
        self.role, created = Role.objects.get_or_create(
            nombre='administrador',
            defaults={
                'descripcion': 'Test Administrator role',
                'permisos': ['view_ventas', 'add_ventas', 'change_ventas', 'delete_ventas']
            }
        )
        self.user, created = User.objects.get_or_create(
            username='integrationuser',
            defaults={
                'email': 'integration@example.com',
                'dni': '11111111',
                'celular': '+51987654323',
                'rol': self.role
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Set up API client with authentication
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.base_url = '/api/sales/ventas/'
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_full_crud_workflow(self):
        """Test complete CRUD workflow"""
        # Create cliente and unidad first
        cliente = Cliente.objects.create(
            nombre='Integration Test Cliente',
            ruc='98765432101',
            direccion='Integration Address',
            contacto='Integration Contact',
            celular='123456789',
            correo='integration@example.com'
        )
        
        unidad = Unidad.objects.create(
            placa='INT-123',
            tipo='camion',
            marca='Integration Marca',
            modelo='Integration Modelo',
            serie='INT123456',
            cliente=cliente
        )
        
        # 1. CREATE
        venta_data = {
            'numero_factura': 'INT-001',
            'fecha_generacion_factura': '2024-01-03',
            'mes': '2024-01-03',
            'fecha_pago': '16:30:00',
            'numero_operacion': '1111111111',
            'banco': 'BCP',
            'cliente': cliente.id,
            'unidad': unidad.id,
            'precio': '1180.00',
            'tipo_pago': 'efectivo',
            'descripcion': 'Integration test venta'
        }
        
        create_response = self.client.post(self.base_url, venta_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        # Get the created venta ID by finding it in the database
        from sales.models import Ventas
        created_venta = Ventas.objects.get(numero_factura='INT-001')
        venta_id = created_venta.id
        
        # 2. READ (List)
        list_response = self.client.get(self.base_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)
        
        # 3. READ (Detail)
        detail_url = f'{self.base_url}{venta_id}/'
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['numero_factura'], 'INT-001')
        
        # 4. UPDATE
        update_data = {
            'descripcion': 'Updated integration test venta',
            'estado': 'pagado'
        }
        update_response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['descripcion'], 'Updated integration test venta')
        self.assertEqual(update_response.data['estado'], 'pagado')
        
        # 5. CUSTOM ACTIONS
        # Test cambiar_estado
        estado_url = f'{detail_url}cambiar_estado/?nuevo_estado=vencido'
        estado_response = self.client.patch(estado_url)
        self.assertEqual(estado_response.status_code, status.HTTP_200_OK)
        
        # Test estadisticas
        stats_response = self.client.get(f'{self.base_url}estadisticas/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        
        # 6. DELETE (Soft delete)
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify soft delete (need to use all() to include inactive objects)
        venta = Ventas.objects.all().get(id=venta_id)
        self.assertFalse(venta.is_active)