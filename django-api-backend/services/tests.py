from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from entities.models import Cliente, Unidad, Proveedor
from inventory.models import GPS, SIMCard
from authentication.models import Role
from .models import TipoTrabajo, Servicio
from .serializers import ServicioFlexibleSerializer

User = get_user_model()


class ServicioFlexibleTestCase(APITestCase):
    """
    Tests para el servicio flexible que maneja diferentes tipos de trabajo
    usando el tipo 'otro' con observaciones descriptivas.
    """
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear roles
        self.rol_admin = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        
        self.rol_tecnico = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de campo'
        )
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='87654321',
            celular='987654321',
            rol=self.rol_admin,
            is_staff=True,
            is_superuser=True
        )
        
        # Crear técnico
        self.tecnico = User.objects.create_user(
            username='tecnico1',
            email='tecnico@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            dni='12345678',
            celular='987654320',
            rol=self.rol_tecnico
        )
        
        # Crear grupo de técnicos y agregar el usuario
        from django.contrib.auth.models import Group
        tecnicos_group, created = Group.objects.get_or_create(name='Tecnicos')
        self.tecnico.groups.add(tecnicos_group)
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            direccion='Dirección Test',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com'
        )
        
        # Crear unidad
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Corolla',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        # Crear tipos de trabajo
        self.tipo_instalacion = TipoTrabajo.objects.create(
            nombre='instalacion_nueva',
            descripcion='Instalación nueva de GPS'
        )
        
        self.tipo_mantenimiento = TipoTrabajo.objects.create(
            nombre='mantenimiento_preventivo',
            descripcion='Mantenimiento preventivo'
        )
        
        self.tipo_otro = TipoTrabajo.objects.create(
            nombre='otro',
            descripcion='Otros tipos de trabajo'
        )
        
        # Crear proveedor primero (requerido para GPS y SIM)
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='98765432101',
            direccion='Av. Test 123',
            contacto='Carlos Vendedor',
            celular='987654322',
            correo='proveedor@test.com'
        )
        
        # Crear GPS con todos los campos requeridos
        self.gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='123456789012345',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='F001-123',
            proveedor=self.proveedor,
            estado='no_asignado',
            proceso='en_produccion'
        )
        
        # Crear SIM Card con todos los campos requeridos
        self.sim_card = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='F001-124',
            numero_chip='987654321',
            icc='ICC123456789',
            proveedor=self.proveedor,
            estado='no_asignado',
            proceso='en_produccion'  # Changed to valid assignable process
        )
        
        # Autenticar usuario
        self.client.force_authenticate(user=self.admin_user)
        
        # URL base para servicios flexibles
        self.url_base = '/api/services/servicios-flexibles/'
    
    def test_crear_servicio_mantenimiento_sin_equipos(self):
        """Test creating a maintenance service without equipment."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_mantenimiento.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Mantenimiento preventivo sin cambio de equipos',
            'precio': '150.00',
            'observaciones': 'Revisión general del sistema GPS existente',
            'motivo_sin_equipos': 'Mantenimiento preventivo - no requiere equipos nuevos'
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Servicio.objects.count(), 1)
        
        servicio = Servicio.objects.first()
        self.assertEqual(servicio.tipo_trabajo, self.tipo_mantenimiento)
        self.assertIsNone(servicio.gps)
        self.assertIsNone(servicio.sim_card)
        self.assertIn('Revisión general', servicio.observaciones)
    
    def test_crear_servicio_instalacion_accesorio(self):
        """Test para crear servicio de instalación de accesorio usando tipo 'otro'."""
        data = {
            'fecha': '2024-01-16T14:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Instalación de cámara de seguridad adicional',
            'observaciones': 'Instalación de cámara de seguridad adicional en vehículo - Sistema independiente que no requiere GPS ni SIM Card. Incluye cableado, montaje y configuración básica.',
            'precio': 200.00,
            'requiere_gps': False,
            'requiere_sim_card': False,
            'motivo_sin_equipos': 'Instalación de accesorio independiente, no requiere GPS ni SIM'
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        servicio = Servicio.objects.first()
        self.assertEqual(servicio.tipo_trabajo, self.tipo_otro)
        self.assertIsNone(servicio.gps)
        self.assertIsNone(servicio.sim_card)
        self.assertIn('cámara de seguridad', servicio.observaciones)
    
    def test_crear_servicio_revision_tecnica(self):
        """Test para crear servicio de revisión técnica usando tipo 'otro'."""
        data = {
            'fecha': '2024-01-18T11:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Diagnóstico de fallas en el sistema de rastreo',
            'observaciones': 'Revisión técnica para diagnóstico de fallas - Análisis de conectividad, verificación de señal GPS, pruebas de transmisión de datos. Servicio de diagnóstico sin instalación de equipos.',
            'precio': 100.00,
            'requiere_gps': False,
            'requiere_sim_card': False,
            'motivo_sin_equipos': 'Servicio de diagnóstico técnico, no requiere equipos nuevos'
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        servicio = Servicio.objects.first()
        self.assertIn('diagnóstico', servicio.observaciones)
        self.assertIn('Revisión técnica', servicio.observaciones)
    
    def test_validacion_observaciones_tipo_otro(self):
        """Test para validar que el tipo 'otro' requiere observaciones descriptivas."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Servicio especial',
            'observaciones': 'Corto',  # Menos de 10 caracteres
            'precio': 150.00
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('observaciones', response.data)
    
    def test_validacion_observaciones_vacias_tipo_otro(self):
        """Test para validar que el tipo 'otro' no acepta observaciones vacías."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Servicio especial',
            'observaciones': '',  # Vacío
            'precio': 150.00
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('observaciones', response.data)
    
    def test_auto_ajuste_flags_por_keywords(self):
        """Test para verificar el auto-ajuste de flags basado en keywords en observaciones."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Servicio especial',
            'observaciones': 'Mantenimiento sin cambio de equipos - Revisión del sistema existente',
            'precio': 150.00,
            'requiere_gps': True,  # Se debería cambiar a False automáticamente
            'requiere_sim_card': True  # Se debería cambiar a False automáticamente
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        servicio = Servicio.objects.first()
        # Los flags deberían haberse ajustado automáticamente
        # El motivo_sin_equipos es un campo write_only del serializer, no del modelo
        # Verificamos que el servicio se creó correctamente sin equipos
        self.assertIsNone(servicio.gps)
        self.assertIsNone(servicio.sim_card)
    
    def test_instalacion_nueva_con_equipos(self):
        """Test para crear instalación nueva con equipos."""
        data = {
            'fecha': '2024-01-17T09:00:00Z',
            'tipo_trabajo': self.tipo_instalacion.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'gps': self.gps.id,
            'sim_card': self.sim_card.id,
            'descripcion': 'Instalación completa de sistema GPS',
            'observaciones': 'Instalación completa con GPS y SIM Card nuevos, configuración de plataforma de monitoreo.',
            'precio': 500.00,
            'requiere_gps': True,
            'requiere_sim_card': True
        }
        
        response = self.client.post(self.url_base, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        servicio = Servicio.objects.first()
        self.assertEqual(servicio.gps, self.gps)
        self.assertEqual(servicio.sim_card, self.sim_card)
    
    def test_filtro_servicios_sin_equipos(self):
        """Test para filtrar servicios sin equipos."""
        # Crear servicio sin equipos
        Servicio.objects.create(
            fecha='2024-01-15T10:00:00Z',
            tipo_trabajo=self.tipo_otro,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            descripcion='Mantenimiento sin equipos',
            observaciones='Mantenimiento sin cambio de equipos',
            precio=150.00
        )
        
        # Crear servicio con equipos
        Servicio.objects.create(
            fecha='2024-01-17T09:00:00Z',
            tipo_trabajo=self.tipo_instalacion,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            gps=self.gps,
            sim_card=self.sim_card,
            descripcion='Instalación con equipos',
            precio=500.00
        )
        
        # Filtrar servicios sin equipos
        response = self.client.get(f'{self.url_base}?sin_equipos=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Mantenimiento sin equipos', response.data['results'][0]['descripcion'])
    
    def test_endpoint_validar_requerimientos(self):
        """Test para el endpoint de validación de requerimientos."""
        url = f'{self.url_base}validar_requerimientos/'
        
        # Test con tipo 'otro'
        response = self.client.get(f'{url}?tipo_trabajo_id={self.tipo_otro.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('requerimientos', response.data)
        self.assertIn('ejemplos_observaciones', response.data['requerimientos'])
        self.assertTrue(response.data['requerimientos']['requiere_observaciones_detalladas'])
    
    def test_endpoint_estadisticas_flexibles(self):
        """Test para el endpoint de estadísticas flexibles."""
        # Crear algunos servicios de prueba
        Servicio.objects.create(
            fecha='2024-01-15T10:00:00Z',
            tipo_trabajo=self.tipo_otro,
            tecnico=self.tecnico,
            cliente=self.cliente,
            unidad=self.unidad,
            descripcion='Mantenimiento sin equipos',
            precio=150.00
        )
        
        url = f'{self.url_base}estadisticas_flexibles/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('resumen_general', response.data)
        self.assertIn('estadisticas_por_tipo', response.data)
        self.assertIn('servicios_sin_equipos_por_mes', response.data)


class ServicioFlexibleSerializerTestCase(TestCase):
    """Tests específicos para el serializer flexible."""
    
    def setUp(self):
        """Configuración inicial para los tests del serializer."""
        # Crear roles necesarios
        self.rol_admin = Role.objects.create(nombre='administrador')
        self.rol_tecnico = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de campo'
        )
        
        self.tecnico = User.objects.create_user(
            username='tecnico1',
            email='tecnico@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            dni='12345678',
            celular='987654321',
            rol=self.rol_tecnico
        )
        
        # Crear grupo de técnicos y agregar el usuario
        from django.contrib.auth.models import Group
        tecnicos_group, created = Group.objects.get_or_create(name='Tecnicos')
        self.tecnico.groups.add(tecnicos_group)
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='12345678901',
            direccion='Dirección Test',
            contacto='Juan Pérez',
            celular='987654321',
            correo='cliente@test.com'
        )
        
        self.unidad = Unidad.objects.create(
            tipo='bus',
            placa='ABC-123',
            marca='Toyota',
            modelo='Corolla',
            serie='VIN123456789',
            cliente=self.cliente
        )
        
        self.tipo_otro = TipoTrabajo.objects.create(
            nombre='otro',
            descripcion='Otros tipos de trabajo'
        )
    
    def test_serializer_keywords_detection(self):
        """Test para verificar la detección de keywords en observaciones."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Servicio especial',
            'observaciones': 'Instalación de accesorio independiente del sistema GPS principal',
            'precio': 150.00,
            'requiere_gps': True,
            'requiere_sim_card': True
        }
        
        serializer = ServicioFlexibleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Verificar que los flags se ajustaron automáticamente
        validated_data = serializer.validated_data
        self.assertFalse(validated_data.get('requiere_gps', True))
        self.assertFalse(validated_data.get('requiere_sim_card', True))
    
    def test_serializer_observaciones_minimas(self):
        """Test para verificar validación de observaciones mínimas."""
        data = {
            'fecha': '2024-01-15T10:00:00Z',
            'tipo_trabajo': self.tipo_otro.id,
            'tecnico_dni': self.tecnico.dni,
            'cliente': self.cliente.id,
            'unidad': self.unidad.id,
            'descripcion': 'Servicio especial',
            'observaciones': 'Corto',  # Menos de 10 caracteres
            'precio': 150.00
        }
        
        serializer = ServicioFlexibleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('observaciones', serializer.errors)
