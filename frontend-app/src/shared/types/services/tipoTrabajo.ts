// src/shared/types/services/tipoTrabajo.ts
import type { BaseEntity, PaginationParams } from './common';

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

// Interface for updating work types - allows partial updates of any TipoTrabajoCreateData field
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
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