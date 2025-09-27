"""
Configuración específica para testing.
"""

from .base import *

# Indicador de que estamos en modo testing
TESTING = True

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Desactivar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Configuración de caché para tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-sessions',
    }
}

# Configuración de logging para tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Desactivar debug para tests
DEBUG = False

# Secret key para tests
SECRET_KEY = 'test-secret-key-not-for-production'

# Configuración de email para tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Configuración de archivos estáticos para tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configuración de media para tests
MEDIA_ROOT = '/tmp/test_media'

# Configuración de REST Framework para tests
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
})

# Configuración de paginación para tests
REST_FRAMEWORK['PAGE_SIZE'] = 10

# Configuración específica para tests de búsqueda
SEARCH_CONFIG = {
    'entities.cliente': {
        'boost_fields': {
            'nombre': 2.0,
            'documento': 1.5,
            'email': 1.0,
        },
        'fuzzy_search': True,
        'min_score': 0.1,
    },
    'entities.proveedor': {
        'boost_fields': {
            'nombre': 2.0,
            'documento': 1.5,
        },
        'fuzzy_search': True,
    },
    'entities.unidad': {
        'boost_fields': {
            'placa': 3.0,
            'numero_motor': 2.0,
            'numero_chasis': 2.0,
        },
        'fuzzy_search': False,
    },
    'inventory.gps': {
        'boost_fields': {
            'imei': 3.0,
            'marca': 2.0,
            'modelo': 2.0,
        },
        'fuzzy_search': True,
    },
    'sales.venta': {
        'boost_fields': {
            'numero_factura': 3.0,
            'cliente__nombre': 2.0,
        },
        'fuzzy_search': True,
    },
    'services.servicio': {
        'boost_fields': {
            'numero_orden': 3.0,
            'cliente__nombre': 2.0,
        },
        'fuzzy_search': True,
    },
}

# Configuración de paginación por módulo para tests
PAGINATION_CONFIG = {
    'entities': 'todoapi.utils.pagination.SmallResultsSetPagination',
    'inventory': 'todoapi.utils.pagination.SmallResultsSetPagination',
    'sales': 'todoapi.utils.pagination.SmallResultsSetPagination',
    'services': 'todoapi.utils.pagination.SmallResultsSetPagination',
    'dashboard': 'todoapi.utils.pagination.DashboardPagination',
    'reports': 'todoapi.utils.pagination.LargeResultsSetPagination',
}

# Configuración de tiempo de caché reducido para tests
CACHE_TIMEOUT = {
    'search_suggestions': 60,  # 1 minuto
    'search_history': 60,      # 1 minuto
    'stats': 60,               # 1 minuto
    'trends': 60,              # 1 minuto
    'performance': 60,         # 1 minuto
}

# Desactivar throttling para tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Configuración de timezone para tests
USE_TZ = True
TIME_ZONE = 'UTC'

# Configuración de idioma para tests
LANGUAGE_CODE = 'es-co'
USE_I18N = True
USE_L10N = True

# Password hashers más rápidos para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Configuración de CORS para tests
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configuración de CSRF para tests
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Configuración de archivos de prueba
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configuración específica para tests de API
API_TEST_CONFIG = {
    'default_format': 'json',
    'authentication_required': True,
    'permission_required': True,
    'pagination_enabled': True,
    'filtering_enabled': True,
    'search_enabled': True,
    'ordering_enabled': True,
}

# Configuración de métricas para tests
METRICS_CONFIG = {
    'enable_query_logging': True,
    'enable_performance_tracking': True,
    'enable_search_analytics': True,
    'enable_cache_metrics': True,
}

# Configuración de features flags para tests
FEATURE_FLAGS = {
    'advanced_search': True,
    'business_intelligence': True,
    'adaptive_pagination': True,
    'search_suggestions': True,
    'search_history': True,
    'performance_metrics': True,
    'trends_analysis': True,
    'cache_optimization': True,
}

print("🧪 Configuración de testing cargada exitosamente")