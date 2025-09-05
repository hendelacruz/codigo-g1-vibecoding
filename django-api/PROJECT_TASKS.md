# ✅ TODO-App API - Plan de Tareas por Fases

## 📋 Checklist Completo del Proyecto

Este documento contiene todas las tareas necesarias para desarrollar la TODO-App API, organizadas por fases y con formato de checklist para facilitar el seguimiento del progreso.

---

## 🚀 FASE 1: SETUP Y CONFIGURACIÓN INICIAL

### 📦 Setup del Proyecto

- [ ] **T1.1** - Crear entorno virtual en `/Volumes/HENRY/codigo-vibecoding/proyectos-henry/codigo-g1-vibecoding/django-api`
  ```bash
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  ```

- [ ] **T1.2** - Crear archivo `requirements.txt` con dependencias iniciales
  - Django 5.0+
  - djangorestframework 3.15+
  - djangorestframework-simplejwt
  - django-cors-headers
  - django-filter
  - drf-spectacular
  - python-decouple
  - psycopg2-binary (PostgreSQL)

- [ ] **T1.3** - Instalar dependencias del proyecto
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **T1.4** - Crear proyecto Django
  ```bash
  django-admin startproject todoapi .
  ```

- [ ] **T1.5** - Crear aplicación principal 'tasks'
  ```bash
  python manage.py startapp tasks
  ```

- [ ] **T1.6** - Crear aplicación 'authentication'
  ```bash
  python manage.py startapp authentication
  ```

### ⚙️ Configuración Django

- [ ] **T1.7** - Configurar `settings.py` básico
  - Agregar apps instaladas (DRF, CORS, etc.)
  - Configurar base de datos SQLite para desarrollo
  - Configurar internacionalización (es-ES)
  - Configurar zona horaria

- [ ] **T1.8** - Configurar Django REST Framework en settings
  - DEFAULT_AUTHENTICATION_CLASSES
  - DEFAULT_PERMISSION_CLASSES
  - DEFAULT_PAGINATION_CLASS
  - PAGE_SIZE

- [ ] **T1.9** - Configurar autenticación JWT
  - Instalar y configurar SimpleJWT
  - Configurar tiempos de expiración
  - Configurar algoritmos de encriptación

- [ ] **T1.10** - Configurar CORS
  - Permitir orígenes para desarrollo
  - Configurar headers permitidos
  - Configurar métodos HTTP permitidos

- [ ] **T1.11** - Configurar variables de entorno
  - Crear archivo `.env`
  - Configurar SECRET_KEY
  - Configurar DEBUG
  - Configurar DATABASE_URL

- [ ] **T1.12** - Crear archivo `.gitignore`
  - Ignorar venv/
  - Ignorar .env
  - Ignorar __pycache__/
  - Ignorar db.sqlite3
  - Ignorar .DS_Store

### 🗄️ Base de Datos Inicial

- [ ] **T1.13** - Ejecutar migraciones iniciales
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

- [ ] **T1.14** - Crear superusuario
  ```bash
  python manage.py createsuperuser
  ```

- [ ] **T1.15** - Verificar servidor de desarrollo
  ```bash
  python manage.py runserver
  ```

### 📁 Estructura de Proyecto

- [ ] **T1.16** - Crear estructura de carpetas
  ```
  todoapi/
  ├── authentication/
  ├── tasks/
  ├── todoapi/
  │   ├── settings/
  │   │   ├── __init__.py
  │   │   ├── base.py
  │   │   ├── development.py
  │   │   └── production.py
  │   └── urls.py
  ├── requirements.txt
  ├── .env
  └── .gitignore
  ```

- [ ] **T1.17** - Configurar settings modulares
  - Separar configuraciones por ambiente
  - Configurar base.py con configuraciones comunes
  - Configurar development.py
  - Configurar production.py

---

## 🔐 FASE 2: AUTENTICACIÓN Y USUARIOS

### 👤 Modelos de Usuario

- [ ] **T2.1** - Configurar modelo User personalizado (opcional)
  - Evaluar si usar User de Django por defecto
  - Crear modelo personalizado si es necesario
  - Configurar AUTH_USER_MODEL en settings

- [ ] **T2.2** - Crear serializers de autenticación
  - UserRegistrationSerializer
  - UserLoginSerializer
  - UserProfileSerializer
  - ChangePasswordSerializer

### 🔑 Endpoints de Autenticación

- [ ] **T2.3** - Implementar vista de registro
  - POST /api/auth/register/
  - Validaciones de email único
  - Validaciones de contraseña segura
  - Hasheo automático de contraseña

- [ ] **T2.4** - Implementar vista de login
  - POST /api/auth/login/
  - Validación de credenciales
  - Generación de tokens JWT
  - Respuesta con access y refresh token

- [ ] **T2.5** - Implementar vista de refresh token
  - POST /api/auth/refresh/
  - Validación de refresh token
  - Generación de nuevo access token

- [ ] **T2.6** - Implementar vista de logout
  - POST /api/auth/logout/
  - Invalidación de tokens (blacklist)

### 👥 Gestión de Perfil

- [ ] **T2.7** - Implementar vista de perfil
  - GET /api/users/profile/
  - Mostrar información del usuario autenticado
  - Excluir campos sensibles (password)

- [ ] **T2.8** - Implementar actualización de perfil
  - PUT /api/users/profile/
  - PATCH /api/users/profile/
  - Validaciones de datos
  - Protección contra modificación de campos críticos

- [ ] **T2.9** - Implementar cambio de contraseña
  - POST /api/users/change-password/
  - Validación de contraseña actual
  - Validación de nueva contraseña
  - Hasheo automático

### 🔒 Configuración de Seguridad

- [ ] **T2.10** - Configurar permisos y autenticación
  - IsAuthenticated para endpoints protegidos
  - AllowAny para registro y login
  - Configurar middleware de autenticación

- [ ] **T2.11** - Implementar validaciones de seguridad
  - Validación de fuerza de contraseña
  - Validación de formato de email
  - Rate limiting básico

- [ ] **T2.12** - Configurar URLs de autenticación
  - Crear authentication/urls.py
  - Incluir en urls.py principal
  - Documentar endpoints

---

## ✅ FASE 3: MODELOS Y CRUD DE TAREAS

### 📊 Modelo de Tareas

- [ ] **T3.1** - Crear modelo Task
  - Campo title (CharField, max_length=200)
  - Campo description (TextField, opcional)
  - Campo status (CharField con choices)
  - Campo user (ForeignKey a User)
  - Campo created_at (DateTimeField, auto_now_add)
  - Campo updated_at (DateTimeField, auto_now)
  - Campo completed_at (DateTimeField, opcional)

- [ ] **T3.2** - Definir choices para estados
  - 'pendiente': 'Pendiente'
  - 'en_progreso': 'En Progreso'
  - 'completada': 'Completada'

- [ ] **T3.3** - Agregar métodos al modelo Task
  - __str__ method
  - Método para marcar como completada
  - Método para cambiar estado
  - Meta class con ordering

- [ ] **T3.4** - Crear y ejecutar migraciones
  ```bash
  python manage.py makemigrations tasks
  python manage.py migrate
  ```

### 📝 Serializers de Tareas

- [ ] **T3.5** - Crear TaskSerializer básico
  - Incluir todos los campos necesarios
  - Excluir user del input (auto-asignación)
  - Validaciones de título y descripción

- [ ] **T3.6** - Crear TaskCreateSerializer
  - Solo campos necesarios para creación
  - Validaciones específicas
  - Método create personalizado

- [ ] **T3.7** - Crear TaskUpdateSerializer
  - Campos editables
  - Validaciones de estado
  - Método update personalizado
  - Lógica para completed_at

- [ ] **T3.8** - Crear TaskListSerializer
  - Campos optimizados para listado
  - Información mínima necesaria
  - Campos calculados si es necesario

### 🔄 ViewSets y Vistas

- [ ] **T3.9** - Crear TaskViewSet
  - Heredar de ModelViewSet
  - Configurar queryset filtrado por usuario
  - Configurar serializer_class
  - Configurar permission_classes

- [ ] **T3.10** - Implementar método get_queryset
  - Filtrar tareas por usuario autenticado
  - Optimizar queries con select_related
  - Aplicar ordering por defecto

- [ ] **T3.11** - Implementar método perform_create
  - Asignar usuario automáticamente
  - Validaciones adicionales
  - Logging de creación

- [ ] **T3.12** - Implementar método perform_update
  - Validar ownership
  - Actualizar completed_at si es necesario
  - Logging de modificaciones

- [ ] **T3.13** - Implementar método perform_destroy
  - Validar ownership
  - Soft delete opcional
  - Logging de eliminación

### 🌐 URLs y Routing

- [ ] **T3.14** - Configurar URLs de tareas
  - Crear tasks/urls.py
  - Configurar router para ViewSet
  - Incluir en urls.py principal

- [ ] **T3.15** - Documentar endpoints de tareas
  - GET /api/tasks/ (listar)
  - POST /api/tasks/ (crear)
  - GET /api/tasks/{id}/ (detalle)
  - PUT /api/tasks/{id}/ (actualizar completo)
  - PATCH /api/tasks/{id}/ (actualizar parcial)
  - DELETE /api/tasks/{id}/ (eliminar)

---

## 🔍 FASE 4: FUNCIONALIDADES AVANZADAS

### 🔎 Filtros y Búsqueda

- [ ] **T4.1** - Configurar django-filter
  - Instalar y configurar en settings
  - Crear TaskFilter class
  - Configurar filtros por estado

- [ ] **T4.2** - Implementar filtro por estado
  - Filtro exact para status
  - Filtro multiple choice
  - Validación de estados válidos

- [ ] **T4.3** - Implementar búsqueda por texto
  - SearchFilter en title
  - SearchFilter en description
  - Búsqueda case-insensitive

- [ ] **T4.4** - Implementar filtros de fecha
  - Filtro por rango de created_at
  - Filtro por rango de updated_at
  - Filtro por completed_at

- [ ] **T4.5** - Configurar ordenamiento
  - OrderingFilter
  - Campos permitidos para ordering
  - Ordering por defecto

### 📄 Paginación

- [ ] **T4.6** - Configurar paginación global
  - PageNumberPagination
  - Configurar page_size por defecto
  - Configurar max_page_size

- [ ] **T4.7** - Personalizar respuesta de paginación
  - Información de total de páginas
  - Información de total de elementos
  - Links de navegación

- [ ] **T4.8** - Implementar paginación por cursor (opcional)
  - Para listas muy grandes
  - Mejor rendimiento
  - Configuración específica

### ✅ Validaciones Avanzadas

- [ ] **T4.9** - Validaciones de negocio
  - Validar transiciones de estado válidas
  - Validar longitud de título y descripción
  - Validar caracteres especiales

- [ ] **T4.10** - Validaciones de integridad
  - Validar ownership en updates
  - Validar existencia de recursos
  - Validar permisos específicos

- [ ] **T4.11** - Manejo de errores personalizado
  - Custom exception handler
  - Mensajes de error consistentes
  - Códigos de error específicos

### 🚀 Optimización de Performance

- [ ] **T4.12** - Optimizar queries
  - Usar select_related para ForeignKeys
  - Usar prefetch_related para relaciones inversas
  - Evitar N+1 queries

- [ ] **T4.13** - Implementar índices de base de datos
  - Índice en user_id
  - Índice en status
  - Índice en created_at
  - Índice compuesto user_id + status

- [ ] **T4.14** - Configurar cache (opcional)
  - Cache de queries frecuentes
  - Cache de respuestas API
  - Configurar Redis si es necesario

---

## 📚 FASE 5: DOCUMENTACIÓN Y TESTING

### 📖 Documentación Automática

- [ ] **T5.1** - Configurar drf-spectacular
  - Instalar y configurar en settings
  - Configurar esquema OpenAPI
  - Configurar información del proyecto

- [ ] **T5.2** - Documentar serializers
  - Agregar docstrings a serializers
  - Documentar campos y validaciones
  - Ejemplos de uso

- [ ] **T5.3** - Documentar ViewSets
  - Agregar docstrings a métodos
  - Documentar parámetros de query
  - Documentar respuestas esperadas

- [ ] **T5.4** - Configurar Swagger UI
  - URL para documentación interactiva
  - Configurar autenticación en Swagger
  - Personalizar interfaz

- [ ] **T5.5** - Generar documentación estática
  - Exportar esquema OpenAPI
  - Generar documentación en formato markdown
  - Crear README del proyecto

### 🧪 Testing Básico

- [ ] **T5.6** - Configurar entorno de testing
  - Configurar base de datos de test
  - Configurar fixtures básicas
  - Configurar factory_boy (opcional)

- [ ] **T5.7** - Tests de autenticación
  - Test de registro de usuario
  - Test de login exitoso/fallido
  - Test de refresh token
  - Test de logout

- [ ] **T5.8** - Tests de CRUD de tareas
  - Test de creación de tarea
  - Test de listado de tareas
  - Test de actualización de tarea
  - Test de eliminación de tarea

- [ ] **T5.9** - Tests de permisos
  - Test de acceso sin autenticación
  - Test de acceso a tareas de otros usuarios
  - Test de operaciones no permitidas

- [ ] **T5.10** - Tests de filtros y búsqueda
  - Test de filtro por estado
  - Test de búsqueda por texto
  - Test de ordenamiento
  - Test de paginación

### 📋 Documentación del Proyecto

- [ ] **T5.11** - Crear README.md completo
  - Descripción del proyecto
  - Instrucciones de instalación
  - Instrucciones de uso
  - Ejemplos de API calls

- [ ] **T5.12** - Documentar API endpoints
  - Lista completa de endpoints
  - Parámetros requeridos/opcionales
  - Ejemplos de requests/responses
  - Códigos de error

- [ ] **T5.13** - Crear guía de desarrollo
  - Configuración del entorno
  - Estructura del proyecto
  - Convenciones de código
  - Proceso de contribución

---

## 🚀 FASE 6: CONFIGURACIÓN PARA PRODUCCIÓN

### 🔧 Configuración de Producción

- [ ] **T6.1** - Configurar settings de producción
  - DEBUG = False
  - ALLOWED_HOSTS configurado
  - Configuración de base de datos PostgreSQL
  - Configuración de archivos estáticos

- [ ] **T6.2** - Configurar variables de entorno
  - SECRET_KEY desde variable de entorno
  - DATABASE_URL para PostgreSQL
  - Configuraciones de email (opcional)
  - Configuraciones de cache

- [ ] **T6.3** - Configurar seguridad adicional
  - HTTPS obligatorio
  - Configurar CORS para producción
  - Configurar CSP headers
  - Rate limiting avanzado

- [ ] **T6.4** - Configurar logging
  - Logs de aplicación
  - Logs de errores
  - Logs de acceso
  - Rotación de logs

### 📦 Preparación para Deploy

- [ ] **T6.5** - Crear requirements de producción
  - requirements/base.txt
  - requirements/development.txt
  - requirements/production.txt
  - Versiones específicas

- [ ] **T6.6** - Configurar archivos de deploy
  - Dockerfile (opcional)
  - docker-compose.yml (opcional)
  - Procfile para Heroku
  - Scripts de deploy

- [ ] **T6.7** - Configurar base de datos de producción
  - Migraciones en producción
  - Backup y restore
  - Configuración de conexiones

- [ ] **T6.8** - Testing en ambiente de staging
  - Deploy en ambiente de pruebas
  - Tests de integración
  - Tests de carga básicos
  - Validación de funcionalidades

### 🔍 Monitoreo y Mantenimiento

- [ ] **T6.9** - Configurar monitoreo básico
  - Health check endpoint
  - Métricas de aplicación
  - Alertas básicas

- [ ] **T6.10** - Documentar proceso de deploy
  - Pasos de deploy
  - Rollback procedures
  - Troubleshooting común

---

## 📊 RESUMEN DE PROGRESO

### Contadores por Fase
- **FASE 1**: 17 tareas - Setup y Configuración
- **FASE 2**: 12 tareas - Autenticación y Usuarios  
- **FASE 3**: 15 tareas - Modelos y CRUD de Tareas
- **FASE 4**: 14 tareas - Funcionalidades Avanzadas
- **FASE 5**: 13 tareas - Documentación y Testing
- **FASE 6**: 10 tareas - Configuración para Producción

**TOTAL: 81 tareas**

### Estimación de Tiempo
- **FASE 1**: 2-3 días
- **FASE 2**: 3-4 días
- **FASE 3**: 4-5 días
- **FASE 4**: 3-4 días
- **FASE 5**: 3-4 días
- **FASE 6**: 2-3 días

**TOTAL ESTIMADO: 17-23 días de desarrollo**

---

## 🎯 NOTAS IMPORTANTES

### ⚠️ Dependencias Críticas
- Completar FASE 1 antes de continuar
- FASE 2 debe estar completa antes de FASE 3
- Testing (FASE 5) puede ejecutarse en paralelo con FASE 4

### 🔄 Tareas Iterativas
- Testing debe ejecutarse después de cada funcionalidad
- Documentación debe actualizarse continuamente
- Refactoring puede ser necesario entre fases

### 📈 Métricas de Éxito
- [ ] Todas las tareas marcadas como completadas
- [ ] API funcional con todos los endpoints
- [ ] Documentación completa y actualizada
- [ ] Tests pasando al 100%
- [ ] Deploy exitoso en producción

---

**Documento refactorizado:** $(date)  
**Versión:** 2.0  
**Basado en:** PROJECT_TASKS_P.md  
**Próxima actualización:** Después de completar FASE 1