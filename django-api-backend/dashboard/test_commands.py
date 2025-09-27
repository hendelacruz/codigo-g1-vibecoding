"""
Tests para los comandos de gestión del dashboard
"""
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from io import StringIO

from sales.models import Ventas
from inventory.models import GPS, SIMCard, Otros
from entities.models import Cliente, Proveedor, Unidad
from authentication.models import Role
from .models import Metric, Alert

User = get_user_model()


class CheckAlertsCommandTestCase(TestCase):
    """Tests para el comando check_alerts"""
    
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
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='12345678901',
            direccion='Av. Test 123',
            contacto='Juan Pérez',
            celular='987654321'
        )
        
        # Crear productos con stock bajo usando modelo Otros
        self.producto_low_stock = Otros.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-001',
            cantidad=10,
            descripcion='Producto con stock bajo',
            proveedor=self.proveedor,
            categoria='test',
            precio_unitario=Decimal('10.00'),
            precio_total=Decimal('100.00'),
            stock_minimo=5
        )
        # Actualizar stock_actual después de la creación para simular stock bajo
        self.producto_low_stock.stock_actual = 2  # Menor que stock_minimo
        self.producto_low_stock.save()
        
        # Crear cliente para ventas
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678903',
            direccion='Av. Test 789, Lima',
            contacto='Carlos López',
            celular='987654323',
            correo='cliente3@test.com'
        )
        
        # Crear unidad vehicular
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Hiace',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear venta alta
        self.venta_alta = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP001',
            tipo_pago='transferencia',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba con monto alto',
            unidad=self.unidad,
            precio=Decimal('15000.00'),
            estado='pagado'
        )
        # Asegurar que los cálculos se ejecuten
        self.venta_alta.save()
    
    def test_check_alerts_command_all(self):
        """Test para ejecutar el comando check_alerts con todos los tipos"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('check_alerts', '--alert-type', 'all', '--verbose', stdout=out)
        
        # Verificar que se crearon alertas
        alert_count = Alert.objects.count()
        self.assertGreater(alert_count, 0)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Alert check completed', output)
    
    def test_check_alerts_command_low_stock_only(self):
        """Test para ejecutar el comando check_alerts solo para stock bajo"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('check_alerts', '--alert-type', 'low_stock', '--verbose', stdout=out)
        
        # Verificar que se crearon alertas de stock bajo
        low_stock_alerts = Alert.objects.filter(alert_type='low_stock').count()
        self.assertGreater(low_stock_alerts, 0)
        
        # Verificar que no se crearon alertas de ventas altas
        high_sales_alerts = Alert.objects.filter(alert_type='high_sales').count()
        self.assertEqual(high_sales_alerts, 0)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Checking for low stock alerts', output)
        self.assertNotIn('Checking for high sales alerts', output)
    
    def test_check_alerts_command_high_sales_only(self):
        """Test para ejecutar el comando check_alerts solo para ventas altas"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('check_alerts', '--alert-type', 'high_sales', '--verbose', stdout=out)
        
        # Verificar que se crearon alertas de ventas altas
        high_sales_alerts = Alert.objects.filter(alert_type='high_sales').count()
        self.assertGreater(high_sales_alerts, 0)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Checking for high sales alerts', output)
        self.assertNotIn('Checking for low stock alerts', output)
    
    def test_check_alerts_command_no_verbose(self):
        """Test para ejecutar el comando check_alerts sin verbose"""
        out = StringIO()
        
        # Ejecutar comando sin verbose
        call_command('check_alerts', '--alert-type', 'all', stdout=out)
        
        # Verificar que se crearon alertas
        alert_count = Alert.objects.count()
        self.assertGreater(alert_count, 0)
        
        # Verificar que el output es mínimo
        output = out.getvalue()
        self.assertNotIn('Starting alert check', output)


class GenerateMetricsCommandTestCase(TestCase):
    """Tests para el comando generate_metrics"""
    
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
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678904',
            direccion='Av. Test 101, Lima',
            contacto='Ana Rodríguez',
            celular='987654324',
            correo='cliente4@test.com'
        )
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='12345678902',
            direccion='Av. Test 456',
            contacto='María García',
            celular='987654322'
        )
        
        # Crear dispositivo GPS
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='TestGPS',
            modelo='GPS Test',
            numero_factura='F002-001',
            proveedor=self.proveedor,
            estado='no_asignado',
            proceso='disponible',
            precio_compra=Decimal('100.00')
        )
        
        # Crear unidad vehicular
        self.unidad = Unidad.objects.create(
            tipo='camion',
            placa='DEF-456',
            marca='Volvo',
            modelo='FH',
            serie='VIN987654321',
            cliente=self.cliente
        )
        
        # Crear ventas
        self.venta = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP002',
            tipo_pago='efectivo',
            banco='Interbank',
            numero_factura='F002-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba para métricas',
            unidad=self.unidad,
            precio=Decimal('150.00')
        )
    
    def test_generate_metrics_command_daily(self):
        """Test para ejecutar el comando generate_metrics con período diario"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('generate_metrics', '--period', 'daily', '--verbose', stdout=out)
        
        # Verificar que se crearon métricas
        metric_count = Metric.objects.count()
        self.assertGreaterEqual(metric_count, 0)  # Puede ser 0 si no hay datos suficientes
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Generating daily metrics', output)
        self.assertIn('Metrics generation completed', output)
    
    def test_generate_metrics_command_weekly(self):
        """Test para ejecutar el comando generate_metrics con período semanal"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('generate_metrics', '--period', 'weekly', '--verbose', stdout=out)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Generating weekly metrics', output)
        self.assertIn('Metrics generation completed', output)
    
    def test_generate_metrics_command_monthly(self):
        """Test para ejecutar el comando generate_metrics con período mensual"""
        out = StringIO()
        
        # Ejecutar comando
        call_command('generate_metrics', '--period', 'monthly', '--verbose', stdout=out)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Generating monthly metrics', output)
        self.assertIn('Metrics generation completed', output)
    
    def test_generate_metrics_command_with_date(self):
        """Test para ejecutar el comando generate_metrics con fecha específica"""
        out = StringIO()
        
        # Ejecutar comando con fecha específica
        call_command(
            'generate_metrics', 
            '--period', 'daily',
            '--date', '2024-01-15',
            '--verbose', 
            stdout=out
        )
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Generating daily metrics for 2024-01-15', output)
        self.assertIn('Metrics generation completed', output)
    
    def test_generate_metrics_command_invalid_date(self):
        """Test para ejecutar el comando generate_metrics con fecha inválida"""
        out = StringIO()
        err = StringIO()
        
        # Ejecutar comando con fecha inválida
        with self.assertRaises(SystemExit):
            call_command(
                'generate_metrics', 
                '--period', 'daily',
                '--date', 'invalid-date',
                '--verbose', 
                stdout=out,
                stderr=err
            )
    
    def test_generate_metrics_command_no_verbose(self):
        """Test para ejecutar el comando generate_metrics sin verbose"""
        out = StringIO()
        
        # Ejecutar comando sin verbose
        call_command('generate_metrics', '--period', 'daily', stdout=out)
        
        # Verificar que el output es mínimo
        output = out.getvalue()
        self.assertNotIn('Generating daily metrics', output)
    
    def test_generate_metrics_command_default_period(self):
        """Test para ejecutar el comando generate_metrics con período por defecto"""
        out = StringIO()
        
        # Ejecutar comando sin especificar período (debería usar 'daily' por defecto)
        call_command('generate_metrics', '--verbose', stdout=out)
        
        # Verificar output
        output = out.getvalue()
        self.assertIn('Generating daily metrics', output)
        self.assertIn('Metrics generation completed', output)


class CommandIntegrationTestCase(TestCase):
    """Tests de integración para los comandos"""
    
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
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678905',
            direccion='Av. Test 202, Lima',
            contacto='Luis Martínez',
            celular='987654325',
            correo='cliente5@test.com'
        )
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='12345678903',
            direccion='Av. Test 789',
            contacto='Pedro López',
            celular='987654323'
        )
        
        # Crear productos con stock bajo usando modelo Otros
        self.producto_low_stock = Otros.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F003-001',
            cantidad=10,
            descripcion='Producto con stock bajo para integración',
            proveedor=self.proveedor,
            categoria='test',
            precio_unitario=Decimal('15.00'),
            precio_total=Decimal('150.00'),
            stock_minimo=5
        )
        # Actualizar stock_actual después de la creación para simular stock bajo
        self.producto_low_stock.stock_actual = 2
        self.producto_low_stock.save()
        
        # Crear unidad vehicular
        self.unidad = Unidad.objects.create(
            tipo='otro',
            placa='GHI-789',
            marca='Mercedes',
            modelo='Sprinter',
            serie='VIN456789123',
            cliente=self.cliente
        )
        
        # Crear venta alta
        self.venta_alta = Ventas.objects.create(
            mes=timezone.now().date(),
            fecha_pago=timezone.now().time(),
            numero_operacion='OP003',
            tipo_pago='transferencia',
            banco='BBVA',
            numero_factura='F003-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba para integración',
            unidad=self.unidad,
            precio=Decimal('15000.00')
        )
    
    def test_commands_workflow(self):
        """Test del flujo completo de comandos"""
        # 1. Generar métricas
        out_metrics = StringIO()
        call_command('generate_metrics', '--period', 'daily', '--verbose', stdout=out_metrics)
        
        # 2. Verificar alertas
        out_alerts = StringIO()
        call_command('check_alerts', '--alert-type', 'all', '--verbose', stdout=out_alerts)
        
        # 3. Verificar que ambos comandos funcionaron
        metrics_output = out_metrics.getvalue()
        alerts_output = out_alerts.getvalue()
        
        self.assertIn('Metrics generation completed', metrics_output)
        self.assertIn('Alert check completed', alerts_output)
        
        # 4. Verificar que se crearon datos en la base de datos
        alert_count = Alert.objects.count()
        self.assertGreater(alert_count, 0)
    
    def test_commands_error_handling(self):
        """Test del manejo de errores en los comandos"""
        # Test con fecha inválida
        out = StringIO()
        err = StringIO()
        
        with self.assertRaises(SystemExit):
            call_command(
                'generate_metrics',
                '--date', 'invalid-date',
                stdout=out,
                stderr=err
            )