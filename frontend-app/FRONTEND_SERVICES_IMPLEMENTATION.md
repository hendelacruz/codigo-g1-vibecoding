# 🛠️ Fases de Implementación Frontend - Módulo Services
## React + Vite + TypeScript Implementation Guide

### 📋 Resumen del Módulo Services

El módulo **Services** gestiona servicios técnicos realizados a clientes, incluyendo:

- **TipoTrabajo**: Categorías de servicios (instalación, mantenimiento, etc.)
- **Servicio**: Trabajos realizados en unidades vehiculares
- **Estados**: pendiente, en_proceso, completado, cancelado, reprogramado
- **Relaciones**: Cliente, Unidad, Técnico, GPS, SIM Card

---

## 🎯 FASE 1: Setup Inicial y Configuración Base

### 1.1 Estructura de Carpetas ✅ IMPLEMENTADA

**Nueva estructura organizada por features:**

```
src/
├── features/
│   └── services/                    # Módulo Services completo
│       ├── api/                     # Servicios de API
│       │   ├── servicesApi.ts       # Configuración base de API
│       │   ├── tipoTrabajoApi.ts    # API de TipoTrabajo
│       │   └── servicioApi.ts       # API de Servicio
│       ├── components/              # Componentes del módulo
│       │   ├── TipoTrabajo/
│       │   │   ├── TipoTrabajoList.tsx
│       │   │   ├── TipoTrabajoForm.tsx
│       │   │   ├── TipoTrabajoCard.tsx
│       │   │   └── TipoTrabajoModal.tsx
│       │   ├── Servicio/
│       │   │   ├── ServicioList.tsx
│       │   │   ├── ServicioForm.tsx
│       │   │   ├── ServicioCard.tsx
│       │   │   ├── ServicioModal.tsx
│       │   │   ├── ServicioFilters.tsx
│       │   │   └── ServicioDashboard.tsx
│       │   └── shared/
│       │       ├── ServiceStatusBadge.tsx
│       │       ├── ServiceTypeSelect.tsx
│       │       └── ServiceDatePicker.tsx
│       ├── hooks/                   # Custom hooks del módulo
│       │   ├── useTipoTrabajo.ts
│       │   ├── useServicio.ts
│       │   └── useServiceFilters.ts
│       ├── utils/                   # Utilidades del módulo
│       │   └── serviceHelpers.ts
│       ├── types/                   # Tipos TypeScript (vacío por ahora)
│       └── index.ts                 # Exportaciones del módulo
├── shared/                          # Recursos compartidos globales
│   ├── types/                       # Tipos globales
│   │   └── services/
│   │       ├── tipoTrabajo.ts
│   │       ├── servicio.ts
│   │       └── common.ts
│   └── utils/
│       └── services/
│           └── serviceConstants.ts
└── pages/                           # Páginas principales
    └── services/
        ├── ServicesPage.tsx
        ├── TipoTrabajoPage.tsx
        └── ServicioDashboard.tsx
```

**✅ Cambios Implementados:**
- ✅ Movidos todos los archivos API a `src/features/services/api/`
- ✅ Movidos todos los hooks a `src/features/services/hooks/`
- ✅ Movidos todos los componentes a `src/features/services/components/`
- ✅ Movidas las utilidades a `src/features/services/utils/`
- ✅ Creado archivo `index.ts` para exportaciones centralizadas
- ✅ Actualizados todos los imports para usar las nuevas rutas
- ✅ Eliminadas carpetas vacías de la estructura anterior
- ✅ Resueltos conflictos de configuración de API

### 1.2 Dependencias Necesarias
```bash
# Las siguientes dependencias ya están instaladas en el proyecto:
# @tanstack/react-query - Para manejo de estado del servidor
# axios - Para peticiones HTTP
# react-hook-form - Para manejo de formularios
# @hookform/resolvers - Para resolvers de validación
# zod - Para validación de schemas y type safety
# react-router-dom - Para routing
# @radix-ui/react-* - Para componentes UI accesibles
# react-icons - Para iconos
# date-fns - Para manejo de fechas
# tailwindcss - Para estilos
# sonner - Para notificaciones
# class-variance-authority - Para variants de componentes
# clsx - Para conditional classes

# TypeScript ya está configurado en el proyecto
# No es necesario instalar dependencias adicionales
```

### 1.3 Tipos y Interfaces Base
```typescript
// src/types/services/common.ts
export type EstadoServicio = 'pendiente' | 'en_proceso' | 'completado' | 'cancelado' | 'reprogramado';

export type TipoTrabajoValue = 'instalacion_nueva' | 'mantenimiento_preventivo' | 'mantenimiento_correctivo' | 'otro';

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
}

export interface DateRangeFilter {
  fecha_desde?: string;
  fecha_hasta?: string;
}
```

```typescript
// src/types/services/tipoTrabajo.ts
import { BaseEntity } from './common';

export interface TipoTrabajo extends BaseEntity {
  nombre: string;
  nombre_display: string;
  descripcion: string;
  precio_base: number;
  duracion_estimada: number; // en minutos
  requiere_gps: boolean;
  requiere_sim: boolean;
  servicios_count?: number;
}

export interface TipoTrabajoCreateData {
  nombre: string;
  descripcion: string;
  precio_base: number;
  duracion_estimada: number;
  requiere_gps: boolean;
  requiere_sim: boolean;
}

export interface TipoTrabajoUpdateData extends Partial<TipoTrabajoCreateData> {}

export interface TipoTrabajoFilters extends PaginationParams {
  is_active?: boolean;
  requiere_gps?: boolean;
  requiere_sim?: boolean;
}

export interface TipoTrabajoEstadisticas {
  total_tipos: number;
  activos: number;
  inactivos: number;
  servicios_por_tipo: Array<{
    tipo: string;
    tipo_display: string;
    count: number;
    precio_promedio: number;
  }>;
}
```

```typescript
// src/types/services/servicio.ts
import { BaseEntity, EstadoServicio, DateRangeFilter, PaginationParams } from './common';

export interface Servicio extends BaseEntity {
  fecha: string;
  tipo_trabajo: number;
  tipo_trabajo_nombre: string;
  tecnico_dni: string;
  tecnico_nombre: string;
  cliente: number;
  cliente_nombre: string;
  unidad: number;
  unidad_placa: string;
  gps?: number;
  gps_codigo?: string;
  sim_card?: number;
  sim_numero?: string;
  descripcion: string;
  precio: number;
  estado_servicio: EstadoServicio;
  observaciones?: string;
  fecha_completado?: string;
  calificacion?: number;
}

export interface ServicioCreateData {
  fecha: string;
  tipo_trabajo: number;
  tecnico_dni: string;
  cliente: number;
  unidad: number;
  gps?: number;
  sim_card?: number;
  descripcion: string;
  precio: number;
  estado_servicio: EstadoServicio;
  observaciones?: string;
}

export interface ServicioUpdateData extends Partial<ServicioCreateData> {}

export interface ServicioFilters extends PaginationParams, DateRangeFilter {
  estado_servicio?: EstadoServicio;
  tipo_trabajo?: number;
  tecnico_dni?: string;
  cliente?: number;
}

export interface ServicioEstadisticas {
  total_servicios: number;
  pendientes: number;
  en_proceso: number;
  completados: number;
  cancelados: number;
  reprogramados: number;
  ingresos_total: number;
  ingresos_mes_actual: number;
  promedio_calificacion: number;
}

export interface ServicioDashboard {
  estadisticas: ServicioEstadisticas;
  servicios_por_tipo: Array<{
    tipo: string;
    tipo_display: string;
    count: number;
    ingresos: number;
  }>;
  tecnicos_activos: Array<{
    id: string;
    nombre: string;
    servicios_count: number;
    calificacion_promedio: number;
  }>;
  servicios_recientes: Servicio[];
}
```

### 1.4 Configuración de Constants
```typescript
// src/shared/utils/services/serviceConstants.ts
import { EstadoServicio, TipoTrabajoValue } from '../../types/services/common';

export interface EstadoChoice {
  value: EstadoServicio;
  label: string;
  color: 'yellow' | 'blue' | 'green' | 'red' | 'orange';
}

export interface TipoTrabajoChoice {
  value: TipoTrabajoValue;
  label: string;
}

export const ESTADO_SERVICIO_CHOICES: EstadoChoice[] = [
  { value: 'pendiente', label: 'Pendiente', color: 'yellow' },
  { value: 'en_proceso', label: 'En Proceso', color: 'blue' },
  { value: 'completado', label: 'Completado', color: 'green' },
  { value: 'cancelado', label: 'Cancelado', color: 'red' },
  { value: 'reprogramado', label: 'Reprogramado', color: 'orange' }
] as const;

export const TIPO_TRABAJO_CHOICES: TipoTrabajoChoice[] = [
  { value: 'instalacion_nueva', label: 'Instalación Nueva' },
  { value: 'mantenimiento_preventivo', label: 'Mantenimiento Preventivo' },
  { value: 'mantenimiento_correctivo', label: 'Mantenimiento Correctivo' },
  { value: 'otro', label: 'Otro' }
] as const;

export const QUERY_KEYS = {
  TIPO_TRABAJOS: 'tipoTrabajos',
  TIPO_TRABAJO: 'tipoTrabajo',
  TIPO_TRABAJO_SERVICIOS: 'tipoTrabajoServicios',
  TIPO_TRABAJO_ESTADISTICAS: 'tipoTrabajoEstadisticas',
  SERVICIOS: 'servicios',
  SERVICIO: 'servicio',
  SERVICIOS_ESTADISTICAS: 'serviciosEstadisticas',
  SERVICIOS_DASHBOARD: 'serviciosDashboard'
} as const;
```

---

## 🔌 FASE 2: Configuración de API y Servicios

### 2.1 API Base Configuration ✅ IMPLEMENTADA
```typescript
// src/features/services/api/servicesApi.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface ApiConfig extends AxiosRequestConfig {
  baseURL: string;
  headers: Record<string, string>;
}

const config: ApiConfig = {
  baseURL: `${API_BASE_URL}/services`,
  headers: {
    'Content-Type': 'application/json',
  },
};

const servicesApi: AxiosInstance = axios.create(config);

// Interceptor para agregar token de autenticación
servicesApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejo de errores
servicesApi.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default servicesApi;
```

### 2.2 TipoTrabajo API Service ✅ IMPLEMENTADA
```typescript
// src/features/services/api/tipoTrabajoApi.ts
import { AxiosResponse } from 'axios';
import servicesApi from './servicesApi';
import { 
  TipoTrabajo, 
  TipoTrabajoCreateData, 
  TipoTrabajoUpdateData, 
  TipoTrabajoFilters,
  TipoTrabajoEstadisticas 
} from '../../../shared/types/services/tipoTrabajo';
import { ApiResponse } from '../../../shared/types/services/common';
import { Servicio, ServicioFilters } from '../../../shared/types/services/servicio';

export interface TipoTrabajoApiService {
  getAll: (params?: TipoTrabajoFilters) => Promise<AxiosResponse<ApiResponse<TipoTrabajo>>>;
  getById: (id: number) => Promise<AxiosResponse<TipoTrabajo>>;
  create: (data: TipoTrabajoCreateData) => Promise<AxiosResponse<TipoTrabajo>>;
  update: (id: number, data: TipoTrabajoUpdateData) => Promise<AxiosResponse<TipoTrabajo>>;
  partialUpdate: (id: number, data: Partial<TipoTrabajoUpdateData>) => Promise<AxiosResponse<TipoTrabajo>>;
  delete: (id: number) => Promise<AxiosResponse<void>>;
  toggleActive: (id: number) => Promise<AxiosResponse<TipoTrabajo>>;
  getServicios: (id: number, params?: ServicioFilters) => Promise<AxiosResponse<ApiResponse<Servicio>>>;
  getEstadisticas: (params?: Record<string, unknown>) => Promise<AxiosResponse<TipoTrabajoEstadisticas>>;
}

export const tipoTrabajoApi: TipoTrabajoApiService = {
  // GET /api/services/tipos-trabajo/
  getAll: (params = {}) => 
    servicesApi.get<ApiResponse<TipoTrabajo>>('/tipos-trabajo/', { params }),

  // GET /api/services/tipos-trabajo/{id}/
  getById: (id: number) => 
    servicesApi.get<TipoTrabajo>(`/tipos-trabajo/${id}/`),

  // POST /api/services/tipos-trabajo/
  create: (data: TipoTrabajoCreateData) => 
    servicesApi.post<TipoTrabajo>('/tipos-trabajo/', data),

  // PUT /api/services/tipos-trabajo/{id}/
  update: (id: number, data: TipoTrabajoUpdateData) => 
    servicesApi.put<TipoTrabajo>(`/tipos-trabajo/${id}/`, data),

  // PATCH /api/services/tipos-trabajo/{id}/
  partialUpdate: (id: number, data: Partial<TipoTrabajoUpdateData>) => 
    servicesApi.patch<TipoTrabajo>(`/tipos-trabajo/${id}/`, data),

  // DELETE /api/services/tipos-trabajo/{id}/
  delete: (id: number) => 
    servicesApi.delete<void>(`/tipos-trabajo/${id}/`),

  // PATCH /api/services/tipos-trabajo/{id}/toggle_active/
  toggleActive: (id: number) => 
    servicesApi.patch<TipoTrabajo>(`/tipos-trabajo/${id}/toggle_active/`),

  // GET /api/services/tipos-trabajo/{id}/servicios/
  getServicios: (id: number, params = {}) => 
    servicesApi.get<ApiResponse<Servicio>>(`/tipos-trabajo/${id}/servicios/`, { params }),

  // GET /api/services/tipos-trabajo/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get<TipoTrabajoEstadisticas>('/tipos-trabajo/estadisticas/', { params })
};
```

### 2.3 Servicio API Service ✅ IMPLEMENTADA
```typescript
// src/features/services/api/servicioApi.ts
import { AxiosResponse } from 'axios';
import servicesApi from './servicesApi';
import { 
  Servicio, 
  ServicioCreateData, 
  ServicioUpdateData, 
  ServicioFilters,
  ServicioEstadisticas,
  ServicioDashboard 
} from '../../../shared/types/services/servicio';
import { ApiResponse, EstadoServicio } from '../../../shared/types/services/common';

export interface ServicioApiService {
  getAll: (params?: ServicioFilters) => Promise<AxiosResponse<ApiResponse<Servicio>>>;
  getById: (id: number) => Promise<AxiosResponse<Servicio>>;
  create: (data: ServicioCreateData) => Promise<AxiosResponse<Servicio>>;
  update: (id: number, data: ServicioUpdateData) => Promise<AxiosResponse<Servicio>>;
  partialUpdate: (id: number, data: Partial<ServicioUpdateData>) => Promise<AxiosResponse<Servicio>>;
  delete: (id: number) => Promise<AxiosResponse<void>>;
  cambiarEstado: (id: number, estado: EstadoServicio) => Promise<AxiosResponse<Servicio>>;
  toggleActive: (id: number) => Promise<AxiosResponse<Servicio>>;
  getEstadisticas: (params?: Record<string, unknown>) => Promise<AxiosResponse<ServicioEstadisticas>>;
  getDashboard: (params?: Record<string, unknown>) => Promise<AxiosResponse<ServicioDashboard>>;
}

export const servicioApi: ServicioApiService = {
  // GET /api/services/servicios/
  getAll: (params = {}) => 
    servicesApi.get<ApiResponse<Servicio>>('/servicios/', { params }),

  // GET /api/services/servicios/{id}/
  getById: (id: number) => 
    servicesApi.get<Servicio>(`/servicios/${id}/`),

  // POST /api/services/servicios/
  create: (data: ServicioCreateData) => 
    servicesApi.post<Servicio>('/servicios/', data),

  // PUT /api/services/servicios/{id}/
  update: (id: number, data: ServicioUpdateData) => 
    servicesApi.put<Servicio>(`/servicios/${id}/`, data),

  // PATCH /api/services/servicios/{id}/
  partialUpdate: (id: number, data: Partial<ServicioUpdateData>) => 
    servicesApi.patch<Servicio>(`/servicios/${id}/`, data),

  // DELETE /api/services/servicios/{id}/
  delete: (id: number) => 
    servicesApi.delete<void>(`/servicios/${id}/`),

  // PATCH /api/services/servicios/{id}/cambiar_estado/
  cambiarEstado: (id: number, estado: EstadoServicio) => 
    servicesApi.patch<Servicio>(`/servicios/${id}/cambiar_estado/`, { estado }),

  // PATCH /api/services/servicios/{id}/toggle_active/
  toggleActive: (id: number) => 
    servicesApi.patch<Servicio>(`/servicios/${id}/toggle_active/`),

  // GET /api/services/servicios/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get<ServicioEstadisticas>('/servicios/estadisticas/', { params }),

  // GET /api/services/servicios/dashboard/
  getDashboard: (params = {}) => 
    servicesApi.get<ServicioDashboard>('/servicios/dashboard/', { params })
};
```

---

## 🎣 FASE 3: Custom Hooks con React Query

### 3.1 TipoTrabajo Hooks ✅ IMPLEMENTADA
```typescript
// src/features/services/hooks/useTipoTrabajo.ts
import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { toast } from 'sonner';
import { tipoTrabajoApi } from '../api/tipoTrabajoApi';
import { 
  TipoTrabajo, 
  TipoTrabajoCreateData, 
  TipoTrabajoUpdateData, 
  TipoTrabajoFilters,
  TipoTrabajoEstadisticas 
} from '../../../shared/types/services/tipoTrabajo';
import { ApiResponse } from '../../../shared/types/services/common';
import { Servicio, ServicioFilters } from '../../../shared/types/services/servicio';
import { QUERY_KEYS } from '../../../shared/utils/services/serviceConstants';

// Query Hooks
export const useTipoTrabajos = (
  params: TipoTrabajoFilters = {}
): UseQueryResult<ApiResponse<TipoTrabajo>, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.TIPO_TRABAJOS, params],
    queryFn: () => tipoTrabajoApi.getAll(params).then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutos
    retry: 2,
  });
};

export const useTipoTrabajo = (
  id: number | undefined
): UseQueryResult<TipoTrabajo, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.TIPO_TRABAJO, id],
    queryFn: () => tipoTrabajoApi.getById(id!).then(res => res.data),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useTipoTrabajoServicios = (
  id: number | undefined,
  params: ServicioFilters = {}
): UseQueryResult<ApiResponse<Servicio>, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.TIPO_TRABAJO_SERVICIOS, id, params],
    queryFn: () => tipoTrabajoApi.getServicios(id!, params).then(res => res.data),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useTipoTrabajoEstadisticas = (
  params: Record<string, unknown> = {}
): UseQueryResult<TipoTrabajoEstadisticas, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.TIPO_TRABAJO_ESTADISTICAS, params],
    queryFn: () => tipoTrabajoApi.getEstadisticas(params).then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Mutation Hooks
export const useCreateTipoTrabajo = (): UseMutationResult<
  TipoTrabajo,
  AxiosError,
  TipoTrabajoCreateData
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: TipoTrabajoCreateData) => 
      tipoTrabajoApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO_ESTADISTICAS] });
      toast.success('Tipo de trabajo creado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al crear tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const useUpdateTipoTrabajo = (): UseMutationResult<
  TipoTrabajo,
  AxiosError,
  { id: number; data: TipoTrabajoUpdateData }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TipoTrabajoUpdateData }) => 
      tipoTrabajoApi.update(id, data).then(res => res.data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO, variables.id] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO_ESTADISTICAS] });
      toast.success('Tipo de trabajo actualizado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al actualizar tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const usePartialUpdateTipoTrabajo = (): UseMutationResult<
  TipoTrabajo,
  AxiosError,
  { id: number; data: Partial<TipoTrabajoUpdateData> }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TipoTrabajoUpdateData> }) => 
      tipoTrabajoApi.partialUpdate(id, data).then(res => res.data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO, variables.id] });
      toast.success('Tipo de trabajo actualizado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al actualizar tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const useDeleteTipoTrabajo = (): UseMutationResult<
  void,
  AxiosError,
  number
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => tipoTrabajoApi.delete(id).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO_ESTADISTICAS] });
      toast.success('Tipo de trabajo eliminado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al eliminar tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const useToggleActiveTipoTrabajo = (): UseMutationResult<
  TipoTrabajo,
  AxiosError,
  number
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => tipoTrabajoApi.toggleActive(id).then(res => res.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TIPO_TRABAJO, data.id] });
      toast.success(`Tipo de trabajo ${data.is_active ? 'activado' : 'desactivado'} exitosamente`);
    },
    onError: (error: AxiosError) => {
      toast.error('Error al cambiar estado del tipo de trabajo');
      console.error('Error:', error);
    },
  });
};
```

### 3.2 Servicio Hooks ✅ IMPLEMENTADA
```typescript
// src/features/services/hooks/useServicio.ts
import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { toast } from 'sonner';
import { servicioApi } from '../api/servicioApi';
import { 
  Servicio, 
  ServicioCreateData, 
  ServicioUpdateData, 
  ServicioFilters,
  ServicioEstadisticas,
  ServicioDashboard 
} from '../../../shared/types/services/servicio';
import { ApiResponse, EstadoServicio } from '../../../shared/types/services/common';
import { QUERY_KEYS } from '../../../shared/utils/services/serviceConstants';

// Query Hooks
export const useServicios = (
  params: ServicioFilters = {}
): UseQueryResult<ApiResponse<Servicio>, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.SERVICIOS, params],
    queryFn: () => servicioApi.getAll(params).then(res => res.data),
    staleTime: 2 * 60 * 1000, // 2 minutos
    retry: 2,
  });
};

export const useServicio = (
  id: number | undefined
): UseQueryResult<Servicio, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.SERVICIO, id],
    queryFn: () => servicioApi.getById(id!).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useServiciosEstadisticas = (
  params: Record<string, unknown> = {}
): UseQueryResult<ServicioEstadisticas, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.SERVICIOS_ESTADISTICAS, params],
    queryFn: () => servicioApi.getEstadisticas(params).then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useServiciosDashboard = (
  params: Record<string, unknown> = {}
): UseQueryResult<ServicioDashboard, AxiosError> => {
  return useQuery({
    queryKey: [QUERY_KEYS.SERVICIOS_DASHBOARD, params],
    queryFn: () => servicioApi.getDashboard(params).then(res => res.data),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Mutation Hooks
export const useCreateServicio = (): UseMutationResult<
  Servicio,
  AxiosError,
  ServicioCreateData
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ServicioCreateData) => 
      servicioApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_ESTADISTICAS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_DASHBOARD] });
      toast.success('Servicio creado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al crear servicio');
      console.error('Error:', error);
    },
  });
};

export const useUpdateServicio = (): UseMutationResult<
  Servicio,
  AxiosError,
  { id: number; data: ServicioUpdateData }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ServicioUpdateData }) => 
      servicioApi.update(id, data).then(res => res.data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIO, variables.id] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_ESTADISTICAS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_DASHBOARD] });
      toast.success('Servicio actualizado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al actualizar servicio');
      console.error('Error:', error);
    },
  });
};

export const usePartialUpdateServicio = (): UseMutationResult<
  Servicio,
  AxiosError,
  { id: number; data: Partial<ServicioUpdateData> }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ServicioUpdateData> }) => 
      servicioApi.partialUpdate(id, data).then(res => res.data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIO, variables.id] });
      toast.success('Servicio actualizado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al actualizar servicio');
      console.error('Error:', error);
    },
  });
};

export const useDeleteServicio = (): UseMutationResult<
  void,
  AxiosError,
  number
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => servicioApi.delete(id).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_ESTADISTICAS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_DASHBOARD] });
      toast.success('Servicio eliminado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al eliminar servicio');
      console.error('Error:', error);
    },
  });
};

export const useCambiarEstadoServicio = (): UseMutationResult<
  Servicio,
  AxiosError,
  { id: number; estado: EstadoServicio }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: EstadoServicio }) => 
      servicioApi.cambiarEstado(id, estado).then(res => res.data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIO, variables.id] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_ESTADISTICAS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS_DASHBOARD] });
      toast.success('Estado del servicio actualizado exitosamente');
    },
    onError: (error: AxiosError) => {
      toast.error('Error al cambiar estado del servicio');
      console.error('Error:', error);
    },
  });
};

export const useToggleActiveServicio = (): UseMutationResult<
  Servicio,
  AxiosError,
  number
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => servicioApi.toggleActive(id).then(res => res.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIOS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SERVICIO, data.id] });
      toast.success(`Servicio ${data.is_active ? 'activado' : 'desactivado'} exitosamente`);
    },
    onError: (error: AxiosError) => {
      toast.error('Error al cambiar estado del servicio');
      console.error('Error:', error);
    },
  });
};
```

---

## 🧩 FASE 4: Componentes Base y Reutilizables

### 4.1 Service Status Badge
```typescript
// src/components/services/shared/ServiceStatusBadge.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../lib/utils';
import { EstadoServicio } from '../../../types/services/common';
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border font-medium',
  {
    variants: {
      size: {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-2 text-base'
      },
      color: {
        yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        blue: 'bg-blue-100 text-blue-800 border-blue-200',
        green: 'bg-green-100 text-green-800 border-green-200',
        red: 'bg-red-100 text-red-800 border-red-200',
        orange: 'bg-orange-100 text-orange-800 border-orange-200'
      }
    },
    defaultVariants: {
      size: 'sm',
      color: 'blue'
    }
  }
);

interface ServiceStatusBadgeProps extends VariantProps<typeof badgeVariants> {
  estado: EstadoServicio;
  className?: string;
}

const ServiceStatusBadge: React.FC<ServiceStatusBadgeProps> = ({ 
  estado, 
  size = 'sm', 
  className 
}) => {
  const estadoInfo = ESTADO_SERVICIO_CHOICES.find(e => e.value === estado);
  
  if (!estadoInfo) return null;

  return (
    <span className={cn(badgeVariants({ size, color: estadoInfo.color }), className)}>
      {estadoInfo.label}
    </span>
  );
};

export default ServiceStatusBadge;
```

### 4.2 Service Type Select
```typescript
// src/components/services/shared/ServiceTypeSelect.tsx
import React from 'react';
import * as Select from '@radix-ui/react-select';
import { HiChevronDown, HiCheck } from 'react-icons/hi2';
import { useTipoTrabajos } from '../../../hooks/services/useTipoTrabajo';
import { cn } from '../../../lib/utils';

interface ServiceTypeSelectProps {
  value?: number | null;
  onChange: (value: number | null) => void;
  placeholder?: string;
  isDisabled?: boolean;
  className?: string;
  error?: string;
}

const ServiceTypeSelect: React.FC<ServiceTypeSelectProps> = ({ 
  value, 
  onChange, 
  placeholder = "Seleccionar tipo...", 
  isDisabled = false,
  className,
  error
}) => {
  const { data: tipoTrabajos, isLoading } = useTipoTrabajos({ is_active: true });

  const options = tipoTrabajos?.results?.map(tipo => ({
    value: tipo.id.toString(),
    label: tipo.nombre_display
  })) || [];

  if (isLoading) {
    return (
      <div className={cn(
        "w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500",
        className
      )}>
        Cargando...
      </div>
    );
  }

  return (
    <div className="w-full">
      <Select.Root 
        value={value?.toString() || ''} 
        onValueChange={(val) => onChange(val ? parseInt(val) : null)} 
        disabled={isDisabled}
      >
        <Select.Trigger 
          className={cn(
            "inline-flex items-center justify-between rounded-md border bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 w-full disabled:bg-gray-50 disabled:text-gray-500",
            error 
              ? "border-red-300 focus:border-red-500 focus:ring-red-500" 
              : "border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            className
          )}
        >
          <Select.Value placeholder={placeholder} />
          <Select.Icon>
            <HiChevronDown className="h-4 w-4" />
          </Select.Icon>
        </Select.Trigger>
        
        <Select.Portal>
          <Select.Content className="overflow-hidden rounded-md bg-white shadow-lg border border-gray-200 z-50">
            <Select.Viewport className="p-1">
              {options.map((option) => (
                <Select.Item
                  key={option.value}
                  value={option.value}
                  className="relative flex cursor-pointer select-none items-center rounded-sm px-8 py-2 text-sm outline-none focus:bg-blue-50 data-[highlighted]:bg-blue-50"
                >
                  <Select.ItemIndicator className="absolute left-2 inline-flex items-center">
                    <HiCheck className="h-4 w-4" />
                  </Select.ItemIndicator>
                  <Select.ItemText>{option.label}</Select.ItemText>
                </Select.Item>
              ))}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>
      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}
    </div>
  );
};

export default ServiceTypeSelect;
```

### 4.3 Service Filters Component
```typescript
// src/components/services/Servicio/ServicioFilters.tsx
import React, { useState } from 'react';
import { HiMagnifyingGlass, HiFunnel } from 'react-icons/hi2';
import ServiceTypeSelect from '../shared/ServiceTypeSelect';
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';
import { ServicioFilters as ServicioFiltersType } from '../../../types/services/servicio';

interface ServicioFiltersProps {
  filters: ServicioFiltersType;
  onFiltersChange: (filters: ServicioFiltersType) => void;
  className?: string;
}

const ServicioFilters: React.FC<ServicioFiltersProps> = ({ 
  filters, 
  onFiltersChange,
  className 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = <K extends keyof ServicioFiltersType>(
    key: K, 
    value: ServicioFiltersType[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className={`bg-white p-4 rounded-lg shadow-sm border ${className || ''}`}>
      {/* Búsqueda principal */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <HiMagnifyingGlass className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar servicios..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <HiFunnel className="h-5 w-5" />
          Filtros
        </button>
      </div>

      {/* Filtros expandidos */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado
            </label>
            <select
              value={filters.estado_servicio || ''}
              onChange={(e) => handleFilterChange('estado_servicio', e.target.value as any)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los estados</option>
              {ESTADO_SERVICIO_CHOICES.map(estado => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo de Trabajo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Trabajo
            </label>
            <ServiceTypeSelect
              value={filters.tipo_trabajo || null}
              onChange={(value) => handleFilterChange('tipo_trabajo', value)}
              placeholder="Todos los tipos"
            />
          </div>

          {/* Fecha Desde */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fecha Desde
            </label>
            <input
              type="date"
              value={filters.fecha_desde || ''}
              onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fecha Hasta */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fecha Hasta
            </label>
            <input
              type="date"
              value={filters.fecha_hasta || ''}
              onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Botón limpiar filtros */}
          <div className="md:col-span-2 lg:col-span-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Limpiar filtros
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ServicioFilters;
```

---

## 📋 FASE 5: Componentes de Lista y Tarjetas

### 5.1 Servicio Card Component
```typescript
// src/components/services/Servicio/ServicioCard.tsx
import React from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  HiCalendar, 
  HiUser, 
  HiTruck,
  HiCurrencyDollar,
  HiEye,
  HiPencil
} from 'react-icons/hi2';
import ServiceStatusBadge from '../shared/ServiceStatusBadge';
import { Servicio } from '../../../types/services/servicio';
import { EstadoServicio } from '../../../types/services/common';

interface ServicioCardProps {
  servicio: Servicio;
  onView: (servicio: Servicio) => void;
  onEdit: (servicio: Servicio) => void;
  onChangeStatus: (servicioId: number, nuevoEstado: EstadoServicio) => void;
  className?: string;
}

const ServicioCard: React.FC<ServicioCardProps> = ({ 
  servicio, 
  onView, 
  onEdit, 
  onChangeStatus,
  className 
}) => {
  const formatDate = (dateString: string): string => {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es });
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(price);
  };

  const getStatusAction = () => {
    switch (servicio.estado_servicio) {
      case 'pendiente':
        return (
          <button
            onClick={() => onChangeStatus(servicio.id, 'en_proceso')}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Iniciar
          </button>
        );
      case 'en_proceso':
        return (
          <button
            onClick={() => onChangeStatus(servicio.id, 'completado')}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Completar
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200 ${className || ''}`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {servicio.tipo_trabajo_nombre}
            </h3>
            <p className="text-sm text-gray-500">
              ID: {servicio.id}
            </p>
          </div>
          <ServiceStatusBadge estado={servicio.estado_servicio} />
        </div>

        {/* Información principal */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <HiCalendar className="h-4 w-4 mr-2 flex-shrink-0" />
            <span>{formatDate(servicio.fecha)}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <HiUser className="h-4 w-4 mr-2 flex-shrink-0" />
            <span className="font-medium">{servicio.tecnico_nombre}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <HiTruck className="h-4 w-4 mr-2 flex-shrink-0" />
            <span>{servicio.cliente_nombre} - {servicio.unidad_placa}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <HiCurrencyDollar className="h-4 w-4 mr-2 flex-shrink-0" />
            <span className="font-semibold text-green-600">
              {formatPrice(servicio.precio)}
            </span>
          </div>
        </div>

        {/* Descripción */}
        {servicio.descripcion && (
          <div className="mb-4">
            <p className="text-sm text-gray-700 line-clamp-2">
              {servicio.descripcion}
            </p>
          </div>
        )}

        {/* Acciones */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="flex space-x-2">
            <button
              onClick={() => onView(servicio)}
              className="flex items-center px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            >
              <HiEye className="h-4 w-4 mr-1" />
              Ver
            </button>
            <button
              onClick={() => onEdit(servicio)}
              className="flex items-center px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded-md transition-colors"
            >
              <HiPencil className="h-4 w-4 mr-1" />
              Editar
            </button>
          </div>
          
          {/* Cambio rápido de estado */}
          {getStatusAction()}
        </div>
      </div>
    </div>
  );
};

export default ServicioCard;
```

### 5.2 Servicio List Component
```typescript
// src/components/services/Servicio/ServicioList.tsx
import React, { useState } from 'react';
import { useServicios, useCambiarEstadoServicio } from '../../../hooks/services/useServicio';
import ServicioCard from './ServicioCard';
import ServicioFilters from './ServicioFilters';
import ServicioModal from './ServicioModal';
import LoadingSpinner from '../../common/LoadingSpinner';
import Pagination from '../../common/Pagination';
import { Servicio } from '../../../types/services/servicio';
import { ServicioFilters as ServicioFiltersType } from '../../../types/services/servicio';
import { EstadoServicio } from '../../../types/services/common';

type ModalMode = 'view' | 'edit' | 'create';

const ServicioList: React.FC = () => {
  const [filters, setFilters] = useState<ServicioFiltersType>({});
  const [selectedServicio, setSelectedServicio] = useState<Servicio | null>(null);
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const { data: serviciosData, isLoading, error } = useServicios({
    ...filters,
    page: currentPage,
    page_size: 12
  });

  const cambiarEstadoMutation = useCambiarEstadoServicio();

  const handleView = (servicio: Servicio) => {
    setSelectedServicio(servicio);
    setModalMode('view');
  };

  const handleEdit = (servicio: Servicio) => {
    setSelectedServicio(servicio);
    setModalMode('edit');
  };

  const handleCreate = () => {
    setSelectedServicio(null);
    setModalMode('create');
  };

  const handleChangeStatus = (servicioId: number, nuevoEstado: EstadoServicio) => {
    cambiarEstadoMutation.mutate({ id: servicioId, estado: nuevoEstado });
  };

  const closeModal = () => {
    setSelectedServicio(null);
    setModalMode(null);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600">Error al cargar servicios</div>;

  const servicios = serviciosData?.results || [];
  const totalPages = Math.ceil((serviciosData?.count || 0) / 12);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Servicios</h1>
          <p className="text-gray-600">
            {serviciosData?.count || 0} servicios encontrados
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Nuevo Servicio
        </button>
      </div>

      {/* Filtros */}
      <ServicioFilters
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Lista de servicios */}
      {servicios.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No se encontraron servicios</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servicios.map((servicio) => (
              <ServicioCard
                key={servicio.id}
                servicio={servicio}
                onView={handleView}
                onEdit={handleEdit}
                onChangeStatus={handleChangeStatus}
              />
            ))}
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          )}
        </>
      )}

      {/* Modal */}
      {modalMode && (
        <ServicioModal
          mode={modalMode}
          servicio={selectedServicio}
          onClose={closeModal}
        />
      )}
    </div>
  );
};

export default ServicioList;
```

---

## 📝 FASE 6: Formularios y Modales

### 6.1 Servicio Form Component
```typescript
// src/components/services/Servicio/ServicioForm.tsx
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCreateServicio, useUpdateServicio } from '../../../hooks/services/useServicio';
import ServiceTypeSelect from '../shared/ServiceTypeSelect';
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';
import { Servicio, ServicioCreateData, ServicioUpdateData } from '../../../types/services/servicio';

const schema = z.object({
  fecha: z.string().min(1, 'La fecha es requerida'),
  tipo_trabajo: z.number().min(1, 'El tipo de trabajo es requerido'),
  tecnico_dni: z.string().min(8, 'El DNI debe tener al menos 8 caracteres').max(8, 'El DNI debe tener máximo 8 caracteres'),
  cliente: z.number().min(1, 'El cliente es requerido'),
  unidad: z.number().min(1, 'La unidad es requerida'),
  gps: z.number().optional(),
  sim_card: z.number().optional(),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  precio: z.number().positive('El precio debe ser positivo'),
  estado_servicio: z.enum(['pendiente', 'en_proceso', 'completado', 'cancelado', 'reprogramado']),
  observaciones: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface ServicioFormProps {
  servicio?: Servicio | null;
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}

const ServicioForm: React.FC<ServicioFormProps> = ({ 
  servicio, 
  onSuccess, 
  onCancel,
  className 
}) => {
  const isEditing = !!servicio;
  const createMutation = useCreateServicio();
  const updateMutation = useUpdateServicio();

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      fecha: servicio?.fecha ? new Date(servicio.fecha).toISOString().split('T')[0] : '',
      tipo_trabajo: servicio?.tipo_trabajo || 0,
      tecnico_dni: servicio?.tecnico_dni || '',
      cliente: servicio?.cliente || 0,
      unidad: servicio?.unidad || 0,
      gps: servicio?.gps,
      sim_card: servicio?.sim_card,
      descripcion: servicio?.descripcion || '',
      precio: servicio?.precio || 0,
      estado_servicio: servicio?.estado_servicio || 'pendiente',
      observaciones: servicio?.observaciones || '',
    }
  });

  const onSubmit = async (data: FormData) => {
    try {
      if (isEditing) {
        await updateMutation.mutateAsync({ id: servicio.id, data });
      } else {
        await createMutation.mutateAsync(data);
      }
      reset();
      onSuccess?.();
    } catch (error) {
      console.error('Error al guardar servicio:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={cn('space-y-6', className)}>
      {/* Implementación del formulario */}
    </form>
  );
};

export default ServicioForm;
```

---

## 📊 ESTADO ACTUAL DE IMPLEMENTACIÓN

### ✅ COMPLETADO - FASE 1: Reorganización de Estructura

**Fecha de implementación:** Diciembre 2024

#### 🎯 Problemas Resueltos:

1. **Conflictos de Configuración de API**
   - ❌ **Problema:** Múltiples instancias de axios con configuraciones diferentes
   - ✅ **Solución:** Unificada configuración en `src/features/services/api/servicesApi.ts`

2. **Estructura Inconsistente**
   - ❌ **Problema:** Archivos dispersos en diferentes carpetas (`src/services/`, `src/hooks/services/`, etc.)
   - ✅ **Solución:** Reorganización completa bajo `src/features/services/`

3. **Imports Incorrectos**
   - ❌ **Problema:** Referencias a rutas obsoletas y conflictos de dependencias
   - ✅ **Solución:** Actualizados todos los imports para usar las nuevas rutas

#### 🏗️ Nueva Estructura Implementada:

```
src/features/services/
├── api/                     ✅ IMPLEMENTADO
│   ├── servicesApi.ts       # Configuración unificada de API
│   ├── tipoTrabajoApi.ts    # API de TipoTrabajo
│   └── servicioApi.ts       # API de Servicio
├── hooks/                   ✅ IMPLEMENTADO
│   ├── useTipoTrabajo.ts    # Hooks para TipoTrabajo
│   ├── useServicio.ts       # Hooks para Servicio
│   └── useServiceFilters.ts # Hooks para filtros
├── components/              ✅ MOVIDO (pendiente implementación)
│   ├── TipoTrabajo/
│   ├── Servicio/
│   └── shared/
├── utils/                   ✅ IMPLEMENTADO
│   └── serviceHelpers.ts    # Utilidades del módulo
├── types/                   📝 VACÍO (tipos en shared/)
└── index.ts                 ✅ IMPLEMENTADO (exportaciones centralizadas)
```

#### 🔧 Mejoras Implementadas:

- **✅ API Unificada:** Una sola instancia de axios con interceptors consistentes
- **✅ Estructura Modular:** Organización por features para mejor mantenibilidad
- **✅ Imports Limpios:** Rutas relativas cortas y consistentes
- **✅ Módulo Exportable:** Archivo `index.ts` para importaciones centralizadas
- **✅ TypeScript Estricto:** Tipado completo y consistente
- **✅ Patrón Unificado:** Misma estructura que otros módulos del proyecto

#### 🚀 Beneficios Obtenidos:

1. **Sin Conflictos:** Eliminados conflictos de configuración de API
2. **Mantenibilidad:** Código organizado y fácil de mantener
3. **Escalabilidad:** Estructura preparada para crecimiento del módulo
4. **Consistencia:** Patrón unificado con el resto del proyecto
5. **Developer Experience:** Imports más limpios y navegación más fácil

### 📋 PRÓXIMOS PASOS:

#### FASE 2: Implementación de Componentes UI
- [ ] Implementar componentes de TipoTrabajo
- [ ] Implementar componentes de Servicio
- [ ] Crear componentes compartidos (badges, selects, etc.)

#### FASE 3: Integración y Testing
- [ ] Integrar con páginas principales
- [ ] Implementar validaciones con Zod
- [ ] Agregar tests unitarios

#### FASE 4: Optimización y Polish
- [ ] Optimizar performance con React.memo
- [ ] Implementar lazy loading
- [ ] Agregar documentación Storybook

---

**📝 Nota:** Esta reorganización establece las bases sólidas para el desarrollo del módulo Services, eliminando conflictos técnicos y proporcionando una estructura escalable y mantenible.