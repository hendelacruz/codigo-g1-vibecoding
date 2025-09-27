"""
Tests para las vistas del dashboard
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

from sales.models import Ventas
from inventory.models import GPS, SIMCard
from entities.models import Cliente, Proveedor, Unidad
from authentication.models import Role
from .models import Metric, Alert
from django.utils import timezone

User = get_user_model()


class DashboardViewSetTestCase(APITestCase):
    """Tests para DashboardViewSet"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'can_view': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar autenticación JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678906',
            direccion='Av. Test 303, Lima',
            contacto='Patricia Silva',
            celular='987654326',
            correo='cliente6@test.com'
        )
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='20123456789',
            direccion='Av. Proveedor 123',
            contacto='María García',
            celular='987654321'
        )
        
        # Crear unidad vehicular
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear productos
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='Teltonika',
            modelo='GPS Test',
            numero_factura='F001-123',
            proveedor=self.proveedor,
            estado='no_asignado',
            proceso='disponible',
            precio_compra=Decimal('100.00')
        )
        
        # Crear ventas
        self.venta = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP123456',
            tipo_pago='transferencia',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Servicio de GPS mensual',
            unidad=self.unidad,
            precio=Decimal('118.00'),
            importe=Decimal('100.00'),
            igv=Decimal('18.00'),
            total=Decimal('118.00'),
            estado='pagado'
        )
        
        # Crear métricas de prueba
        from datetime import datetime
        
        self.metric = Metric.objects.create(
            name='total_sales_count',
            metric_type='sales',
            value=Decimal('5'),
            period_type='daily',
            period_start=datetime.combine(self.venta.created_at.date(), datetime.min.time()),
            period_end=datetime.combine(self.venta.created_at.date(), datetime.max.time()),
            created_by=self.user
        )
    
    def test_get_sales_kpis(self):
        """Test para obtener KPIs de ventas"""
        url = reverse('dashboard:dashboard-sales-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_sales_count', response.data)
        self.assertIn('total_sales_amount', response.data)
        self.assertIn('average_sale_amount', response.data)
    
    def test_get_sales_kpis_with_period(self):
        """Test para obtener KPIs de ventas con período específico"""
        url = reverse('dashboard:dashboard-sales-kpis')
        response = self.client.get(url, {
            'period_start': '2024-01-01',
            'period_end': '2024-12-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('period_start', response.data)
        self.assertIn('period_end', response.data)
    
    def test_get_inventory_kpis(self):
        """Test para obtener KPIs de inventario"""
        url = reverse('dashboard:dashboard-inventory-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('gps_devices', response.data)
        self.assertIn('sim_cards', response.data)
        self.assertIn('other_products', response.data)
        self.assertIn('low_stock_products', response.data)
        
        # Verificar estructura de gps_devices
        self.assertIn('total', response.data['gps_devices'])
        self.assertIn('available', response.data['gps_devices'])
        self.assertIn('damaged', response.data['gps_devices'])
        
        # Verificar estructura de sim_cards
        self.assertIn('total', response.data['sim_cards'])
        self.assertIn('available', response.data['sim_cards'])
        self.assertIn('assigned', response.data['sim_cards'])
    
    def test_get_user_kpis(self):
        """Test para obtener KPIs de usuarios"""
        url = reverse('dashboard:dashboard-user-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('active_users', response.data)
        self.assertIn('new_users_this_period', response.data)
        self.assertIn('users_by_role', response.data)
        self.assertIn('recent_users', response.data)
    
    def test_get_financial_kpis(self):
        """Test para obtener KPIs financieros"""
        url = reverse('dashboard:dashboard-financial-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_tax', response.data)
        self.assertIn('net_revenue', response.data)
    
    def test_get_comprehensive_dashboard(self):
        """Test para obtener dashboard completo"""
        url = reverse('dashboard:dashboard-comprehensive')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sales_kpis', response.data)
        self.assertIn('inventory_kpis', response.data)
        self.assertIn('user_kpis', response.data)
        self.assertIn('financial_kpis', response.data)
        self.assertIn('generated_at', response.data)
    
    def test_unauthorized_access(self):
        """Test para acceso no autorizado"""
        # Remover credenciales
        self.client.credentials()
        
        url = reverse('dashboard:dashboard-sales-kpis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_date_format(self):
        """Test para formato de fecha inválido"""
        url = reverse('dashboard:dashboard-sales-kpis')
        response = self.client.get(url, {
            'period_start': 'invalid-date',
            'period_end': '2024-12-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MetricViewSetTestCase(APITestCase):
    """Tests para MetricViewSet"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'can_view': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar autenticación JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear métricas de prueba
        from datetime import datetime
        
        self.metric1 = Metric.objects.create(
            name='total_sales_count',
            metric_type='sales',
            value=Decimal('5'),
            period_type='daily',
            period_start=datetime(2024, 1, 15),
            period_end=datetime(2024, 1, 15, 23, 59, 59),
            created_by=self.user
        )
        
        self.metric2 = Metric.objects.create(
            name='total_gps_count',
            metric_type='inventory',
            value=Decimal('10'),
            period_type='weekly',
            period_start=datetime(2024, 1, 15),
            period_end=datetime(2024, 1, 21, 23, 59, 59),
            created_by=self.user
        )
    
    def test_list_metrics(self):
        """Test para listar métricas"""
        url = reverse('dashboard:metric-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_metrics_by_type(self):
        """Test para filtrar métricas por tipo"""
        url = reverse('dashboard:metric-list')
        response = self.client.get(url, {'metric_type': 'sales'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['metric_type'], 'sales')
    
    def test_filter_metrics_by_period_type(self):
        """Test para filtrar métricas por tipo de período"""
        url = reverse('dashboard:metric-list')
        response = self.client.get(url, {'period_type': 'daily'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['period_type'], 'daily')
    
    def test_filter_metrics_by_date_range(self):
        """Test para filtrar métricas por rango de fechas"""
        url = reverse('dashboard:metric-list')
        response = self.client.get(url, {
            'period_start_after': '2024-01-01',
            'period_start_before': '2024-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_metric_detail(self):
        """Test para obtener detalle de una métrica"""
        url = reverse('dashboard:metric-detail', kwargs={'pk': self.metric1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'total_sales_count')
        self.assertEqual(response.data['value'], '5.00')
    
    def test_create_metric(self):
        """Test para crear una nueva métrica"""
        url = reverse('dashboard:metric-list')
        data = {
            'name': 'total_revenue',
            'value': '1000.00',
            'metric_type': 'financial',
            'period_type': 'monthly',
            'period_start': '2024-02-01T00:00:00Z',
            'period_end': '2024-02-28T23:59:59Z'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Metric.objects.count(), 3)
    
    def test_update_metric(self):
        """Test para actualizar una métrica"""
        url = reverse('dashboard:metric-detail', kwargs={'pk': self.metric1.pk})
        data = {
            'name': 'total_sales_count',
            'value': '10.00',
            'metric_type': 'sales',
            'period_type': 'daily',
            'period_start': '2024-01-15T00:00:00Z',
            'period_end': '2024-01-15T23:59:59Z'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.metric1.refresh_from_db()
        self.assertEqual(self.metric1.value, Decimal('10.00'))
    
    def test_delete_metric(self):
        """Test para eliminar una métrica"""
        url = reverse('dashboard:metric-detail', kwargs={'pk': self.metric1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Metric.objects.count(), 1)


class AlertViewSetTestCase(APITestCase):
    """Tests para AlertViewSet"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear rol de prueba
        self.rol = Role.objects.create(
            nombre='operador',
            descripcion='Rol de operador para tests',
            permisos={'can_view': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol
        )
        
        # Configurar autenticación JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear alertas de prueba
        self.alert1 = Alert.objects.create(
            title='GPS Stock Alert',
            alert_type='low_stock',
            severity='medium',
            message='GPS Test stock is low',
            status='active'
        )
        
        self.alert2 = Alert.objects.create(
            title='High Sales Alert',
            alert_type='high_sales',
            severity='high',
            message='High sales detected',
            status='active'
        )
        
        self.alert3 = Alert.objects.create(
            title='Resolved Alert',
            alert_type='low_stock',
            severity='low',
            message='Resolved alert',
            status='resolved'
        )
    
    def test_list_alerts(self):
        """Test para listar alertas"""
        url = reverse('dashboard:alert-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_filter_alerts_by_type(self):
        """Test para filtrar alertas por tipo"""
        url = reverse('dashboard:alert-list')
        response = self.client.get(url, {'alert_type': 'low_stock'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_alerts_by_severity(self):
        """Test para filtrar alertas por severidad"""
        url = reverse('dashboard:alert-list')
        response = self.client.get(url, {'severity': 'high'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['severity'], 'high')
    
    def test_filter_active_alerts(self):
        """Test para filtrar alertas activas"""
        url = reverse('dashboard:alert-list')
        response = self.client.get(url, {'status': 'active'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        for alert in response.data['results']:
            self.assertEqual(alert['status'], 'active')
    
    def test_get_alert_detail(self):
        """Test para obtener detalle de una alerta"""
        url = reverse('dashboard:alert-detail', kwargs={'pk': self.alert1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['alert_type'], 'low_stock')
        self.assertEqual(response.data['message'], 'GPS Test stock is low')
    
    def test_acknowledge_alert(self):
        """Test para reconocer una alerta"""
        url = reverse('dashboard:alert-acknowledge', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert1.refresh_from_db()
        self.assertEqual(self.alert1.acknowledged_by, self.user)
        self.assertIsNotNone(self.alert1.acknowledged_at)
    
    def test_resolve_alert(self):
        """Test para resolver una alerta"""
        url = reverse('dashboard:alert-resolve', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert1.refresh_from_db()
        self.assertEqual(self.alert1.status, 'resolved')
        self.assertIsNotNone(self.alert1.resolved_at)
    
    def test_acknowledge_nonexistent_alert(self):
        """Test para reconocer una alerta que no existe"""
        url = reverse('dashboard:alert-acknowledge', kwargs={'pk': 99999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_resolve_nonexistent_alert(self):
        """Test para resolver una alerta que no existe"""
        url = reverse('dashboard:alert-resolve', kwargs={'pk': 99999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_alert(self):
        """Test para crear una nueva alerta"""
        url = reverse('dashboard:alert-list')
        data = {
            'title': 'System Alert',
            'alert_type': 'system_error',
            'severity': 'medium',
            'message': 'System maintenance required',
            'status': 'active'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alert.objects.count(), 4)
    
    def test_update_alert(self):
        """Test para actualizar una alerta"""
        url = reverse('dashboard:alert-detail', kwargs={'pk': self.alert1.pk})
        data = {
            'title': 'Updated GPS Alert',
            'alert_type': 'low_stock',
            'severity': 'high',
            'message': 'Updated message',
            'status': 'active'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert1.refresh_from_db()
        self.assertEqual(self.alert1.severity, 'high')
        self.assertEqual(self.alert1.message, 'Updated message')
    
    def test_delete_alert(self):
        """Test para eliminar una alerta"""
        url = reverse('dashboard:alert-detail', kwargs={'pk': self.alert1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Alert.objects.count(), 2)