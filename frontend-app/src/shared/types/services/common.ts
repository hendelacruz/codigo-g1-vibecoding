// src/shared/types/services/common.ts
export type EstadoServicio = 'pendiente' | 'programado' | 'en_proceso' | 'completado' | 'cancelado' | 'reprogramado';

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