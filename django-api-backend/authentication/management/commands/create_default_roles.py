from django.core.management.base import BaseCommand
from authentication.models import Role


class Command(BaseCommand):
    """
    Comando para crear los roles por defecto del sistema
    """
    help = 'Crea los roles por defecto del sistema'

    def handle(self, *args, **options):
        """
        Crea los roles básicos del sistema si no existen
        """
        roles_data = [
            {
                'nombre': 'ADMIN',
                'descripcion': 'Administrador del sistema con acceso completo',
                'permisos': {
                    'usuarios': ['create', 'read', 'update', 'delete'],
                    'roles': ['create', 'read', 'update', 'delete'],
                    'gps': ['create', 'read', 'update', 'delete'],
                    'reportes': ['create', 'read', 'update', 'delete'],
                    'configuracion': ['create', 'read', 'update', 'delete']
                }
            },
            {
                'nombre': 'SUPERVISOR',
                'descripcion': 'Supervisor con acceso a gestión de usuarios y reportes',
                'permisos': {
                    'usuarios': ['create', 'read', 'update'],
                    'roles': ['read'],
                    'gps': ['read', 'update'],
                    'reportes': ['create', 'read', 'update'],
                    'configuracion': ['read']
                }
            },
            {
                'nombre': 'OPERADOR',
                'descripcion': 'Operador con acceso básico al sistema',
                'permisos': {
                    'usuarios': ['read'],
                    'gps': ['read'],
                    'reportes': ['read'],
                    'configuracion': ['read']
                }
            },
            {
                'nombre': 'CONDUCTOR',
                'descripcion': 'Conductor con acceso limitado para reportar ubicación',
                'permisos': {
                    'gps': ['create', 'read'],
                    'reportes': ['read']
                }
            }
        ]

        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                nombre=role_data['nombre'],
                defaults={
                    'descripcion': role_data['descripcion'],
                    'permisos': role_data['permisos']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Rol "{role.nombre}" creado exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Rol "{role.nombre}" ya existe')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Se crearon {created_count} roles nuevos')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n📋 Todos los roles ya existían')
            )