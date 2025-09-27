// Service utility functions and helpers
import type { Servicio } from '../api/servicioApi';

// Service status utilities
export const SERVICE_STATUSES = {
  PENDIENTE: 'pendiente',
  PROGRAMADO: 'programado',
  EN_PROCESO: 'en_proceso',
  COMPLETADO: 'completado',
  CANCELADO: 'cancelado',
  REPROGRAMADO: 'reprogramado',
} as const;

export const SERVICE_STATUS_LABELS: Record<Servicio['estado_servicio'], string> = {
  pendiente: 'Pendiente',
  programado: 'Programado',
  en_proceso: 'En Proceso',
  completado: 'Completado',
  cancelado: 'Cancelado',
  reprogramado: 'Reprogramado',
};

export const SERVICE_STATUS_COLORS: Record<Servicio['estado_servicio'], string> = {
  pendiente: 'bg-yellow-100 text-yellow-800',
  programado: 'bg-blue-100 text-blue-800',
  en_proceso: 'bg-orange-100 text-orange-800',
  completado: 'bg-green-100 text-green-800',
  cancelado: 'bg-red-100 text-red-800',
  reprogramado: 'bg-purple-100 text-purple-800',
};

// Date utilities
export const formatServiceDate = (date: Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const isServiceOverdue = (servicio: Servicio): boolean => {
  if (servicio.estado_servicio === 'completado' || servicio.estado_servicio === 'cancelado') {
    return false;
  }
  
  const now = new Date();
  const scheduledDate = new Date(servicio.fecha);
  
  return scheduledDate < now;
};

export const getServiceDuration = (servicio: Servicio): number | null => {
  if (!servicio.fecha || !servicio.fecha_completado) {
    return null;
  }
  
  const start = new Date(servicio.fecha);
  const end = new Date(servicio.fecha_completado);
  
  return end.getTime() - start.getTime();
};

// Validation utilities
export const isValidServiceStatus = (status: string): status is Servicio['estado_servicio'] => {
  return Object.values(SERVICE_STATUSES).includes(status as Servicio['estado_servicio']);
};

export const canUpdateServiceStatus = (
  currentStatus: Servicio['estado_servicio'], 
  newStatus: Servicio['estado_servicio']
): boolean => {
  // Define valid status transitions
  const validTransitions: Record<Servicio['estado_servicio'], Servicio['estado_servicio'][]> = {
    pendiente: ['programado', 'en_proceso', 'cancelado', 'reprogramado'],
    programado: ['en_proceso', 'cancelado', 'reprogramado'],
    en_proceso: ['completado', 'cancelado', 'reprogramado'],
    completado: [], // No transitions from completed
    cancelado: ['pendiente', 'programado', 'reprogramado'], // Can reactivate
    reprogramado: ['pendiente', 'programado', 'en_proceso', 'cancelado'],
  };
  
  return validTransitions[currentStatus].includes(newStatus);
};

// Filter utilities
export const getActiveServicesCount = (servicios: Servicio[]): number => {
  return servicios.filter(s => 
    s.estado_servicio === 'pendiente' || s.estado_servicio === 'en_proceso'
  ).length;
};

export const getOverdueServicesCount = (servicios: Servicio[]): number => {
  return servicios.filter(isServiceOverdue).length;
};

export const groupServicesByStatus = (servicios: Servicio[]): Record<Servicio['estado_servicio'], Servicio[]> => {
  return servicios.reduce((acc, servicio) => {
    if (!acc[servicio.estado_servicio]) {
      acc[servicio.estado_servicio] = [];
    }
    acc[servicio.estado_servicio].push(servicio);
    return acc;
  }, {} as Record<Servicio['estado_servicio'], Servicio[]>);
};