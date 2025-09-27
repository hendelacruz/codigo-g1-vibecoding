import React from 'react'
import { render, type RenderOptions, type RenderResult } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider } from 'react-redux'
import { configureStore, type Store } from '@reduxjs/toolkit'
import { BrowserRouter } from 'react-router-dom'

// Import reducers
import authReducer from '../../auth/authSlice'
import entitiesReducer from '../../entities/entitiesSlice'

// Types
import type { Servicio } from '../../../shared/types/services/servicio'
import type { TipoTrabajo } from '../../../shared/types/services/tipoTrabajo'

/**
 * Mock data for testing
 */
export const mockServicios: Servicio[] = [
  {
    id: 1,
    fecha: '2024-01-15',
    tipo_trabajo: 1,
    tipo_trabajo_nombre: 'Instalación',
    tecnico_id: 1,
    tecnico_dni: '12345678',
    tecnico_nombre: 'Juan Pérez',
    cliente: 1,
    cliente_nombre: 'Cliente Test 1',
    unidad: 1,
    unidad_placa: 'ABC-123',
    gps: 1,
    gps_codigo: 'GPS001',
    sim_card: 1,
    sim_numero: '987654321',
    descripcion: 'Instalación de GPS en vehículo',
    precio: 150.00,
    estado_servicio: 'pendiente',
    observaciones: 'Servicio de prueba',
    is_active: true,
    created_at: '2024-01-10T10:00:00Z',
    updated_at: '2024-01-10T10:00:00Z'
  },
  {
    id: 2,
    fecha: '2024-01-16',
    tipo_trabajo: 2,
    tipo_trabajo_nombre: 'Mantenimiento',
    tecnico_id: 2,
    tecnico_dni: '87654321',
    tecnico_nombre: 'María García',
    cliente: 2,
    cliente_nombre: 'Cliente Test 2',
    unidad: 2,
    unidad_placa: 'DEF-456',
    gps: 2,
    gps_codigo: 'GPS002',
    descripcion: 'Mantenimiento preventivo',
    precio: 80.00,
    estado_servicio: 'completado',
    observaciones: 'Mantenimiento preventivo completado',
    fecha_completado: '2024-01-16T17:00:00Z',
    calificacion: 5,
    is_active: true,
    created_at: '2024-01-11T10:00:00Z',
    updated_at: '2024-01-16T17:00:00Z'
  },
  {
    id: 3,
    fecha: '2024-01-17',
    tipo_trabajo: 1,
    tipo_trabajo_nombre: 'Instalación',
    tecnico_id: 1,
    tecnico_dni: '12345678',
    tecnico_nombre: 'Juan Pérez',
    cliente: 1,
    cliente_nombre: 'Cliente Test 1',
    unidad: 3,
    unidad_placa: 'GHI-789',
    descripcion: 'Instalación en progreso',
    precio: 150.00,
    estado_servicio: 'en_proceso',
    observaciones: 'En progreso',
    is_active: true,
    created_at: '2024-01-12T10:00:00Z',
    updated_at: '2024-01-17T10:00:00Z'
  }
]

export const mockTipoTrabajos: TipoTrabajo[] = [
  {
    id: 1,
    nombre: 'instalacion',
    nombre_display: 'Instalación',
    descripcion: 'Instalación de dispositivos GPS',
    precio_base: 150.00,
    duracion_estimada: 480, // 8 horas en minutos
    requiere_gps: true,
    requiere_sim: true,
    servicios_count: 2,
    is_active: true,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z'
  },
  {
    id: 2,
    nombre: 'mantenimiento',
    nombre_display: 'Mantenimiento',
    descripcion: 'Mantenimiento preventivo de dispositivos',
    precio_base: 80.00,
    duracion_estimada: 240, // 4 horas en minutos
    requiere_gps: false,
    requiere_sim: false,
    servicios_count: 1,
    is_active: true,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z'
  },
  {
    id: 3,
    nombre: 'reparacion',
    nombre_display: 'Reparación',
    descripcion: 'Reparación de dispositivos dañados',
    precio_base: 120.00,
    duracion_estimada: 360, // 6 horas en minutos
    requiere_gps: true,
    requiere_sim: false,
    servicios_count: 0,
    is_active: false,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z'
  }
]

/**
 * Create a test store with initial state
 */
export const createTestStore = (initialState?: any): Store => {
  return configureStore({
    reducer: {
      auth: authReducer,
      entities: entitiesReducer,
    },
    preloadedState: initialState,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,
      }),
  })
}

/**
 * Create a test query client with default options for testing
 */
export const createTestQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

/**
 * Custom render function with all providers
 */
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialState?: any
  store?: Store
  queryClient?: QueryClient
}

export const renderWithProviders = (
  ui: React.ReactElement,
  {
    initialState,
    store = createTestStore(initialState),
    queryClient = createTestQueryClient(),
    ...renderOptions
  }: CustomRenderOptions = {}
): RenderResult & { store: Store; queryClient: QueryClient } => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <BrowserRouter>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </Provider>
    </BrowserRouter>
  )

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    store,
    queryClient,
  }
}

/**
 * Helper to create mock API responses
 */
export const createMockApiResponse = <T,>(data: T, total?: number) => ({
  results: Array.isArray(data) ? data : [data],
  count: total ?? (Array.isArray(data) ? data.length : 1),
  next: null,
  previous: null,
})

/**
 * Helper to wait for queries to settle
 */
export const waitForQueriesToSettle = async (queryClient: QueryClient) => {
  const queries = queryClient.getQueryCache().getAll()
  await Promise.all(
    queries.map(query => {
      if (query.state.status === 'pending') {
        return query.promise
      }
      return Promise.resolve()
    })
  )
}

/**
 * Mock user with permissions for testing
 */
export const mockAuthenticatedUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  role: 'admin',
  permissions: ['view_servicio', 'add_servicio', 'change_servicio', 'delete_servicio'],
  is_active: true,
  date_joined: '2024-01-01T10:00:00Z',
}

/**
 * Initial auth state for testing
 */
export const mockAuthState = {
  user: mockAuthenticatedUser,
  token: 'mock-token',
  isAuthenticated: true,
  isLoading: false,
  error: null,
  permissions: mockAuthenticatedUser.permissions,
}

/**
 * Helper to create authenticated render
 */
export const renderWithAuth = (
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
) => {
  const initialState = {
    auth: mockAuthState,
    ...options.initialState,
  }

  return renderWithProviders(ui, {
    ...options,
    initialState,
  })
}