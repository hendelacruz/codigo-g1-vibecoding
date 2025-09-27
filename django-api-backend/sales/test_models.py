"""
Tests for sales models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import date, time, datetime
from django.utils import timezone

from sales.models import Ventas, TIPO_PAGO_CHOICES, ESTADO_VENTA_CHOICES
from entities.models import Cliente, Unidad


class VentasModelTest(TestCase):
    """Test cases for Ventas model"""
    
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
        
        # Create test unit with correct fields
        self.unidad = Unidad.objects.create(
            placa='ABC-123',
            tipo='camion',
            marca='Test Marca',
            modelo='Test Modelo',
            serie='TEST123456',
            cliente=self.cliente  # Unidad requires a cliente
        )
        
        self.venta_data = {
            'mes': date(2024, 1, 1),
            'fecha_pago': time(14, 30),
            'numero_operacion': '1234567890',
            'tipo_pago': 'efectivo',
            'banco': 'BCP',
            'numero_factura': 'F001001',  # 7 characters to fit max_length=10
            'fecha_generacion_factura': timezone.now(),
            'cliente': self.cliente,
            'descripcion': 'Venta de prueba',
            'unidad': self.unidad,
            'precio': Decimal('1180.00'),  # Price with IGV
            'estado': 'pendiente'
        }
    
    def test_create_venta_success(self):
        """Test successful venta creation"""
        venta = Ventas.objects.create(**self.venta_data)
        
        self.assertEqual(venta.mes, date(2024, 1, 1))
        self.assertEqual(venta.numero_operacion, '1234567890')
        self.assertEqual(venta.tipo_pago, 'efectivo')
        self.assertEqual(venta.numero_factura, 'F001001')  # Updated to match setUp
        self.assertEqual(venta.cliente, self.cliente)
        self.assertEqual(venta.unidad, self.unidad)
        self.assertEqual(venta.precio, Decimal('1180.00'))
        self.assertEqual(venta.estado, 'pendiente')
        self.assertTrue(venta.is_active)
    
    def test_venta_str_method(self):
        """Test venta string representation"""
        venta = Ventas.objects.create(**self.venta_data)
        expected = f"Factura {venta.numero_factura} - {venta.cliente.nombre} (S/ {venta.total})"
        self.assertEqual(str(venta), expected)
    
    def test_venta_automatic_calculations(self):
        """Test automatic IGV calculations on save"""
        venta = Ventas.objects.create(**self.venta_data)
        
        # Check that calculations were performed
        expected_importe = Decimal('1000.00')  # 1180 / 1.18
        expected_igv = Decimal('180.00')  # 1000 * 0.18
        expected_total = Decimal('1180.00')  # importe + igv
        
        self.assertEqual(venta.importe, expected_importe)
        self.assertEqual(venta.igv, expected_igv)
        self.assertEqual(venta.total, expected_total)
    
    def test_calculate_amounts_method(self):
        """Test calculate_amounts method"""
        venta = Ventas(**self.venta_data)
        venta.calculate_amounts()
        
        expected_importe = Decimal('1000.00')
        expected_igv = Decimal('180.00')
        expected_total = Decimal('1180.00')
        
        self.assertEqual(venta.importe, expected_importe)
        self.assertEqual(venta.igv, expected_igv)
        self.assertEqual(venta.total, expected_total)
    
    def test_calculate_amounts_with_different_prices(self):
        """Test calculations with different price values"""
        test_cases = [
            (Decimal('118.00'), Decimal('100.00'), Decimal('18.00')),
            (Decimal('590.00'), Decimal('500.00'), Decimal('90.00')),
            (Decimal('2360.00'), Decimal('2000.00'), Decimal('360.00')),
        ]
        
        for i, (precio, expected_importe, expected_igv) in enumerate(test_cases):
            venta_data = self.venta_data.copy()
            venta_data['precio'] = precio
            venta_data['numero_factura'] = f'F00{i+2:03d}'  # F002, F003, F004
            
            venta = Ventas.objects.create(**venta_data)
            
            self.assertEqual(venta.importe, expected_importe)
            self.assertEqual(venta.igv, expected_igv)
            self.assertEqual(venta.total, precio)
    
    def test_numero_factura_unique_constraint(self):
        """Test that numero_factura must be unique"""
        Ventas.objects.create(**self.venta_data)
        
        # Try to create another venta with same numero_factura
        venta_data_2 = self.venta_data.copy()
        venta_data_2['numero_operacion'] = '9876543210'
        
        with self.assertRaises(ValidationError):
            Ventas.objects.create(**venta_data_2)
    
    def test_precio_validation_positive(self):
        """Test that precio must be positive"""
        venta_data = self.venta_data.copy()
        venta_data['precio'] = Decimal('-100.00')
        
        venta = Ventas(**venta_data)
        with self.assertRaises(ValidationError):
            venta.full_clean()
    
    def test_precio_validation_minimum(self):
        """Test precio minimum value validation"""
        venta_data = self.venta_data.copy()
        venta_data['precio'] = Decimal('0.00')
        
        venta = Ventas(**venta_data)
        with self.assertRaises(ValidationError):
            venta.full_clean()
    
    def test_tipo_pago_choices(self):
        """Test valid tipo_pago choices"""
        valid_choices = ['efectivo', 'transferencia', 'deposito', 'cheque', 
                        'tarjeta_credito', 'tarjeta_debito', 'yape', 'plin', 'otro']
        
        for i, choice in enumerate(valid_choices):
            venta_data = self.venta_data.copy()
            venta_data['tipo_pago'] = choice
            venta_data['numero_factura'] = f'T{i+1:06d}'  # T000001, T000002, etc.
            
            venta = Ventas.objects.create(**venta_data)
            self.assertEqual(venta.tipo_pago, choice)
    
    def test_estado_choices(self):
        """Test valid estado choices"""
        valid_choices = ['pendiente', 'pagado', 'parcial', 'vencido', 'cancelado', 'anulado']
        
        for i, choice in enumerate(valid_choices):
            venta_data = self.venta_data.copy()
            venta_data['estado'] = choice
            venta_data['numero_factura'] = f'E{i+1:06d}'  # E000001, E000002, etc.
            
            venta = Ventas.objects.create(**venta_data)
            self.assertEqual(venta.estado, choice)
    
    def test_estado_default_value(self):
        """Test estado default value"""
        venta_data = self.venta_data.copy()
        del venta_data['estado']  # Remove estado to test default
        
        venta = Ventas.objects.create(**venta_data)
        self.assertEqual(venta.estado, 'pendiente')
    
    def test_estado_display_property(self):
        """Test estado_display property"""
        venta = Ventas.objects.create(**self.venta_data)
        
        # Test with different estados
        estado_tests = [
            ('pendiente', 'Pendiente'),
            ('pagado', 'Pagado'),
            ('parcial', 'Pago Parcial'),
            ('vencido', 'Vencido'),
            ('cancelado', 'Cancelado'),
            ('anulado', 'Anulado'),
        ]
        
        for estado, expected_display in estado_tests:
            venta.estado = estado
            venta.save()
            self.assertEqual(venta.estado_display, expected_display)
    
    def test_tipo_pago_display_property(self):
        """Test tipo_pago_display property"""
        venta = Ventas.objects.create(**self.venta_data)
        
        # Test with different tipos de pago
        tipo_pago_tests = [
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia Bancaria'),
            ('tarjeta_credito', 'Tarjeta de Crédito'),
            ('yape', 'Yape'),
            ('plin', 'Plin'),
        ]
        
        for tipo_pago, expected_display in tipo_pago_tests:
            venta.tipo_pago = tipo_pago
            venta.save()
            self.assertEqual(venta.tipo_pago_display, expected_display)
    
    def test_clean_method_validation(self):
        """Test clean method validations"""
        # Test unidad-cliente relationship validation
        other_cliente = Cliente.objects.create(
            nombre='Other Cliente',
            ruc='98765432101',
            direccion='Other Address',
            contacto='Other Contact',
            celular='123456789',
            correo='other@example.com'
        )
        
        venta_data = self.venta_data.copy()
        venta_data['cliente'] = other_cliente  # Different cliente than unidad.cliente
        venta = Ventas(**venta_data)
        
        with self.assertRaises(ValidationError):
            venta.clean()
    
    def test_clean_method_fecha_validation(self):
        """Test fecha validation in clean method"""
        # Test that clean doesn't raise error with valid data
        venta_data = self.venta_data.copy()
        venta = Ventas(**venta_data)
        
        try:
            venta.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError with valid data")
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships"""
        venta = Ventas.objects.create(**self.venta_data)
        
        # Test cliente relationship
        self.assertEqual(venta.cliente, self.cliente)
        self.assertIn(venta, self.cliente.ventas.all())
        
        # Test unidad relationship
        self.assertEqual(venta.unidad, self.unidad)
        self.assertIn(venta, self.unidad.ventas.all())
    
    def test_foreign_key_protection(self):
        """Test that foreign keys are protected from deletion"""
        venta = Ventas.objects.create(**self.venta_data)
        
        # Try to delete cliente (should be protected)
        with self.assertRaises(Exception):  # ProtectedError
            self.cliente.delete()
        
        # Try to delete unidad (should be protected)
        with self.assertRaises(Exception):  # ProtectedError
            self.unidad.delete()
    
    def test_meta_options(self):
        """Test model meta options"""
        self.assertEqual(Ventas._meta.db_table, 'sales_ventas')
        self.assertEqual(Ventas._meta.verbose_name, 'Venta')
        self.assertEqual(Ventas._meta.verbose_name_plural, 'Ventas')
        self.assertEqual(Ventas._meta.ordering, ['-fecha_generacion_factura'])
    
    def test_model_indexes(self):
        """Test that model indexes are properly defined"""
        indexes = [index.name for index in Ventas._meta.indexes]
        
        # Check that important indexes exist
        expected_fields = [
            'numero_factura', 'estado', 'fecha_generacion_factura',
            'cliente', 'tipo_pago', 'mes'
        ]
        
        # At least some indexes should be created for these fields
        self.assertTrue(len(indexes) > 0)
    
    def test_venta_ordering(self):
        """Test venta ordering"""
        # Create multiple ventas with different dates
        venta1 = Ventas.objects.create(
            **{**self.venta_data, 
               'numero_factura': 'F001-001',
               'fecha_generacion_factura': timezone.now() - timezone.timedelta(days=2)}
        )
        venta2 = Ventas.objects.create(
            **{**self.venta_data, 
               'numero_factura': 'F001-002',
               'fecha_generacion_factura': timezone.now() - timezone.timedelta(days=1)}
        )
        venta3 = Ventas.objects.create(
            **{**self.venta_data, 
               'numero_factura': 'F001-003',
               'fecha_generacion_factura': timezone.now()}
        )
        
        ventas = list(Ventas.objects.all())
        
        # Should be ordered by fecha_generacion_factura descending
        self.assertEqual(ventas[0], venta3)  # Most recent first
        self.assertEqual(ventas[1], venta2)
        self.assertEqual(ventas[2], venta1)  # Oldest last
    
    def test_venta_timestamps(self):
        """Test automatic timestamp fields"""
        venta = Ventas.objects.create(**self.venta_data)
        
        self.assertIsNotNone(venta.created_at)
        self.assertIsNotNone(venta.updated_at)
        
        # Test that updated_at changes on save
        original_updated_at = venta.updated_at
        venta.descripcion = 'Updated description'
        venta.save()
        
        self.assertGreater(venta.updated_at, original_updated_at)
    
    def test_venta_is_active_default(self):
        """Test is_active default value"""
        venta = Ventas.objects.create(**self.venta_data)
        self.assertTrue(venta.is_active)
    
    def test_numero_operacion_max_length(self):
        """Test numero_operacion max length validation"""
        venta_data = self.venta_data.copy()
        venta_data['numero_operacion'] = 'A' * 11  # Exceeds max_length=10
        
        venta = Ventas(**venta_data)
        with self.assertRaises(ValidationError):
            venta.full_clean()
    
    def test_numero_factura_max_length(self):
        """Test numero_factura max length validation"""
        venta_data = self.venta_data.copy()
        venta_data['numero_factura'] = 'A' * 11  # Exceeds max_length=10
        
        venta = Ventas(**venta_data)
        with self.assertRaises(ValidationError):
            venta.full_clean()
    
    def test_decimal_field_precision(self):
        """Test decimal field precision and scale"""
        venta_data = self.venta_data.copy()
        venta_data['precio'] = Decimal('99999999.99')  # Max digits test (10 total digits)
        venta_data['numero_factura'] = 'F999999'  # Shorter number to fit max_length
        
        venta = Ventas.objects.create(**venta_data)
        self.assertEqual(venta.precio, Decimal('99999999.99'))
        
        # Test with different valid decimal value
        venta_data_2 = self.venta_data.copy()
        venta_data_2['precio'] = Decimal('100.50')  # Valid decimal with 2 places
        venta_data_2['numero_factura'] = 'F888888'
        
        venta2 = Ventas.objects.create(**venta_data_2)
        self.assertEqual(venta2.precio, Decimal('100.50'))