import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { 
  useTipoTrabajos, 
  useTipoTrabajo, 
  useCreateTipoTrabajo, 
  useUpdateTipoTrabajo, 
  useDeleteTipoTrabajo,
  useTipoTrabajoEstadisticas 
} from '../useTipoTrabajo'
import { mockTipoTrabajos, createMockApiResponse } from '../../__tests__/test-utils'
import type { TipoTrabajoCreateData, TipoTrabajoUpdateData } from '../../../../shared/types/services/tipoTrabajo'

// Configuración del servidor MSW
const server = setupServer(
  // GET /api/tipo-trabajos/
  http.get('/api/tipo-trabajos/', ({ request }) => {
    const url = new URL(request.url)
    const page = url.searchParams.get('page') || '1'
    const pageSize = url.searchParams.get('page_size') || '10'
    const search = url.searchParams.get('search')
    const requiereGps = url.searchParams.get('requiere_gps')
    const requiereSim = url.searchParams.get('requiere_sim')
    
    let filteredTipoTrabajos = mockTipoTrabajos
    
    if (search) {
      filteredTipoTrabajos = filteredTipoTrabajos.filter(tt => 
        tt.nombre.toLowerCase().includes(search.toLowerCase()) ||
        tt.descripcion?.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    if (requiereGps !== null) {
      filteredTipoTrabajos = filteredTipoTrabajos.filter(tt => 
        tt.requiere_gps === (requiereGps === 'true')
      )
    }
    
    if (requiereSim !== null) {
      filteredTipoTrabajos = filteredTipoTrabajos.filter(tt => 
        tt.requiere_sim === (requiereSim === 'true')
      )
    }

    return HttpResponse.json(createMockApiResponse(filteredTipoTrabajos))
  }),

  // GET /api/tipo-trabajos/:id/
  http.get('/api/tipo-trabajos/:id/', ({ params }) => {
    const { id } = params
    const tipoTrabajo = mockTipoTrabajos.find(tt => tt.id === parseInt(id as string))
    
    if (!tipoTrabajo) {
      return HttpResponse.json({ detail: 'Tipo de trabajo not found' }, { status: 404 })
    }

    return HttpResponse.json(tipoTrabajo)
  }),

  // POST /api/tipo-trabajos/
  http.post('/api/tipo-trabajos/', async ({ request }) => {
    const body = await request.json() as TipoTrabajoCreateData
    const newTipoTrabajo = {
      id: mockTipoTrabajos.length + 1,
      ...body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true
    }

    return HttpResponse.json(newTipoTrabajo, { status: 201 })
  }),

  // PUT /api/tipo-trabajos/:id/
  http.put('/api/tipo-trabajos/:id/', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as TipoTrabajoUpdateData
    const tipoTrabajo = mockTipoTrabajos.find(tt => tt.id === parseInt(id as string))
    
    if (!tipoTrabajo) {
      return HttpResponse.json({ detail: 'Tipo de trabajo not found' }, { status: 404 })
    }

    const updatedTipoTrabajo = {
      ...tipoTrabajo,
      ...body,
      updated_at: new Date().toISOString()
    }

    return HttpResponse.json(updatedTipoTrabajo)
  }),

  // DELETE /api/tipo-trabajos/:id/
  http.delete('/api/tipo-trabajos/:id/', ({ params }) => {
    const { id } = params
    const tipoTrabajo = mockTipoTrabajos.find(tt => tt.id === parseInt(id as string))
    
    if (!tipoTrabajo) {
      return HttpResponse.json({ detail: 'Tipo de trabajo not found' }, { status: 404 })
    }

    return new HttpResponse(null, { status: 204 })
  }),

  // GET /api/tipo-trabajos/estadisticas/
  http.get('/api/tipo-trabajos/estadisticas/', () => {
    const estadisticas = {
      total_tipos: mockTipoTrabajos.length,
      tipos_con_gps: mockTipoTrabajos.filter(tt => tt.requiere_gps).length,
      tipos_con_sim: mockTipoTrabajos.filter(tt => tt.requiere_sim).length,
      precio_promedio: mockTipoTrabajos.length > 0 
        ? mockTipoTrabajos.reduce((sum, tt) => sum + (tt.precio_base || 0), 0) / mockTipoTrabajos.length 
        : 0,
      duracion_promedio: mockTipoTrabajos.length > 0 
        ? mockTipoTrabajos.reduce((sum, tt) => sum + (tt.duracion_estimada || 0), 0) / mockTipoTrabajos.length 
        : 0,
      precio_maximo: Math.max(...mockTipoTrabajos.map(tt => tt.precio_base || 0)),
      precio_minimo: Math.min(...mockTipoTrabajos.map(tt => tt.precio_base || 0))
    }

    return HttpResponse.json(estadisticas)
  })
)

// Helper para crear wrapper con QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
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

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useTipoTrabajo Integration Tests', () => {
  beforeEach(() => {
    server.listen({ onUnhandledRequest: 'error' })
  })

  afterEach(() => {
    server.resetHandlers()
    vi.clearAllMocks()
  })

  afterAll(() => {
    server.close()
  })

  describe('useTipoTrabajos', () => {
    it('debe cargar tipos de trabajo correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useTipoTrabajos(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(Array.isArray(result.current.data)).toBe(true)
      expect(result.current.data?.length).toBeGreaterThan(0)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('debe aplicar filtro de búsqueda correctamente', async () => {
      const wrapper = createWrapper()
      const searchTerm = 'Instalación'
      const { result } = renderHook(
        () => useTipoTrabajos({ search: searchTerm }), 
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      // Verificar que todos los tipos devueltos contienen el término de búsqueda
      result.current.data?.forEach(tipoTrabajo => {
        const matchesSearch = 
          tipoTrabajo.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tipoTrabajo.descripcion?.toLowerCase().includes(searchTerm.toLowerCase())
        expect(matchesSearch).toBe(true)
      })
    })

    it('debe manejar errores de red', async () => {
      // Simular error del servidor
      server.use(
        http.get('/api/tipo-trabajos/', () => {
          return HttpResponse.json({ error: 'Server error' }, { status: 500 })
        })
      )

      const wrapper = createWrapper()
      const { result } = renderHook(() => useTipoTrabajos(), { wrapper })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toBeDefined()
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('useTipoTrabajo', () => {
    it('debe cargar un tipo de trabajo específico', async () => {
      const wrapper = createWrapper()
      const tipoTrabajoId = mockTipoTrabajos[0]?.id || 1
      const { result } = renderHook(() => useTipoTrabajo(tipoTrabajoId), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(result.current.data?.id).toBe(tipoTrabajoId)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('debe manejar tipo de trabajo no encontrado', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useTipoTrabajo(999), { wrapper })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toBeDefined()
      expect(result.current.data).toBeUndefined()
    })
  })

  describe('useCreateTipoTrabajo', () => {
    it('debe crear un tipo de trabajo correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useCreateTipoTrabajo(), { wrapper })

      const newTipoTrabajoData: TipoTrabajoCreateData = {
        nombre: 'Nuevo Tipo de Trabajo',
        descripcion: 'Descripción del nuevo tipo',
        precio_base: 250.00,
        duracion_estimada: 120,
        requiere_gps: true,
        requiere_sim: false
      }

      await result.current.mutateAsync(newTipoTrabajoData)

      expect(result.current.isSuccess).toBe(true)
      expect(result.current.data).toBeDefined()
      expect(result.current.data?.nombre).toBe(newTipoTrabajoData.nombre)
      expect(result.current.data?.precio_base).toBe(newTipoTrabajoData.precio_base)
      expect(result.current.data?.requiere_gps).toBe(newTipoTrabajoData.requiere_gps)
    })
  })

  describe('useUpdateTipoTrabajo', () => {
    it('debe actualizar un tipo de trabajo correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useUpdateTipoTrabajo(), { wrapper })

      const tipoTrabajoId = mockTipoTrabajos[0]?.id || 1
      const updateData: TipoTrabajoUpdateData = {
        nombre: 'Tipo Actualizado',
        precio_base: 300.00,
        duracion_estimada: 180,
        requiere_gps: false
      }

      await result.current.mutateAsync({ id: tipoTrabajoId, data: updateData })

      expect(result.current.isSuccess).toBe(true)
      expect(result.current.data).toBeDefined()
      expect(result.current.data?.nombre).toBe(updateData.nombre)
      expect(result.current.data?.precio_base).toBe(updateData.precio_base)
      expect(result.current.data?.requiere_gps).toBe(updateData.requiere_gps)
    })
  })

  describe('useDeleteTipoTrabajo', () => {
    it('debe eliminar un tipo de trabajo correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useDeleteTipoTrabajo(), { wrapper })

      const tipoTrabajoId = mockTipoTrabajos[0]?.id || 1

      await result.current.mutateAsync(tipoTrabajoId)

      expect(result.current.isSuccess).toBe(true)
    })
  })

  describe('useTipoTrabajoEstadisticas', () => {
    it('debe cargar estadísticas correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useTipoTrabajoEstadisticas(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(result.current.data?.total_tipos).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.tipos_con_gps).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.tipos_con_sim).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.precio_promedio).toBeGreaterThanOrEqual(0)
    })
  })
})