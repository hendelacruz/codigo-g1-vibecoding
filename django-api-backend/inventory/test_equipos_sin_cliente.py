from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from entities.models import Proveedor, Cliente
from .models import GPS, SIMCard
from authentication.models import Role

User = get_user_model()


class EquiposSinClienteTestCase(APITestCase):
    """
    Test case para verificar la funcionalidad de crear equipos sin asignar a cliente.
    
    Esto es importante para el flujo de trabajo donde:
    1. Se compran equipos y se registran en inventario
    2. Posteriormente se asignan a clientes cuando se realizan servicios
    """
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear rol de administrador
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            dni='12345678',
            celular='+51987654321',
            rol=self.admin_role
        )
        
        # Crear proveedor para los equipos
        self.proveedor = Proveedor.objects.create(
            nombre='TechProvider S.A.C.',
            ruc='20123456789',
            direccion='Av. Tecnología 123, Lima',
            contacto='Juan Pérez',
            celular='987654321',
            correo='ventas@techprovider.com'
        )
        
        # Crear cliente para tests de asignación posterior
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            ruc='20987654321',
            direccion='Av. Cliente 456, Lima',
            contacto='María García',
            celular='912345678',
            correo='contacto@clientetest.com'
        )
        
        # Autenticar como administrador
        self.client.force_authenticate(user=self.admin_user)
        
        # URLs para los endpoints
        self.gps_url = reverse('inventory:gps-list')
        self.simcard_url = reverse('inventory:simcard-list')
    
    def test_crear_gps_sin_cliente(self):
        """Test para crear un dispositivo GPS sin asignar a cliente"""
        data = {
            'fecha_compra': timezone.now().isoformat(),
            'imei': '490154203237518',
            'marca': 'Teltonika',
            'modelo': 'FMB920',
            'numero_factura': 'FAC-001',
            'proveedor': self.proveedor.id,
            'precio_compra': 250.00,
            'observaciones': 'GPS comprado para stock general'
        }
        
        response = self.client.post(self.gps_url, data, format='json')
        
        # Debug: imprimir respuesta si hay error
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GPS.objects.count(), 1)
        
        gps = GPS.objects.first()
        self.assertEqual(gps.imei, '490154203237518')
        self.assertEqual(gps.marca, 'Teltonika')
        self.assertEqual(gps.modelo, 'FMB920')
        self.assertIsNone(gps.cliente)  # No debe tener cliente asignado
        self.assertEqual(gps.estado, 'no_asignado')  # Estado por defecto
        self.assertEqual(gps.proceso, 'en_produccion')  # Proceso por defecto
        self.assertTrue(gps.is_active)
        
        # Verificar que la respuesta incluye la información correcta
        self.assertIsNone(response.data['cliente'])
        self.assertIsNone(response.data['cliente_info'])
        self.assertEqual(response.data['estado'], 'no_asignado')
        self.assertEqual(response.data['estado_display'], 'No Asignado')
    
    def test_crear_simcard_sin_cliente(self):
        """Test para crear una tarjeta SIM sin asignar a cliente"""
        data = {
            'fecha_compra': timezone.now().isoformat(),
            'numero_factura': 'FAC-SIM-001',
            'numero_chip': '987654321',
            'icc': '12345678901234567890',  # ICC válido de 20 caracteres
            'proveedor': self.proveedor.id,
            'plan': 'Plan Básico 5GB',
            'precio_compra': 50.00,
            'observaciones': 'SIM Card para stock general'
        }
        
        response = self.client.post(self.simcard_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SIMCard.objects.count(), 1)
        
        simcard = SIMCard.objects.first()
        self.assertEqual(simcard.numero_chip, '987654321')
        self.assertEqual(simcard.icc, '12345678901234567890')
        self.assertEqual(simcard.plan, 'Plan Básico 5GB')
        self.assertIsNone(simcard.cliente)  # No debe tener cliente asignado
        self.assertEqual(simcard.estado, 'no_asignado')  # Estado por defecto
        self.assertEqual(simcard.proceso, 'en_produccion')  # Proceso por defecto
        self.assertTrue(simcard.is_active)
        
        # Verificar que la respuesta incluye la información correcta
        self.assertIsNone(response.data['cliente'])
        self.assertIsNone(response.data['cliente_info'])
        self.assertEqual(response.data['estado'], 'no_asignado')
        self.assertEqual(response.data['estado_display'], 'No Asignado')
    
    def test_asignar_cliente_posterior_gps(self):
        """Test para asignar un cliente a un GPS que inicialmente no tenía cliente"""
        # Crear GPS sin cliente
        gps = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='490154203237519',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor,
            precio_compra=250.00
        )
        
        self.assertIsNone(gps.cliente)
        self.assertEqual(gps.estado, 'no_asignado')
        
        # Asignar cliente usando el método del modelo
        gps.asignar_cliente(self.cliente, 'Asignación para nuevo servicio')
        
        # Verificar que se asignó correctamente
        gps.refresh_from_db()
        self.assertEqual(gps.cliente, self.cliente)
        self.assertEqual(gps.estado, 'asignado')
        
        # Verificar que se puede actualizar vía API
        update_data = {
            'cliente': self.cliente.id,
            'estado': 'asignado'
        }
        
        response = self.client.patch(
            f'{self.gps_url}{gps.id}/', 
            update_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cliente'], self.cliente.id)
        self.assertEqual(response.data['estado'], 'asignado')
    
    def test_asignar_cliente_posterior_simcard(self):
        """Test para asignar un cliente a una SIM Card que inicialmente no tenía cliente"""
        # Crear SIM Card sin cliente
        simcard = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC-SIM-001',
            numero_chip='987654321',
            icc='12345678901234567891',
            proveedor=self.proveedor,
            plan='Plan Básico 5GB',
            precio_compra=50.00
        )
        
        self.assertIsNone(simcard.cliente)
        self.assertEqual(simcard.estado, 'no_asignado')
        
        # Asignar cliente usando el método del modelo
        simcard.asignar_cliente(self.cliente, 'Asignación para nuevo servicio')
        
        # Verificar que se asignó correctamente
        simcard.refresh_from_db()
        self.assertEqual(simcard.cliente, self.cliente)
        self.assertEqual(simcard.estado, 'asignado')
        
        # Verificar que se puede actualizar vía API
        update_data = {
            'cliente': self.cliente.id,
            'estado': 'asignado'
        }
        
        response = self.client.patch(
            f'{self.simcard_url}{simcard.id}/', 
            update_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cliente'], self.cliente.id)
        self.assertEqual(response.data['estado'], 'asignado')
    
    def test_filtrar_equipos_sin_cliente(self):
        """Test para filtrar equipos que no tienen cliente asignado"""
        # Limpiar datos existentes para asegurar aislamiento del test
        GPS.objects.all().delete()
        SIMCard.objects.all().delete()
        
        # Crear GPS sin cliente
        gps_sin_cliente = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='490154203237520',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-001',
            proveedor=self.proveedor
        )
        
        # Crear GPS con cliente
        gps_con_cliente = GPS.objects.create(
            fecha_compra=timezone.now(),
            imei='490154203237521',
            marca='Teltonika',
            modelo='FMB920',
            numero_factura='FAC-002',
            proveedor=self.proveedor,
            cliente=self.cliente,
            estado='asignado'
        )
        
        # Crear SIM Card sin cliente
        sim_sin_cliente = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC-SIM-001',
            numero_chip='987654321',
            icc='12345678901234567892',
            proveedor=self.proveedor
        )
        
        # Crear SIM Card con cliente
        sim_con_cliente = SIMCard.objects.create(
            fecha_compra=timezone.now(),
            numero_factura='FAC-SIM-002',
            numero_chip='987654322',
            icc='12345678901234567893',
            proveedor=self.proveedor,
            cliente=self.cliente,
            estado='asignado'
        )
        
        # Filtrar GPS sin cliente
        response = self.client.get(f'{self.gps_url}?sin_cliente=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], gps_sin_cliente.id)
        
        # Filtrar SIM Cards sin cliente
        response = self.client.get(f'{self.simcard_url}?sin_cliente=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], sim_sin_cliente.id)
        
        # Filtrar GPS con cliente
        response = self.client.get(f'{self.gps_url}?con_cliente=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], gps_con_cliente.id)
    
    def test_validacion_campos_requeridos_sin_cliente(self):
        """Test para verificar que los campos requeridos siguen siendo validados"""
        # Test GPS sin campos requeridos
        data_gps_incompleta = {
            'marca': 'Teltonika',
            'modelo': 'FMB920'
            # Faltan: fecha_compra, imei, numero_factura, proveedor
        }
        
        response = self.client.post(self.gps_url, data_gps_incompleta, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_compra', response.data)
        self.assertIn('imei', response.data)
        self.assertIn('numero_factura', response.data)
        self.assertIn('proveedor', response.data)
        
        # Test SIM Card sin campos requeridos
        data_sim_incompleta = {
            'plan': 'Plan Básico'
            # Faltan: fecha_compra, numero_factura, numero_chip, icc, proveedor
        }
        
        response = self.client.post(self.simcard_url, data_sim_incompleta, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_compra', response.data)
        self.assertIn('numero_chip', response.data)
        self.assertIn('icc', response.data)
        self.assertIn('numero_factura', response.data)
        self.assertIn('proveedor', response.data)
    
    def test_crear_multiples_equipos_sin_cliente(self):
        """Test para crear múltiples equipos sin cliente para stock"""
        # Crear múltiples GPS con IMEIs válidos
        valid_imeis = ['490154203237518', '490154203237526', '490154203237534', '490154203237542', '490154203237559']
        gps_data = [
            {
                'fecha_compra': timezone.now().isoformat(),
                'imei': valid_imeis[i],
                'marca': 'Teltonika',
                'modelo': 'FMB920',
                'numero_factura': f'FAC-GPS-{i:03d}',
                'proveedor': self.proveedor.id,
                'precio_compra': 250.00,
                'observaciones': f'GPS #{i+1} para stock'
            }
            for i in range(5)  # 5 GPS
        ]
        
        for data in gps_data:
            response = self.client.post(self.gps_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Crear múltiples SIM Cards con ICCs válidos
        valid_iccs = ['12345678901234567890', '12345678901234567891', '12345678901234567892', '12345678901234567893', '12345678901234567894']
        sim_data = []
        for i in range(5):
            sim_data.append({
                'fecha_compra': timezone.now().isoformat(),
                'numero_factura': f'FAC-SIM-{i:03d}',
                'numero_chip': f'98765432{i}',
                'icc': valid_iccs[i],
                'proveedor': self.proveedor.id,
                'plan': 'Plan Básico 5GB',
                'estado': 'no_asignado'
            })
        
        for data in sim_data:
            response = self.client.post(self.simcard_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se crearon todos los equipos
        self.assertEqual(GPS.objects.count(), 5)
        self.assertEqual(SIMCard.objects.count(), 5)
        
        # Verificar que todos están sin cliente asignado
        gps_sin_cliente = GPS.objects.filter(cliente__isnull=True, estado='no_asignado')
        sim_sin_cliente = SIMCard.objects.filter(cliente__isnull=True, estado='no_asignado')
        
        self.assertEqual(gps_sin_cliente.count(), 5)
        self.assertEqual(sim_sin_cliente.count(), 5)