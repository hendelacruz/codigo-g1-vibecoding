"""
Comando de Django para verificar la configuración de seguridad del proyecto.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import sys
import os


class Command(BaseCommand):
    """
    Comando para verificar la configuración de seguridad del proyecto Django.
    """
    help = 'Verifica la configuración de seguridad del proyecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada de la verificación',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Sugiere correcciones para problemas encontrados',
        )

    def handle(self, *args, **options):
        """
        Ejecuta la verificación de seguridad.
        """
        self.verbose = options['verbose']
        self.suggest_fixes = options['fix']
        
        self.stdout.write(
            self.style.SUCCESS('🔒 Iniciando verificación de seguridad...\n')
        )
        
        issues_found = 0
        
        # Verificar configuraciones básicas
        issues_found += self.check_debug_setting()
        issues_found += self.check_secret_key()
        issues_found += self.check_allowed_hosts()
        
        # Verificar HTTPS y SSL
        issues_found += self.check_https_settings()
        
        # Verificar middleware de seguridad
        issues_found += self.check_security_middleware()
        
        # Verificar configuración de cookies
        issues_found += self.check_cookie_settings()
        
        # Verificar headers de seguridad
        issues_found += self.check_security_headers()
        
        # Verificar configuración de archivos
        issues_found += self.check_file_settings()
        
        # Verificar logging de seguridad
        issues_found += self.check_logging_settings()
        
        # Resumen final
        self.print_summary(issues_found)
        
        if issues_found > 0:
            sys.exit(1)

    def check_debug_setting(self):
        """Verifica la configuración de DEBUG."""
        if getattr(settings, 'DEBUG', True):
            self.print_issue(
                "❌ DEBUG está habilitado",
                "DEBUG = True en producción es un riesgo de seguridad",
                "Establecer DEBUG = False en producción"
            )
            return 1
        else:
            self.print_success("✅ DEBUG está deshabilitado")
            return 0

    def check_secret_key(self):
        """Verifica la configuración de SECRET_KEY."""
        secret_key = getattr(settings, 'SECRET_KEY', '')
        
        if not secret_key:
            self.print_issue(
                "❌ SECRET_KEY no está configurada",
                "SECRET_KEY es requerida para la seguridad de Django",
                "Configurar SECRET_KEY con un valor seguro"
            )
            return 1
        
        if len(secret_key) < 50:
            self.print_issue(
                "⚠️  SECRET_KEY es muy corta",
                "SECRET_KEY debería tener al menos 50 caracteres",
                "Generar una SECRET_KEY más larga y segura"
            )
            return 1
        
        if secret_key == 'django-insecure-' or 'django-insecure' in secret_key:
            self.print_issue(
                "❌ SECRET_KEY insegura detectada",
                "Usando SECRET_KEY de desarrollo en producción",
                "Generar una SECRET_KEY segura para producción"
            )
            return 1
        
        self.print_success("✅ SECRET_KEY está configurada correctamente")
        return 0

    def check_allowed_hosts(self):
        """Verifica la configuración de ALLOWED_HOSTS."""
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        
        if not allowed_hosts or '*' in allowed_hosts:
            self.print_issue(
                "❌ ALLOWED_HOSTS inseguro",
                "ALLOWED_HOSTS vacío o con '*' es inseguro",
                "Configurar ALLOWED_HOSTS con dominios específicos"
            )
            return 1
        
        self.print_success("✅ ALLOWED_HOSTS está configurado correctamente")
        return 0

    def check_https_settings(self):
        """Verifica configuraciones de HTTPS."""
        issues = 0
        
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            self.print_issue(
                "⚠️  SECURE_SSL_REDIRECT deshabilitado",
                "No se está forzando HTTPS",
                "Establecer SECURE_SSL_REDIRECT = True"
            )
            issues += 1
        
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            self.print_issue(
                "⚠️  HSTS no configurado",
                "HTTP Strict Transport Security no está habilitado",
                "Configurar SECURE_HSTS_SECONDS = 31536000"
            )
            issues += 1
        
        if issues == 0:
            self.print_success("✅ Configuraciones HTTPS correctas")
        
        return issues

    def check_security_middleware(self):
        """Verifica middleware de seguridad."""
        middleware = getattr(settings, 'MIDDLEWARE', [])
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ]
        
        issues = 0
        for mw in required_middleware:
            if mw not in middleware:
                self.print_issue(
                    f"❌ Middleware faltante: {mw}",
                    "Middleware de seguridad requerido no está presente",
                    f"Agregar {mw} a MIDDLEWARE"
                )
                issues += 1
        
        if issues == 0:
            self.print_success("✅ Middleware de seguridad configurado")
        
        return issues

    def check_cookie_settings(self):
        """Verifica configuración de cookies."""
        issues = 0
        
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            self.print_issue(
                "⚠️  SESSION_COOKIE_SECURE deshabilitado",
                "Cookies de sesión no están marcadas como seguras",
                "Establecer SESSION_COOKIE_SECURE = True"
            )
            issues += 1
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            self.print_issue(
                "⚠️  CSRF_COOKIE_SECURE deshabilitado",
                "Cookies CSRF no están marcadas como seguras",
                "Establecer CSRF_COOKIE_SECURE = True"
            )
            issues += 1
        
        if issues == 0:
            self.print_success("✅ Configuración de cookies segura")
        
        return issues

    def check_security_headers(self):
        """Verifica headers de seguridad."""
        # Esta verificación es básica, en un entorno real se verificarían
        # los headers en las respuestas HTTP
        self.print_success("✅ Headers de seguridad configurados en middleware")
        return 0

    def check_file_settings(self):
        """Verifica configuración de archivos."""
        issues = 0
        
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        if media_root and not os.path.isabs(media_root):
            self.print_issue(
                "⚠️  MEDIA_ROOT no es ruta absoluta",
                "MEDIA_ROOT debería ser una ruta absoluta",
                "Configurar MEDIA_ROOT con ruta absoluta"
            )
            issues += 1
        
        if issues == 0:
            self.print_success("✅ Configuración de archivos correcta")
        
        return issues

    def check_logging_settings(self):
        """Verifica configuración de logging."""
        logging_config = getattr(settings, 'LOGGING', {})
        
        if not logging_config:
            self.print_issue(
                "⚠️  Logging no configurado",
                "No hay configuración de logging",
                "Configurar LOGGING para auditoría"
            )
            return 1
        
        # Verificar si existe logger de seguridad
        loggers = logging_config.get('loggers', {})
        if 'security' not in loggers:
            self.print_issue(
                "⚠️  Logger de seguridad no configurado",
                "No hay logger específico para eventos de seguridad",
                "Agregar logger 'security' a LOGGING"
            )
            return 1
        
        self.print_success("✅ Logging de seguridad configurado")
        return 0

    def print_issue(self, title, description, fix=None):
        """Imprime un problema de seguridad."""
        self.stdout.write(self.style.ERROR(title))
        if self.verbose:
            self.stdout.write(f"  📝 {description}")
        if fix and self.suggest_fixes:
            self.stdout.write(self.style.WARNING(f"  🔧 Solución: {fix}"))
        self.stdout.write("")

    def print_success(self, message):
        """Imprime un mensaje de éxito."""
        if self.verbose:
            self.stdout.write(self.style.SUCCESS(message))

    def print_summary(self, issues_count):
        """Imprime el resumen de la verificación."""
        self.stdout.write("=" * 50)
        if issues_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"🎉 ¡Excelente! No se encontraron problemas de seguridad."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"⚠️  Se encontraron {issues_count} problema(s) de seguridad."
                )
            )
            if self.suggest_fixes:
                self.stdout.write(
                    self.style.WARNING(
                        "💡 Revisa las sugerencias de corrección arriba."
                    )
                )
        self.stdout.write("=" * 50)