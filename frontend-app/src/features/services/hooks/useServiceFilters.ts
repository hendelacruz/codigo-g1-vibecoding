// Custom hook for Service Filters management
import { useState, useCallback } from 'react';
import type { ServicioFilters } from '../api/servicioApi';

export interface UseServiceFiltersReturn {
  filters: ServicioFilters;
  setFilter: <K extends keyof ServicioFilters>(key: K, value: ServicioFilters[K]) => void;
  clearFilters: () => void;
  resetFilters: () => void;
  hasActiveFilters: boolean;
}

const defaultFilters: ServicioFilters = {};

export const useServiceFilters = (initialFilters: ServicioFilters = defaultFilters): UseServiceFiltersReturn => {
  const [filters, setFilters] = useState<ServicioFilters>(initialFilters);

  const setFilter = useCallback(<K extends keyof ServicioFilters>(
    key: K, 
    value: ServicioFilters[K]
  ) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const hasActiveFilters = Object.keys(filters).some(key => {
    const value = filters[key as keyof ServicioFilters];
    return value !== undefined && value !== null && value !== '';
  });

  return {
    filters,
    setFilter,
    clearFilters,
    resetFilters,
    hasActiveFilters,
  };
};