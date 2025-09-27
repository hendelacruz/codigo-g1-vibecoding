// src/features/services/__tests__/mocks/handlers.ts
import { http, HttpResponse } from 'msw'
import type { Servicio, ServicioCreateData, ServicioUpdateData, ServicioEstadisticas } from '../../../../shared/types/services/servicio'
import type { TipoTrabajo, TipoTrabajoCreateData, TipoTrabajoUpdateData, TipoTrabajoEstadisticas } from '../../../../shared/types/services/tipoTrabajo'
import type { ApiResponse } from '../../../../shared/types/services/common'
import { createMockApiResponse } from '../../../__tests__/test-utils'

const API_BASE = '/api/services'

// Mock data
const mockServicios: Servicio[] = [
  {
    id: 1,
    fecha: '2024-01-15',
    tipo_trabajo: 1,
    tipo_trabajo_nombre: 'Instalación Nueva',
    tecnico_id: 1,
    tecnico_dni: '12345678',
    tecnico_nombre: 'Juan Pérez',
    cliente: 1,
    cliente_nombre: 'Empresa ABC',
    unidad: 1,
    unidad_placa: 'ABC-123',
    gps: 1,
    gps_codigo: 'GPS001',
    sim_card: 1,
    sim_numero: '987654321',
    descripcion: 'Instalación de GPS y SIM',
    precio: 150.00,
    estado_servicio: 'completado',
    observaciones: 'Servicio completado exitosamente',
    fecha_completado: '2024-01-15T16:30:00Z',
    calificacion: 5,
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-01-15T16:30:00Z',
    is_active: true
  },
  {
    id: 2,
    fecha: '2024-01-16',
    tipo_trabajo: 2,
    tipo_trabajo_nombre: 'Mantenimiento Preventivo',
    tecnico_id: 2,
    tecnico_dni: '87654321',
    tecnico_nombre: 'María García',
    cliente: 2,
    cliente_nombre: 'Transportes XYZ',
    unidad: 2,
    unidad_placa: 'XYZ-456',
    descripcion: 'Mantenimiento preventivo del sistema',
    precio: 80.00,
    estado_servicio: 'pendiente',
    created_at: '2024-01-16T09:00:00Z',
    updated_at: '2024-01-16T09:00:00Z',
    is_active: true
  }
]

const mockTipoTrabajos: TipoTrabajo[] = [
  {
    id: 1,
    nombre: 'instalacion_nueva',
    nombre_display: 'Instalación Nueva',
    descripcion: 'Instalación completa de GPS y SIM',
    precio_base: 150.00,
    duracion_estimada: 120,
    requiere_gps: true,
    requiere_sim: true,
    servicios_count: 25,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    is_active: true
  },
  {
    id: 2,
    nombre: 'mantenimiento_preventivo',
    nombre_display: 'Mantenimiento Preventivo',
    descripcion: 'Mantenimiento preventivo del sistema',
    precio_base: 80.00,
    duracion_estimada: 60,
    requiere_gps: false,
    requiere_sim: false,
    servicios_count: 15,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    is_active: true
  }
]

export const serviciosHandlers = [
  // GET /api/services/servicios/
  http.get(`${API_BASE}/servicios/`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '10')
    const search = url.searchParams.get('search')
    const estado = url.searchParams.get('estado_servicio')

    let filteredServicios = [...mockServicios]

    if (search) {
      filteredServicios = filteredServicios.filter(servicio =>
        servicio.descripcion.toLowerCase().includes(search.toLowerCase()) ||
        servicio.cliente_nombre.toLowerCase().includes(search.toLowerCase())
      )
    }

    if (estado) {
      filteredServicios = filteredServicios.filter(servicio => servicio.estado_servicio === estado)
    }

    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedServicios = filteredServicios.slice(startIndex, endIndex)

    const response = createMockApiResponse(paginatedServicios)

    return HttpResponse.json(response)
  }),

  // GET /api/services/servicios/{id}/
  http.get(`${API_BASE}/servicios/:id`, ({ params }) => {
    const id = parseInt(params.id as string)
    const servicio = mockServicios.find(s => s.id === id)
    
    if (!servicio) {
      return HttpResponse.json({ detail: 'Servicio not found' }, { status: 404 })
    }

    return HttpResponse.json(servicio)
  }),

  // POST /api/services/servicios/
  http.post(`${API_BASE}/servicios/`, async ({ request }) => {
    const data = await request.json() as ServicioCreateData

    const newServicio: Servicio = {
      id: mockServicios.length + 1,
      fecha: data.fecha,
      tipo_trabajo: data.tipo_trabajo,
      tipo_trabajo_nombre: 'Instalación Nueva',
      tecnico_id: 1,
      tecnico_dni: data.tecnico_dni,
      tecnico_nombre: 'Juan Pérez',
      cliente: data.cliente,
      cliente_nombre: 'Cliente Test',
      unidad: data.unidad,
      unidad_placa: 'ABC-123',
      gps: data.gps,
      sim_card: data.sim_card,
      descripcion: data.descripcion,
      precio: data.precio,
      estado_servicio: data.estado_servicio,
      observaciones: data.observaciones,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true
    }

    mockServicios.push(newServicio)
    return HttpResponse.json(newServicio, { status: 201 })
  }),

  // PUT /api/services/servicios/{id}/
  http.put(`${API_BASE}/servicios/:id`, async ({ params, request }) => {
    const id = parseInt(params.id as string)
    const data = await request.json() as ServicioUpdateData
    const index = mockServicios.findIndex(s => s.id === id)

    if (index === -1) {
      return HttpResponse.json({ detail: 'Servicio not found' }, { status: 404 })
    }

    const updatedServicio: Servicio = {
      ...mockServicios[index],
      ...data,
      updated_at: new Date().toISOString()
    }

    mockServicios[index] = updatedServicio
    return HttpResponse.json(updatedServicio)
  }),

  // DELETE /api/services/servicios/{id}/
  http.delete(`${API_BASE}/servicios/:id`, ({ params }) => {
    const id = parseInt(params.id as string)
    const index = mockServicios.findIndex(s => s.id === id)

    if (index === -1) {
      return HttpResponse.json({ detail: 'Servicio not found' }, { status: 404 })
    }

    mockServicios.splice(index, 1)
    return HttpResponse.json({}, { status: 204 })
  }),

  // GET /api/services/servicios/estadisticas/
  http.get(`${API_BASE}/servicios/estadisticas/`, () => {
    const stats: ServicioEstadisticas = {
      total_servicios: mockServicios.length,
      pendientes: mockServicios.filter(s => s.estado_servicio === 'pendiente').length,
      en_proceso: mockServicios.filter(s => s.estado_servicio === 'en_proceso').length,
      completados: mockServicios.filter(s => s.estado_servicio === 'completado').length,
      cancelados: mockServicios.filter(s => s.estado_servicio === 'cancelado').length,
      reprogramados: mockServicios.filter(s => s.estado_servicio === 'reprogramado').length,
      ingresos_total: mockServicios.reduce((sum, s) => sum + s.precio, 0),
      ingresos_mes_actual: mockServicios
        .filter(s => new Date(s.fecha).getMonth() === new Date().getMonth())
        .reduce((sum, s) => sum + s.precio, 0),
      promedio_calificacion: mockServicios
        .filter(s => s.calificacion)
        .reduce((sum, s, _, arr) => sum + (s.calificacion || 0) / arr.length, 0)
    }

    return HttpResponse.json(stats)
  })
]

export const tipoTrabajosHandlers = [
  // GET /api/services/tipos-trabajo/
  http.get(`${API_BASE}/tipos-trabajo/`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '10')
    const search = url.searchParams.get('search')
    const isActive = url.searchParams.get('is_active')

    let filteredTipos = [...mockTipoTrabajos]

    if (search) {
      filteredTipos = filteredTipos.filter(tipo =>
        tipo.nombre.toLowerCase().includes(search.toLowerCase()) ||
        tipo.descripcion.toLowerCase().includes(search.toLowerCase())
      )
    }

    if (isActive !== null) {
      filteredTipos = filteredTipos.filter(tipo => tipo.is_active === (isActive === 'true'))
    }

    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedTipos = filteredTipos.slice(startIndex, endIndex)

    const response = createMockApiResponse(paginatedTipos)

    return HttpResponse.json(response)
  }),

  // GET /api/services/tipos-trabajo/{id}/
  http.get(`${API_BASE}/tipos-trabajo/:id`, ({ params }) => {
    const id = parseInt(params.id as string)
    const tipo = mockTipoTrabajos.find(t => t.id === id)
    
    if (!tipo) {
      return HttpResponse.json({ detail: 'TipoTrabajo not found' }, { status: 404 })
    }

    return HttpResponse.json(tipo)
  }),

  // POST /api/services/tipos-trabajo/
  http.post(`${API_BASE}/tipos-trabajo/`, async ({ request }) => {
    const data = await request.json() as TipoTrabajoCreateData

    const newTipo: TipoTrabajo = {
      id: mockTipoTrabajos.length + 1,
      nombre: data.nombre,
      nombre_display: data.nombre.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      descripcion: data.descripcion,
      precio_base: data.precio_base,
      duracion_estimada: data.duracion_estimada,
      requiere_gps: data.requiere_gps,
      requiere_sim: data.requiere_sim,
      servicios_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true
    }

    mockTipoTrabajos.push(newTipo)
    return HttpResponse.json(newTipo, { status: 201 })
  }),

  // PUT /api/services/tipos-trabajo/{id}/
  http.put(`${API_BASE}/tipos-trabajo/:id`, async ({ params, request }) => {
    const id = parseInt(params.id as string)
    const data = await request.json() as TipoTrabajoUpdateData
    const index = mockTipoTrabajos.findIndex(t => t.id === id)

    if (index === -1) {
      return HttpResponse.json({ detail: 'TipoTrabajo not found' }, { status: 404 })
    }

    const updatedTipo: TipoTrabajo = {
      ...mockTipoTrabajos[index],
      ...data,
      nombre_display: data.nombre ? data.nombre.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : mockTipoTrabajos[index].nombre_display,
      updated_at: new Date().toISOString()
    }

    mockTipoTrabajos[index] = updatedTipo
    return HttpResponse.json(updatedTipo)
  }),

  // DELETE /api/services/tipos-trabajo/{id}/
  http.delete(`${API_BASE}/tipos-trabajo/:id`, ({ params }) => {
    const id = parseInt(params.id as string)
    const index = mockTipoTrabajos.findIndex(t => t.id === id)

    if (index === -1) {
      return HttpResponse.json({ detail: 'TipoTrabajo not found' }, { status: 404 })
    }

    mockTipoTrabajos.splice(index, 1)
    return HttpResponse.json({}, { status: 204 })
  }),

  // GET /api/services/tipos-trabajo/estadisticas/
  http.get(`${API_BASE}/tipos-trabajo/estadisticas/`, () => {
    const stats: TipoTrabajoEstadisticas = {
      total_tipos: mockTipoTrabajos.length,
      activos: mockTipoTrabajos.filter(t => t.is_active).length,
      inactivos: mockTipoTrabajos.filter(t => !t.is_active).length,
      servicios_por_tipo: mockTipoTrabajos.map(tipo => ({
        tipo: tipo.nombre,
        tipo_display: tipo.nombre_display,
        count: tipo.servicios_count || 0,
        precio_promedio: tipo.precio_base
      }))
    }

    return HttpResponse.json(stats)
  })
]

// Error handlers
export const errorHandlers = [
  http.get(`${API_BASE}/servicios/error`, () => {
    return HttpResponse.json({ detail: 'Internal server error' }, { status: 500 })
  }),

  http.get(`${API_BASE}/tipos-trabajo/error`, () => {
    return HttpResponse.json({ detail: 'Internal server error' }, { status: 500 })
  })
]

export const handlers = [
  ...serviciosHandlers,
  ...tipoTrabajosHandlers,
  ...errorHandlers
]