# 📋 Requerimientos Frontend - Sistema Logístico React

## 🎯 Descripción del Proyecto

Aplicación web frontend desarrollada en **React 18+ con Vite** para el sistema de gestión logística, integrando con la API Django REST Framework existente. La aplicación manejará autenticación JWT, gestión de entidades, inventario, servicios, ventas y dashboard administrativo.

## 🛠️ Stack Tecnológico Principal

### Core Framework
- **React 18.2+** - Framework principal con Concurrent Features
- **Vite 5+** - Build tool y dev server
- **TypeScript 5+** - Tipado estático estricto
- **React Router DOM 6+** - Routing y navegación

### Estado y Datos
- **Redux Toolkit (RTK) 2.0+** - Gestión de estado global
- **RTK Query** - Manejo de estado del servidor y cache
- **Axios 1.6+** - Cliente HTTP para API calls
- **Immer** - Inmutabilidad (incluido en RTK)

### UI y Estilos
- **Shadcn/ui** - Componentes UI base accesibles
- **Radix UI** - Primitivos de UI (base de Shadcn)
- **Tailwind CSS 3.4+** - Framework de estilos utility-first
- **Lucide React** - Iconografía moderna
- **Class Variance Authority (CVA)** - Gestión de variantes de componentes

### Formularios y Validación
- **React Hook Form 7.48+** - Gestión de formularios performante
- **Zod 3.22+** - Validación de schemas y type safety
- **@hookform/resolvers** - Integración RHF con Zod

### Desarrollo y Calidad
- **ESLint 8+** - Linting de código
- **Prettier 3+** - Formateo de código
- **TypeScript ESLint** - Reglas específicas para TS
- **Husky** - Git hooks para calidad de código

## 📦 Dependencias Completas

### Dependencias de Producción

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4",
    "axios": "^1.6.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-button": "^1.0.4",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-form": "^0.0.3",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",
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
}
```

### Dependencias de Desarrollo

```json
{
  "devDependencies": {
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
}
```

## 🏗️ Arquitectura y Estructura del Proyecto

### Estructura de Carpetas

```
src/
├── app/                          # Configuración de la aplicación
│   ├── store.ts                 # Configuración del store Redux
│   ├── hooks.ts                 # Hooks tipados de Redux
│   └── providers.tsx            # Providers de la aplicación
├── components/                   # Componentes reutilizables
│   ├── ui/                      # Componentes base de Shadcn/ui
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── table.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   ├── layout/                  # Componentes de layout
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── main-layout.tsx
│   │   └── auth-layout.tsx
│   ├── forms/                   # Formularios específicos
│   │   ├── cliente-form.tsx
│   │   ├── proveedor-form.tsx
│   │   ├── unidad-form.tsx
│   │   └── ...
│   └── features/                # Componentes por funcionalidad
│       ├── auth/
│       ├── dashboard/
│       ├── entities/
│       ├── inventory/
│       ├── services/
│       └── sales/
├── features/                     # Slices de Redux por funcionalidad
│   ├── auth/
│   │   ├── authSlice.ts
│   │   ├── authAPI.ts
│   │   └── types.ts
│   ├── entities/
│   │   ├── clientesSlice.ts
│   │   ├── proveedoresSlice.ts
│   │   ├── unidadesSlice.ts
│   │   ├── entitiesAPI.ts
│   │   └── types.ts
│   ├── inventory/
│   │   ├── gpsSlice.ts
│   │   ├── simcardsSlice.ts
│   │   ├── otrosSlice.ts
│   │   ├── inventoryAPI.ts
│   │   └── types.ts
│   ├── services/
│   │   ├── serviciosSlice.ts
│   │   ├── tiposTrabajoSlice.ts
│   │   ├── servicesAPI.ts
│   │   └── types.ts
│   ├── sales/
│   │   ├── ventasSlice.ts
│   │   ├── salesAPI.ts
│   │   └── types.ts
│   └── dashboard/
│       ├── dashboardSlice.ts
│       ├── dashboardAPI.ts
│       └── types.ts
├── hooks/                        # Custom hooks
│   ├── useAuth.ts
│   ├── useLocalStorage.ts
│   ├── useDebounce.ts
│   ├── usePermissions.ts
│   └── useToast.ts
├── lib/                          # Configuraciones y utilidades
│   ├── axios.ts                 # Configuración de Axios
│   ├── utils.ts                 # Utilidades generales
│   ├── validations.ts           # Schemas de Zod
│   └── constants.ts             # Constantes de la aplicación
├── pages/                        # Páginas principales
│   ├── auth/
│   │   ├── login.tsx
│   │   └── unauthorized.tsx
│   ├── dashboard/
│   │   └── dashboard.tsx
│   ├── entities/
│   │   ├── clientes/
│   │   ├── proveedores/
│   │   └── unidades/
│   ├── inventory/
│   │   ├── gps/
│   │   ├── simcards/
│   │   └── otros/
│   ├── services/
│   │   ├── servicios/
│   │   └── tipos-trabajo/
│   └── sales/
│       └── ventas/
├── types/                        # Definiciones de tipos globales
│   ├── api.ts                   # Tipos de respuestas de API
│   ├── auth.ts                  # Tipos de autenticación
│   ├── entities.ts              # Tipos de entidades
│   ├── inventory.ts             # Tipos de inventario
│   ├── services.ts              # Tipos de servicios
│   └── sales.ts                 # Tipos de ventas
├── utils/                        # Utilidades específicas
│   ├── formatters.ts            # Formateo de datos
│   ├── validators.ts            # Validadores personalizados
│   └── permissions.ts           # Lógica de permisos
└── styles/                       # Estilos globales
    ├── globals.css              # Estilos globales + Tailwind
    └── components.css           # Estilos de componentes
```

## 🔧 Configuraciones Requeridas

### 1. Vite Configuration (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@/components': resolve(__dirname, './src/components'),
      '@/features': resolve(__dirname, './src/features'),
      '@/hooks': resolve(__dirname, './src/hooks'),
      '@/lib': resolve(__dirname, './src/lib'),
      '@/pages': resolve(__dirname, './src/pages'),
      '@/types': resolve(__dirname, './src/types'),
      '@/utils': resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
})
```

### 2. TypeScript Configuration (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/features/*": ["./src/features/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/pages/*": ["./src/pages/*"],
      "@/types/*": ["./src/types/*"],
      "@/utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 3. Tailwind Configuration (tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### 4. Variables de Entorno (.env)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=10000

# Authentication
VITE_TOKEN_STORAGE_KEY=auth_token
VITE_REFRESH_TOKEN_KEY=refresh_token

# Application
VITE_APP_NAME=Sistema Logístico
VITE_APP_VERSION=1.0.0

# Development
VITE_DEV_TOOLS=true
```

## 🔐 Funcionalidades de Autenticación

### Requerimientos de Autenticación
- **Login con JWT** - Username/password con tokens access y refresh
- **Refresh automático** - Renovación transparente de tokens
- **Logout seguro** - Limpieza de tokens y redirección
- **Protección de rutas** - Guards basados en autenticación y roles
- **Gestión de sesión** - Persistencia y expiración de sesión
- **Roles y permisos** - Control de acceso granular

### Estados de Autenticación en Redux
```typescript
interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  permissions: Permission[]
}
```

## 📊 Módulos Principales

### 1. Dashboard
- **KPIs en tiempo real** - Métricas de ventas, inventario, servicios
- **Gráficos interactivos** - Charts con Recharts
- **Alertas del sistema** - Notificaciones importantes
- **Resumen de actividades** - Últimas acciones del usuario

### 2. Gestión de Entidades
- **Clientes** - CRUD completo con validación de RUC
- **Proveedores** - Gestión de proveedores y productos
- **Unidades Vehiculares** - Registro y seguimiento de vehículos

### 3. Inventario
- **Dispositivos GPS** - Control de stock y estados
- **SIM Cards** - Gestión de líneas y asignaciones
- **Otros Productos** - Inventario general con alertas de stock

### 4. Servicios
- **Tipos de Trabajo** - Categorización de servicios
- **Servicios** - Gestión completa del ciclo de vida
- **Estados y seguimiento** - Workflow de estados

### 5. Ventas
- **Registro de ventas** - Formularios complejos con validación
- **Estados de venta** - Workflow de aprobación
- **Reportes** - Generación de reportes y estadísticas

## 🎨 Componentes UI Requeridos

### Componentes Base (Shadcn/ui)
- **Button** - Variantes primary, secondary, ghost, destructive
- **Input** - Text, email, password, number, tel
- **Form** - Integración con React Hook Form
- **Dialog** - Modales para CRUD operations
- **Table** - Tablas con sorting, filtering, pagination
- **Select** - Dropdowns con búsqueda
- **Checkbox** - Selección múltiple
- **Switch** - Toggle states
- **Toast** - Notificaciones de feedback
- **Alert** - Mensajes de estado
- **Badge** - Estados y categorías
- **Card** - Contenedores de información
- **Tabs** - Navegación por secciones
- **Progress** - Indicadores de progreso
- **Skeleton** - Loading states

### Componentes Personalizados
- **DataTable** - Tabla avanzada con filtros y acciones
- **SearchInput** - Input con debounce para búsquedas
- **StatusBadge** - Badge con colores por estado
- **ConfirmDialog** - Confirmación de acciones destructivas
- **FormField** - Wrapper para campos de formulario
- **LoadingSpinner** - Indicador de carga
- **ErrorBoundary** - Manejo de errores de componentes
- **ProtectedRoute** - Guard de rutas autenticadas

## 🔄 Integración con API Django

### Configuración de Axios con Redux Toolkit
```typescript
// Interceptors para tokens JWT
// Manejo automático de refresh tokens
// Serialización de errores para Redux
// Timeout y retry logic
// Request/Response logging en desarrollo
```

### RTK Query Endpoints
- **Auth API** - Login, logout, refresh, profile
- **Entities API** - Clientes, proveedores, unidades
- **Inventory API** - GPS, SIM cards, otros productos
- **Services API** - Servicios y tipos de trabajo
- **Sales API** - Ventas y reportes
- **Dashboard API** - KPIs y métricas
- **Exports API** - Generación de reportes
- **Imports API** - Carga masiva de datos

## 📋 Validaciones y Formularios

### Schemas de Validación con Zod
```typescript
// Validación de RUC (11 dígitos)
// Validación de DNI (8 dígitos)
// Validación de celular (9 dígitos, inicia con 9)
// Validación de placas vehiculares
// Validación de emails
// Validación de fechas
// Validación de números de serie
```

### Formularios con React Hook Form
- **Formularios dinámicos** - Campos condicionales
- **Validación en tiempo real** - Feedback inmediato
- **Manejo de errores** - Mensajes específicos por campo
- **Autocompletado** - Sugerencias basadas en datos existentes
- **Guardado automático** - Draft states para formularios largos

## 🚀 Características de Performance

### Optimizaciones
- **Code splitting** - Lazy loading de páginas
- **Memoización** - React.memo para componentes pesados
- **Virtualización** - Para listas largas de datos
- **Debouncing** - En búsquedas y filtros
- **Caching inteligente** - RTK Query con invalidación selectiva
- **Bundle optimization** - Tree shaking y chunk splitting

### Métricas de Performance
- **First Contentful Paint** < 1.5s
- **Largest Contentful Paint** < 2.5s
- **Time to Interactive** < 3.5s
- **Bundle size** < 500KB (gzipped)

## 🔒 Seguridad

### Medidas de Seguridad
- **Sanitización de inputs** - Prevención de XSS
- **Validación client-side** - Primera línea de defensa
- **Tokens seguros** - Almacenamiento y transmisión
- **HTTPS enforcement** - Comunicación encriptada
- **CSP headers** - Content Security Policy
- **Rate limiting** - Prevención de abuso

## 🧪 Testing (Opcional)

### Testing Stack (si se requiere)
- **Vitest** - Test runner rápido
- **React Testing Library** - Testing de componentes
- **MSW** - Mocking de API calls
- **Playwright** - E2E testing

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+
- **Large Desktop**: 1440px+

### Características Responsive
- **Mobile-first approach** - Diseño desde móvil
- **Touch-friendly** - Botones y controles accesibles
- **Adaptive layouts** - Grids que se adaptan
- **Progressive enhancement** - Funcionalidades adicionales en desktop

## 🎯 Criterios de Aceptación

### Funcionalidad
- ✅ Autenticación JWT completa
- ✅ CRUD para todas las entidades
- ✅ Filtros y búsquedas en tiempo real
- ✅ Validación de formularios robusta
- ✅ Manejo de errores comprehensivo
- ✅ Estados de carga y feedback visual
- ✅ Exportación e importación de datos

### Performance
- ✅ Carga inicial < 3 segundos
- ✅ Navegación fluida entre páginas
- ✅ Búsquedas con debounce < 300ms
- ✅ Actualizaciones de estado inmediatas

### UX/UI
- ✅ Interfaz intuitiva y consistente
- ✅ Feedback visual para todas las acciones
- ✅ Accesibilidad WCAG 2.1 AA
- ✅ Responsive en todos los dispositivos
- ✅ Dark mode support (opcional)

### Calidad de Código
- ✅ TypeScript strict mode
- ✅ ESLint sin warnings
- ✅ Prettier formatting
- ✅ Componentes reutilizables
- ✅ Arquitectura escalable

## 🚀 Plan de Implementación

### Fase 1: Setup y Autenticación (Semana 1)
1. Configuración del proyecto con Vite + TypeScript
2. Setup de Redux Toolkit y RTK Query
3. Configuración de Shadcn/ui y Tailwind
4. Implementación de autenticación JWT
5. Protección de rutas y layout base

### Fase 2: Módulos Core (Semana 2-3)
1. Dashboard con KPIs básicos
2. Gestión de entidades (Clientes, Proveedores, Unidades)
3. Formularios con validación completa
4. Tablas con filtros y paginación

### Fase 3: Inventario y Servicios (Semana 4)
1. Módulo de inventario completo
2. Gestión de servicios y tipos de trabajo
3. Estados y workflows

### Fase 4: Ventas y Reportes (Semana 5)
1. Módulo de ventas completo
2. Generación de reportes
3. Exportación e importación de datos

### Fase 5: Optimización y Testing (Semana 6)
1. Optimizaciones de performance
2. Testing de componentes críticos
3. Refinamiento de UX/UI
4. Documentación final

---

## 📞 Soporte y Documentación

Para implementación exitosa, consultar:
- **API Documentation**: `/docs/API_DOCUMENTATION.md`
- **Frontend Integration Guide**: `/docs/FRONTEND_INTEGRATION_GUIDE.md`
- **Shadcn/ui Documentation**: https://ui.shadcn.com/
- **Redux Toolkit Documentation**: https://redux-toolkit.js.org/
- **React Hook Form Documentation**: https://react-hook-form.com/

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2025  
**Autor**: Equipo de Desarrollo Frontend