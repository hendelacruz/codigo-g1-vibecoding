import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { 
  useServicios, 
  useServicio, 
  useCreateServicio, 
  useUpdateServicio, 
  useDeleteServicio,
  useServicioEstadisticas 
} from '../useServicio'
import { mockServicios, createMockApiResponse } from '../../__tests__/test-utils'
import type { ServicioCreateData, ServicioUpdateData } from '../../../../shared/types/services/servicio'

// Configuración del servidor MSW
const server = setupServer(
  // GET /api/servicios/
  rest.get('/api/servicios/', (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1'
    const pageSize = req.url.searchParams.get('page_size') || '10'
    const estado = req.url.searchParams.get('estado_servicio')
    
    let filteredServicios = mockServicios
    if (estado) {
      filteredServicios = mockServicios.filter(s => s.estado_servicio === estado)
    }

    return res(
      ctx.status(200),
      ctx.json(createMockApiResponse(filteredServicios))
    )
  }),

  // GET /api/servicios/:id/
  rest.get('/api/servicios/:id/', (req, res, ctx) => {
    const { id } = req.params
    const servicio = mockServicios.find(s => s.id === parseInt(id as string))
    
    if (!servicio) {
      return res(ctx.status(404), ctx.json({ detail: 'Servicio not found' }))
    }

    return res(ctx.status(200), ctx.json(servicio))
  }),

  // POST /api/servicios/
  rest.post('/api/servicios/', async (req, res, ctx) => {
    const body = await req.json() as ServicioCreateData
    const newServicio = {
      id: mockServicios.length + 1,
      ...body,
      fecha: body.fecha || new Date().toISOString().split('T')[0],
      estado_servicio: 'pendiente' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true
    }

    return res(ctx.status(201), ctx.json(newServicio))
  }),

  // PUT /api/servicios/:id/
  rest.put('/api/servicios/:id/', async (req, res, ctx) => {
    const { id } = req.params
    const body = await req.json() as ServicioUpdateData
    const servicio = mockServicios.find(s => s.id === parseInt(id as string))
    
    if (!servicio) {
      return res(ctx.status(404), ctx.json({ detail: 'Servicio not found' }))
    }

    const updatedServicio = {
      ...servicio,
      ...body,
      updated_at: new Date().toISOString()
    }

    return res(ctx.status(200), ctx.json(updatedServicio))
  }),

  // DELETE /api/servicios/:id/
  rest.delete('/api/servicios/:id/', (req, res, ctx) => {
    const { id } = req.params
    const servicio = mockServicios.find(s => s.id === parseInt(id as string))
    
    if (!servicio) {
      return res(ctx.status(404), ctx.json({ detail: 'Servicio not found' }))
    }

    return res(ctx.status(204))
  }),

  // GET /api/servicios/estadisticas/
  rest.get('/api/servicios/estadisticas/', (req, res, ctx) => {
    const estadisticas = {
      total_servicios: mockServicios.length,
      servicios_pendientes: mockServicios.filter(s => s.estado_servicio === 'pendiente').length,
      servicios_completados: mockServicios.filter(s => s.estado_servicio === 'completado').length,
      servicios_en_proceso: mockServicios.filter(s => s.estado_servicio === 'en_proceso').length,
      servicios_cancelados: mockServicios.filter(s => s.estado_servicio === 'cancelado').length,
      ingresos_totales: mockServicios.reduce((sum, s) => sum + (s.precio || 0), 0),
      promedio_precio: mockServicios.length > 0 
        ? mockServicios.reduce((sum, s) => sum + (s.precio || 0), 0) / mockServicios.length 
        : 0
    }

    return res(ctx.status(200), ctx.json(estadisticas))
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

describe('useServicio Integration Tests', () => {
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

  describe('useServicios', () => {
    it('debe cargar servicios correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicios(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(Array.isArray(result.current.data)).toBe(true)
      expect(result.current.data?.length).toBeGreaterThan(0)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('debe aplicar filtros correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(
        () => useServicios({ estado_servicio: 'pendiente' }), 
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      // Verificar que todos los servicios devueltos tienen estado 'pendiente'
      result.current.data?.forEach(servicio => {
        expect(servicio.estado_servicio).toBe('pendiente')
      })
    })

    it('debe manejar errores de red', async () => {
      // Simular error del servidor
      server.use(
        rest.get('/api/servicios/', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Server error' }))
        })
      )

      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicios(), { wrapper })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toBeDefined()
      expect(result.current.data).toBeUndefined()
    })

    it('debe refetch correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicios(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      const initialData = result.current.data
      
      // Ejecutar refetch
      await result.current.refetch()

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(result.current.data).toEqual(initialData)
    })
  })

  describe('useServicio', () => {
    it('debe cargar un servicio específico', async () => {
      const wrapper = createWrapper()
      const servicioId = mockServicios[0]?.id || 1
      const { result } = renderHook(() => useServicio(servicioId), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(result.current.data?.id).toBe(servicioId)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('debe manejar servicio no encontrado', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicio(999), { wrapper })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(result.current.error).toBeDefined()
      expect(result.current.data).toBeUndefined()
    })

    it('no debe ejecutar query si id es 0 o undefined', () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicio(0), { wrapper })

      expect(result.current.isPending).toBe(true)
      expect(result.current.fetchStatus).toBe('idle')
    })
  })

  describe('useCreateServicio', () => {
    it('debe crear un servicio correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useCreateServicio(), { wrapper })

      const newServicioData: ServicioCreateData = {
        tipo_trabajo: 1,
        tecnico_id: 1,
        cliente: 1,
        descripcion: 'Nuevo servicio de prueba',
        precio: 150.00,
        fecha: '2024-01-15'
      }

      await result.current.mutateAsync(newServicioData)

      expect(result.current.isSuccess).toBe(true)
      expect(result.current.data).toBeDefined()
      expect(result.current.data?.descripcion).toBe(newServicioData.descripcion)
      expect(result.current.data?.precio).toBe(newServicioData.precio)
    })

    it('debe manejar errores de validación', async () => {
      // Simular error de validación
      server.use(
        rest.post('/api/servicios/', (req, res, ctx) => {
          return res(
            ctx.status(400), 
            ctx.json({ 
              descripcion: ['Este campo es requerido'],
              precio: ['Debe ser un número positivo']
            })
          )
        })
      )

      const wrapper = createWrapper()
      const { result } = renderHook(() => useCreateServicio(), { wrapper })

      const invalidData = {} as ServicioCreateData

      try {
        await result.current.mutateAsync(invalidData)
      } catch (error) {
        expect(error).toBeDefined()
      }

      expect(result.current.isError).toBe(true)
    })
  })

  describe('useUpdateServicio', () => {
    it('debe actualizar un servicio correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useUpdateServicio(), { wrapper })

      const servicioId = mockServicios[0]?.id || 1
      const updateData: ServicioUpdateData = {
        descripcion: 'Descripción actualizada',
        precio: 200.00,
        estado_servicio: 'completado'
      }

      await result.current.mutateAsync({ id: servicioId, data: updateData })

      expect(result.current.isSuccess).toBe(true)
      expect(result.current.data).toBeDefined()
      expect(result.current.data?.descripcion).toBe(updateData.descripcion)
      expect(result.current.data?.precio).toBe(updateData.precio)
    })

    it('debe manejar servicio no encontrado en actualización', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useUpdateServicio(), { wrapper })

      const updateData: ServicioUpdateData = {
        descripcion: 'Descripción actualizada'
      }

      try {
        await result.current.mutateAsync({ id: 999, data: updateData })
      } catch (error) {
        expect(error).toBeDefined()
      }

      expect(result.current.isError).toBe(true)
    })
  })

  describe('useDeleteServicio', () => {
    it('debe eliminar un servicio correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useDeleteServicio(), { wrapper })

      const servicioId = mockServicios[0]?.id || 1

      await result.current.mutateAsync(servicioId)

      expect(result.current.isSuccess).toBe(true)
    })

    it('debe manejar servicio no encontrado en eliminación', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useDeleteServicio(), { wrapper })

      try {
        await result.current.mutateAsync(999)
      } catch (error) {
        expect(error).toBeDefined()
      }

      expect(result.current.isError).toBe(true)
    })
  })

  describe('useServicioEstadisticas', () => {
    it('debe cargar estadísticas correctamente', async () => {
      const wrapper = createWrapper()
      const { result } = renderHook(() => useServicioEstadisticas(), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
      expect(result.current.data?.total_servicios).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.servicios_pendientes).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.servicios_completados).toBeGreaterThanOrEqual(0)
      expect(result.current.data?.ingresos_totales).toBeGreaterThanOrEqual(0)
    })

    it('debe aplicar parámetros de filtro en estadísticas', async () => {
      const wrapper = createWrapper()
      const params = { fecha_inicio: '2024-01-01', fecha_fin: '2024-12-31' }
      const { result } = renderHook(() => useServicioEstadisticas(params), { wrapper })

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true)
      })

      expect(result.current.data).toBeDefined()
    })
  })

  describe('Invalidación de cache', () => {
    it('debe invalidar queries relacionadas después de crear', async () => {
      const wrapper = createWrapper()
      
      // Primero cargar la lista
      const { result: listResult } = renderHook(() => useServicios(), { wrapper })
      await waitFor(() => expect(listResult.current.isSuccess).toBe(true))
      
      const initialCount = listResult.current.data?.length || 0

      // Crear nuevo servicio
      const { result: createResult } = renderHook(() => useCreateServicio(), { wrapper })
      
      const newServicioData: ServicioCreateData = {
        tipo_trabajo: 1,
        tecnico_id: 1,
        cliente: 1,
        descripcion: 'Servicio para invalidación',
        precio: 100.00
      }

      await createResult.current.mutateAsync(newServicioData)

      // Verificar que la lista se actualiza automáticamente
      await waitFor(() => {
        expect(listResult.current.data?.length).toBeGreaterThan(initialCount)
      })
    })
  })
})