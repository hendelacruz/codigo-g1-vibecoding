// src/features/services/hooks/useTipoTrabajo.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tipoTrabajoApi } from '../api/tipoTrabajoApi';
import type { 
  TipoTrabajoCreateData, 
  TipoTrabajoUpdateData, 
  TipoTrabajoFilters 
} from '../../../shared/types/services/tipoTrabajo';

// Query keys for TipoTrabajo
export const TIPO_TRABAJO_QUERY_KEYS = {
  all: ['tipoTrabajo'] as const,
  lists: () => [...TIPO_TRABAJO_QUERY_KEYS.all, 'list'] as const,
  list: (filters: TipoTrabajoFilters) => [...TIPO_TRABAJO_QUERY_KEYS.lists(), filters] as const,
  details: () => [...TIPO_TRABAJO_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: number) => [...TIPO_TRABAJO_QUERY_KEYS.details(), id] as const,
  estadisticas: () => [...TIPO_TRABAJO_QUERY_KEYS.all, 'estadisticas'] as const,
} as const;

// Hook for fetching all tipos de trabajo
export const useTipoTrabajos = (filters: TipoTrabajoFilters = {}) => {
  return useQuery({
    queryKey: TIPO_TRABAJO_QUERY_KEYS.list(filters),
    queryFn: () => tipoTrabajoApi.getAll(filters),
    select: (data) => data.data,
  });
};

// Hook for fetching a single tipo de trabajo
export const useTipoTrabajo = (id: number) => {
  return useQuery({
    queryKey: TIPO_TRABAJO_QUERY_KEYS.detail(id),
    queryFn: () => tipoTrabajoApi.getById(id),
    select: (data) => data.data,
    enabled: !!id,
  });
};

// Hook for creating a tipo de trabajo
export const useCreateTipoTrabajo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TipoTrabajoCreateData) => tipoTrabajoApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for updating a tipo de trabajo
export const useUpdateTipoTrabajo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TipoTrabajoUpdateData }) => 
      tipoTrabajoApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.detail(id) });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for partial update of a tipo de trabajo
export const usePartialUpdateTipoTrabajo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TipoTrabajoUpdateData> }) => 
      tipoTrabajoApi.partialUpdate(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.detail(id) });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for deleting a tipo de trabajo
export const useDeleteTipoTrabajo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => tipoTrabajoApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for toggling active status
export const useToggleActiveTipoTrabajo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => tipoTrabajoApi.toggleActive(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.detail(id) });
      queryClient.invalidateQueries({ queryKey: TIPO_TRABAJO_QUERY_KEYS.estadisticas() });
    },
  });
};

// Hook for fetching servicios of a tipo de trabajo
export const useTipoTrabajoServicios = (id: number, filters = {}) => {
  return useQuery({
    queryKey: [...TIPO_TRABAJO_QUERY_KEYS.detail(id), 'servicios', filters],
    queryFn: () => tipoTrabajoApi.getServicios(id, filters),
    select: (data) => data.data,
    enabled: !!id,
  });
};

// Hook for fetching estadisticas
export const useTipoTrabajoEstadisticas = (params = {}) => {
  return useQuery({
    queryKey: [...TIPO_TRABAJO_QUERY_KEYS.estadisticas(), params],
    queryFn: () => tipoTrabajoApi.getEstadisticas(params),
    select: (data) => data.data,
  });
};