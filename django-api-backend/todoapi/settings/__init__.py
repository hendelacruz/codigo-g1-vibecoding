# Settings package initialization
"""
Configuración automática de settings basada en el entorno.
Por defecto carga la configuración de desarrollo.
"""

import os

# Determinar qué configuración cargar basado en la variable de entorno
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    # Por defecto usar development
    from .development import *