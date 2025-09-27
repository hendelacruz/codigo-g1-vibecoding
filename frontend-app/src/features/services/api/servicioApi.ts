// src/features/services/api/servicioApi.ts
import type { AxiosResponse } from 'axios';
import servicesApi from './servicesApi';
import type { 
  Servicio, 
  ServicioCreateData, 
  ServicioUpdateData, 
  ServicioFilters,
  ServicioEstadisticas
} from '../../../shared/types/services/servicio';

// Re-export types for convenience
export type { Servicio, ServicioCreateData, ServicioUpdateData, ServicioFilters, ServicioEstadisticas };
import type { ApiResponse, EstadoServicio } from '../../../shared/types/services/common';

export interface ServicioApiService {
  getAll: (params?: ServicioFilters) => Promise<AxiosResponse<ApiResponse<Servicio>>>;
  getById: (id: number) => Promise<AxiosResponse<Servicio>>;
  create: (data: ServicioCreateData) => Promise<AxiosResponse<Servicio>>;
  update: (id: number, data: ServicioUpdateData) => Promise<AxiosResponse<Servicio>>;
  partialUpdate: (id: number, data: Partial<ServicioUpdateData>) => Promise<AxiosResponse<Servicio>>;
  delete: (id: number) => Promise<AxiosResponse<void>>;
  updateStatus: (id: number, status: EstadoServicio) => Promise<AxiosResponse<Servicio>>;
  toggleActive: (id: number) => Promise<AxiosResponse<Servicio>>;
  getEstadisticas: (params?: Record<string, unknown>) => Promise<AxiosResponse<ServicioEstadisticas>>;
  getByTipoTrabajo: (tipoTrabajoId: number, params?: ServicioFilters) => Promise<AxiosResponse<ApiResponse<Servicio>>>;
}

export const servicioApi: ServicioApiService = {
  // GET /api/services/servicios/
  getAll: (params = {}) => 
    servicesApi.get<ApiResponse<Servicio>>('/api/services/servicios/', { params }),

  // GET /api/services/servicios/{id}/
  getById: (id: number) => 
    servicesApi.get<Servicio>(`/api/services/servicios/${id}/`),

  // POST /api/services/servicios/
  create: (data: ServicioCreateData) => 
    servicesApi.post<Servicio>('/api/services/servicios/', data),

  // PUT /api/services/servicios/{id}/
  update: (id: number, data: ServicioUpdateData) => 
    servicesApi.put<Servicio>(`/api/services/servicios/${id}/`, data),

  // PATCH /api/services/servicios/{id}/
  partialUpdate: (id: number, data: Partial<ServicioUpdateData>) => 
    servicesApi.patch<Servicio>(`/api/services/servicios/${id}/`, data),

  // DELETE /api/services/servicios/{id}/
  delete: (id: number) => 
    servicesApi.delete<void>(`/api/services/servicios/${id}/`),

  // PATCH /api/services/servicios/{id}/status/
  updateStatus: (id: number, status: EstadoServicio) => 
    servicesApi.patch<Servicio>(`/api/services/servicios/${id}/status/`, { status }),

  // PATCH /api/services/servicios/{id}/toggle_active/
  toggleActive: (id: number) => 
    servicesApi.patch<Servicio>(`/api/services/servicios/${id}/toggle_active/`),

  // GET /api/services/servicios/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get<ServicioEstadisticas>('/api/services/servicios/estadisticas/', { params }),

  // GET /api/services/servicios/?tipo_trabajo={tipoTrabajoId}
  getByTipoTrabajo: (tipoTrabajoId: number, params = {}) => 
    servicesApi.get<ApiResponse<Servicio>>('/api/services/servicios/', { 
      params: { ...params, tipo_trabajo: tipoTrabajoId } 
    })
};