from django.apps import AppConfig


class TodoapiConfig(AppConfig):
    """
    Configuración de la aplicación principal todoapi.
    
    Esta aplicación contiene utilidades compartidas, middleware de seguridad,
    comandos de management y configuraciones centralizadas.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todoapi'
    verbose_name = 'Sistema Logístico API'
    
    def ready(self):
        """
        Método ejecutado cuando la aplicación está lista.
        Aquí se pueden registrar señales, validaciones iniciales, etc.
        """
        # Import security validators to ensure they're loaded
        try:
            from . import utils
        except ImportError:
            pass