/**
 * Hook personalizado para obtener unidades filtradas por cliente
 * Proporciona funcionalidad para cargar unidades automáticamente cuando se selecciona un cliente
 */

import { useCallback, useEffect, useMemo } from 'react'
import { useUnidades, useClientes } from '../../entities/useEntities'
import type { UnidadVehicular, Cliente } from '../../entities/entitiesTypes'

interface UseUnidadesByClientOptions {
  clienteId?: string | number | null | undefined
  includeInactive?: boolean
  autoLoad?: boolean
}

interface UseUnidadesByClientReturn {
  unidades: UnidadVehicular[]
  isLoading: boolean
  error: string | null
  loadUnidadesByClient: (clienteId: number) => Promise<void>
  clearUnidades: () => void
  findClienteByPlaca: (placa: string) => Cliente | null
}

/**
 * Hook para manejar unidades filtradas por cliente
 */
export const useUnidadesByClient = ({
  clienteId,
  includeInactive = false,
  autoLoad = true
}: UseUnidadesByClientOptions = {}): UseUnidadesByClientReturn => {
  const {
    items: allUnidades,
    isLoading: unidadesLoading,
    error: unidadesError,
    loadUnidades,
    clearErrors: clearUnidadesErrors
  } = useUnidades()

  const {
    items: allClientes,
    isLoading: clientesLoading,
    error: clientesError,
    loadActivos: loadClientesActivos
  } = useClientes()

  // Convertir clienteId a número si es string
  const numericClienteId = useMemo(() => {
    if (clienteId === null || clienteId === undefined || clienteId === '') return null
    const result = typeof clienteId === 'string' ? parseInt(clienteId, 10) : clienteId
    return isNaN(result) ? null : result
  }, [clienteId])

  // Filtrar unidades por cliente
  const unidades = useMemo(() => {
    if (numericClienteId === null || numericClienteId === undefined) {
      return []
    }

    return allUnidades.filter(unidad => {
      const matches = unidad.cliente_id === numericClienteId;
      const shouldInclude = includeInactive || unidad.is_active;
      return matches && shouldInclude;
    });
  }, [allUnidades, numericClienteId, includeInactive])

  /**
   * Función para cargar unidades específicas de un cliente
   */
  const loadUnidadesByClient = useCallback(async (clienteId: number): Promise<void> => {
    try {
      clearUnidadesErrors()
      // Cargar unidades con filtro de cliente específico
      const filters = { 
        cliente_id: clienteId,
        ...(includeInactive ? {} : { is_active: true })
      }
      await loadUnidades(filters)
    } catch (error) {
      console.error('Error loading unidades by client:', error)
      throw error
    }
  }, [loadUnidades, includeInactive, clearUnidadesErrors])

  // Función para limpiar unidades
  const clearUnidades = useCallback(() => {
    clearUnidadesErrors()
  }, [clearUnidadesErrors])

  // Función para encontrar cliente por placa
  const findClienteByPlaca = useCallback((placa: string): Cliente | null => {
    if (!placa.trim()) return null
    
    const normalizedPlaca = placa.toLowerCase().trim()
    const unidadEncontrada = allUnidades.find(unidad => 
      unidad.placa?.toLowerCase() === normalizedPlaca
    )
    
    if (!unidadEncontrada) return null
    
    // Buscar el cliente asociado a esta unidad
    const clienteEncontrado = allClientes.find(cliente => 
      cliente.id === unidadEncontrada.cliente_id
    )
    
    return clienteEncontrado || null
  }, [allUnidades, allClientes])

  // Auto-cargar unidades cuando cambia el cliente (si autoLoad está habilitado)
  useEffect(() => {
    console.log('useUnidadesByClient - useEffect triggered:', { autoLoad, numericClienteId })
    if (autoLoad && numericClienteId) {
      console.log('useUnidadesByClient - calling loadUnidadesByClient with:', numericClienteId)
      loadUnidadesByClient(numericClienteId)
    }
  }, [numericClienteId, autoLoad, loadUnidadesByClient])

  // Cargar todas las unidades y clientes al montar el componente para permitir búsqueda por placa
  useEffect(() => {
    if (allUnidades.length === 0) {
      loadUnidades({ is_active: !includeInactive })
    }
    if (allClientes.length === 0) {
      loadClientesActivos()
    }
  }, [loadUnidades, loadClientesActivos, includeInactive, allUnidades.length, allClientes.length])

  return {
    unidades,
    isLoading: unidadesLoading || clientesLoading,
    error: unidadesError || clientesError,
    loadUnidadesByClient,
    clearUnidades,
    findClienteByPlaca
  }
}

export default useUnidadesByClient