# 🚀 Plan de Desarrollo Frontend - Fases Detalladas

## 📋 Descripción General

Este documento define las fases específicas para el desarrollo del frontend React + Vite + TypeScript del sistema logístico, con tareas concretas y detalladas para cada etapa del desarrollo.

---

## 🏗️ FASE 0: PREPARACIÓN Y SETUP INICIAL

### 📦 Tareas de Configuración Base

#### T0.1: Inicialización del Proyecto
- [ ] Crear proyecto con Vite usando template React + TypeScript
- [ ] Configurar estructura de carpetas según arquitectura definida
- [ ] Inicializar repositorio Git con .gitignore apropiado
- [ ] Crear archivo README.md con instrucciones de desarrollo

#### T0.2: Instalación de Dependencias Core
- [ ] Instalar React 18.3.1+ y React DOM (última versión estable)
- [ ] Instalar React Router DOM 6+
- [ ] Instalar TypeScript 5.9.2+ y tipos necesarios
- [ ] Configurar Vite 5+ con plugin React SWC

#### T0.3: Configuración de TypeScript
- [ ] Crear tsconfig.json con configuración estricta
- [ ] Configurar paths aliases (@/, @/components, etc.)
- [ ] Habilitar strict mode y opciones de seguridad
- [ ] Crear tsconfig.node.json para configuración de Vite

#### T0.4: Configuración de Vite
- [ ] Configurar vite.config.ts con aliases
- [ ] Configurar proxy para API Django (puerto 8000)
- [ ] Configurar build optimization y code splitting
- [ ] Configurar servidor de desarrollo en puerto 3000

#### T0.5: Variables de Entorno
- [ ] Crear archivo .env con variables de configuración
- [ ] Definir VITE_API_BASE_URL para conexión con Django
- [ ] Configurar variables para tokens y autenticación
- [ ] Crear .env.example para documentación

---

## 🎨 FASE 1: CONFIGURACIÓN DE UI Y ESTILOS

### 🎯 Tareas de Configuración de Estilos

#### T1.1: Instalación de Tailwind CSS
- [ ] Instalar Tailwind CSS 4.1.13+ (última versión estable) y dependencias
- [ ] Instalar autoprefixer y postcss
- [ ] Configurar tailwind.config.js con tema personalizado
- [ ] Crear postcss.config.js

#### T1.2: Configuración de Shadcn/ui
- [ ] Instalar shadcn/ui CLI
- [ ] Inicializar shadcn/ui en el proyecto
- [ ] Configurar components.json con configuraciones
- [ ] Instalar componentes base necesarios

#### T1.3: Instalación de Radix UI
- [ ] Instalar primitivos de Radix UI necesarios
- [ ] Configurar componentes de diálogo y dropdown
- [ ] Instalar componentes de formulario
- [ ] Configurar componentes de navegación

#### T1.4: Configuración de Iconos y Utilidades
- [ ] Instalar Lucide React para iconografía
- [ ] Instalar class-variance-authority (CVA)
- [ ] Instalar clsx y tailwind-merge
- [ ] Configurar utilidades de estilos

#### T1.5: Estilos Globales
- [ ] Crear src/styles/globals.css con variables CSS
- [ ] Configurar variables de color del tema
- [ ] Importar estilos de Tailwind
- [ ] Configurar estilos base de componentes

---

## 🔧 FASE 2: CONFIGURACIÓN DE ESTADO Y API

### 📊 Tareas de Redux Toolkit

#### T2.1: Instalación de Redux Toolkit
- [ ] Instalar @reduxjs/toolkit 2.9.0+ (última versión estable)
- [ ] Instalar react-redux 9.0+
- [ ] Configurar tipos de TypeScript para Redux
- [ ] Crear hooks tipados para Redux

#### T2.2: Configuración del Store
- [ ] Crear src/app/store.ts con configuración base
- [ ] Configurar middleware y DevTools
- [ ] Crear src/app/hooks.ts con hooks tipados
- [ ] Configurar persistencia de estado si necesario

#### T2.3: Configuración de RTK Query
- [ ] Configurar baseQuery con fetchBaseQuery
- [ ] Crear API slice base con configuración común
- [ ] Configurar interceptors para autenticación
- [ ] Configurar manejo de errores global

#### T2.4: Instalación de Axios
- [ ] Instalar Axios 1.12.2+ (última versión estable) como respaldo
- [ ] Crear src/lib/axios.ts con configuración
- [ ] Configurar interceptors para tokens JWT
- [ ] Configurar timeout y retry logic

---

## 🔐 FASE 3: SISTEMA DE AUTENTICACIÓN

### 🛡️ Tareas de Autenticación JWT

#### T3.1: Tipos de Autenticación
- [ ] Crear src/types/auth.ts con interfaces
- [ ] Definir User interface con roles
- [ ] Definir AuthState interface
- [ ] Definir tipos para tokens JWT

#### T3.2: Auth Slice de Redux
- [ ] Crear src/features/auth/authSlice.ts
- [ ] Implementar estados de autenticación
- [ ] Crear reducers para login/logout
- [ ] Implementar manejo de tokens

#### T3.3: Auth API con RTK Query
- [ ] Crear src/features/auth/authAPI.ts
- [ ] Implementar endpoint de login
- [ ] Implementar endpoint de refresh token
- [ ] Implementar endpoint de logout
- [ ] Implementar endpoint de perfil de usuario

#### T3.4: Hooks de Autenticación
- [ ] Crear src/hooks/useAuth.ts
- [ ] Implementar hook para estado de autenticación
- [ ] Crear hook para permisos de usuario
- [ ] Implementar hook para logout

#### T3.5: Persistencia de Tokens
- [ ] Crear src/hooks/useLocalStorage.ts
- [ ] Implementar almacenamiento seguro de tokens
- [ ] Configurar limpieza automática de tokens expirados
- [ ] Implementar recuperación de sesión al cargar app

---

## 🧭 FASE 4: ROUTING Y NAVEGACIÓN

### 🗺️ Tareas de React Router

#### T4.1: Configuración de Router
- [ ] Crear src/app/router.tsx con configuración base
- [ ] Definir rutas principales de la aplicación
- [ ] Configurar rutas anidadas para módulos
- [ ] Implementar manejo de rutas no encontradas

#### T4.2: Componentes de Layout
- [ ] Crear src/components/layout/MainLayout.tsx
- [ ] Crear src/components/layout/AuthLayout.tsx
- [ ] Implementar Header con navegación
- [ ] Implementar Sidebar con menú principal

#### T4.3: Protección de Rutas
- [ ] Crear src/components/ProtectedRoute.tsx
- [ ] Implementar guards de autenticación
- [ ] Crear guards basados en roles
- [ ] Implementar redirecciones automáticas

#### T4.4: Navegación Principal
- [ ] Crear src/components/layout/Sidebar.tsx
- [ ] Implementar menú con iconos y estados activos
- [ ] Configurar navegación responsive
- [ ] Implementar breadcrumbs

---

## 📝 FASE 5: FORMULARIOS Y VALIDACIÓN

### 🔍 Tareas de React Hook Form y Zod

#### T5.1: Instalación de Formularios
- [ ] Instalar react-hook-form 7.62.0+ (última versión estable)
- [ ] Instalar @hookform/resolvers
- [ ] Instalar zod 4.0+ (última versión estable) para validación
- [ ] Configurar tipos de TypeScript

#### T5.2: Schemas de Validación
- [ ] Crear src/lib/validations.ts
- [ ] Implementar schema para validación de RUC (11 dígitos)
- [ ] Implementar schema para validación de DNI (8 dígitos)
- [ ] Implementar schema para validación de celular (9 dígitos)
- [ ] Implementar schema para validación de email
- [ ] Implementar schema para validación de placas vehiculares

#### T5.3: Componentes de Formulario Base
- [ ] Crear src/components/ui/form.tsx (Shadcn)
- [ ] Crear src/components/ui/input.tsx
- [ ] Crear src/components/ui/select.tsx
- [ ] Crear src/components/ui/textarea.tsx
- [ ] Crear src/components/ui/checkbox.tsx

#### T5.4: Hooks de Formulario
- [ ] Crear src/hooks/useFormValidation.ts
- [ ] Implementar hook para manejo de errores
- [ ] Crear hook para autocompletado
- [ ] Implementar hook para guardado automático

---

## 📊 FASE 6: COMPONENTES UI BASE

### 🎨 Tareas de Componentes Shadcn/ui

#### T6.1: Componentes de Datos
- [ ] Instalar y configurar Table component
- [ ] Crear DataTable con sorting y filtering
- [ ] Implementar paginación personalizada
- [ ] Configurar estados de carga para tablas

#### T6.2: Componentes de Feedback
- [ ] Instalar y configurar Toast component
- [ ] Crear sistema de notificaciones global
- [ ] Implementar Alert component
- [ ] Crear Loading Spinner personalizado

#### T6.3: Componentes de Navegación
- [ ] Instalar y configurar Tabs component
- [ ] Crear Breadcrumbs component
- [ ] Implementar Pagination component
- [ ] Configurar Progress indicators

#### T6.4: Componentes de Interacción
- [ ] Instalar y configurar Dialog component
- [ ] Crear ConfirmDialog para acciones destructivas
- [ ] Implementar Popover component
- [ ] Configurar Tooltip component

#### T6.5: Componentes de Estado
- [ ] Crear Badge component con variantes
- [ ] Implementar StatusBadge para estados
- [ ] Crear Skeleton loaders
- [ ] Implementar Error Boundary

---

## 🏢 FASE 7: MÓDULO DE ENTIDADES

### 👥 Tareas del Módulo Entities

#### T7.1: Tipos de Entidades
- [ ] Crear src/types/entities.ts
- [ ] Definir interface Cliente con validaciones
- [ ] Definir interface Proveedor
- [ ] Definir interface Unidad vehicular
- [ ] Crear tipos para respuestas de API

#### T7.2: API de Entidades
- [ ] Crear src/features/entities/entitiesAPI.ts
- [ ] Implementar endpoints CRUD para clientes
- [ ] Implementar endpoints CRUD para proveedores
- [ ] Implementar endpoints CRUD para unidades
- [ ] Configurar filtros y búsquedas

#### T7.3: Slices de Redux para Entidades
- [ ] Crear src/features/entities/clientesSlice.ts
- [ ] Crear src/features/entities/proveedoresSlice.ts
- [ ] Crear src/features/entities/unidadesSlice.ts
- [ ] Implementar estados de carga y error

#### T7.4: Formularios de Entidades
- [ ] Crear src/components/forms/ClienteForm.tsx
- [ ] Crear src/components/forms/ProveedorForm.tsx
- [ ] Crear src/components/forms/UnidadForm.tsx
- [ ] Implementar validación en tiempo real

#### T7.5: Páginas de Entidades
- [ ] Crear src/pages/entities/clientes/ClientesPage.tsx
- [ ] Crear src/pages/entities/proveedores/ProveedoresPage.tsx
- [ ] Crear src/pages/entities/unidades/UnidadesPage.tsx
- [ ] Implementar listados con filtros y búsqueda

---

## 📦 FASE 8: MÓDULO DE INVENTARIO

### 🔧 Tareas del Módulo Inventory

#### T8.1: Tipos de Inventario
- [ ] Crear src/types/inventory.ts
- [ ] Definir interface GPS con estados
- [ ] Definir interface SIMCard
- [ ] Definir interface Otros productos
- [ ] Crear enums para estados de inventario

#### T8.2: API de Inventario
- [ ] Crear src/features/inventory/inventoryAPI.ts
- [ ] Implementar endpoints para GPS
- [ ] Implementar endpoints para SIM cards
- [ ] Implementar endpoints para otros productos
- [ ] Configurar filtros por estado y marca

#### T8.3: Slices de Redux para Inventario
- [ ] Crear src/features/inventory/gpsSlice.ts
- [ ] Crear src/features/inventory/simcardsSlice.ts
- [ ] Crear src/features/inventory/otrosSlice.ts
- [ ] Implementar acciones para cambio de estado

#### T8.4: Formularios de Inventario
- [ ] Crear src/components/forms/GPSForm.tsx
- [ ] Crear src/components/forms/SIMCardForm.tsx
- [ ] Crear src/components/forms/OtrosForm.tsx
- [ ] Implementar validación de números de serie

#### T8.5: Páginas de Inventario
- [ ] Crear src/pages/inventory/gps/GPSPage.tsx
- [ ] Crear src/pages/inventory/simcards/SIMCardsPage.tsx
- [ ] Crear src/pages/inventory/otros/OtrosPage.tsx
- [ ] Implementar alertas de stock bajo

---

## 🛠️ FASE 9: MÓDULO DE SERVICIOS

### ⚙️ Tareas del Módulo Services

#### T9.1: Tipos de Servicios
- [ ] Crear src/types/services.ts
- [ ] Definir interface TipoTrabajo
- [ ] Definir interface Servicio con workflow
- [ ] Crear enums para estados de servicio
- [ ] Definir tipos para asignación de técnicos

#### T9.2: API de Servicios
- [ ] Crear src/features/services/servicesAPI.ts
- [ ] Implementar endpoints para tipos de trabajo
- [ ] Implementar endpoints CRUD para servicios
- [ ] Configurar filtros por estado y técnico
- [ ] Implementar endpoints de estadísticas

#### T9.3: Slices de Redux para Servicios
- [ ] Crear src/features/services/tiposTrabajoSlice.ts
- [ ] Crear src/features/services/serviciosSlice.ts
- [ ] Implementar acciones para cambio de estado
- [ ] Configurar cache de datos frecuentes

#### T9.4: Formularios de Servicios
- [ ] Crear src/components/forms/TipoTrabajoForm.tsx
- [ ] Crear src/components/forms/ServicioForm.tsx
- [ ] Implementar selección de cliente y unidad
- [ ] Configurar asignación de técnicos

#### T9.5: Páginas de Servicios
- [ ] Crear src/pages/services/tipos/TiposTrabajoPage.tsx
- [ ] Crear src/pages/services/servicios/ServiciosPage.tsx
- [ ] Implementar vista de calendario para servicios
- [ ] Crear dashboard de servicios por técnico

---

## 💰 FASE 10: MÓDULO DE VENTAS

### 🛒 Tareas del Módulo Sales

#### T10.1: Tipos de Ventas
- [ ] Crear src/types/sales.ts
- [ ] Definir interface Venta con detalles
- [ ] Crear enums para estados de venta
- [ ] Definir tipos para métodos de pago
- [ ] Crear interface para reportes de ventas

#### T10.2: API de Ventas
- [ ] Crear src/features/sales/salesAPI.ts
- [ ] Implementar endpoints CRUD para ventas
- [ ] Configurar filtros por fecha y estado
- [ ] Implementar endpoints de reportes
- [ ] Configurar endpoints de estadísticas

#### T10.3: Slices de Redux para Ventas
- [ ] Crear src/features/sales/ventasSlice.ts
- [ ] Implementar acciones para workflow de ventas
- [ ] Configurar estados de facturación
- [ ] Implementar cache para reportes

#### T10.4: Formularios de Ventas
- [ ] Crear src/components/forms/VentaForm.tsx
- [ ] Implementar selección de productos
- [ ] Configurar cálculo automático de totales
- [ ] Implementar validación de stock

#### T10.5: Páginas de Ventas
- [ ] Crear src/pages/sales/ventas/VentasPage.tsx
- [ ] Implementar vista de detalle de venta
- [ ] Crear página de reportes de ventas
- [ ] Implementar generación de facturas

---

## 📈 FASE 11: MÓDULO DE DASHBOARD

### 📊 Tareas del Dashboard

#### T11.1: Instalación de Gráficos
- [ ] Instalar recharts 2.8+ para gráficos
- [ ] Instalar date-fns 2.30+ para manejo de fechas
- [ ] Configurar tipos de TypeScript para charts
- [ ] Crear utilidades para formateo de datos

#### T11.2: Tipos de Dashboard
- [ ] Crear src/types/dashboard.ts
- [ ] Definir interfaces para KPIs
- [ ] Crear tipos para métricas de tiempo
- [ ] Definir interfaces para alertas

#### T11.3: API de Dashboard
- [ ] Crear src/features/dashboard/dashboardAPI.ts
- [ ] Implementar endpoints para KPIs generales
- [ ] Configurar endpoints para métricas de ventas
- [ ] Implementar endpoints para alertas del sistema
- [ ] Configurar cache con invalidación temporal

#### T11.4: Componentes de Dashboard
- [ ] Crear src/components/dashboard/KPICard.tsx
- [ ] Crear src/components/dashboard/SalesChart.tsx
- [ ] Crear src/components/dashboard/InventoryChart.tsx
- [ ] Crear src/components/dashboard/AlertsList.tsx

#### T11.5: Página Principal de Dashboard
- [ ] Crear src/pages/dashboard/DashboardPage.tsx
- [ ] Implementar grid responsive para KPIs
- [ ] Configurar actualización automática de datos
- [ ] Implementar filtros por período de tiempo

---

## 🔄 FASE 12: IMPORTACIÓN Y EXPORTACIÓN

### 📤 Tareas de Import/Export

#### T12.1: Tipos de Import/Export
- [ ] Crear src/types/imports.ts
- [ ] Crear src/types/exports.ts
- [ ] Definir interfaces para templates
- [ ] Crear tipos para progreso de tareas

#### T12.2: API de Import/Export
- [ ] Crear src/features/imports/importsAPI.ts
- [ ] Crear src/features/exports/exportsAPI.ts
- [ ] Implementar upload de archivos Excel
- [ ] Configurar descarga de reportes
- [ ] Implementar seguimiento de progreso

#### T12.3: Componentes de Import/Export
- [ ] Crear src/components/imports/FileUpload.tsx
- [ ] Crear src/components/exports/ExportDialog.tsx
- [ ] Implementar progress indicators
- [ ] Crear componentes de validación de datos

#### T12.4: Páginas de Import/Export
- [ ] Crear src/pages/imports/ImportsPage.tsx
- [ ] Crear src/pages/exports/ExportsPage.tsx
- [ ] Implementar historial de importaciones
- [ ] Configurar descarga de templates

---

## 🎨 FASE 13: OPTIMIZACIÓN Y UX

### ⚡ Tareas de Performance

#### T13.1: Optimización de Componentes
- [ ] Implementar React.memo en componentes pesados
- [ ] Configurar useMemo para cálculos costosos
- [ ] Implementar useCallback para funciones
- [ ] Optimizar re-renders innecesarios

#### T13.2: Code Splitting
- [ ] Implementar lazy loading para páginas
- [ ] Configurar dynamic imports para módulos
- [ ] Optimizar bundle splitting en Vite
- [ ] Implementar preloading de rutas críticas

#### T13.3: Optimización de Estado
- [ ] Configurar selectores optimizados en Redux
- [ ] Implementar normalización de datos
- [ ] Optimizar cache de RTK Query
- [ ] Configurar invalidación selectiva

#### T13.4: UX Improvements
- [ ] Implementar skeleton loaders
- [ ] Configurar estados de error amigables
- [ ] Implementar feedback visual para acciones
- [ ] Crear animaciones suaves con CSS

---

## 🧪 FASE 14: TESTING (OPCIONAL)

### 🔬 Tareas de Testing

#### T14.1: Configuración de Testing
- [ ] Instalar Vitest como test runner
- [ ] Instalar React Testing Library
- [ ] Configurar MSW para mocking de API
- [ ] Configurar setup de testing

#### T14.2: Tests de Componentes
- [ ] Crear tests para componentes UI base
- [ ] Implementar tests para formularios
- [ ] Crear tests para hooks personalizados
- [ ] Implementar tests de integración

#### T14.3: Tests de Redux
- [ ] Crear tests para slices de Redux
- [ ] Implementar tests para API endpoints
- [ ] Crear tests para selectors
- [ ] Implementar tests de flujos completos

---

## 🚀 FASE 15: DEPLOYMENT Y DOCUMENTACIÓN

### 📚 Tareas Finales

#### T15.1: Configuración de Build
- [ ] Optimizar configuración de Vite para producción
- [ ] Configurar variables de entorno para producción
- [ ] Implementar análisis de bundle size
- [ ] Configurar sourcemaps para debugging

#### T15.2: Documentación
- [ ] Crear README.md completo con instrucciones
- [ ] Documentar componentes principales
- [ ] Crear guía de desarrollo
- [ ] Documentar APIs y hooks

#### T15.3: Deployment
- [ ] Configurar scripts de build
- [ ] Preparar archivos para deployment
- [ ] Configurar CI/CD si es necesario
- [ ] Crear checklist de deployment

---

## 📋 CHECKLIST DE DEPENDENCIAS COMPLETO

### 🔧 Dependencias de Producción
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "@reduxjs/toolkit": "^2.0.1",
  "react-redux": "^9.0.4",
  "axios": "^1.6.2",
  "react-hook-form": "^7.48.2",
  "@hookform/resolvers": "^3.3.2",
  "zod": "^3.22.4",
  "lucide-react": "^0.294.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.0.0",
  "date-fns": "^2.30.0",
  "recharts": "^2.8.0"
}
```

### 🛠️ Dependencias de Desarrollo
```json
{
  "@types/react": "^18.2.37",
  "@types/react-dom": "^18.2.15",
  "@types/node": "^20.9.0",
  "@vitejs/plugin-react-swc": "^3.5.0",
  "vite": "^5.0.0",
  "typescript": "^5.2.2",
  "eslint": "^8.53.0",
  "@typescript-eslint/eslint-plugin": "^6.10.0",
  "@typescript-eslint/parser": "^6.10.0",
  "eslint-plugin-react": "^7.33.2",
  "eslint-plugin-react-hooks": "^4.6.0",
  "eslint-plugin-react-refresh": "^0.4.4",
  "prettier": "^3.1.0",
  "prettier-plugin-tailwindcss": "^0.5.7",
  "tailwindcss": "^3.3.6",
  "autoprefixer": "^10.4.16",
  "postcss": "^8.4.32",
  "husky": "^8.0.3",
  "lint-staged": "^15.1.0"
}
```

### 📦 Dependencias de Shadcn/ui
```json
{
  "@radix-ui/react-alert-dialog": "^1.1.2",
  "@radix-ui/react-avatar": "^1.1.1",
  "@radix-ui/react-button": "^1.1.0",
  "@radix-ui/react-checkbox": "^1.1.2",
  "@radix-ui/react-dialog": "^1.1.2",
  "@radix-ui/react-dropdown-menu": "^2.1.2",
  "@radix-ui/react-form": "^0.1.0",
  "@radix-ui/react-label": "^2.1.0",
  "@radix-ui/react-popover": "^1.1.2",
  "@radix-ui/react-progress": "^1.1.0",
  "@radix-ui/react-select": "^2.1.2",
  "@radix-ui/react-separator": "^1.1.0",
  "@radix-ui/react-slot": "^1.1.0",
  "@radix-ui/react-switch": "^1.1.1",
  "@radix-ui/react-tabs": "^1.1.1",
  "@radix-ui/react-toast": "^1.2.2",
  "@radix-ui/react-tooltip": "^1.1.2"
}
```

---

## 🎯 CRITERIOS DE ÉXITO POR FASE

### ✅ Fase 0-2: Setup Completo
- Proyecto inicializado con todas las dependencias
- TypeScript configurado sin errores
- Vite funcionando con proxy a Django
- Tailwind y Shadcn/ui operativos

### ✅ Fase 3-4: Autenticación y Navegación
- Login/logout funcional con JWT
- Rutas protegidas implementadas
- Layout principal responsive
- Navegación entre módulos operativa

### ✅ Fase 5-6: Formularios y UI
- Validación con Zod funcionando
- Componentes UI base implementados
- Formularios con feedback visual
- Sistema de notificaciones activo

### ✅ Fase 7-11: Módulos Principales
- CRUD completo para todas las entidades
- Filtros y búsquedas operativas
- Dashboard con KPIs en tiempo real
- Estados de carga y error manejados

### ✅ Fase 12-15: Finalización
- Import/export funcionando
- Performance optimizada
- Documentación completa
- Aplicación lista para producción

---

## 📞 NOTAS IMPORTANTES PARA VIBE CODING

### 🚨 Puntos Críticos a Recordar

1. **Orden de Dependencias**: Instalar siempre las dependencias core antes que las específicas
2. **TypeScript Strict**: Mantener configuración estricta desde el inicio
3. **API Endpoints**: Verificar que Django esté corriendo en puerto 8000
4. **Proxy Configuration**: Configurar proxy en Vite antes de hacer llamadas a API
5. **Token Management**: Implementar refresh automático desde el inicio
6. **Error Boundaries**: Implementar manejo de errores en cada módulo
7. **Loading States**: Nunca dejar acciones sin feedback visual
8. **Responsive Design**: Probar en móvil desde el primer componente
9. **Performance**: Implementar lazy loading desde las primeras páginas
10. **Validation**: Validar tanto en cliente como confirmar en servidor

### 🔧 Comandos Esenciales
```bash
# Inicializar proyecto
npm create vite@latest frontend-logistico -- --template react-ts

# Instalar dependencias base
npm install react-router-dom @reduxjs/toolkit react-redux

# Configurar Shadcn/ui
npx shadcn-ui@latest init

# Desarrollo
npm run dev

# Build para producción
npm run build
```

---

**📝 Nota**: Este documento debe ser seguido secuencialmente para evitar errores de dependencias y configuración. Cada fase debe completarse antes de pasar a la siguiente.