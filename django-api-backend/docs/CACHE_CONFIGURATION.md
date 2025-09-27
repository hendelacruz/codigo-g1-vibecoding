# 🗄️ Configuración de Caché y Sesiones

## 🎯 Descripción General

Este documento explica la configuración de caché y sesiones en el proyecto Django API Backend, incluyendo las diferentes opciones para desarrollo y producción.

## 🔧 Configuraciones por Entorno

### 📝 Desarrollo (development.py)

**Configuración Actual**: Caché en memoria local (LocMemCache)

```python
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
```

**Ventajas**:
- ✅ No requiere servicios externos (Redis)
- ✅ Rápido para desarrollo
- ✅ Fácil de configurar
- ✅ No requiere instalación adicional

**Desventajas**:
- ❌ Los datos se pierden al reiniciar el servidor
- ❌ No compartido entre procesos
- ❌ Limitado por memoria RAM

### 🚀 Producción (production.py)

**Configuración**: Redis Cache

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_CACHE_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'todoapi',
        'TIMEOUT': 300,
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_SESSIONS_URL', default='redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'todoapi_sessions',
        'TIMEOUT': 86400,
    }
}
```

**Ventajas**:
- ✅ Persistente entre reinicios
- ✅ Compartido entre múltiples procesos/servidores
- ✅ Alto rendimiento
- ✅ Escalable

**Desventajas**:
- ❌ Requiere Redis instalado y configurado
- ❌ Dependencia externa adicional

## 🔄 Configuración de Sesiones

### Desarrollo
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
```

### Producción
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
```

## 🛠️ Instalación de Redis (Para Producción)

### macOS (usando Homebrew)
```bash
# Instalar Redis
brew install redis

# Iniciar Redis
brew services start redis

# Verificar que funciona
redis-cli ping
# Debería responder: PONG
```

### Ubuntu/Debian
```bash
# Instalar Redis
sudo apt update
sudo apt install redis-server

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar que funciona
redis-cli ping
```

### Docker (Recomendado para desarrollo con Redis)
```bash
# Ejecutar Redis en Docker
docker run -d --name redis-todoapi -p 6379:6379 redis:7-alpine

# Verificar que funciona
docker exec redis-todoapi redis-cli ping
```

## 🔍 Solución de Problemas Comunes

### Error: "InvalidCacheBackendError: The connection 'sessions' doesn't exist"

**Causa**: Redis no está disponible pero la configuración lo requiere.

**Solución**:
1. **Para desarrollo**: Usar configuración LocMemCache (ya implementada)
2. **Para producción**: Instalar y configurar Redis

### Error: "Connection refused" con Redis

**Causa**: Redis no está ejecutándose.

**Solución**:
```bash
# Verificar estado de Redis
brew services list | grep redis

# Iniciar Redis si no está ejecutándose
brew services start redis
```

### Sesiones no persisten entre reinicios

**Causa**: Usando LocMemCache en desarrollo.

**Solución**: Normal en desarrollo. Para persistencia, usar Redis o database sessions.

## 📊 Monitoreo de Caché

### Comandos útiles para Redis
```bash
# Conectar a Redis
redis-cli

# Ver todas las claves
KEYS *

# Ver información del servidor
INFO

# Limpiar toda la caché
FLUSHALL

# Ver estadísticas de memoria
INFO memory
```

### Logs de Django
```python
# En settings, habilitar logs de caché
LOGGING = {
    'loggers': {
        'django.core.cache': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## 🔄 Alternativas de Configuración

### 1. Database Sessions (Alternativa simple)
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### 2. File-based Cache (Para desarrollo sin Redis)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache',
    }
}
```

### 3. Dummy Cache (Para testing)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

## 📝 Variables de Entorno

### Desarrollo (.env)
```bash
# No se requieren variables adicionales para LocMemCache
```

### Producción (.env)
```bash
# Redis URLs
REDIS_CACHE_URL=redis://127.0.0.1:6379/1
REDIS_SESSIONS_URL=redis://127.0.0.1:6379/2

# Para Redis con autenticación
REDIS_CACHE_URL=redis://:password@127.0.0.1:6379/1
REDIS_SESSIONS_URL=redis://:password@127.0.0.1:6379/2

# Para Redis en la nube (ejemplo: Redis Cloud)
REDIS_CACHE_URL=redis://username:password@host:port/db
```

## 🎯 Recomendaciones

### Para Desarrollo
- ✅ Usar LocMemCache (configuración actual)
- ✅ Deshabilitar rate limiting
- ✅ Usar sesiones en caché para compatibilidad con Swagger

### Para Producción
- ✅ Usar Redis para caché y sesiones
- ✅ Configurar backup de Redis
- ✅ Monitorear uso de memoria
- ✅ Configurar clustering si es necesario

### Para Testing
- ✅ Usar DummyCache para tests unitarios
- ✅ Usar LocMemCache para tests de integración

---

*Documento creado para el proyecto Sistema Logístico Django API*  
*Versión: 1.0 | Fecha: Septiembre 2025*  
*Equipo: Vibe Coding - Grupo G1*