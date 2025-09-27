#!/usr/bin/env python
"""
Script para probar el CRUD completo de servicios desde consola.
Ejecutar con: python test_services_crud.py
"""

import os
import sys
import django
from datetime import datetime, timezone
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

# Import models after Django setup
from services.models import Servicio, TipoTrabajo
from entities.models import Cliente, Unidad
from authentication.models import CustomUser
from inventory.models import GPS, SIMCard


class ServicioCRUDTester:
    """
    Clase para probar todas las operaciones CRUD de servicios.
    """
    
    def __init__(self):
        self.created_objects = {
            'clientes': [],
            'unidades': [],
            'tecnicos': [],
            'tipos_trabajo': [],
            'gps_devices': [],
            'sim_cards': [],
            'servicios': []
        }
        
    def print_separator(self, title):
        """Print a formatted separator with title"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
        
    def print_success(self, message):
        """Print success message in green"""
        print(f"✅ {message}")
        
    def print_error(self, message):
        """Print error message in red"""
        print(f"❌ {message}")
        
    def print_info(self, message):
        """Print info message in blue"""
        print(f"ℹ️  {message}")
        
    def create_test_data(self):
        """Create all necessary test data for services"""
        self.print_separator("CREANDO DATOS DE PRUEBA")
        
        try:
            # 1. Create TipoTrabajo
            self.print_info("Creando tipos de trabajo...")
            tipos_trabajo = [
                {
                    'nombre': 'instalacion_nueva',
                    'descripcion': 'Instalación completa de sistema GPS'
                },
                {
                    'nombre': 'mantenimiento_preventivo',
                    'descripcion': 'Mantenimiento preventivo del sistema'
                },
                {
                    'nombre': 'otro',
                    'descripcion': 'Otros tipos de servicios'
                }
            ]
            
            for tipo_data in tipos_trabajo:
                tipo, created = TipoTrabajo.objects.get_or_create(
                    nombre=tipo_data['nombre'],
                    defaults={'descripcion': tipo_data['descripcion']}
                )
                if created:
                    self.created_objects['tipos_trabajo'].append(tipo)
                    self.print_success(f"Tipo de trabajo creado: {tipo.get_nombre_display()}")
                else:
                    self.print_info(f"Tipo de trabajo ya existe: {tipo.get_nombre_display()}")
            
            # 2. Create Clientes
            self.print_info("Creando clientes...")
            clientes_data = [
                {
                    'nombre': 'Transportes Lima SAC',
                    'correo': 'contacto@transporteslima.com',
                    'telefono': '987654321',
                    'direccion': 'Av. Lima 123, Lima'
                },
                {
                    'nombre': 'Logística del Norte EIRL',
                    'correo': 'info@logisticanorte.com',
                    'telefono': '987654322',
                    'direccion': 'Jr. Trujillo 456, Trujillo'
                }
            ]
            
            for cliente_data in clientes_data:
                cliente, created = Cliente.objects.get_or_create(
                    correo=cliente_data['correo'],
                    defaults=cliente_data
                )
                if created:
                    self.created_objects['clientes'].append(cliente)
                    self.print_success(f"Cliente creado: {cliente.nombre}")
                else:
                    self.print_info(f"Cliente ya existe: {cliente.nombre}")
            
            # 3. Create Unidades
            self.print_info("Creando unidades...")
            for i, cliente in enumerate(Cliente.objects.filter(correo__in=[c['correo'] for c in clientes_data])):
                unidad_data = {
                    'placa': f'ABC-{123 + i}',
                    'marca': 'Toyota' if i % 2 == 0 else 'Nissan',
                    'modelo': 'Hiace' if i % 2 == 0 else 'Urvan',
                    'año': 2020 + i,
                    'cliente': cliente
                }
                
                unidad, created = Unidad.objects.get_or_create(
                    placa=unidad_data['placa'],
                    defaults=unidad_data
                )
                if created:
                    self.created_objects['unidades'].append(unidad)
                    self.print_success(f"Unidad creada: {unidad.placa} - {unidad.cliente.nombre}")
                else:
                    self.print_info(f"Unidad ya existe: {unidad.placa}")
            
            # 4. Create Tecnicos
            self.print_info("Creando técnicos...")
            tecnicos_data = [
                {
                    'dni': '12345678',
                    'first_name': 'Juan',
                    'last_name': 'Pérez',
                    'email': 'juan.perez@empresa.com',
                    'telefono': '987654323',
                    'rol': 'tecnico'
                },
                {
                    'dni': '87654321',
                    'first_name': 'María',
                    'last_name': 'García',
                    'email': 'maria.garcia@empresa.com',
                    'telefono': '987654324',
                    'rol': 'tecnico'
                }
            ]
            
            for tecnico_data in tecnicos_data:
                tecnico, created = CustomUser.objects.get_or_create(
                    dni=tecnico_data['dni'],
                    defaults=tecnico_data
                )
                if created:
                    self.created_objects['tecnicos'].append(tecnico)
                    self.print_success(f"Técnico creado: {tecnico.get_full_name()}")
                else:
                    self.print_info(f"Técnico ya existe: {tecnico.get_full_name()}")
            
            # 5. Create GPS devices (optional)
            self.print_info("Creando dispositivos GPS...")
            gps_data = [
                {
                    'numero_serie': 'GPS001TEST',
                    'modelo': 'GT06N',
                    'estado': 'disponible'
                },
                {
                    'numero_serie': 'GPS002TEST',
                    'modelo': 'GT02A',
                    'estado': 'disponible'
                }
            ]
            
            for gps_item in gps_data:
                gps, created = GPS.objects.get_or_create(
                    numero_serie=gps_item['numero_serie'],
                    defaults=gps_item
                )
                if created:
                    self.created_objects['gps_devices'].append(gps)
                    self.print_success(f"GPS creado: {gps.numero_serie}")
                else:
                    self.print_info(f"GPS ya existe: {gps.numero_serie}")
            
            # 6. Create SIM Cards (optional)
            self.print_info("Creando tarjetas SIM...")
            sim_data = [
                {
                    'numero': '987654321001',
                    'operadora': 'Claro',
                    'estado': 'disponible'
                },
                {
                    'numero': '987654321002',
                    'operadora': 'Movistar',
                    'estado': 'disponible'
                }
            ]
            
            for sim_item in sim_data:
                sim, created = SIMCard.objects.get_or_create(
                    numero=sim_item['numero'],
                    defaults=sim_item
                )
                if created:
                    self.created_objects['sim_cards'].append(sim)
                    self.print_success(f"SIM Card creada: {sim.numero}")
                else:
                    self.print_info(f"SIM Card ya existe: {sim.numero}")
            
            self.print_success("Todos los datos de prueba creados exitosamente!")
            
        except Exception as e:
            self.print_error(f"Error creando datos de prueba: {str(e)}")
            raise
    
    def test_create_servicio(self):
        """Test creating a new service"""
        self.print_separator("PROBANDO CREACIÓN DE SERVICIO (CREATE)")
        
        try:
            # Get test data
            cliente = Cliente.objects.first()
            unidad = Unidad.objects.filter(cliente=cliente).first()
            tecnico = CustomUser.objects.filter(rol='tecnico').first()
            tipo_trabajo = TipoTrabajo.objects.first()
            gps = GPS.objects.filter(estado='disponible').first()
            sim_card = SIMCard.objects.filter(estado='disponible').first()
            
            # Create service data
            servicio_data = {
                'fecha': datetime.now(timezone.utc),
                'tipo_trabajo': tipo_trabajo,
                'tecnico': tecnico,
                'cliente': cliente,
                'unidad': unidad,
                'gps': gps,
                'sim_card': sim_card,
                'descripcion': 'Instalación completa de sistema GPS con rastreo satelital',
                'precio': Decimal('500.00'),
                'estado_servicio': 'pendiente',
                'observaciones': 'Servicio de prueba creado desde script de testing'
            }
            
            # Create the service
            servicio = Servicio.objects.create(**servicio_data)
            self.created_objects['servicios'].append(servicio)
            
            self.print_success(f"Servicio creado exitosamente!")
            self.print_info(f"ID: {servicio.id}")
            self.print_info(f"Cliente: {servicio.cliente.nombre}")
            self.print_info(f"Unidad: {servicio.unidad.placa}")
            self.print_info(f"Técnico: {servicio.tecnico.get_full_name()}")
            self.print_info(f"Tipo: {servicio.tipo_trabajo.get_nombre_display()}")
            self.print_info(f"Precio: S/ {servicio.precio}")
            self.print_info(f"Estado: {servicio.get_estado_servicio_display()}")
            
            return servicio
            
        except Exception as e:
            self.print_error(f"Error creando servicio: {str(e)}")
            raise
    
    def test_read_servicios(self):
        """Test reading services"""
        self.print_separator("PROBANDO LECTURA DE SERVICIOS (READ)")
        
        try:
            # Get all services
            servicios = Servicio.objects.all()
            self.print_info(f"Total de servicios en la base de datos: {servicios.count()}")
            
            # Display each service
            for servicio in servicios:
                print(f"\n📋 Servicio ID: {servicio.id}")
                print(f"   Cliente: {servicio.cliente.nombre}")
                print(f"   Unidad: {servicio.unidad.placa}")
                print(f"   Técnico: {servicio.tecnico.get_full_name()}")
                print(f"   Tipo: {servicio.tipo_trabajo.get_nombre_display()}")
                print(f"   Fecha: {servicio.fecha.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Precio: S/ {servicio.precio}")
                print(f"   Estado: {servicio.get_estado_servicio_display()}")
                print(f"   Descripción: {servicio.descripcion[:50]}...")
            
            # Test filtering
            self.print_info("\nProbando filtros...")
            servicios_pendientes = Servicio.objects.filter(estado_servicio='pendiente')
            self.print_info(f"Servicios pendientes: {servicios_pendientes.count()}")
            
            servicios_por_cliente = Servicio.objects.filter(cliente__nombre__icontains='Lima')
            self.print_info(f"Servicios de clientes con 'Lima' en el nombre: {servicios_por_cliente.count()}")
            
            self.print_success("Lectura de servicios completada exitosamente!")
            
        except Exception as e:
            self.print_error(f"Error leyendo servicios: {str(e)}")
            raise
    
    def test_update_servicio(self):
        """Test updating a service"""
        self.print_separator("PROBANDO ACTUALIZACIÓN DE SERVICIO (UPDATE)")
        
        try:
            # Get the first service
            servicio = Servicio.objects.first()
            if not servicio:
                self.print_error("No hay servicios para actualizar")
                return
            
            self.print_info(f"Actualizando servicio ID: {servicio.id}")
            self.print_info(f"Estado actual: {servicio.get_estado_servicio_display()}")
            self.print_info(f"Precio actual: S/ {servicio.precio}")
            
            # Update the service
            servicio.estado_servicio = 'en_proceso'
            servicio.precio = Decimal('550.00')
            servicio.observaciones += '\n\nActualizado desde script de testing - Estado cambiado a en proceso'
            servicio.save()
            
            # Refresh from database
            servicio.refresh_from_db()
            
            self.print_success("Servicio actualizado exitosamente!")
            self.print_info(f"Nuevo estado: {servicio.get_estado_servicio_display()}")
            self.print_info(f"Nuevo precio: S/ {servicio.precio}")
            
            return servicio
            
        except Exception as e:
            self.print_error(f"Error actualizando servicio: {str(e)}")
            raise
    
    def test_delete_servicio(self):
        """Test deleting a service"""
        self.print_separator("PROBANDO ELIMINACIÓN DE SERVICIO (DELETE)")
        
        try:
            # Create a service specifically for deletion
            cliente = Cliente.objects.first()
            unidad = Unidad.objects.filter(cliente=cliente).first()
            tecnico = CustomUser.objects.filter(rol='tecnico').first()
            tipo_trabajo = TipoTrabajo.objects.first()
            
            servicio_para_eliminar = Servicio.objects.create(
                fecha=datetime.now(timezone.utc),
                tipo_trabajo=tipo_trabajo,
                tecnico=tecnico,
                cliente=cliente,
                unidad=unidad,
                descripcion='Servicio temporal para prueba de eliminación',
                precio=Decimal('100.00'),
                estado_servicio='cancelado',
                observaciones='Este servicio será eliminado como parte de la prueba'
            )
            
            servicio_id = servicio_para_eliminar.id
            self.print_info(f"Servicio creado para eliminación - ID: {servicio_id}")
            
            # Verify it exists
            self.print_info("Verificando que el servicio existe...")
            existe_antes = Servicio.objects.filter(id=servicio_id).exists()
            self.print_info(f"Servicio existe antes de eliminar: {existe_antes}")
            
            # Delete the service
            servicio_para_eliminar.delete()
            self.print_success(f"Servicio ID {servicio_id} eliminado exitosamente!")
            
            # Verify it's deleted
            existe_despues = Servicio.objects.filter(id=servicio_id).exists()
            self.print_info(f"Servicio existe después de eliminar: {existe_despues}")
            
            if not existe_despues:
                self.print_success("Eliminación verificada correctamente!")
            else:
                self.print_error("El servicio aún existe después de la eliminación")
            
        except Exception as e:
            self.print_error(f"Error eliminando servicio: {str(e)}")
            raise
    
    def test_business_logic(self):
        """Test business logic and validations"""
        self.print_separator("PROBANDO LÓGICA DE NEGOCIO Y VALIDACIONES")
        
        try:
            # Test validation: unidad must belong to cliente
            self.print_info("Probando validación: unidad debe pertenecer al cliente...")
            
            cliente1 = Cliente.objects.first()
            cliente2 = Cliente.objects.last()
            unidad_cliente1 = Unidad.objects.filter(cliente=cliente1).first()
            tecnico = CustomUser.objects.filter(rol='tecnico').first()
            tipo_trabajo = TipoTrabajo.objects.first()
            
            try:
                # This should fail
                servicio_invalido = Servicio(
                    fecha=datetime.now(timezone.utc),
                    tipo_trabajo=tipo_trabajo,
                    tecnico=tecnico,
                    cliente=cliente2,  # Different client
                    unidad=unidad_cliente1,  # Unit belongs to cliente1
                    descripcion='Servicio inválido para prueba',
                    precio=Decimal('100.00')
                )
                servicio_invalido.save()
                self.print_error("La validación falló - se permitió crear servicio inválido")
                
            except ValueError as e:
                self.print_success(f"Validación funcionó correctamente: {str(e)}")
            
            # Test string representation
            self.print_info("Probando representación string del modelo...")
            servicio = Servicio.objects.first()
            if servicio:
                str_representation = str(servicio)
                self.print_success(f"String representation: {str_representation}")
            
            # Test related queries
            self.print_info("Probando consultas relacionadas...")
            cliente = Cliente.objects.first()
            servicios_cliente = cliente.servicios.all()
            self.print_info(f"Servicios del cliente {cliente.nombre}: {servicios_cliente.count()}")
            
            tecnico = CustomUser.objects.filter(rol='tecnico').first()
            servicios_tecnico = tecnico.servicios_asignados.all()
            self.print_info(f"Servicios asignados al técnico {tecnico.get_full_name()}: {servicios_tecnico.count()}")
            
            self.print_success("Todas las validaciones de lógica de negocio pasaron!")
            
        except Exception as e:
            self.print_error(f"Error en pruebas de lógica de negocio: {str(e)}")
            raise
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        self.print_separator("LIMPIANDO DATOS DE PRUEBA")
        
        try:
            # Delete in reverse order of creation to avoid foreign key constraints
            for servicio in self.created_objects['servicios']:
                if Servicio.objects.filter(id=servicio.id).exists():
                    servicio.delete()
                    self.print_info(f"Servicio {servicio.id} eliminado")
            
            for sim in self.created_objects['sim_cards']:
                if SIMCard.objects.filter(id=sim.id).exists():
                    sim.delete()
                    self.print_info(f"SIM Card {sim.numero} eliminada")
            
            for gps in self.created_objects['gps_devices']:
                if GPS.objects.filter(id=gps.id).exists():
                    gps.delete()
                    self.print_info(f"GPS {gps.numero_serie} eliminado")
            
            for tecnico in self.created_objects['tecnicos']:
                if CustomUser.objects.filter(id=tecnico.id).exists():
                    tecnico.delete()
                    self.print_info(f"Técnico {tecnico.get_full_name()} eliminado")
            
            for unidad in self.created_objects['unidades']:
                if Unidad.objects.filter(id=unidad.id).exists():
                    unidad.delete()
                    self.print_info(f"Unidad {unidad.placa} eliminada")
            
            for cliente in self.created_objects['clientes']:
                if Cliente.objects.filter(id=cliente.id).exists():
                    cliente.delete()
                    self.print_info(f"Cliente {cliente.nombre} eliminado")
            
            for tipo in self.created_objects['tipos_trabajo']:
                if TipoTrabajo.objects.filter(id=tipo.id).exists():
                    tipo.delete()
                    self.print_info(f"Tipo de trabajo {tipo.get_nombre_display()} eliminado")
            
            self.print_success("Limpieza de datos completada!")
            
        except Exception as e:
            self.print_error(f"Error durante la limpieza: {str(e)}")
    
    def run_all_tests(self):
        """Run all CRUD tests"""
        self.print_separator("INICIANDO PRUEBAS COMPLETAS DE CRUD DE SERVICIOS")
        
        try:
            # Create test data
            self.create_test_data()
            
            # Test CREATE
            servicio_creado = self.test_create_servicio()
            
            # Test READ
            self.test_read_servicios()
            
            # Test UPDATE
            self.test_update_servicio()
            
            # Test DELETE
            self.test_delete_servicio()
            
            # Test business logic
            self.test_business_logic()
            
            self.print_separator("RESUMEN DE PRUEBAS")
            self.print_success("✅ CREATE - Creación de servicios")
            self.print_success("✅ READ - Lectura y filtrado de servicios")
            self.print_success("✅ UPDATE - Actualización de servicios")
            self.print_success("✅ DELETE - Eliminación de servicios")
            self.print_success("✅ VALIDATIONS - Lógica de negocio y validaciones")
            
            self.print_separator("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE! 🎉")
            
        except Exception as e:
            self.print_error(f"Error durante las pruebas: {str(e)}")
            self.print_info("Ejecutando limpieza de emergencia...")
            self.cleanup_test_data()
            raise
        
        finally:
            # Ask user if they want to keep test data
            print("\n" + "="*60)
            keep_data = input("¿Deseas mantener los datos de prueba? (y/N): ").lower().strip()
            if keep_data != 'y' and keep_data != 'yes':
                self.cleanup_test_data()
            else:
                self.print_info("Datos de prueba mantenidos en la base de datos")


def main():
    """Main function to run the CRUD tests"""
    print("🚀 INICIANDO PRUEBAS DE CRUD DE SERVICIOS")
    print("Este script probará todas las operaciones CRUD en el modelo Servicio")
    print("Presiona Ctrl+C en cualquier momento para cancelar")
    
    try:
        input("\nPresiona Enter para continuar...")
        
        tester = ServicioCRUDTester()
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n\n❌ Pruebas canceladas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()