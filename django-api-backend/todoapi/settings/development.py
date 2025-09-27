"""
Configuración para entorno de desarrollo.
"""

from .base import *
from decouple import config, Csv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=Csv())

# Database for development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings for frontend access
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)  # Only for development
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = [
    'content-type',
    'x-total-count',
    'x-page-count',
    'link',
]

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
]

# Development-specific middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'todoapi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Development-specific cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'todoapi-dev-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'todoapi-dev-sessions',
        'TIMEOUT': 86400,  # 24 hours for sessions
        'OPTIONS': {
            'MAX_ENTRIES': 500,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# Development-specific rate limiting (more permissive for frontend development)
RATE_LIMIT_ENABLE = True  # Keep enabled but with higher limits
RATE_LIMIT_CACHE = 'default'

# Override rate limits for development
RATE_LIMITS = {
    'default': {'requests': 2000, 'window': 3600},    # 2000 requests per hour for development
    'auth': {'requests': 5000, 'window': 3600},       # 5000 requests per hour for authenticated users
    'strict': {'requests': 200, 'window': 60},        # 200 requests per minute for sensitive endpoints
    'login': {'requests': 100, 'window': 300},        # 100 login attempts per 5 minutes
    'register': {'requests': 50, 'window': 3600},     # 50 registrations per hour per IP
    'password_reset': {'requests': 50, 'window': 3600}, # 50 password resets per hour
    'sales_create': {'requests': 1000, 'window': 3600}, # 1000 sales creations per hour
    'exports': {'requests': 200, 'window': 3600},     # 200 exports per hour
    'inventory': {'requests': 2000, 'window': 3600},  # 2000 inventory requests per hour
    'dashboard': {'requests': 1000, 'window': 3600},  # 1000 dashboard requests per hour
}

# Celery configuration for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True