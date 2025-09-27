from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import Role

User = get_user_model()


class Command(BaseCommand):
    """
    Comando para crear un usuario administrador con rol ADMIN
    """
    help = 'Crea un usuario administrador con rol ADMIN'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario')
        parser.add_argument('--email', type=str, help='Email del usuario')
        parser.add_argument('--password', type=str, help='Contraseña del usuario')
        parser.add_argument('--dni', type=str, help='DNI del usuario')

    def handle(self, *args, **options):
        """
        Crea un usuario administrador
        """
        # Valores por defecto
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@todoapi.com'
        password = options.get('password') or 'admin123'
        dni = options.get('dni') or '12345678'

        try:
            # Obtener el rol ADMIN
            admin_role = Role.objects.get(nombre='ADMIN')
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠ El usuario "{username}" ya existe')
                )
                return

            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                dni=dni,
                first_name='Administrador',
                last_name='Sistema',
                rol=admin_role,
                is_staff=True,
                is_superuser=True
            )

            self.stdout.write(
                self.style.SUCCESS(f'✓ Usuario administrador "{username}" creado exitosamente')
            )
            self.stdout.write(f'  📧 Email: {email}')
            self.stdout.write(f'  🔑 Password: {password}')
            self.stdout.write(f'  🆔 DNI: {dni}')
            self.stdout.write(f'  👤 Rol: {admin_role.nombre}')

        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Error: El rol ADMIN no existe. Ejecuta primero: python manage.py create_default_roles')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear el usuario: {str(e)}')
            )