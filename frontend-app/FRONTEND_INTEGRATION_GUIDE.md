# Guía de Integración Frontend - React + Vite

Esta guía te ayudará a integrar tu aplicación React + Vite con el backend Django API de manera moderna y minimalista.

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Configuración de Axios](#configuración-de-axios)
4. [Autenticación JWT](#autenticación-jwt)
5. [Gestión de Estado](#gestión-de-estado)
6. [Endpoints Disponibles](#endpoints-disponibles)
7. [Ejemplos de Implementación](#ejemplos-de-implementación)
8. [Validaciones con Zod](#validaciones-con-zod)
9. [Manejo de Errores](#manejo-de-errores)
10. [Testing](#testing)

## 🚀 Configuración Inicial

### Crear el Proyecto React + Vite

```bash
npm create vite@latest frontend-app -- --template react-ts
cd frontend-app
npm install
```

### Dependencias Recomendadas

```bash
# Core dependencies
npm install axios @tanstack/react-query zustand

# Form handling
npm install react-hook-form @hookform/resolvers zod

# UI Components
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-toast

# Styling
npm install tailwindcss postcss autoprefixer
npm install clsx tailwind-merge class-variance-authority

# Date handling
npm install date-fns

# Development
npm install -D @types/node
```

### Configuración de Tailwind CSS

```bash
npx tailwindcss init -p
```

**tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

## 📁 Estructura del Proyecto

```
src/
├── app/
│   ├── providers/
│   │   ├── QueryProvider.tsx
│   │   └── AuthProvider.tsx
│   └── router/
│       └── AppRouter.tsx
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Toast.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Layout.tsx
│   └── features/
│       ├── auth/
│       ├── inventory/
│       ├── sales/
│       └── dashboard/
├── hooks/
│   ├── api/
│   │   ├── useAuth.ts
│   │   ├── useInventory.ts
│   │   └── useSales.ts
│   └── utils/
│       ├── useLocalStorage.ts
│       └── useDebounce.ts
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   ├── utils.ts
│   └── validations.ts
├── stores/
│   ├── authStore.ts
│   ├── uiStore.ts
│   └── userStore.ts
├── types/
│   ├── api.ts
│   ├── auth.ts
│   └── entities.ts
└── pages/
    ├── LoginPage.tsx
    ├── DashboardPage.tsx
    ├── InventoryPage.tsx
    └── SalesPage.tsx
```

## 🔧 Configuración de Axios

**src/lib/api.ts**
```typescript
import axios, { AxiosError, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/authStore'

// Base URL del backend Django
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Crear instancia de Axios
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor para agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor para manejo de errores
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config

    // Si el token expiró, intentar renovarlo
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          })
          
          const newToken = response.data.access
          useAuthStore.getState().setToken(newToken)
          
          // Reintentar la petición original
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Si falla el refresh, cerrar sesión
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
```

## 🔐 Autenticación JWT

### Store de Autenticación (Zustand)

**src/stores/authStore.ts**
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '@/lib/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  dni: string
  rol_nombre: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  checkAuthStatus: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login/', {
            username,
            password
          })

          const { access, refresh, user } = response.data
          
          set({
            user,
            token: access,
            refreshToken: refresh,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false
        })
      },

      setToken: (token: string) => {
        set({ token })
      },

      checkAuthStatus: async () => {
        const token = get().token
        if (!token) return

        try {
          const response = await api.get('/auth/status/')
          set({ user: response.data.user, isAuthenticated: true })
        } catch (error) {
          get().logout()
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)
```

### Hook de Autenticación

**src/hooks/api/useAuth.ts**
```typescript
import { useMutation, useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import api from '@/lib/api'

export const useAuth = () => {
  const { login, logout, checkAuthStatus, user, isAuthenticated, isLoading } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      login(username, password),
    onSuccess: () => {
      // Redirect to dashboard or refresh page
      window.location.href = '/dashboard'
    }
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      await api.post('/auth/logout/')
      logout()
    },
    onSuccess: () => {
      window.location.href = '/login'
    }
  })

  const { data: authStatus } = useQuery({
    queryKey: ['auth-status'],
    queryFn: checkAuthStatus,
    enabled: isAuthenticated,
    refetchInterval: 5 * 60 * 1000, // Check every 5 minutes
  })

  return {
    user,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    loginError: loginMutation.error,
    logoutError: logoutMutation.error
  }
}
```

## 🗂️ Endpoints Disponibles

### Autenticación
- `POST /auth/login/` - Iniciar sesión
- `POST /auth/logout/` - Cerrar sesión
- `POST /auth/token/refresh/` - Renovar token
- `GET /auth/status/` - Estado de autenticación
- `GET /auth/profile/` - Perfil del usuario
- `PUT /auth/change-password/` - Cambiar contraseña

### Inventario
- `GET /api/inventory/gps/` - Listar dispositivos GPS
- `POST /api/inventory/gps/` - Crear dispositivo GPS
- `GET /api/inventory/gps/{id}/` - Detalle de GPS
- `PUT /api/inventory/gps/{id}/` - Actualizar GPS
- `DELETE /api/inventory/gps/{id}/` - Eliminar GPS

- `GET /api/inventory/simcards/` - Listar tarjetas SIM
- `POST /api/inventory/simcards/` - Crear tarjeta SIM
- `GET /api/inventory/simcards/{id}/` - Detalle de SIM
- `PUT /api/inventory/simcards/{id}/` - Actualizar SIM

- `GET /api/inventory/otros/` - Listar otros productos
- `POST /api/inventory/otros/` - Crear producto
- `PUT /api/inventory/otros/{id}/adjust-stock/` - Ajustar stock

### Ventas
- `GET /api/sales/ventas/` - Listar ventas
- `POST /api/sales/ventas/` - Crear venta
- `GET /api/sales/ventas/{id}/` - Detalle de venta
- `PUT /api/sales/ventas/{id}/` - Actualizar venta
- `GET /api/sales/ventas/stats/` - Estadísticas de ventas

### Entidades
- `GET /api/entities/clientes/` - Listar clientes
- `POST /api/entities/clientes/` - Crear cliente
- `GET /api/entities/clientes/{id}/` - Detalle de cliente
- `PUT /api/entities/clientes/{id}/` - Actualizar cliente

- `GET /api/entities/unidades/` - Listar unidades vehiculares
- `POST /api/entities/unidades/` - Crear unidad
- `GET /api/entities/unidades/{id}/` - Detalle de unidad

- `GET /api/entities/proveedores/` - Listar proveedores
- `POST /api/entities/proveedores/` - Crear proveedor

### Servicios
- `GET /api/services/servicios/` - Listar servicios
- `POST /api/services/servicios/` - Crear servicio
- `GET /api/services/tipos-trabajo/` - Listar tipos de trabajo

### Dashboard
- `GET /api/dashboard/kpis/` - KPIs del dashboard

## 💻 Ejemplos de Implementación

### Componente de Login

**src/components/features/auth/LoginForm.tsx**
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/hooks/api/useAuth'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required')
})

type LoginFormData = z.infer<typeof loginSchema>

export const LoginForm = () => {
  const { login, isLoading, loginError } = useAuth()
  
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  const onSubmit = (data: LoginFormData) => {
    login(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input
          {...register('username')}
          placeholder="Username"
          error={errors.username?.message}
        />
      </div>
      
      <div>
        <Input
          {...register('password')}
          type="password"
          placeholder="Password"
          error={errors.password?.message}
        />
      </div>

      {loginError && (
        <div className="text-red-500 text-sm">
          Error: {loginError.message}
        </div>
      )}

      <Button
        type="submit"
        isLoading={isLoading}
        className="w-full"
      >
        Iniciar Sesión
      </Button>
    </form>
  )
}
```

### Hook para Inventario

**src/hooks/api/useInventory.ts**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { GPS, SIMCard, OtroProducto } from '@/types/inventory'

// GPS Hooks
export const useGPSDevices = () => {
  return useQuery({
    queryKey: ['gps-devices'],
    queryFn: async () => {
      const response = await api.get('/api/inventory/gps/')
      return response.data
    }
  })
}

export const useCreateGPS = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: Partial<GPS>) => {
      const response = await api.post('/api/inventory/gps/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gps-devices'] })
    }
  })
}

export const useUpdateGPS = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<GPS> }) => {
      const response = await api.put(`/api/inventory/gps/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gps-devices'] })
    }
  })
}

// SIM Cards Hooks
export const useSIMCards = () => {
  return useQuery({
    queryKey: ['sim-cards'],
    queryFn: async () => {
      const response = await api.get('/api/inventory/simcards/')
      return response.data
    }
  })
}

export const useCreateSIMCard = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: Partial<SIMCard>) => {
      const response = await api.post('/api/inventory/simcards/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sim-cards'] })
    }
  })
}

// Otros Productos Hooks
export const useOtrosProductos = () => {
  return useQuery({
    queryKey: ['otros-productos'],
    queryFn: async () => {
      const response = await api.get('/api/inventory/otros/')
      return response.data
    }
  })
}

export const useAdjustStock = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ 
      id, 
      cantidad, 
      motivo 
    }: { 
      id: number; 
      cantidad: number; 
      motivo?: string 
    }) => {
      const response = await api.put(`/api/inventory/otros/${id}/adjust-stock/`, {
        cantidad,
        motivo
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['otros-productos'] })
    }
  })
}
```

### Componente de Lista de Inventario

**src/components/features/inventory/GPSList.tsx**
```typescript
import { useState } from 'react'
import { useGPSDevices, useUpdateGPS } from '@/hooks/api/useInventory'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { GPS } from '@/types/inventory'

export const GPSList = () => {
  const { data: gpsDevices, isLoading, error } = useGPSDevices()
  const updateGPS = useUpdateGPS()
  const [selectedGPS, setSelectedGPS] = useState<GPS | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleStatusChange = (gps: GPS, newStatus: string) => {
    updateGPS.mutate({
      id: gps.id,
      data: { estado: newStatus }
    })
  }

  if (isLoading) return <div>Cargando dispositivos GPS...</div>
  if (error) return <div>Error al cargar dispositivos</div>

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Dispositivos GPS</h2>
        <Button onClick={() => setIsModalOpen(true)}>
          Agregar GPS
        </Button>
      </div>

      <div className="grid gap-4">
        {gpsDevices?.map((gps: GPS) => (
          <div key={gps.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{gps.marca} {gps.modelo}</h3>
                <p className="text-gray-600">IMEI: {gps.imei}</p>
                <p className="text-sm">
                  Estado: 
                  <span className={`ml-1 px-2 py-1 rounded text-xs ${
                    gps.estado === 'no_asignado' ? 'bg-green-100 text-green-800' :
                    gps.estado === 'activo' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {gps.estado_display}
                  </span>
                </p>
                <p className="text-sm text-gray-500">
                  Proveedor: {gps.proveedor_info?.nombre}
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    setSelectedGPS(gps)
                    setIsModalOpen(true)
                  }}
                >
                  Editar
                </Button>
                
                <select
                  value={gps.estado}
                  onChange={(e) => handleStatusChange(gps, e.target.value)}
                  className="text-sm border rounded px-2 py-1"
                >
                  <option value="disponible">Disponible</option>
                  <option value="activo">Activo</option>
                  <option value="asignado">Asignado</option>
                  <option value="en_mantenimiento">En Mantenimiento</option>
                  <option value="dañado">Dañado</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedGPS(null)
        }}
        title={selectedGPS ? 'Editar GPS' : 'Agregar GPS'}
      >
        {/* GPS Form Component */}
      </Modal>
    </div>
  )
}
```

## ✅ Validaciones con Zod

**src/lib/validations.ts**
```typescript
import { z } from 'zod'

// Validaciones para GPS
export const gpsSchema = z.object({
  fecha_compra: z.string().min(1, 'Fecha de compra es requerida'),
  imei: z.string()
    .length(15, 'IMEI debe tener 15 dígitos')
    .regex(/^\d{15}$/, 'IMEI debe contener solo números'),
  marca: z.string().min(1, 'Marca es requerida').max(20),
  modelo: z.string().min(1, 'Modelo es requerido').max(20),
  numero_factura: z.string().min(1, 'Número de factura es requerido').max(20),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja']),
  precio_compra: z.number().min(0).optional(),
  observaciones: z.string().optional()
})

// Validaciones para SIM Card
export const simCardSchema = z.object({
  fecha_compra: z.string().min(1, 'Fecha de compra es requerida'),
  numero_factura: z.string().min(1, 'Número de factura es requerido').max(20),
  numero_chip: z.string()
    .length(9, 'Número de chip debe tener 9 dígitos')
    .regex(/^\d{9}$/, 'Número de chip debe contener solo números'),
  icc: z.string().min(1, 'ICC es requerido').max(20),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja']),
  operadora: z.string().max(50).optional(),
  plan: z.string().max(100).optional(),
  precio_compra: z.number().min(0).optional(),
  observaciones: z.string().optional()
})

// Validaciones para Ventas
export const ventaSchema = z.object({
  mes: z.string().min(1, 'Mes es requerido'),
  fecha_pago: z.string().min(1, 'Hora de pago es requerida'),
  numero_operacion: z.string().min(1, 'Número de operación es requerido').max(10),
  tipo_pago: z.enum(['efectivo', 'transferencia', 'deposito', 'cheque', 'tarjeta_credito', 'tarjeta_debito', 'yape', 'plin', 'otro']),
  banco: z.string().min(1, 'Banco es requerido'),
  numero_factura: z.string().min(1, 'Número de factura es requerido').max(10),
  fecha_generacion_factura: z.string().min(1, 'Fecha de factura es requerida'),
  cliente: z.number().min(1, 'Cliente es requerido'),
  descripcion: z.string().min(1, 'Descripción es requerida'),
  unidad: z.number().min(1, 'Unidad es requerida'),
  precio: z.number().min(0.01, 'Precio debe ser mayor a 0'),
  estado: z.enum(['pendiente', 'pagado', 'parcial', 'vencido', 'cancelado', 'anulado']).default('pendiente')
})

// Validaciones para Cliente
export const clienteSchema = z.object({
  nombre: z.string().min(1, 'Nombre es requerido').max(200),
  ruc: z.string()
    .length(11, 'RUC debe tener 11 dígitos')
    .regex(/^\d{11}$/, 'RUC debe contener solo números'),
  direccion: z.string().min(1, 'Dirección es requerida'),
  contacto: z.string().min(1, 'Contacto es requerido').max(100),
  celular: z.string()
    .length(9, 'Celular debe tener 9 dígitos')
    .regex(/^\d{9}$/, 'Celular debe contener solo números'),
  correo: z.string().email('Email inválido')
})

// Validaciones para Unidad Vehicular
export const unidadSchema = z.object({
  tipo: z.enum(['bus', 'camion', 'otro']),
  placa: z.string()
    .min(6, 'Placa debe tener al menos 6 caracteres')
    .max(10, 'Placa debe tener máximo 10 caracteres')
    .regex(/^[A-Z0-9-]{6,10}$/, 'Formato de placa inválido'),
  marca: z.string().min(1, 'Marca es requerida').max(50),
  modelo: z.string().min(1, 'Modelo es requerido').max(50),
  serie: z.string().min(1, 'Serie es requerida').max(50),
  cliente: z.number().min(1, 'Cliente es requerido')
})

export type GPSFormData = z.infer<typeof gpsSchema>
export type SIMCardFormData = z.infer<typeof simCardSchema>
export type VentaFormData = z.infer<typeof ventaSchema>
export type ClienteFormData = z.infer<typeof clienteSchema>
export type UnidadFormData = z.infer<typeof unidadSchema>
```

## 🚨 Manejo de Errores

**src/lib/errorHandler.ts**
```typescript
import { AxiosError } from 'axios'
import { toast } from '@/components/ui/Toast'

export interface APIError {
  message: string
  field?: string
  code?: string
}

export const handleAPIError = (error: unknown): APIError => {
  if (error instanceof AxiosError) {
    // Error de respuesta del servidor
    if (error.response?.data) {
      const data = error.response.data
      
      // Error de validación de campos
      if (typeof data === 'object' && !data.message) {
        const firstField = Object.keys(data)[0]
        const firstError = Array.isArray(data[firstField]) 
          ? data[firstField][0] 
          : data[firstField]
        
        return {
          message: firstError,
          field: firstField,
          code: error.response.status.toString()
        }
      }
      
      // Error con mensaje específico
      if (data.message || data.detail) {
        return {
          message: data.message || data.detail,
          code: error.response.status.toString()
        }
      }
    }
    
    // Error de red o timeout
    if (error.code === 'ECONNABORTED') {
      return {
        message: 'La petición tardó demasiado tiempo. Intenta nuevamente.',
        code: 'TIMEOUT'
      }
    }
    
    if (error.code === 'ERR_NETWORK') {
      return {
        message: 'Error de conexión. Verifica tu conexión a internet.',
        code: 'NETWORK_ERROR'
      }
    }
    
    // Error HTTP genérico
    return {
      message: `Error ${error.response?.status}: ${error.message}`,
      code: error.response?.status.toString()
    }
  }
  
  // Error desconocido
  return {
    message: 'Ha ocurrido un error inesperado. Intenta nuevamente.',
    code: 'UNKNOWN_ERROR'
  }
}

// Hook para manejo de errores con toast
export const useErrorHandler = () => {
  const showError = (error: unknown) => {
    const apiError = handleAPIError(error)
    toast.error(apiError.message)
    return apiError
  }
  
  return { showError }
}
```

## 🧪 Testing

### Configuración de Testing

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event jsdom
```

**vitest.config.ts**
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**src/test/setup.ts**
```typescript
import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from './mocks/server'

// Establish API mocking before all tests
beforeAll(() => server.listen())

// Reset any request handlers that we may add during the tests
afterEach(() => server.resetHandlers())

// Clean up after the tests are finished
afterAll(() => server.close())
```

### Ejemplo de Test para Hook de Autenticación

**src/hooks/api/__tests__/useAuth.test.ts**
```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuth } from '../useAuth'
import { useAuthStore } from '@/stores/authStore'

// Mock del store
vi.mock('@/stores/authStore')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useAuth', () => {
  it('should login successfully', async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined)
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      logout: vi.fn(),
      checkAuthStatus: vi.fn(),
      token: null,
      refreshToken: null,
      setToken: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    })

    result.current.login({ username: 'testuser', password: 'password123' })

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123')
    })
  })

  it('should handle login error', async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      logout: vi.fn(),
      checkAuthStatus: vi.fn(),
      token: null,
      refreshToken: null,
      setToken: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    })

    result.current.login({ username: 'testuser', password: 'wrongpassword' })

    await waitFor(() => {
      expect(result.current.loginError).toBeDefined()
    })
  })
})
```

### Test para Componente de Login

**src/components/features/auth/__tests__/LoginForm.test.tsx**
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LoginForm } from '../LoginForm'

// Mock del hook useAuth
vi.mock('@/hooks/api/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    isLoading: false,
    loginError: null,
  }),
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('LoginForm', () => {
  it('should render login form', () => {
    render(<LoginForm />, { wrapper: createWrapper() })
    
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
  })

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginForm />, { wrapper: createWrapper() })
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument()
      expect(screen.getByText('Password is required')).toBeInTheDocument()
    })
  })

  it('should submit form with valid data', async () => {
    const user = userEvent.setup()
    const mockLogin = vi.fn()
    
    vi.doMock('@/hooks/api/useAuth', () => ({
      useAuth: () => ({
        login: mockLogin,
        isLoading: false,
        loginError: null,
      }),
    }))
    
    render(<LoginForm />, { wrapper: createWrapper() })
    
    await user.type(screen.getByPlaceholderText('Username'), 'testuser')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      })
    })
  })
})
```

## 🔧 Variables de Entorno

**`.env.development`**
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=Sistema de Gestión
VITE_APP_VERSION=1.0.0
```

**`.env.production`**
```env
VITE_API_URL=https://your-production-api.com
VITE_APP_NAME=Sistema de Gestión
VITE_APP_VERSION=1.0.0
```

## 📝 Notas Importantes

1. **Autenticación**: El backend usa JWT con refresh tokens. Asegúrate de manejar la renovación automática.

2. **CORS**: El backend está configurado para desarrollo local. Para producción, actualiza `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS`.

3. **Validaciones**: Usa las mismas validaciones del backend en el frontend para mejor UX.

4. **Estados de Carga**: Siempre maneja estados de loading y error en tus componentes.

5. **Optimización**: Usa React Query para cache automático y optimistic updates.

6. **Seguridad**: Nunca expongas tokens en logs o console. Usa HTTPS en producción.

7. **Performance**: Implementa lazy loading para páginas y componentes pesados.

## 🚀 Comandos Útiles

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Tests
npm run test

# Tests con coverage
npm run test:coverage

# Linting
npm run lint

# Type checking
npm run type-check
```

---

Esta guía te proporciona una base sólida para integrar tu frontend React + Vite con el backend Django. Adapta los ejemplos según tus necesidades específicas y mantén siempre las mejores prácticas de desarrollo.