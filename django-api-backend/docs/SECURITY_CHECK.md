# Comando de Verificación de Seguridad

## Descripción

El comando `check_security` es una herramienta personalizada que analiza la configuración de seguridad de la aplicación Django y proporciona recomendaciones específicas para mejorar la postura de seguridad.

## Uso

```bash
python manage.py check_security [--verbose]
```

### Opciones

- `--verbose`: Muestra información detallada sobre cada verificación

## Verificaciones Realizadas

### 1. Configuración DEBUG
- ✅ **Correcto**: `DEBUG = False` en producción
- ❌ **Problema**: `DEBUG = True` en producción

### 2. SECRET_KEY
- ✅ **Correcto**: SECRET_KEY tiene al menos 50 caracteres
- ⚠️ **Advertencia**: SECRET_KEY es muy corta

### 3. ALLOWED_HOSTS
- ✅ **Correcto**: ALLOWED_HOSTS está configurado apropiadamente
- ❌ **Problema**: ALLOWED_HOSTS permite cualquier host

### 4. HTTPS y SSL
- ✅ **Correcto**: `SECURE_SSL_REDIRECT = True`
- ⚠️ **Advertencia**: HTTPS no está forzado

### 5. HTTP Strict Transport Security (HSTS)
- ✅ **Correcto**: HSTS configurado con valores apropiados
- ⚠️ **Advertencia**: HSTS no está habilitado

### 6. Middleware de Seguridad
- ✅ **Correcto**: Middleware de seguridad personalizado está configurado
- ❌ **Problema**: Falta middleware de seguridad

### 7. Cookies Seguras
- ✅ **Correcto**: `SESSION_COOKIE_SECURE = True`
- ⚠️ **Advertencia**: Cookies de sesión no están marcadas como seguras

### 8. Cookies CSRF
- ✅ **Correcto**: `CSRF_COOKIE_SECURE = True`
- ⚠️ **Advertencia**: Cookies CSRF no están marcadas como seguras

### 9. Headers de Seguridad
- ✅ **Correcto**: Headers de seguridad configurados
- ❌ **Problema**: Headers de seguridad faltantes

### 10. Configuración de Archivos
- ✅ **Correcto**: Configuración de archivos es segura
- ⚠️ **Advertencia**: Configuración de archivos puede mejorarse

### 11. Logger de Seguridad
- ✅ **Correcto**: Logger de seguridad configurado
- ⚠️ **Advertencia**: No hay logger específico para eventos de seguridad

## Configuraciones por Entorno

### Desarrollo
En desarrollo, es normal tener algunas advertencias:
- `DEBUG = True` (necesario para desarrollo)
- `SECURE_SSL_REDIRECT = False` (no se usa HTTPS localmente)
- `SESSION_COOKIE_SECURE = False` (no se usa HTTPS localmente)
- `CSRF_COOKIE_SECURE = False` (no se usa HTTPS localmente)

### Producción
En producción, todas las verificaciones deberían pasar:
- `DEBUG = False`
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- HSTS configurado apropiadamente

## Ejemplo de Salida

```bash
🔒 Iniciando verificación de seguridad...

✅ SECRET_KEY está configurada correctamente
✅ ALLOWED_HOSTS está configurado correctamente
⚠️  SECURE_SSL_REDIRECT deshabilitado
  📝 No se está forzando HTTPS

✅ Middleware de seguridad configurado
✅ Headers de seguridad configurados en middleware
✅ Configuración de archivos correcta

==================================================
⚠️  Se encontraron 3 problema(s) de seguridad.
==================================================
```

## Implementación

El comando está implementado en:
- `todoapi/management/commands/check_security.py`

### Características Técnicas

- **Herencia**: Extiende `BaseCommand` de Django
- **Validaciones**: Utiliza las configuraciones de Django para verificar seguridad
- **Salida**: Formato colorizado con emojis para mejor legibilidad
- **Logging**: Integrado con el sistema de logging de Django

### Métodos Principales

- `handle()`: Punto de entrada principal del comando
- `check_debug_setting()`: Verifica configuración DEBUG
- `check_secret_key()`: Valida la SECRET_KEY
- `check_allowed_hosts()`: Verifica ALLOWED_HOSTS
- `check_ssl_settings()`: Valida configuraciones SSL/HTTPS
- `check_hsts_settings()`: Verifica HSTS
- `check_middleware()`: Valida middleware de seguridad
- `check_cookie_settings()`: Verifica configuraciones de cookies
- `check_security_headers()`: Valida headers de seguridad
- `check_file_settings()`: Verifica configuraciones de archivos
- `check_logging()`: Valida configuración de logging

## Mejores Prácticas

1. **Ejecutar regularmente**: Incluir en CI/CD pipeline
2. **Revisar antes de deploy**: Ejecutar antes de cada despliegue a producción
3. **Documentar excepciones**: Si alguna verificación no aplica, documentar por qué
4. **Actualizar regularmente**: Mantener las verificaciones actualizadas con nuevas amenazas

## Integración con CI/CD

```yaml
# Ejemplo para GitHub Actions
- name: Security Check
  run: python manage.py check_security
  env:
    DJANGO_SETTINGS_MODULE: todoapi.settings.production
```

## Extensión

Para agregar nuevas verificaciones:

1. Crear método `check_nueva_verificacion()`
2. Agregar llamada en `handle()`
3. Documentar la nueva verificación en este archivo