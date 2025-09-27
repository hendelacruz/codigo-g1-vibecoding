// src/hooks/useTechnicians.ts
import { useQuery } from '@tanstack/react-query';
import { getUsers } from '../services/userService';
import type { User } from '../shared/types/common';

/**
 * Hook para obtener usuarios con rol de técnico
 * Utiliza React Query para cache y gestión de estado
 */
export const useTechnicians = () => {
  const {
    data,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['users', 'technicians'],
    queryFn: () => getUsers({ role: 'tecnico' }),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos (reemplaza cacheTime en v5)
  });

  // DEBUG: Logs temporales para debuggear
  console.log('🔍 useTechnicians DEBUG:');
  console.log('  - isLoading:', isLoading);
  console.log('  - error:', error);
  console.log('  - data:', data);
  console.log('  - data?.data:', data?.data);

  // Extraer usuarios de la respuesta paginada y filtrar solo técnicos activos
  const users = data?.data || [];
  console.log('  - users (before filter):', users);
  console.log('  - users length:', users.length);

  const technicians = users.filter((user: User) => {
    const isActive = user.is_active;
    const isTechnician = user.rol_nombre === 'tecnico';
    console.log(`  - User ${user.id} (${user.first_name} ${user.last_name}):`, {
      is_active: isActive,
      rol_nombre: user.rol_nombre,
      isTechnician,
      willBeIncluded: isActive && isTechnician
    });
    return isActive && isTechnician;
  });

  console.log('  - technicians (after filter):', technicians);
  console.log('  - technicians length:', technicians.length);

  return {
    technicians,
    isLoading,
    error,
    refetch,
    isEmpty: technicians.length === 0,
    total: data?.total || 0
  };
};

/**
 * Hook para obtener un técnico específico por ID
 */
export const useTechnicianById = (technicianId?: number) => {
  const { technicians, isLoading } = useTechnicians();
  
  const technician = technicianId 
    ? technicians.find((tech: User) => tech.id === technicianId)
    : undefined;

  return {
    technician,
    isLoading,
    notFound: !isLoading && technicianId && !technician
  };
};