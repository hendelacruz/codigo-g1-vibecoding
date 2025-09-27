# 🛠️ Módulo Services - Guía de Implementación Paso a Paso

## React + TypeScript + Vite + Redux Toolkit

### 📋 Resumen del Módulo Services

El módulo **Services** gestiona servicios técnicos realizados a clientes, siguiendo la arquitectura establecida en tu proyecto:

- **TipoTrabajo**: Categorías de servicios (instalación, mantenimiento, etc.)
- **Servicio**: Trabajos realizados en unidades vehiculares
- **Estados**: pendiente, en_proceso, completado, cancelado, reprogramado
- **Relaciones**: Cliente, Unidad, Técnico, GPS, SIM Card

---

## 🎯 PASO 1: Crear la Estructura del Feature

### 1.1 Crear la carpeta del módulo Services

```bash
mkdir -p src/features/services
mkdir -p src/features/services/components
mkdir -p src/features/services/hooks
mkdir -p src/features/services/__tests__
```

### 1.2 Estructura final esperada

```
src/features/services/
├── servicesTypes.ts           # Interfaces TypeScript
├── servicesAPI.ts             # Servicios API con axios
├── servicesSlice.ts           # Redux slice con async thunks
├── validations.ts             # Esquemas Zod para validación
├── index.ts                   # Punto de entrada del módulo
├── useServices.ts             # Hook personalizado principal
├── hooks/
│   ├── useTipoTrabajo.ts      # Hook para tipos de trabajo
│   ├── useServicio.ts         # Hook para servicios
│   └── useServiceFilters.ts   # Hook para filtros
├── components/
│   ├── ServicesPage.tsx       # Página principal
│   ├── ServicesDashboard.tsx  # Dashboard con estadísticas
│   ├── TipoTrabajoList.tsx    # Lista de tipos de trabajo
│   ├── TipoTrabajoForm.tsx    # Formulario tipo trabajo
│   ├── ServicioList.tsx       # Lista de servicios
│   ├── ServicioForm.tsx       # Formulario de servicio
│   ├── ServicioCard.tsx       # Tarjeta de servicio
│   ├── ServicioFilters.tsx    # Filtros de servicios
│   └── shared/
│       ├── ServiceStatusBadge.tsx
│       ├── ServiceTypeSelect.tsx
│       └── ServiceDatePicker.tsx
└── __tests__/
    ├── services-crud-test.ts  # Tests manuales
    └── services.test.tsx      # Tests unitarios
```

---

## 🔧 PASO 2: Implementar Types (servicesTypes.ts)

Crear el archivo `src/features/services/servicesTypes.ts`:

```typescript
/**
 * Types para el módulo de servicios
 * Incluye interfaces para TipoTrabajo y Servicio
 */

// ==================== TIPO TRABAJO INTERFACES ====================

export interface TipoTrabajo {
  id: number
  nombre: string
  descripcion?: string
  precio_base?: number
  duracion_estimada?: number // en minutos
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateTipoTrabajoData {
  nombre: string
  descripcion?: string
  precio_base?: number
  duracion_estimada?: number
  is_active?: boolean
}

export interface UpdateTipoTrabajoData extends Partial<CreateTipoTrabajoData> {}

// ==================== SERVICIO INTERFACES ====================

export type EstadoServicio = 'pendiente' | 'en_proceso' | 'completado' | 'cancelado' | 'reprogramado'

export interface Servicio {
  id: number
  fecha_programada: string
  fecha_inicio?: string
  fecha_fin?: string
  estado: EstadoServicio
  observaciones?: string
  precio_final?: number
  created_at: string
  updated_at: string
  
  // Relaciones
  cliente_id: number
  unidad_id: number
  tipo_trabajo_id: number
  tecnico_id?: number
  
  // Información relacionada (populated)
  cliente_info?: {
    id: number
    nombre: string
  }
  unidad_info?: {
    id: number
    placa: string
    marca: string
    modelo: string
  }
  tipo_trabajo_info?: {
    id: number
    nombre: string
    precio_base?: number
  }
  tecnico_info?: {
    id: number
    nombre: string
  }
}

export interface CreateServicioData {
  fecha_programada: string
  estado?: EstadoServicio
  observaciones?: string
  precio_final?: number
  cliente_id: number
  unidad_id: number
  tipo_trabajo_id: number
  tecnico_id?: number
}

export interface UpdateServicioData extends Partial<CreateServicioData> {}

// ==================== FILTERS ====================

export interface TipoTrabajoFilters {
  search?: string
  is_active?: boolean
  precio_min?: number
  precio_max?: number
}

export interface ServicioFilters {
  search?: string
  estado?: EstadoServicio
  cliente_id?: number
  unidad_id?: number
  tipo_trabajo_id?: number
  tecnico_id?: number
  fecha_desde?: string
  fecha_hasta?: string
}

// ==================== STATE INTERFACES ====================

export interface ServicesState {
  tipoTrabajos: {
    items: TipoTrabajo[]
    isLoading: boolean
    error: string | null
  }
  servicios: {
    items: Servicio[]
    isLoading: boolean
    error: string | null
  }
  stats: ServicesStats | null
}

export interface ServicesStats {
  totalServicios: number
  serviciosPendientes: number
  serviciosEnProceso: number
  serviciosCompletados: number
  serviciosCancelados: number
  serviciosReprogramados: number
  totalTipoTrabajos: number
  tipoTrabajosActivos: number
}

// ==================== API RESPONSES ====================

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ServicesAPIResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface APIError {
  message: string
  status?: number
  details?: Record<string, string[]>
}

// ==================== CONSTANTS ====================

export const ESTADO_SERVICIO_OPTIONS = [
  { value: 'pendiente', label: 'Pendiente', color: 'yellow' },
  { value: 'en_proceso', label: 'En Proceso', color: 'blue' },
  { value: 'completado', label: 'Completado', color: 'green' },
  { value: 'cancelado', label: 'Cancelado', color: 'red' },
  { value: 'reprogramado', label: 'Reprogramado', color: 'orange' }
] as const

// ==================== TYPE GUARDS ====================

export const isTipoTrabajo = (entity: unknown): entity is TipoTrabajo => {
  return (
    typeof entity === 'object' &&
    entity !== null &&
    'id' in entity &&
    'nombre' in entity &&
    'is_active' in entity
  )
}

export const isServicio = (entity: unknown): entity is Servicio => {
  return (
    typeof entity === 'object' &&
    entity !== null &&
    'id' in entity &&
    'estado' in entity &&
    'cliente_id' in entity &&
    'unidad_id' in entity &&
    'tipo_trabajo_id' in entity
  )
}

export type ServiceEntityType = 'tipoTrabajos' | 'servicios'
```

---

## 🌐 PASO 3: Implementar API Layer (servicesAPI.ts)

Crear el archivo `src/features/services/servicesAPI.ts`:

```typescript
import { api } from '../../shared/lib/api'
import type {
  TipoTrabajo,
  Servicio,
  CreateTipoTrabajoData,
  UpdateTipoTrabajoData,
  CreateServicioData,
  UpdateServicioData,
  TipoTrabajoFilters,
  ServicioFilters,
  PaginatedResponse,
  ServicesStats
} from './servicesTypes'

// ==================== TIPO TRABAJO API ====================

export const tipoTrabajoAPI = {
  // Listar tipos de trabajo
  list: async (filters?: TipoTrabajoFilters): Promise<PaginatedResponse<TipoTrabajo>> => {
    const params = new URLSearchParams()
    
    if (filters?.search) params.append('search', filters.search)
    if (filters?.is_active !== undefined) params.append('is_active', String(filters.is_active))
    if (filters?.precio_min) params.append('precio_min', String(filters.precio_min))
    if (filters?.precio_max) params.append('precio_max', String(filters.precio_max))
    
    const response = await api.get(`/services/tipos-trabajo/?${params}`)
    return response.data
  },

  // Obtener tipo de trabajo por ID
  getById: async (id: number): Promise<TipoTrabajo> => {
    const response = await api.get(`/services/tipos-trabajo/${id}/`)
    return response.data
  },

  // Crear tipo de trabajo
  create: async (data: CreateTipoTrabajoData): Promise<TipoTrabajo> => {
    const response = await api.post('/services/tipos-trabajo/', data)
    return response.data
  },

  // Actualizar tipo de trabajo
  update: async (id: number, data: UpdateTipoTrabajoData): Promise<TipoTrabajo> => {
    const response = await api.put(`/services/tipos-trabajo/${id}/`, data)
    return response.data
  },

  // Eliminar tipo de trabajo
  delete: async (id: number): Promise<void> => {
    await api.delete(`/services/tipos-trabajo/${id}/`)
  },

  // Toggle activo/inactivo
  toggleActive: async (id: number): Promise<TipoTrabajo> => {
    const response = await api.patch(`/services/tipos-trabajo/${id}/toggle-active/`)
    return response.data
  }
}

// ==================== SERVICIO API ====================

export const servicioAPI = {
  // Listar servicios
  list: async (filters?: ServicioFilters): Promise<PaginatedResponse<Servicio>> => {
    const params = new URLSearchParams()
    
    if (filters?.search) params.append('search', filters.search)
    if (filters?.estado) params.append('estado', filters.estado)
    if (filters?.cliente_id) params.append('cliente_id', String(filters.cliente_id))
    if (filters?.unidad_id) params.append('unidad_id', String(filters.unidad_id))
    if (filters?.tipo_trabajo_id) params.append('tipo_trabajo_id', String(filters.tipo_trabajo_id))
    if (filters?.tecnico_id) params.append('tecnico_id', String(filters.tecnico_id))
    if (filters?.fecha_desde) params.append('fecha_desde', filters.fecha_desde)
    if (filters?.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta)
    
    const response = await api.get(`/services/servicios/?${params}`)
    return response.data
  },

  // Obtener servicio por ID
  getById: async (id: number): Promise<Servicio> => {
    const response = await api.get(`/services/servicios/${id}/`)
    return response.data
  },

  // Crear servicio
  create: async (data: CreateServicioData): Promise<Servicio> => {
    const response = await api.post('/services/servicios/', data)
    return response.data
  },

  // Actualizar servicio
  update: async (id: number, data: UpdateServicioData): Promise<Servicio> => {
    const response = await api.put(`/services/servicios/${id}/`, data)
    return response.data
  },

  // Eliminar servicio
  delete: async (id: number): Promise<void> => {
    await api.delete(`/services/servicios/${id}/`)
  },

  // Cambiar estado del servicio
  changeStatus: async (id: number, estado: string): Promise<Servicio> => {
    const response = await api.patch(`/services/servicios/${id}/change-status/`, { estado })
    return response.data
  }
}

// ==================== STATS API ====================

export const servicesStatsAPI = {
  // Obtener estadísticas generales
  getStats: async (): Promise<ServicesStats> => {
    const response = await api.get('/services/stats/')
    return response.data
  }
}

// ==================== MAIN API EXPORT ====================

export const servicesAPI = {
  tipoTrabajo: tipoTrabajoAPI,
  servicio: servicioAPI,
  stats: servicesStatsAPI
}
```

---

## 🔄 PASO 4: Implementar Redux Slice (servicesSlice.ts)

Crear el archivo `src/features/services/servicesSlice.ts`:

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { servicesAPI } from './servicesAPI'
import type {
  ServicesState,
  TipoTrabajo,
  Servicio,
  CreateTipoTrabajoData,
  UpdateTipoTrabajoData,
  CreateServicioData,
  UpdateServicioData,
  TipoTrabajoFilters,
  ServicioFilters,
  ServicesStats
} from './servicesTypes'

// ==================== INITIAL STATE ====================

const initialState: ServicesState = {
  tipoTrabajos: {
    items: [],
    isLoading: false,
    error: null
  },
  servicios: {
    items: [],
    isLoading: false,
    error: null
  },
  stats: null
}

// ==================== TIPO TRABAJO ASYNC THUNKS ====================

export const fetchTipoTrabajos = createAsyncThunk(
  'services/fetchTipoTrabajos',
  async (filters?: TipoTrabajoFilters) => {
    const response = await servicesAPI.tipoTrabajo.list(filters)
    return response.results
  }
)

export const fetchTipoTrabajo = createAsyncThunk(
  'services/fetchTipoTrabajo',
  async (id: number) => {
    return await servicesAPI.tipoTrabajo.getById(id)
  }
)

export const createTipoTrabajo = createAsyncThunk(
  'services/createTipoTrabajo',
  async (data: CreateTipoTrabajoData) => {
    return await servicesAPI.tipoTrabajo.create(data)
  }
)

export const updateTipoTrabajo = createAsyncThunk(
  'services/updateTipoTrabajo',
  async ({ id, data }: { id: number; data: UpdateTipoTrabajoData }) => {
    return await servicesAPI.tipoTrabajo.update(id, data)
  }
)

export const deleteTipoTrabajo = createAsyncThunk(
  'services/deleteTipoTrabajo',
  async (id: number) => {
    await servicesAPI.tipoTrabajo.delete(id)
    return id
  }
)

export const toggleTipoTrabajoActive = createAsyncThunk(
  'services/toggleTipoTrabajoActive',
  async (id: number) => {
    return await servicesAPI.tipoTrabajo.toggleActive(id)
  }
)

// ==================== SERVICIO ASYNC THUNKS ====================

export const fetchServicios = createAsyncThunk(
  'services/fetchServicios',
  async (filters?: ServicioFilters) => {
    const response = await servicesAPI.servicio.list(filters)
    return response.results
  }
)

export const fetchServicio = createAsyncThunk(
  'services/fetchServicio',
  async (id: number) => {
    return await servicesAPI.servicio.getById(id)
  }
)

export const createServicio = createAsyncThunk(
  'services/createServicio',
  async (data: CreateServicioData) => {
    return await servicesAPI.servicio.create(data)
  }
)

export const updateServicio = createAsyncThunk(
  'services/updateServicio',
  async ({ id, data }: { id: number; data: UpdateServicioData }) => {
    return await servicesAPI.servicio.update(id, data)
  }
)

export const deleteServicio = createAsyncThunk(
  'services/deleteServicio',
  async (id: number) => {
    await servicesAPI.servicio.delete(id)
    return id
  }
)

export const changeServicioStatus = createAsyncThunk(
  'services/changeServicioStatus',
  async ({ id, estado }: { id: number; estado: string }) => {
    return await servicesAPI.servicio.changeStatus(id, estado)
  }
)

// ==================== STATS ASYNC THUNKS ====================

export const fetchServicesStats = createAsyncThunk(
  'services/fetchStats',
  async () => {
    return await servicesAPI.stats.getStats()
  }
)

// ==================== SLICE ====================

const servicesSlice = createSlice({
  name: 'services',
  initialState,
  reducers: {
    clearServicesErrors: (state) => {
      state.tipoTrabajos.error = null
      state.servicios.error = null
    },
    clearTipoTrabajosError: (state) => {
      state.tipoTrabajos.error = null
    },
    clearServiciosError: (state) => {
      state.servicios.error = null
    }
  },
  extraReducers: (builder) => {
    // ==================== TIPO TRABAJO REDUCERS ====================
    
    // Fetch TipoTrabajos
    builder
      .addCase(fetchTipoTrabajos.pending, (state) => {
        state.tipoTrabajos.isLoading = true
        state.tipoTrabajos.error = null
      })
      .addCase(fetchTipoTrabajos.fulfilled, (state, action) => {
        state.tipoTrabajos.isLoading = false
        state.tipoTrabajos.items = action.payload
      })
      .addCase(fetchTipoTrabajos.rejected, (state, action) => {
        state.tipoTrabajos.isLoading = false
        state.tipoTrabajos.error = action.error.message || 'Error al cargar tipos de trabajo'
      })

    // Create TipoTrabajo
    builder
      .addCase(createTipoTrabajo.fulfilled, (state, action) => {
        state.tipoTrabajos.items.push(action.payload)
      })

    // Update TipoTrabajo
    builder
      .addCase(updateTipoTrabajo.fulfilled, (state, action) => {
        const index = state.tipoTrabajos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.tipoTrabajos.items[index] = action.payload
        }
      })

    // Delete TipoTrabajo
    builder
      .addCase(deleteTipoTrabajo.fulfilled, (state, action) => {
        state.tipoTrabajos.items = state.tipoTrabajos.items.filter(item => item.id !== action.payload)
      })

    // Toggle TipoTrabajo Active
    builder
      .addCase(toggleTipoTrabajoActive.fulfilled, (state, action) => {
        const index = state.tipoTrabajos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.tipoTrabajos.items[index] = action.payload
        }
      })

    // ==================== SERVICIO REDUCERS ====================
    
    // Fetch Servicios
    builder
      .addCase(fetchServicios.pending, (state) => {
        state.servicios.isLoading = true
        state.servicios.error = null
      })
      .addCase(fetchServicios.fulfilled, (state, action) => {
        state.servicios.isLoading = false
        state.servicios.items = action.payload
      })
      .addCase(fetchServicios.rejected, (state, action) => {
        state.servicios.isLoading = false
        state.servicios.error = action.error.message || 'Error al cargar servicios'
      })

    // Create Servicio
    builder
      .addCase(createServicio.fulfilled, (state, action) => {
        state.servicios.items.push(action.payload)
      })

    // Update Servicio
    builder
      .addCase(updateServicio.fulfilled, (state, action) => {
        const index = state.servicios.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.servicios.items[index] = action.payload
        }
      })

    // Delete Servicio
    builder
      .addCase(deleteServicio.fulfilled, (state, action) => {
        state.servicios.items = state.servicios.items.filter(item => item.id !== action.payload)
      })

    // Change Servicio Status
    builder
      .addCase(changeServicioStatus.fulfilled, (state, action) => {
        const index = state.servicios.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.servicios.items[index] = action.payload
        }
      })

    // ==================== STATS REDUCERS ====================
    
    builder
      .addCase(fetchServicesStats.fulfilled, (state, action) => {
        state.stats = action.payload
      })
  }
})

export const {
  clearServicesErrors,
  clearTipoTrabajosError,
  clearServiciosError
} = servicesSlice.actions

export default servicesSlice.reducer
```

---

## ✅ PASO 5: Implementar Validaciones (validations.ts)

Crear el archivo `src/features/services/validations.ts`:

```typescript
import { z } from 'zod'

// ==================== TIPO TRABAJO VALIDATIONS ====================

export const createTipoTrabajoSchema = z.object({
  nombre: z.string()
    .min(1, 'El nombre es requerido')
    .max(100, 'El nombre no puede exceder 100 caracteres'),
  descripcion: z.string()
    .max(500, 'La descripción no puede exceder 500 caracteres')
    .optional(),
  precio_base: z.number()
    .min(0, 'El precio base debe ser mayor o igual a 0')
    .optional(),
  duracion_estimada: z.number()
    .min(1, 'La duración estimada debe ser mayor a 0 minutos')
    .optional(),
  is_active: z.boolean().optional().default(true)
})

export const updateTipoTrabajoSchema = createTipoTrabajoSchema.partial()

// ==================== SERVICIO VALIDATIONS ====================

export const createServicioSchema = z.object({
  fecha_programada: z.string()
    .min(1, 'La fecha programada es requerida'),
  estado: z.enum(['pendiente', 'en_proceso', 'completado', 'cancelado', 'reprogramado'])
    .optional()
    .default('pendiente'),
  observaciones: z.string()
    .max(1000, 'Las observaciones no pueden exceder 1000 caracteres')
    .optional(),
  precio_final: z.number()
    .min(0, 'El precio final debe ser mayor o igual a 0')
    .optional(),
  cliente_id: z.number()
    .min(1, 'Debe seleccionar un cliente'),
  unidad_id: z.number()
    .min(1, 'Debe seleccionar una unidad'),
  tipo_trabajo_id: z.number()
    .min(1, 'Debe seleccionar un tipo de trabajo'),
  tecnico_id: z.number()
    .min(1, 'Debe seleccionar un técnico')
    .optional()
})

export const updateServicioSchema = createServicioSchema.partial()

// ==================== FILTER VALIDATIONS ====================

export const tipoTrabajoFiltersSchema = z.object({
  search: z.string().optional(),
  is_active: z.boolean().optional(),
  precio_min: z.number().min(0).optional(),
  precio_max: z.number().min(0).optional()
})

export const servicioFiltersSchema = z.object({
  search: z.string().optional(),
  estado: z.enum(['pendiente', 'en_proceso', 'completado', 'cancelado', 'reprogramado']).optional(),
  cliente_id: z.number().optional(),
  unidad_id: z.number().optional(),
  tipo_trabajo_id: z.number().optional(),
  tecnico_id: z.number().optional(),
  fecha_desde: z.string().optional(),
  fecha_hasta: z.string().optional()
})

// ==================== INFERRED TYPES ====================

export type CreateTipoTrabajoFormData = z.infer<typeof createTipoTrabajoSchema>
export type UpdateTipoTrabajoFormData = z.infer<typeof updateTipoTrabajoSchema>
export type CreateServicioFormData = z.infer<typeof createServicioSchema>
export type UpdateServicioFormData = z.infer<typeof updateServicioSchema>
export type TipoTrabajoFiltersFormData = z.infer<typeof tipoTrabajoFiltersSchema>
export type ServicioFiltersFormData = z.infer<typeof servicioFiltersSchema>
```

---

## 🎣 PASO 6: Implementar Hook Principal (useServices.ts)

Crear el archivo `src/features/services/useServices.ts`:

```typescript
import { useAppDispatch, useAppSelector } from '../../shared/hooks/redux'
import {
  fetchTipoTrabajos,
  fetchTipoTrabajo,
  createTipoTrabajo,
  updateTipoTrabajo,
  deleteTipoTrabajo,
  toggleTipoTrabajoActive,
  fetchServicios,
  fetchServicio,
  createServicio,
  updateServicio,
  deleteServicio,
  changeServicioStatus,
  fetchServicesStats,
  clearServicesErrors,
  clearTipoTrabajosError,
  clearServiciosError
} from './servicesSlice'
import type {
  CreateTipoTrabajoData,
  UpdateTipoTrabajoData,
  CreateServicioData,
  UpdateServicioData,
  TipoTrabajoFilters,
  ServicioFilters
} from './servicesTypes'

export const useServices = () => {
  const dispatch = useAppDispatch()
  const servicesState = useAppSelector((state) => state.services)

  // ==================== TIPO TRABAJO OPERATIONS ====================

  const tipoTrabajoOperations = {
    // Fetch operations
    fetchAll: (filters?: TipoTrabajoFilters) => dispatch(fetchTipoTrabajos(filters)),
    fetchById: (id: number) => dispatch(fetchTipoTrabajo(id)),
    
    // CRUD operations
    create: (data: CreateTipoTrabajoData) => dispatch(createTipoTrabajo(data)),
    update: (id: number, data: UpdateTipoTrabajoData) => 
      dispatch(updateTipoTrabajo({ id, data })),
    delete: (id: number) => dispatch(deleteTipoTrabajo(id)),
    toggleActive: (id: number) => dispatch(toggleTipoTrabajoActive(id)),
    
    // Error handling
    clearError: () => dispatch(clearTipoTrabajosError())
  }

  // ==================== SERVICIO OPERATIONS ====================

  const servicioOperations = {
    // Fetch operations
    fetchAll: (filters?: ServicioFilters) => dispatch(fetchServicios(filters)),
    fetchById: (id: number) => dispatch(fetchServicio(id)),
    
    // CRUD operations
    create: (data: CreateServicioData) => dispatch(createServicio(data)),
    update: (id: number, data: UpdateServicioData) => 
      dispatch(updateServicio({ id, data })),
    delete: (id: number) => dispatch(deleteServicio(id)),
    changeStatus: (id: number, estado: string) => 
      dispatch(changeServicioStatus({ id, estado })),
    
    // Error handling
    clearError: () => dispatch(clearServiciosError())
  }

  // ==================== STATS OPERATIONS ====================

  const statsOperations = {
    fetchStats: () => dispatch(fetchServicesStats())
  }

  // ==================== GENERAL OPERATIONS ====================

  const generalOperations = {
    clearAllErrors: () => dispatch(clearServicesErrors())
  }

  return {
    // State
    tipoTrabajos: servicesState.tipoTrabajos,
    servicios: servicesState.servicios,
    stats: servicesState.stats,
    
    // Operations
    tipoTrabajo: tipoTrabajoOperations,
    servicio: servicioOperations,
    stats: statsOperations,
    general: generalOperations
  }
}
```

---

## 📦 PASO 7: Crear el Index del Módulo (index.ts)

Crear el archivo `src/features/services/index.ts`:

```typescript
// Components
export { ServicesPage } from './components/ServicesPage'
export { ServicesDashboard } from './components/ServicesDashboard'
export { TipoTrabajoList } from './components/TipoTrabajoList'
export { TipoTrabajoForm } from './components/TipoTrabajoForm'
export { ServicioList } from './components/ServicioList'
export { ServicioForm } from './components/ServicioForm'
export { ServicioCard } from './components/ServicioCard'
export { ServicioFilters } from './components/ServicioFilters'

// Shared Components
export { ServiceStatusBadge } from './components/shared/ServiceStatusBadge'
export { ServiceTypeSelect } from './components/shared/ServiceTypeSelect'
export { ServiceDatePicker } from './components/shared/ServiceDatePicker'

// Hooks
export { useServices } from './useServices'

// Types
export type {
  TipoTrabajo,
  Servicio,
  EstadoServicio,
  CreateTipoTrabajoData,
  UpdateTipoTrabajoData,
  CreateServicioData,
  UpdateServicioData,
  TipoTrabajoFilters,
  ServicioFilters,
  ServicesState,
  ServicesStats,
  PaginatedResponse,
  ServicesAPIResponse,
  APIError,
  ServiceEntityType
} from './servicesTypes'

// Redux slice
export { default as servicesReducer } from './servicesSlice'
export {
  fetchTipoTrabajos,
  fetchTipoTrabajo,
  createTipoTrabajo,
  updateTipoTrabajo,
  deleteTipoTrabajo,
  toggleTipoTrabajoActive,
  fetchServicios,
  fetchServicio,
  createServicio,
  updateServicio,
  deleteServicio,
  changeServicioStatus,
  fetchServicesStats,
  clearServicesErrors,
  clearTipoTrabajosError,
  clearServiciosError
} from './servicesSlice'

// API
export { servicesAPI } from './servicesAPI'

// Validations
export {
  createTipoTrabajoSchema,
  updateTipoTrabajoSchema,
  createServicioSchema,
  updateServicioSchema,
  tipoTrabajoFiltersSchema,
  servicioFiltersSchema
} from './validations'

export type {
  CreateTipoTrabajoFormData,
  UpdateTipoTrabajoFormData,
  CreateServicioFormData,
  UpdateServicioFormData,
  TipoTrabajoFiltersFormData,
  ServicioFiltersFormData
} from './validations'
```

---

## 🏪 PASO 8: Integrar con Redux Store

### 8.1 Actualizar el rootReducer

Editar `src/app/rootReducer.ts` para incluir el reducer de services:

```typescript
import { combineReducers } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import inventoryReducer from '../features/inventory/inventorySlice'
import entitiesReducer from '../features/entities/entitiesSlice'
import servicesReducer from '../features/services/servicesSlice' // ← AGREGAR

const rootReducer = combineReducers({
  auth: authReducer,
  inventory: inventoryReducer,
  entities: entitiesReducer,
  services: servicesReducer // ← AGREGAR
})

export type RootState = ReturnType<typeof rootReducer>
export default rootReducer
```

---

## 🧪 PASO 9: Crear Test Manual (Opcional)

Crear el archivo `src/features/services/__tests__/services-crud-test.ts`:

```typescript
/**
 * Test manual para el módulo Services
 * Ejecutar desde la consola del navegador
 */

import { store } from '../../../app/store'
import {
  fetchTipoTrabajos,
  createTipoTrabajo,
  fetchServicios,
  createServicio,
  fetchServicesStats
} from '../servicesSlice'

// Test data
const testTipoTrabajo = {
  nombre: 'Instalación GPS Test',
  descripcion: 'Instalación de dispositivo GPS para pruebas',
  precio_base: 150.00,
  duracion_estimada: 120
}

const testServicio = {
  fecha_programada: '2024-02-15T10:00:00Z',
  estado: 'pendiente' as const,
  observaciones: 'Servicio de prueba',
  precio_final: 150.00,
  cliente_id: 1,
  unidad_id: 1,
  tipo_trabajo_id: 1
}

export const runServicesTests = async () => {
  console.log('🧪 Iniciando tests del módulo Services...')
  
  try {
    // Test 1: Fetch TipoTrabajos
    console.log('📋 Test 1: Fetching TipoTrabajos...')
    await store.dispatch(fetchTipoTrabajos())
    console.log('✅ TipoTrabajos cargados:', store.getState().services.tipoTrabajos.items)
    
    // Test 2: Create TipoTrabajo
    console.log('➕ Test 2: Creating TipoTrabajo...')
    const newTipoTrabajo = await store.dispatch(createTipoTrabajo(testTipoTrabajo))
    console.log('✅ TipoTrabajo creado:', newTipoTrabajo.payload)
    
    // Test 3: Fetch Servicios
    console.log('📋 Test 3: Fetching Servicios...')
    await store.dispatch(fetchServicios())
    console.log('✅ Servicios cargados:', store.getState().services.servicios.items)
    
    // Test 4: Create Servicio
    console.log('➕ Test 4: Creating Servicio...')
    const newServicio = await store.dispatch(createServicio(testServicio))
    console.log('✅ Servicio creado:', newServicio.payload)
    
    // Test 5: Fetch Stats
    console.log('📊 Test 5: Fetching Stats...')
    await store.dispatch(fetchServicesStats())
    console.log('✅ Stats cargadas:', store.getState().services.stats)
    
    console.log('🎉 Todos los tests completados exitosamente!')
    
  } catch (error) {
    console.error('❌ Error en tests:', error)
  }
}

// Para ejecutar desde la consola:
// runServicesTests()
```

---

## 🚀 PASO 10: Próximos Pasos para Componentes

Una vez completados estos pasos, tendrás la base sólida del módulo Services. Los siguientes pasos serían:

### 10.1 Crear componentes básicos:
- `ServiceStatusBadge.tsx` - Badge para mostrar estados
- `ServiceTypeSelect.tsx` - Select para tipos de trabajo
- `ServiceDatePicker.tsx` - Selector de fechas

### 10.2 Crear componentes de lista:
- `TipoTrabajoList.tsx` - Lista de tipos de trabajo
- `ServicioList.tsx` - Lista de servicios
- `ServicioCard.tsx` - Tarjeta individual de servicio

### 10.3 Crear formularios:
- `TipoTrabajoForm.tsx` - Formulario para tipos de trabajo
- `ServicioForm.tsx` - Formulario para servicios

### 10.4 Crear páginas:
- `ServicesPage.tsx` - Página principal del módulo
- `ServicesDashboard.tsx` - Dashboard con estadísticas

### 10.5 Integrar con routing:
- Agregar rutas en `AppRouter.tsx`
- Configurar navegación en el sidebar

---

## ✅ Checklist de Implementación

- [ ] ✅ Crear estructura de carpetas
- [ ] ✅ Implementar `servicesTypes.ts`
- [ ] ✅ Implementar `servicesAPI.ts`
- [ ] ✅ Implementar `servicesSlice.ts`
- [ ] ✅ Implementar `validations.ts`
- [ ] ✅ Implementar `useServices.ts`
- [ ] ✅ Crear `index.ts`
- [ ] ✅ Integrar con Redux store
- [ ] ✅ Crear test manual (opcional)
- [ ] 🔄 Implementar componentes básicos
- [ ] 🔄 Implementar listas y formularios
- [ ] 🔄 Crear páginas principales
- [ ] 🔄 Integrar con routing
- [ ] 🔄 Agregar tests unitarios
- [ ] 🔄 Documentar componentes

---

## 🎯 Resultado Esperado

Al completar estos pasos, tendrás:

1. **Arquitectura sólida** siguiendo los patrones de tu proyecto
2. **TypeScript estricto** con tipos bien definidos
3. **Redux Toolkit** configurado para estado global
4. **API layer** organizado y reutilizable
5. **Validaciones robustas** con Zod
6. **Hook personalizado** para operaciones del módulo
7. **Base preparada** para implementar componentes UI

¡El módulo Services estará listo para comenzar a desarrollar la interfaz de usuario! 🚀