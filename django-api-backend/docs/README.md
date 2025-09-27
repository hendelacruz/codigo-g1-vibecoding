# 📚 Documentación del Sistema de Gestión GPS

Bienvenido a la documentación completa del Sistema de Gestión GPS. Esta carpeta contiene toda la documentación técnica y de usuario necesaria para entender, instalar y usar el sistema.

## 📋 Contenido de la Documentación

### 📖 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
Documentación completa de la API REST, incluyendo:
- Guía de instalación y configuración
- Autenticación y autorización
- Descripción de todos los endpoints
- Ejemplos de uso
- Códigos de error y solución de problemas

### 🌐 Documentación Interactiva

El sistema incluye documentación automática generada con `drf-spectacular`:

#### Swagger UI
- **URL**: `http://localhost:8000/api/docs/swagger/`
- **Descripción**: Interfaz interactiva para probar la API
- **Características**:
  - Prueba endpoints directamente desde el navegador
  - Visualización de esquemas de datos
  - Ejemplos de requests y responses
  - Autenticación integrada

#### ReDoc
- **URL**: `http://localhost:8000/api/docs/redoc/`
- **Descripción**: Documentación estática elegante y fácil de leer
- **Características**:
  - Navegación por módulos
  - Búsqueda integrada
  - Ejemplos de código
  - Responsive design

#### Schema OpenAPI
- **URL**: `http://localhost:8000/api/docs/schema/`
- **Formato**: JSON
- **Uso**: Para generar clientes automáticos o integrar con otras herramientas

## 🚀 Acceso Rápido

### Para Desarrolladores
1. Lee la [documentación de la API](./API_DOCUMENTATION.md)
2. Accede a [Swagger UI](http://localhost:8000/api/docs/swagger/) para pruebas interactivas
3. Consulta los ejemplos de código en cada endpoint

### Para Usuarios Finales
1. Revisa la sección "Inicio Rápido" en [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
2. Consulta los ejemplos de uso específicos
3. Usa la documentación interactiva para entender los datos

### Para Administradores
1. Revisa la sección "Configuración Avanzada"
2. Consulta la guía de despliegue en producción
3. Revisa la sección de solución de problemas

## 🔧 Configuración de la Documentación

La documentación automática está configurada en `todoapi/settings/base.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema de Gestión GPS API',
    'DESCRIPTION': 'API REST para gestión integral de dispositivos GPS, inventario, clientes y servicios',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'TAGS': [
        {'name': 'Authentication', 'description': 'Gestión de usuarios y autenticación'},
        {'name': 'Inventory', 'description': 'Gestión de inventario (GPS, SIM, otros)'},
        {'name': 'Entities', 'description': 'Gestión de clientes, proveedores y unidades'},
        {'name': 'Services', 'description': 'Gestión de servicios técnicos'},
        {'name': 'Sales', 'description': 'Gestión de ventas y cotizaciones'},
        {'name': 'Dashboard', 'description': 'KPIs y métricas del sistema'},
        {'name': 'Exports', 'description': 'Exportación de datos'},
        {'name': 'Imports', 'description': 'Importación de datos'},
    ]
}
```

## 📊 Módulos Documentados

### ✅ Completamente Documentados
- **Authentication** - Gestión de usuarios y autenticación
- **Inventory** - Dispositivos GPS, SIM cards y otros productos
- **Entities** - Clientes, proveedores y unidades vehiculares
- **Services** - Servicios técnicos y mantenimientos
- **Sales** - Ventas y cotizaciones
- **Dashboard** - KPIs y métricas
- **Exports** - Exportación de datos
- **Imports** - Importación de datos

### 📝 Características de la Documentación

Cada endpoint incluye:
- **Summary**: Descripción breve de la funcionalidad
- **Description**: Explicación detallada del endpoint
- **Parameters**: Parámetros de consulta y filtros disponibles
- **Request Schema**: Estructura de datos para requests
- **Response Schema**: Estructura de datos para responses
- **Examples**: Ejemplos de uso prácticos
- **Error Codes**: Códigos de error posibles

## 🔄 Actualización de la Documentación

La documentación se actualiza automáticamente cuando:
1. Se modifican los serializers
2. Se añaden nuevos endpoints
3. Se cambian los esquemas de datos
4. Se actualizan las descripciones en el código

### Regenerar Documentación

```bash
# La documentación se regenera automáticamente
# No se requiere acción manual
python manage.py runserver
```

## 🆘 Soporte

Si encuentras problemas con la documentación:

1. **Verifica que el servidor esté ejecutándose**
2. **Comprueba que tengas permisos de acceso**
3. **Revisa los logs del servidor**
4. **Consulta la sección de solución de problemas**

## 📞 Contacto

Para mejoras o sugerencias sobre la documentación:
- **Email**: dev@empresa.com
- **Issues**: GitHub Issues
- **Wiki**: Documentación del proyecto