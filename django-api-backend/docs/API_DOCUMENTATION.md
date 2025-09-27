# 📚 Documentación de la API - Sistema de Gestión GPS

## 🎯 Introducción

Esta API REST proporciona un sistema completo de gestión para dispositivos GPS, inventario, clientes, proveedores y servicios. Está construida con Django REST Framework y utiliza autenticación JWT.

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- PostgreSQL (para producción) o SQLite (para desarrollo)
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd django-api-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Cargar datos iniciales**
```bash
python manage.py loaddata authentication/fixtures/roles.json
```

8. **Ejecutar servidor**
```bash
python manage.py runserver
```

## 🔐 Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para acceder a los endpoints protegidos:

### 1. Obtener Token

**POST** `/api/auth/login/`

```json
{
    "username": "tu_usuario",
    "password": "tu_contraseña"
}
```

**Respuesta:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "rol": {
            "id": 1,
            "nombre": "Administrador"
        }
    }
}
```

### 2. Usar Token en Requests

Incluir en el header de todas las peticiones:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 3. Renovar Token

**POST** `/api/auth/token/refresh/`

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 📊 Módulos Principales

### 🔧 Authentication
Gestión de usuarios, roles y autenticación.

**Endpoints principales:**
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/profile/` - Obtener perfil
- `PATCH /api/auth/profile/` - Actualizar perfil
- `GET /api/auth/users/` - Listar usuarios
- `POST /api/auth/users/` - Crear usuario

### 📦 Inventory
Gestión de dispositivos GPS, SIM cards y otros productos.

**Endpoints principales:**
- `GET /api/inventory/gps/` - Listar dispositivos GPS
- `POST /api/inventory/gps/` - Crear dispositivo GPS
- `GET /api/inventory/simcards/` - Listar SIM cards
- `GET /api/inventory/otros/` - Listar otros productos

**Filtros disponibles:**
- `estado` - Filtrar por estado (disponible, instalado, mantenimiento)
- `marca` - Filtrar por marca
- `modelo` - Filtrar por modelo
- `search` - Búsqueda en múltiples campos

### 🏢 Entities
Gestión de clientes, proveedores y unidades vehiculares.

**Endpoints principales:**
- `GET /api/entities/clientes/` - Listar clientes
- `POST /api/entities/clientes/` - Crear cliente
- `GET /api/entities/proveedores/` - Listar proveedores
- `GET /api/entities/unidades/` - Listar unidades vehiculares

### 🛠️ Services
Gestión de servicios técnicos y mantenimientos.

**Endpoints principales:**
- `GET /api/services/servicios/` - Listar servicios
- `POST /api/services/servicios/` - Crear servicio
- `GET /api/services/tipos/` - Listar tipos de servicio

### 💰 Sales
Gestión de ventas y cotizaciones.

**Endpoints principales:**
- `GET /api/sales/ventas/` - Listar ventas
- `POST /api/sales/ventas/` - Crear venta
- `GET /api/sales/cotizaciones/` - Listar cotizaciones

### 📈 Dashboard
KPIs y métricas del sistema.

**Endpoints principales:**
- `GET /api/dashboard/overview/` - Vista general del dashboard
- `GET /api/dashboard/sales-kpis/` - KPIs de ventas
- `GET /api/dashboard/inventory-kpis/` - KPIs de inventario
- `GET /api/dashboard/alerts/` - Alertas del sistema

## 🔍 Filtros y Búsquedas

### Filtros Comunes

Todos los endpoints de listado soportan:

- **Paginación**: `?page=1&page_size=20`
- **Ordenamiento**: `?ordering=-created_at`
- **Búsqueda**: `?search=término`
- **Filtros específicos**: Según el modelo

### Ejemplos de Filtros

**GPS con filtros:**
```
GET /api/inventory/gps/?estado=disponible&marca=Teltonika&search=FMB920
```

**Clientes activos:**
```
GET /api/entities/clientes/?is_active=true&search=empresa
```

**Servicios por fecha:**
```
GET /api/services/servicios/?fecha_inicio__gte=2024-01-01&estado=completado
```

## 📝 Ejemplos de Uso

### Crear un Cliente

```bash
curl -X POST http://localhost:8000/api/entities/clientes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Empresa ABC",
    "tipo_documento": "RUC",
    "numero_documento": "20123456789",
    "email": "contacto@empresaabc.com",
    "telefono": "987654321",
    "direccion": "Av. Principal 123"
  }'
```

### Crear un Dispositivo GPS

```bash
curl -X POST http://localhost:8000/api/inventory/gps/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "imei": "123456789012345",
    "marca": "Teltonika",
    "modelo": "FMB920",
    "estado": "disponible",
    "proveedor": 1
  }'
```

### Registrar un Servicio

```bash
curl -X POST http://localhost:8000/api/services/servicios/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unidad": 1,
    "tipo_servicio": 1,
    "descripcion": "Instalación de GPS",
    "fecha_programada": "2024-01-15T10:00:00Z",
    "tecnico_asignado": 2
  }'
```

## 🚨 Códigos de Estado HTTP

- **200 OK** - Operación exitosa
- **201 Created** - Recurso creado exitosamente
- **400 Bad Request** - Error en los datos enviados
- **401 Unauthorized** - Token inválido o expirado
- **403 Forbidden** - Sin permisos para la operación
- **404 Not Found** - Recurso no encontrado
- **500 Internal Server Error** - Error interno del servidor

## 📋 Estructura de Respuestas

### Respuesta Exitosa (Lista)

```json
{
    "count": 25,
    "next": "http://localhost:8000/api/inventory/gps/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "imei": "123456789012345",
            "marca": "Teltonika",
            "modelo": "FMB920",
            "estado": "disponible",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

### Respuesta de Error

```json
{
    "error": "Token inválido",
    "detail": "El token proporcionado no es válido o ha expirado"
}
```

### Errores de Validación

```json
{
    "imei": ["Este campo es requerido."],
    "email": ["Ingrese una dirección de email válida."]
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Seguridad
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutos
JWT_REFRESH_TOKEN_LIFETIME=7  # días

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Configuración de Producción

1. **Configurar PostgreSQL**
2. **Configurar servidor web (Nginx + Gunicorn)**
3. **Configurar SSL/TLS**
4. **Configurar variables de entorno de producción**
5. **Ejecutar collectstatic**

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test inventory.tests
python manage.py test authentication.tests
```

### Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📚 Documentación Interactiva

### Swagger UI
Accede a la documentación interactiva en:
- **Swagger**: `http://localhost:8000/api/docs/swagger/`
- **ReDoc**: `http://localhost:8000/api/docs/redoc/`

### Schema OpenAPI
- **JSON**: `http://localhost:8000/api/docs/schema/`

## 🆘 Solución de Problemas

### Problemas Comunes

1. **Token expirado**
   - Usar el refresh token para obtener uno nuevo
   - Verificar la configuración de JWT_ACCESS_TOKEN_LIFETIME

2. **Error de CORS**
   - Verificar CORS_ALLOWED_ORIGINS en settings
   - Asegurar que el frontend esté en la lista

3. **Error de base de datos**
   - Verificar conexión a la base de datos
   - Ejecutar migraciones pendientes

4. **Error 403 Forbidden**
   - Verificar permisos del usuario
   - Verificar que el token sea válido

### Logs

Los logs se encuentran en:
- Desarrollo: Consola
- Producción: `/var/log/django/`

## 📞 Soporte

Para soporte técnico:
- **Email**: soporte@empresa.com
- **Documentación**: Esta guía
- **Issues**: GitHub Issues

## 🔄 Versionado

La API utiliza versionado semántico:
- **v1.0.0** - Versión inicial
- **v1.1.0** - Nuevas funcionalidades
- **v1.0.1** - Correcciones de bugs

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.