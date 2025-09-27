"""
Tests para los servicios del dashboard
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta

from sales.models import Ventas
from inventory.models import GPS, SIMCard, Otros
from entities.models import Cliente
from authentication.models import Role
from .models import Metric, Alert
from .services import DashboardService, AlertService

User = get_user_model()


class DashboardServiceTestCase(TestCase):
    """Tests para DashboardService"""
    
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
        
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            direccion='Av. Test 123, Lima',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com'
        )
        
        # Crear proveedor para inventario
        from entities.models import Proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='20123456789',
            direccion='Av. Proveedor 123',
            contacto='Ana García',
            celular='987654322'
        )
        
        # Crear productos de inventario
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='Test GPS',
            modelo='GPS Test',
            numero_factura='F001-123',
            proveedor=self.proveedor,
            estado='no_asignado',
            proceso='disponible',
            precio_compra=Decimal('100.00')
        )
        
        self.simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-124',
            numero_chip='987654321',
            icc='89511234567890123456',
            proveedor=self.proveedor,
            operadora='Test Operadora',
            precio_compra=Decimal('50.00')
        )
        
        # Crear unidad vehicular para las ventas
        from entities.models import Unidad
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Mercedes',
            modelo='Sprinter',
            serie='WDB9066331234567',
            cliente=self.cliente
        )
        
        # Crear ventas de prueba
        self.venta1 = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP001',
            tipo_pago='transferencia',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de GPS Test',
            unidad=self.unidad,
            precio=Decimal('150.00'),
            estado='pagado'
        )
        
        self.venta2 = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP002',
            tipo_pago='efectivo',
            banco='Efectivo',
            numero_factura='F001-002',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de SIM Test',
            unidad=self.unidad,
            precio=Decimal('200.00'),
            estado='pendiente'
        )
    
    def test_get_sales_kpis(self):
        """Test para obtener KPIs de ventas"""
        kpis = DashboardService.get_sales_kpis()
        
        # Verificar que se retornan los campos esperados
        expected_fields = [
            'total_sales_count', 'total_sales_amount', 'average_sale_amount',
            'sales_by_status', 'sales_by_month', 'daily_sales_trend',
            'period_start', 'period_end'
        ]
        
        for field in expected_fields:
            self.assertIn(field, kpis)
        
        # Verificar valores específicos
        self.assertEqual(kpis['total_sales_count'], 2)
        self.assertEqual(kpis['total_sales_amount'], Decimal('350.00'))
        self.assertEqual(kpis['average_sale_amount'], Decimal('175.00'))
    
    def test_get_sales_kpis_with_period(self):
        """Test para obtener KPIs de ventas con período específico"""
        period_start = timezone.now() - timedelta(days=7)
        period_end = timezone.now()
        
        kpis = DashboardService.get_sales_kpis(period_start, period_end)
        
        self.assertIsNotNone(kpis['period_start'])
        self.assertIsNotNone(kpis['period_end'])
    
    def test_get_inventory_kpis(self):
        """Test para obtener KPIs de inventario"""
        kpis = DashboardService.get_inventory_kpis()
        
        # Verificar que se retornan las secciones esperadas
        expected_sections = [
            'gps_devices', 'sim_cards', 'other_products', 'low_stock_products'
        ]
        
        for section in expected_sections:
            self.assertIn(section, kpis)
        
        # Verificar estructura de GPS devices
        self.assertIn('total', kpis['gps_devices'])
        self.assertIn('available', kpis['gps_devices'])
        self.assertIn('damaged', kpis['gps_devices'])
        
        # Verificar estructura de SIM cards
        self.assertIn('total', kpis['sim_cards'])
        self.assertIn('available', kpis['sim_cards'])
        self.assertIn('assigned', kpis['sim_cards'])
        
        # Verificar estructura de otros productos
        self.assertIn('total', kpis['other_products'])
        self.assertIn('low_stock_count', kpis['other_products'])
        self.assertIn('total_value', kpis['other_products'])
        
        # Verificar valores específicos
        self.assertEqual(kpis['gps_devices']['total'], 1)
        self.assertEqual(kpis['sim_cards']['total'], 1)
        self.assertEqual(kpis['other_products']['total'], 0)
    
    def test_get_user_kpis(self):
        """Test para obtener KPIs de usuarios"""
        kpis = DashboardService.get_user_kpis()
        
        # Verificar que se retornan los campos esperados
        expected_fields = [
            'total_users', 'active_users', 'new_users_this_period',
            'period_start', 'period_end'
        ]
        
        for field in expected_fields:
            self.assertIn(field, kpis)
        
        # Verificar valores específicos
        self.assertEqual(kpis['total_users'], 1)
        self.assertEqual(kpis['active_users'], 1)
    
    def test_get_financial_kpis(self):
        """Test para obtener KPIs financieros"""
        kpis = DashboardService.get_financial_kpis()
        
        # Verificar que se retornan los campos esperados
        expected_fields = [
            'total_revenue', 'total_tax', 'net_revenue',
            'monthly_revenue_trend', 'period_start', 'period_end'
        ]
        
        for field in expected_fields:
            self.assertIn(field, kpis)
        
        # Verificar valores específicos
        # Total revenue = suma de precios = 150.00 + 200.00 = 350.00
        self.assertEqual(kpis['total_revenue'], Decimal('350.00'))
        # Total tax = IGV calculado automáticamente por el modelo
        # Venta 1: 150.00/1.18 * 0.18 = 22.88, Venta 2: 200.00/1.18 * 0.18 = 30.51
        # Total IGV = 22.88 + 30.51 = 53.39
        self.assertEqual(kpis['total_tax'], Decimal('53.39'))
        # Net revenue = total_revenue - total_tax = 350.00 - 53.39 = 296.61
        self.assertEqual(kpis['net_revenue'], Decimal('296.61'))
    
    def test_get_comprehensive_dashboard(self):
        """Test para obtener dashboard completo"""
        dashboard = DashboardService.get_comprehensive_dashboard()
        
        # Verificar que se retornan todas las secciones
        expected_sections = [
            'sales_kpis', 'inventory_kpis', 'user_kpis', 
            'financial_kpis', 'generated_at'
        ]
        
        for section in expected_sections:
            self.assertIn(section, dashboard)
        
        # Verificar que generated_at es una fecha válida
        self.assertIsInstance(dashboard['generated_at'], datetime)
    
    def test_save_metrics_to_db(self):
        """Test para guardar métricas en la base de datos"""
        metrics_data = {
            'sales_kpis': {'total_sales_amount': 1000, 'total_sales_count': 5},
            'inventory_kpis': {'total_products': 10, 'low_stock_count': 2}
        }
        
        saved_metrics = DashboardService.save_metrics_to_db(metrics_data, 'daily', self.user)
        
        # Verificar que se guardaron métricas
        self.assertTrue(len(saved_metrics) > 0)
        
        # Verificar que las métricas están en la base de datos
        metric_count = Metric.objects.count()
        self.assertGreater(metric_count, 0)
        
        # Verificar campos específicos de las métricas guardadas
        first_metric = saved_metrics[0]
        self.assertIsNotNone(first_metric.name)
        self.assertEqual(first_metric.period_type, 'daily')
        self.assertIsNotNone(first_metric.period_start)
        self.assertIsNotNone(first_metric.period_end)
        self.assertEqual(first_metric.created_by, self.user)


class AlertServiceTestCase(TestCase):
    """Tests para AlertService"""
    
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
        
        # Crear proveedor para inventario
        from entities.models import Proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test Alert',
            ruc='20123456790',
            direccion='Av. Proveedor 456',
            contacto='Carlos López',
            celular='987654323'
        )
        
        # Crear productos de inventario
        self.gps_low_stock = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012346',
            marca='Test GPS',
            modelo='GPS Low Stock',
            numero_factura='F001-125',
            proveedor=self.proveedor,
            precio_compra=Decimal('100.00')
        )
        
        self.simcard_normal_stock = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-126',
            numero_chip='987654322',
            icc='89511234567890123457',
            proveedor=self.proveedor,
            operadora='Test Operadora',
            precio_compra=Decimal('50.00')
        )
        
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678902',
            direccion='Av. Test 456, Lima',
            contacto='María García',
            celular='987654322',
            correo='cliente2@test.com'
        )
        
        # Crear unidad de prueba
        from entities.models import Unidad
        self.unidad = Unidad.objects.create(
            tipo='camion',
            placa='ABC-123',
            marca='Toyota',
            modelo='Hilux',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear producto Otros con stock bajo para test de alertas
        self.otros_low_stock = Otros.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-127',
            cantidad=10,
            descripcion='Producto Test Low Stock',
            proveedor=self.proveedor,
            precio_unitario=Decimal('25.00'),
            stock_minimo=10  # Mínimo mayor que actual
        )
        # Actualizar stock_actual después de la creación (el save() lo establece igual a cantidad)
        self.otros_low_stock.stock_actual = 2  # Stock bajo
        self.otros_low_stock.save()
    
    def test_check_low_stock_alerts(self):
        """Test para verificar alertas de stock bajo"""
        alerts = AlertService.check_low_stock_alerts()
        
        # Debe crear al menos una alerta para el GPS con stock bajo
        self.assertGreater(len(alerts), 0)
        
        # Verificar que la alerta se guardó en la base de datos
        alert_count = Alert.objects.filter(alert_type='low_stock').count()
        self.assertGreater(alert_count, 0)
        
        # Verificar contenido de la alerta
        alert = alerts[0]
        self.assertEqual(alert.alert_type, 'low_stock')
        self.assertEqual(alert.severity, 'high')  # Porque stock_actual (2) <= 5
        self.assertIn('Producto Test Low Stock', alert.message)
    
    def test_check_high_sales_alerts(self):
        """Test para verificar alertas de ventas altas"""
        # Crear venta que supere el umbral
        venta_alta = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP001',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-999',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba alta',
            unidad=self.unidad,
            precio=Decimal('15000.00'),  # Mayor que el umbral por defecto
            estado='pagado'
        )
        # Asegurar que los cálculos se ejecuten
        venta_alta.save()
        
        alerts = AlertService.check_high_sales_alerts(threshold=Decimal('10000.00'))
        
        # Debe crear al menos una alerta
        self.assertGreater(len(alerts), 0)
        
        # Verificar que la alerta se guardó en la base de datos
        alert_count = Alert.objects.filter(alert_type='high_sales').count()
        self.assertGreater(alert_count, 0)
        
        # Verificar contenido de la alerta
        alert = alerts[0]
        self.assertEqual(alert.alert_type, 'high_sales')
        self.assertEqual(alert.severity, 'high')
        self.assertIn('15000', alert.message)
    
    def test_get_active_alerts(self):
        """Test para obtener alertas activas"""
        # Crear una alerta
        Alert.objects.create(
            title='Test Alert',
            alert_type='low_stock',
            severity='medium',
            message='Test alert',
            status='active'
        )
        
        active_alerts = AlertService.get_active_alerts()
        
        # Debe retornar al menos una alerta activa
        self.assertGreater(len(active_alerts), 0)
        
        # Verificar que todas las alertas están activas
        for alert in active_alerts:
            self.assertEqual(alert.status, 'active')
    
    def test_acknowledge_alert(self):
        """Test para reconocer una alerta"""
        # Crear una alerta
        alert = Alert.objects.create(
            title='Test Alert',
            alert_type='low_stock',
            severity='medium',
            message='Test alert',
            status='active'
        )
        
        # Reconocer la alerta
        acknowledged_alert = AlertService.acknowledge_alert(alert.id, self.user)
        
        # Verificar que se reconoció correctamente
        self.assertIsNotNone(acknowledged_alert)
        self.assertEqual(acknowledged_alert.acknowledged_by, self.user)
        self.assertIsNotNone(acknowledged_alert.acknowledged_at)
    
    def test_resolve_alert(self):
        """Test para resolver una alerta"""
        # Crear una alerta
        alert = Alert.objects.create(
            title='Test Alert',
            alert_type='low_stock',
            severity='medium',
            message='Test alert',
            status='active'
        )
        
        # Resolver la alerta
        resolved_alert = AlertService.resolve_alert(alert.id, self.user)
        
        # Verificar que se resolvió correctamente
        self.assertIsNotNone(resolved_alert)
        self.assertEqual(resolved_alert.status, 'resolved')
        self.assertIsNotNone(resolved_alert.resolved_at)
    
    def test_acknowledge_nonexistent_alert(self):
        """Test para reconocer una alerta que no existe"""
        result = AlertService.acknowledge_alert(99999, self.user)
        self.assertIsNone(result)
    
    def test_resolve_nonexistent_alert(self):
        """Test para resolver una alerta que no existe"""
        result = AlertService.resolve_alert(99999, self.user)
        self.assertIsNone(result)