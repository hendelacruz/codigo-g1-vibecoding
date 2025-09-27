// src/features/services/api/tipoTrabajoApi.ts
import type { AxiosResponse } from 'axios';
import servicesApi from './servicesApi';
import type { 
  TipoTrabajo, 
  TipoTrabajoCreateData, 
  TipoTrabajoUpdateData, 
  TipoTrabajoFilters,
  TipoTrabajoEstadisticas 
} from '../../../shared/types/services/tipoTrabajo';
import type { ApiResponse } from '../../../shared/types/services/common';
import type { Servicio, ServicioFilters } from '../../../shared/types/services/servicio';

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
    servicesApi.get<ApiResponse<TipoTrabajo>>('/api/services/tipos-trabajo/', { params }),

  // GET /api/services/tipos-trabajo/{id}/
  getById: (id: number) => 
    servicesApi.get<TipoTrabajo>(`/api/services/tipos-trabajo/${id}/`),

  // POST /api/services/tipos-trabajo/
  create: (data: TipoTrabajoCreateData) => 
    servicesApi.post<TipoTrabajo>('/api/services/tipos-trabajo/', data),

  // PUT /api/services/tipos-trabajo/{id}/
  update: (id: number, data: TipoTrabajoUpdateData) => 
    servicesApi.put<TipoTrabajo>(`/api/services/tipos-trabajo/${id}/`, data),

  // PATCH /api/services/tipos-trabajo/{id}/
  partialUpdate: (id: number, data: Partial<TipoTrabajoUpdateData>) => 
    servicesApi.patch<TipoTrabajo>(`/api/services/tipos-trabajo/${id}/`, data),

  // DELETE /api/services/tipos-trabajo/{id}/
  delete: (id: number) => 
    servicesApi.delete<void>(`/api/services/tipos-trabajo/${id}/`),

  // PATCH /api/services/tipos-trabajo/{id}/toggle_active/
  toggleActive: (id: number) => 
    servicesApi.patch<TipoTrabajo>(`/api/services/tipos-trabajo/${id}/toggle_active/`),

  // GET /api/services/tipos-trabajo/{id}/servicios/
  getServicios: (id: number, params = {}) => 
    servicesApi.get<ApiResponse<Servicio>>(`/api/services/tipos-trabajo/${id}/servicios/`, { params }),

  // GET /api/services/tipos-trabajo/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get<TipoTrabajoEstadisticas>('/api/services/tipos-trabajo/estadisticas/', { params })
};