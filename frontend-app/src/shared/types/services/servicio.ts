// src/shared/types/services/servicio.ts
import type { BaseEntity, EstadoServicio, DateRangeFilter, PaginationParams } from './common';

export interface Servicio extends BaseEntity {
  fecha: string;
  tipo_trabajo: number;
  tipo_trabajo_nombre: string;
  tecnico_id: number;
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

// Interface for updating services - allows partial updates of any ServicioCreateData field
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface ServicioUpdateData extends Partial<ServicioCreateData> {}

export interface ServicioFilters extends PaginationParams, DateRangeFilter {
  estado_servicio?: EstadoServicio;
  tipo_trabajo?: number;
  tecnico_id?: number;
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