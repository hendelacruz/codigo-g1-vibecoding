"""
Tests para los filtros de la aplicación services.
Verifica el funcionamiento correcto de TipoTrabajoFilter y ServicioFilter.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import TipoTrabajo, Servicio, ESTADO_SERVICIO_CHOICES
from .filters import TipoTrabajoFilter, ServicioFilter
from entities.models import Cliente, Unidad, Proveedor
from authentication.models import CustomUser, Role
from inventory.models import GPS, SIMCard


class TipoTrabajoFilterTest(TestCase):
    """Tests para TipoTrabajoFilter."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear rol
        self.rol_tecnico = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de campo'
        )
        
        # Crear tipos de trabajo
        self.tipo_instalacion = TipoTrabajo.objects.create(
            nombre='instalacion_nueva',
            descripcion='Instalación de GPS nuevo'
        )
        self.tipo_mantenimiento = TipoTrabajo.objects.create(
            nombre='mantenimiento_preventivo',
            descripcion='Mantenimiento preventivo del sistema'
        )
        self.tipo_correctivo = TipoTrabajo.objects.create(
            nombre='mantenimiento_correctivo',
            descripcion='Reparación de fallas'
        )
        
        # Crear usuario técnico
        self.tecnico = CustomUser.objects.create_user(
            username='tecnico1',
            email='tecnico1@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol_tecnico
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            direccion='Av. Test 123',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com'
        )
        
        # Crear unidad
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Hiace',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear servicios para probar el filtro mas_solicitados
        for i in range(6):  # Más de 5 servicios para instalacion_nueva
            Servicio.objects.create(
                fecha=timezone.now(),
                tipo_trabajo=self.tipo_instalacion,
                tecnico=self.tecnico,
                cliente=self.cliente,
                unidad=self.unidad,
                descripcion=f'Servicio {i}',
                precio=Decimal('100.00'),
                estado_servicio='completado'
            )
        
        # Solo 2 servicios para mantenimiento_preventivo
        for i in range(2):
            Servicio.objects.create(
                fecha=timezone.now(),
                tipo_trabajo=self.tipo_mantenimiento,
                tecnico=self.tecnico,
                cliente=self.cliente,
                unidad=self.unidad,
                descripcion=f'Mantenimiento {i}',
                precio=Decimal('80.00'),
                estado_servicio='completado'
            )
    
    def test_filter_by_nombre(self):
        """Test filtro por nombre usando choices."""
        filter_data = {'nombre': 'instalacion_nueva'}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.tipo_instalacion)
    
    def test_filter_by_search(self):
        """Test filtro de búsqueda en nombre y descripción."""
        # Buscar por nombre
        filter_data = {'search': 'instalacion'}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.tipo_instalacion)
        
        # Buscar por descripción
        filter_data = {'search': 'preventivo'}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.tipo_mantenimiento)
    
    def test_filter_mas_solicitados(self):
        """Test filtro de tipos de trabajo más solicitados."""
        filter_data = {'mas_solicitados': True}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        
        # Solo instalacion_nueva debería aparecer (tiene 6 servicios > 5)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.tipo_instalacion)
    
    def test_filter_is_active(self):
        """Test filtro por estado activo."""
        # Desactivar un tipo de trabajo
        self.tipo_correctivo.is_active = False
        self.tipo_correctivo.save()
        
        filter_data = {'is_active': True}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 2)
        self.assertNotIn(self.tipo_correctivo, results)


class ServicioFilterTest(TestCase):
    """Tests para ServicioFilter."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear rol
        self.rol_tecnico = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de campo'
        )
        
        # Crear tipo de trabajo
        self.tipo_trabajo = TipoTrabajo.objects.create(
            nombre='instalacion_nueva',
            descripcion='Instalación de GPS'
        )
        
        # Crear usuario técnico
        self.tecnico = CustomUser.objects.create_user(
            username='tecnico1',
            email='tecnico1@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            dni='12345678',
            celular='+51987654321',
            rol=self.rol_tecnico
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            direccion='Av. Test 123',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com'
        )
        
        # Crear unidad
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Hiace',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='20123456789',
            direccion='Av. Proveedor 123',
            contacto='María García',
            celular='987654321'
        )
        
        # Crear GPS y SIM Card
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='F001-123',
            proveedor=self.proveedor,
            estado='disponible'
        )
        
        self.sim_card = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-124',
            numero_chip='987654321',
            icc='ICC123456789',
            proveedor=self.proveedor,
            estado='disponible',
            operadora='Claro'
        )
        
        # Crear servicios de prueba
        self.servicio_pendiente = Servicio.objects.create(
            fecha=timezone.now(),
            tipo_trabajo=self.tipo_trabajo,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            descripcion='Servicio pendiente',
            precio=Decimal('150.00'),
            estado_servicio='pendiente'
        )
        
        # Crear servicio de ayer
        yesterday = timezone.now() - timedelta(days=1)
        self.servicio_completado = Servicio.objects.create(
            fecha=yesterday.replace(hour=9, minute=0, second=0, microsecond=0),
            tipo_trabajo=self.tipo_trabajo,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            gps=self.gps,
            sim_card=self.sim_card,
            descripcion='Servicio completado con GPS',
            precio=Decimal('200.00'),
            estado_servicio='completado'
        )
        
        self.servicio_hoy = Servicio.objects.create(
            fecha=timezone.now().replace(hour=10, minute=0, second=0, microsecond=0),
            tipo_trabajo=self.tipo_trabajo,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            descripcion='Servicio de hoy',
            precio=Decimal('100.00'),
            estado_servicio='en_proceso'
        )
    
    def test_filter_by_estado_servicio(self):
        """Test filtro por estado del servicio."""
        filter_data = {'estado_servicio': 'pendiente'}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.servicio_pendiente)
    
    def test_filter_by_precio_range(self):
        """Test filtros de rango de precio."""
        # Precio mínimo
        filter_data = {'precio_min': 150}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 2)  # servicio_pendiente y servicio_completado
        
        # Precio máximo
        filter_data = {'precio_max': 150}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 2)  # servicio_pendiente y servicio_hoy
    
    def test_filter_by_fecha_range(self):
        """Test filtros de rango de fecha."""
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        # Fecha desde - debe encontrar servicios de hoy
        filter_data = {'fecha_desde': today.strftime('%Y-%m-%d')}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 2)  # servicio_pendiente y servicio_hoy
        
        # Fecha hasta - debe encontrar servicios hasta ayer (inclusive)
        filter_data = {'fecha_hasta': yesterday.strftime('%Y-%m-%d')}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)  # servicio_completado
    
    def test_filter_search(self):
        """Test filtro de búsqueda."""
        filter_data = {'search': 'GPS'}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.servicio_completado)
    
    def test_filter_servicios_pendientes(self):
        """Test filtro de servicios pendientes."""
        filter_data = {'servicios_pendientes': True}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 2)  # pendiente y en_proceso
    
    def test_filter_servicios_hoy(self):
        """Test filtro de servicios de hoy."""
        filter_data = {'servicios_hoy': True}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        # Debería incluir servicios de hoy (servicio_pendiente y servicio_hoy)
        self.assertGreaterEqual(results.count(), 1)
    
    def test_filter_con_gps(self):
        """Test filtro de servicios con GPS."""
        filter_data = {'con_gps': True}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.servicio_completado)
    
    def test_filter_periodo(self):
        """Test filtro por período."""
        filter_data = {'periodo': 'hoy'}
        filterset = ServicioFilter(data=filter_data, queryset=Servicio.objects.all())
        
        self.assertTrue(filterset.is_valid())
        results = filterset.qs
        # Debería incluir servicios de hoy
        self.assertGreaterEqual(results.count(), 1)


class FilterEdgeCasesTest(TestCase):
    """Tests para casos edge de los filtros."""
    
    def setUp(self):
        """Configurar datos mínimos."""
        self.tipo_trabajo = TipoTrabajo.objects.create(
            nombre='instalacion_nueva',
            descripcion='Test'
        )
    
    def test_empty_queryset(self):
        """Test filtros con queryset vacío."""
        filter_data = {'search': 'inexistente'}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.none())
        
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 0)
    
    def test_invalid_filter_values(self):
        """Test con valores de filtro inválidos."""
        # Valor inválido para choice field
        filter_data = {'nombre': 'tipo_inexistente'}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        # El filtro debería ser válido pero no devolver resultados
        self.assertTrue(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 0)
    
    def test_empty_search_values(self):
        """Test con valores de búsqueda vacíos."""
        filter_data = {'search': ''}
        filterset = TipoTrabajoFilter(data=filter_data, queryset=TipoTrabajo.objects.all())
        
        self.assertTrue(filterset.is_valid())
        # Con búsqueda vacía debería devolver todos los resultados
        self.assertEqual(filterset.qs.count(), TipoTrabajo.objects.count())