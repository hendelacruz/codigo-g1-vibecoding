// src/shared/utils/services/serviceConstants.ts
import type { EstadoServicio, TipoTrabajoValue } from '../../types/services/common';

export interface EstadoChoice {
  value: EstadoServicio;
  label: string;
  color: 'yellow' | 'blue' | 'green' | 'red' | 'orange' | 'purple';
}

export interface TipoTrabajoChoice {
  value: TipoTrabajoValue;
  label: string;
}

export const ESTADO_SERVICIO_CHOICES: EstadoChoice[] = [
  { value: 'pendiente', label: 'Pendiente', color: 'yellow' },
  { value: 'programado', label: 'Programado', color: 'blue' },
  { value: 'en_proceso', label: 'En Proceso', color: 'orange' },
  { value: 'completado', label: 'Completado', color: 'green' },
  { value: 'cancelado', label: 'Cancelado', color: 'red' },
  { value: 'reprogramado', label: 'Reprogramado', color: 'purple' }
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