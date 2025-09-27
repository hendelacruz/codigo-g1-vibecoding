// src/features/services/hooks/useServicio.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { servicioApi } from '../api/servicioApi';
import type { 
  ServicioCreateData, 
  ServicioUpdateData, 
  ServicioFilters 
} from '../../../shared/types/services/servicio';
import type { EstadoServicio } from '../../../shared/types/services/common';

// Query keys for Servicio
export const SERVICIO_QUERY_KEYS = {
  all: ['servicio'] as const,
  lists: () => [...SERVICIO_QUERY_KEYS.all, 'list'] as const,
  list: (filters: ServicioFilters) => [...SERVICIO_QUERY_KEYS.lists(), filters] as const,
  details: () => [...SERVICIO_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: number) => [...SERVICIO_QUERY_KEYS.details(), id] as const,
  estadisticas: () => [...SERVICIO_QUERY_KEYS.all, 'estadisticas'] as const,
  byTipoTrabajo: (tipoTrabajoId: number) => [...SERVICIO_QUERY_KEYS.all, 'byTipoTrabajo', tipoTrabajoId] as const,
} as const;

// Hook for fetching all servicios
export const useServicios = (filters: ServicioFilters = {}) => {
  return useQuery({
    queryKey: SERVICIO_QUERY_KEYS.list(filters),
    queryFn: () => servicioApi.getAll(filters),
    select: (data) => data.data,
  });
};

// Hook for fetching a single servicio
export const useServicio = (id: number) => {
  return useQuery({
    queryKey: SERVICIO_QUERY_KEYS.detail(id),
    queryFn: () => servicioApi.getById(id),
    select: (data) => data.data,
    enabled: !!id,
  });
};

// Hook for creating a servicio
export const useCreateServicio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ServicioCreateData) => servicioApi.create(data),
    onSuccess: () => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for updating a servicio
export const useUpdateServicio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ServicioUpdateData }) => 
      servicioApi.update(id, data),
    onSuccess: (_, { id }) => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for partial update of a servicio
export const usePartialUpdateServicio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ServicioUpdateData> }) => 
      servicioApi.partialUpdate(id, data),
    onSuccess: (_, { id }) => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for deleting a servicio
export const useDeleteServicio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => servicioApi.delete(id),
    onSuccess: () => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for updating servicio status
export const useUpdateServicioStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: EstadoServicio }) => 
      servicioApi.updateStatus(id, status),
    onSuccess: (_, { id }) => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for toggling active status
export const useToggleActiveServicio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => servicioApi.toggleActive(id),
    onSuccess: (_, id) => {
      // Invalidate all servicio-related queries to ensure dashboard updates
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: SERVICIO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for fetching servicios by tipo de trabajo
export const useServiciosByTipoTrabajo = (tipoTrabajoId: number, filters: ServicioFilters = {}) => {
  return useQuery({
    queryKey: [...SERVICIO_QUERY_KEYS.byTipoTrabajo(tipoTrabajoId), filters],
    queryFn: () => servicioApi.getByTipoTrabajo(tipoTrabajoId, filters),
    select: (data) => data.data,
    enabled: !!tipoTrabajoId,
  });
};

// Hook for fetching estadisticas
export const useServicioEstadisticas = (params = {}) => {
  return useQuery({
    queryKey: [...SERVICIO_QUERY_KEYS.estadisticas(), params],
    queryFn: () => servicioApi.getEstadisticas(params),
    select: (data) => data.data,
  });
};