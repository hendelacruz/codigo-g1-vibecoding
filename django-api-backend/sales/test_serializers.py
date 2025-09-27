"""
Tests for sales serializers
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from decimal import Decimal
from datetime import date, time
from django.utils import timezone

from sales.serializers import (
    VentasListSerializer, VentasSerializer, VentasCreateSerializer,
    VentasReportSerializer, VentasStatsSerializer
)
from sales.models import Ventas
from entities.models import Cliente, Unidad
from authentication.models import Role

User = get_user_model()


class VentasListSerializerTest(TestCase):
    """Test cases for VentasListSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        
        # Create test role and user
        self.role = Role.objects.create(
            nombre='Test Role',
            descripcion='Test role description'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            rol=self.role
        )
        
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Create test unit
        self.unidad = Unidad.objects.create(
            placa='ABC-123',
            tipo='camion',
            marca='Test Marca',
            modelo='Test Modelo',
            serie='TEST123456',
            cliente=self.cliente
        )
        
        # Create test venta
        self.venta = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba',
            unidad=self.unidad,
            precio=Decimal('1000.00'),
            importe=Decimal('847.46'),
            igv=Decimal('152.54'),
            total=Decimal('1000.00'),
            estado='pendiente'
        )
    
    def test_serialization_success(self):
        """Test successful serialization of venta"""
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = VentasListSerializer(
            self.venta, 
            context={'request': Request(request)}
        )
        data = serializer.data
        
        # Check basic fields that are actually in VentasListSerializer
        self.assertEqual(data['id'], self.venta.id)
        self.assertEqual(data['numero_factura'], 'F001-001')
        self.assertEqual(data['tipo_pago'], 'efectivo')
        self.assertEqual(data['estado'], 'pendiente')
        self.assertEqual(data['precio'], '1000.00')  # Corregido para coincidir con setUp
        self.assertEqual(data['total'], '1000.00')   # Corregido para coincidir con setUp
        
        # Check client fields (not cliente_info, but individual fields)
        self.assertEqual(data['cliente_nombre'], 'Test Cliente')
        self.assertEqual(data['cliente_ruc'], '12345678901')
        
        # Check unit field (not unidad_info, but individual field)
        self.assertEqual(data['unidad_placa'], 'ABC-123')
        
        # Check display fields
        self.assertEqual(data['estado_display'], 'Pendiente')
        self.assertEqual(data['tipo_pago_display'], 'Efectivo')

    
    def test_serialization_with_valid_relations(self):
        """Test serialization with valid relations"""
        venta_with_relations = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='9876543210',
            tipo_pago='transferencia',
            banco='BCP',
            numero_factura='F001-002',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,  # Cliente es requerido
            descripcion='Venta con relaciones',
            unidad=self.unidad,  # Unidad es requerida
            precio=Decimal('590.00'),
            importe=Decimal('500.00'),
            igv=Decimal('90.00'),
            total=Decimal('590.00'),
            estado='pagado'
        )
        
        serializer = VentasListSerializer(venta_with_relations)
        data = serializer.data
        
        # Check that relation fields are properly populated
        self.assertEqual(data['cliente_nombre'], 'Test Cliente')
        self.assertEqual(data['cliente_ruc'], '12345678901')
        self.assertEqual(data['unidad_placa'], 'ABC-123')
        self.assertEqual(data['estado_display'], 'Pagado')
        self.assertEqual(data['tipo_pago_display'], 'Transferencia Bancaria')


class VentasSerializerTest(TestCase):
    """Test cases for VentasSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        
        # Create test role and user
        self.role = Role.objects.create(
            nombre='Test Role',
            descripcion='Test role description'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            rol=self.role
        )
        
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Create test unit
        self.unidad = Unidad.objects.create(
            placa='ABC-123',
            tipo='camion',
            marca='Test Marca',
            modelo='Test Modelo',
            serie='TEST123456',
            cliente=self.cliente
        )
        
        self.venta_data = {
            'mes': '2024-01-01',
            'fecha_pago': '14:30:00',
            'numero_operacion': '1234567890',
            'tipo_pago': 'efectivo',
            'banco': 'BCP',
            'numero_factura': 'F001-001',
            'fecha_generacion_factura': timezone.now().isoformat(),
            'cliente': self.cliente.id,
            'descripcion': 'Venta de prueba',
            'unidad': self.unidad.id,
            'precio': '1000.00',
            'importe': '847.46',
            'igv': '152.54',
            'total': '1000.00',
            'estado': 'pendiente'
        }
    
    def test_serialization_success(self):
        """Test successful serialization"""
        venta = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba',
            unidad=self.unidad,
            precio=Decimal('1000.00'),
            importe=Decimal('847.46'),
            igv=Decimal('152.54'),
            total=Decimal('1000.00'),
            estado='pendiente'
        )
        
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            venta, 
            context={'request': Request(request)}
        )
        data = serializer.data
        
        self.assertEqual(data['numero_factura'], 'F001-001')
        self.assertEqual(data['precio'], '1000.00')
        self.assertEqual(data['estado'], 'pendiente')
        self.assertIn('cliente_info', data)
        self.assertIn('unidad_info', data)
    
    def test_deserialization_success(self):
        """Test successful deserialization"""
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=self.venta_data,
            context={'request': Request(request)}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['numero_factura'], 'F001-001')
        self.assertEqual(validated_data['precio'], Decimal('1000.00'))
        self.assertEqual(validated_data['cliente'], self.cliente)
        self.assertEqual(validated_data['unidad'], self.unidad)
    
    def test_validation_numero_factura_unique(self):
        """Test numero_factura uniqueness validation"""
        # Create existing venta
        Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1111111111',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba existente',
            unidad=self.unidad,
            precio=Decimal('1000.00'),
            importe=Decimal('847.46'),
            igv=Decimal('152.54'),
            total=Decimal('1000.00')
        )
        
        # Try to create another with same numero_factura
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=self.venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('numero_factura', serializer.errors)
    
    def test_validation_precio_positive(self):
        """Test precio positive validation"""
        venta_data = self.venta_data.copy()
        venta_data['precio'] = '-100.00'
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('precio', serializer.errors)
    
    def test_validation_precio_minimum(self):
        """Test precio minimum value validation"""
        venta_data = self.venta_data.copy()
        venta_data['precio'] = '0.00'
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('precio', serializer.errors)
    
    def test_validation_fecha_generacion_future(self):
        """Test fecha_generacion_factura future date validation"""
        venta_data = self.venta_data.copy()
        future_date = timezone.now() + timezone.timedelta(days=1)
        venta_data['fecha_generacion_factura'] = future_date.isoformat()
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_generacion_factura', serializer.errors)
    
    def test_create_method(self):
        """Test create method"""
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=self.venta_data,
            context={'request': Request(request)}
        )
        
        self.assertTrue(serializer.is_valid())
        venta = serializer.save()
        
        self.assertEqual(venta.numero_factura, 'F001-001')
        self.assertEqual(venta.precio, Decimal('1000.00'))
        self.assertEqual(venta.importe, Decimal('847.46'))
        self.assertEqual(venta.igv, Decimal('152.54'))
        self.assertEqual(venta.total, Decimal('1000.00'))
    
    def test_update_method(self):
        """Test update method"""
        venta = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-002',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta original',
            unidad=self.unidad,
            precio=Decimal('1000.00'),
            importe=Decimal('847.46'),
            igv=Decimal('152.54'),
            total=Decimal('1000.00')
        )
        
        update_data = {
            'descripcion': 'Updated description',
            'precio': '2360.00',
            'estado': 'pagado'
        }
        
        request = self.factory.put('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            venta,
            data=update_data,
            partial=True,
            context={'request': Request(request)}
        )
        
        self.assertTrue(serializer.is_valid())
        updated_venta = serializer.save()
        
        self.assertEqual(updated_venta.descripcion, 'Updated description')
        self.assertEqual(updated_venta.precio, Decimal('2360.00'))
        self.assertEqual(updated_venta.estado, 'pagado')
        # Check recalculated amounts
        self.assertEqual(updated_venta.importe, Decimal('2000.00'))
        self.assertEqual(updated_venta.igv, Decimal('360.00'))
        self.assertEqual(updated_venta.total, Decimal('2360.00'))


class VentasCreateSerializerTest(TestCase):
    """Test cases for VentasCreateSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        
        # Create test role and user
        self.role = Role.objects.create(
            nombre='Test Role',
            descripcion='Test role description'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            rol=self.role
        )
        
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Create test unit
        self.unidad = Unidad.objects.create(
            placa='ABC-123',
            tipo='camion',
            marca='Test Marca',
            modelo='Test Modelo',
            serie='TEST123456',
            cliente=self.cliente
        )
        
        self.create_data = {
            'mes': '2024-01-01',
            'fecha_pago': '14:30:00',
            'numero_operacion': '1234567890',
            'tipo_pago': 'efectivo',
            'banco': 'BCP',
            'numero_factura': 'F001-001',
            'fecha_generacion_factura': timezone.now().isoformat(),
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Nueva venta',
            'precio': '1180.00',
            'estado': 'pendiente'
        }
    
    def test_create_serializer_success(self):
        """Test successful creation with minimal data"""
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasCreateSerializer(
            data=self.create_data,
            context={'request': Request(request)}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        venta = serializer.save()
        
        self.assertEqual(venta.numero_factura, 'F001-001')
        self.assertEqual(venta.cliente, self.cliente)
        self.assertEqual(venta.unidad, self.unidad)
        self.assertEqual(venta.precio, Decimal('1180.00'))
        self.assertEqual(venta.estado, 'pendiente')  # Default value
    
    def test_create_serializer_required_fields(self):
        """Test required fields validation"""
        request = self.factory.post('/')
        request.user = self.user
        
        # Test with missing required fields
        incomplete_data = {
            'numero_factura': 'F001-001'
            # Missing cliente, precio
        }
        
        serializer = VentasCreateSerializer(
            data=incomplete_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('cliente', serializer.errors)
        self.assertIn('precio', serializer.errors)


class VentasReportSerializerTest(TestCase):
    """Test cases for VentasReportSerializer"""
    
    def setUp(self):
        """Set up test data"""
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Create test unit
        self.unidad = Unidad.objects.create(
            placa='ABC-123',
            tipo='camion',
            marca='Test Marca',
            modelo='Test Modelo',
            serie='TEST123456',
            cliente=self.cliente
        )
        
        # Create test venta
        self.venta = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=self.cliente,
            descripcion='Venta de prueba',
            unidad=self.unidad,
            precio=Decimal('1180.00'),
            estado='pendiente'
        )
    
    def test_report_serialization(self):
        """Test report serialization with specific fields"""
        serializer = VentasReportSerializer(self.venta)
        data = serializer.data
        
        # Check that only report-specific fields are included
        expected_fields = {
            'id', 'numero_factura', 'fecha_generacion_factura', 'mes', 'mes_display',
            'cliente_nombre', 'cliente_ruc', 'unidad_placa', 'descripcion',
            'precio', 'importe', 'igv', 'total', 'estado', 'estado_display',
            'tipo_pago', 'tipo_pago_display', 'banco', 'numero_operacion'
        }
        
        self.assertEqual(set(data.keys()), expected_fields)
        
        # Check calculated fields
        self.assertEqual(data['cliente_nombre'], 'Test Cliente')
        self.assertEqual(data['unidad_placa'], 'ABC-123')
        self.assertEqual(data['precio'], '1180.00')
        self.assertEqual(data['importe'], '1000.00')
        self.assertEqual(data['igv'], '180.00')
        self.assertEqual(data['total'], '1180.00')


class VentasStatsSerializerTest(TestCase):
    """Test cases for VentasStatsSerializer"""
    
    def setUp(self):
        """Set up test data"""
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
        
        # Create test unidad
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Hiace',
            serie='TEST123456789',
            cliente=self.cliente
        )
        
        # Create multiple ventas for stats
        self.ventas = []
        for i in range(3):
            venta = Ventas.objects.create(
                mes=date(2024, 1, 1),
                fecha_pago=time(14, 30),
                numero_operacion=f'123456789{i}',
                tipo_pago='efectivo',
                numero_factura=f'F001-00{i+1}',
                fecha_generacion_factura=timezone.now(),
                cliente=self.cliente,
                unidad=self.unidad,
                descripcion=f'Servicio de transporte {i+1}',
                banco='BCP',
                precio=Decimal('1180.00'),
                estado='pagado' if i % 2 == 0 else 'pendiente'
            )
            self.ventas.append(venta)
    
    def test_stats_serialization(self):
        """Test stats serialization"""
        # Create aggregated stats data as the serializer expects
        stats_data = {
            'total_ventas': Decimal('3540.00'),  # 3 ventas * 1180
            'total_igv': Decimal('572.40'),      # IGV calculado
            'total_importe': Decimal('2967.60'), # Importe calculado
            'cantidad_ventas': 3,
            'promedio_venta': Decimal('1180.00'),
            'ventas_por_estado': {'pagado': 2, 'pendiente': 1},
            'ventas_por_tipo_pago': {'efectivo': 3},
            'mes': date(2024, 1, 1)
        }
        
        serializer = VentasStatsSerializer(data=stats_data)
        self.assertTrue(serializer.is_valid())
        
        # Check that stats-specific fields are included
        expected_fields = {
            'total_ventas', 'total_igv', 'total_importe', 'cantidad_ventas',
            'promedio_venta', 'ventas_por_estado', 'ventas_por_tipo_pago', 'mes'
        }
        self.assertEqual(set(serializer.validated_data.keys()), expected_fields)
    
    def test_stats_aggregation_compatibility(self):
        """Test that stats serializer works with aggregated data"""
        # Test with minimal required fields
        minimal_stats = {
            'total_ventas': Decimal('1180.00'),
            'total_igv': Decimal('190.80'),
            'total_importe': Decimal('989.20'),
            'cantidad_ventas': 1,
            'promedio_venta': Decimal('1180.00'),
            'ventas_por_estado': {'pagado': 1},
            'ventas_por_tipo_pago': {'efectivo': 1}
        }
        
        serializer = VentasStatsSerializer(data=minimal_stats)
        self.assertTrue(serializer.is_valid())
        
        # Verify required fields are present
        self.assertIn('total_ventas', serializer.validated_data)
        self.assertIn('cantidad_ventas', serializer.validated_data)
        self.assertEqual(serializer.validated_data['total_ventas'], Decimal('1180.00'))


class SerializerValidationTest(TestCase):
    """Test cases for serializer validations"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        
        # Create test role and user
        self.role = Role.objects.create(
            nombre='Test Role',
            descripcion='Test role description'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            rol=self.role
        )
        
        # Create test client
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            ruc='12345678901',
            direccion='Test Address',
            contacto='Test Contact',
            celular='987654321',
            correo='test@example.com'
        )
    
    def test_invalid_tipo_pago(self):
        """Test validation with invalid tipo_pago"""
        venta_data = {
            'numero_factura': 'F001-001',
            'cliente': self.cliente.id,
            'precio': '1180.00',
            'tipo_pago': 'invalid_payment_type'
        }
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo_pago', serializer.errors)
    
    def test_invalid_estado(self):
        """Test validation with invalid estado"""
        venta_data = {
            'numero_factura': 'F001-001',
            'cliente': self.cliente.id,
            'precio': '1180.00',
            'estado': 'invalid_status'
        }
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('estado', serializer.errors)
    
    def test_invalid_cliente_id(self):
        """Test validation with non-existent cliente"""
        venta_data = {
            'numero_factura': 'F001-001',
            'cliente': 99999,  # Non-existent ID
            'precio': '1180.00'
        }
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('cliente', serializer.errors)
    
    def test_decimal_field_validation(self):
        """Test decimal field validation"""
        venta_data = {
            'numero_factura': 'F001-001',
            'cliente': self.cliente.id,
            'precio': 'not_a_number'
        }
        
        request = self.factory.post('/')
        request.user = self.user
        
        serializer = VentasSerializer(
            data=venta_data,
            context={'request': Request(request)}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('precio', serializer.errors)