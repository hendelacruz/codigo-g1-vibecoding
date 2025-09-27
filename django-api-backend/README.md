# 🚀 Sistema Logístico Django API

API RESTful robusta para un sistema logístico integral que gestiona operaciones de compras, ventas, inventario, clientes, unidades vehiculares y servicios técnicos con autenticación JWT y control de roles granulares.

## 📋 Características Principales

- **Autenticación JWT** con roles granulares
- **API RESTful** completa con Django REST Framework
- **Gestión de Inventario** (GPS, SIM Cards, Otros productos)
- **Gestión de Entidades** (Clientes, Proveedores, Unidades Vehiculares)
- **Sistema de Ventas** y facturación
- **Servicios Técnicos** y mantenimiento
- **Exportación de datos** (Excel, PDF)
- **Documentación automática** con Swagger/OpenAPI
- **Configuración modular** por entornos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.0.1, Django REST Framework 3.15.1
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Autenticación**: JWT con djangorestframework-simplejwt
- **Documentación**: drf-spectacular (Swagger/OpenAPI)
- **Tareas Asíncronas**: Celery + Redis
- **Exportación**: openpyxl, pandas, reportlab, weasyprint

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- pip
- virtualenv

### Configuración del Entorno

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd django-api-backend
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
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

7. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

## 📁 Estructura del Proyecto

```
django-api-backend/
├── venv/                          # Entorno virtual
├── todoapi/                       # Proyecto principal
│   ├── settings/                  # Configuraciones modulares
│   │   ├── __init__.py
│   │   ├── base.py               # Configuración base
│   │   ├── development.py        # Configuración desarrollo
│   │   └── production.py         # Configuración producción
│   ├── authentication/           # App de autenticación
│   ├── inventory/                # App de inventario
│   ├── entities/                 # App de entidades
│   ├── services/                 # App de servicios
│   ├── sales/                    # App de ventas
│   ├── exports/                  # App de exportaciones
│   ├── static/                   # Archivos estáticos
│   ├── media/                    # Archivos multimedia
│   └── templates/                # Plantillas
├── requirements.txt              # Dependencias
├── .env.example                  # Variables de entorno ejemplo
├── .gitignore                    # Exclusiones de Git
└── README.md                     # Documentación
```

## 🔧 Configuración por Entornos

### Desarrollo
```bash
export DJANGO_SETTINGS_MODULE=todoapi.settings.development
python manage.py runserver
```

### Producción
```bash
export DJANGO_SETTINGS_MODULE=todoapi.settings.production
python manage.py runserver
```

## 📚 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`
- **Schema JSON**: `http://localhost:8000/api/schema/`

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test authentication

# Ejecutar tests con coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Apps del Proyecto

### 🔐 Authentication
- Gestión de usuarios personalizados
- Autenticación JWT
- Sistema de roles y permisos

### 📦 Inventory
- Gestión de dispositivos GPS
- Gestión de tarjetas SIM
- Gestión de otros productos

### 🏢 Entities
- Gestión de clientes
- Gestión de proveedores
- Gestión de unidades vehiculares

### 🔧 Services
- Servicios técnicos
- Mantenimiento
- Historial de servicios

### 💰 Sales
- Gestión de ventas
- Facturación
- Reportes de ventas

### 📊 Exports
- Exportación a Excel
- Generación de PDFs
- Reportes personalizados

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo de Desarrollo

- **Desarrollador Principal**: [Tu Nombre]
- **Mentor**: Senior Django Developer

## 📞 Soporte

Para soporte y preguntas, contacta a [tu-email@ejemplo.com]