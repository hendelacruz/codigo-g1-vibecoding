/**
 * Custom hooks para el módulo de entidades
 * Proporciona una interfaz simplificada para interactuar con el estado de entidades
 * Siguiendo el patrón del módulo de inventario
 */

import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '../../shared/hooks/redux'
import { 
  // Async thunks
  fetchClientes,
  fetchCliente,
  createCliente,
  updateCliente,
  deleteCliente,
  toggleClienteActive,
  fetchClienteUnidades,
  fetchUnidades,
  fetchUnidad,
  createUnidad,
  updateUnidad,
  deleteUnidad,
  toggleUnidadActive,
  fetchProveedoresEntity,
  fetchProveedor,
  createProveedorEntity,
  updateProveedorEntity,
  deleteProveedor,
  toggleProveedorActive,
  fetchClientesActivos,
  fetchProveedoresActivos,
  // Actions
  clearEntitiesErrors,
  clearClientesError,
  clearUnidadesError,
  clearProveedoresError
} from './entitiesSlice'
import type {
  ClienteFilters,
  CreateClienteData,
  UpdateClienteData,
  UnidadFilters,
  CreateUnidadData,
  UpdateUnidadData,
  ProveedorFilters,
  CreateProveedorData,
  UpdateProveedorData
} from './entitiesTypes'

/**
 * Hook principal para el manejo de entidades
 */
export const useEntities = () => {
  const dispatch = useAppDispatch()
  const entities = useAppSelector((state) => state.entities)

  // ==================== CLIENTES ====================
  
  const loadClientes = useCallback(async (filters?: ClienteFilters) => {
    const result = await dispatch(fetchClientes(filters))
    return result
  }, [dispatch])

  const loadCliente = useCallback(async (id: number) => {
    const result = await dispatch(fetchCliente(id))
    return result
  }, [dispatch])

  const addCliente = useCallback(async (data: CreateClienteData) => {
    const result = await dispatch(createCliente(data))
    return result
  }, [dispatch])

  const editCliente = useCallback(async (id: number, data: UpdateClienteData) => {
    const result = await dispatch(updateCliente({ id, data }))
    return result
  }, [dispatch])

  const removeCliente = useCallback(async (id: number) => {
    const result = await dispatch(deleteCliente(id))
    return result
  }, [dispatch])

  const toggleClienteStatus = useCallback(async (id: number) => {
    const result = await dispatch(toggleClienteActive(id))
    return result
  }, [dispatch])

  const loadClienteUnidades = useCallback(async (id: number) => {
    const result = await dispatch(fetchClienteUnidades(id))
    return result
  }, [dispatch])

  const loadClientesActivos = useCallback(async () => {
    const result = await dispatch(fetchClientesActivos())
    return result
  }, [dispatch])

  // ==================== UNIDADES ====================
  
  const loadUnidades = useCallback(async (filters?: UnidadFilters) => {
    const result = await dispatch(fetchUnidades(filters))
    return result
  }, [dispatch])

  const loadUnidad = useCallback(async (id: number) => {
    const result = await dispatch(fetchUnidad(id))
    return result
  }, [dispatch])

  const addUnidad = useCallback(async (data: CreateUnidadData) => {
    const result = await dispatch(createUnidad(data))
    return result
  }, [dispatch])

  const editUnidad = useCallback(async (id: number, data: UpdateUnidadData) => {
    const result = await dispatch(updateUnidad({ id, data }))
    return result
  }, [dispatch])

  const removeUnidad = useCallback(async (id: number) => {
    const result = await dispatch(deleteUnidad(id))
    return result
  }, [dispatch])

  const toggleUnidadStatus = useCallback(async (id: number) => {
    const result = await dispatch(toggleUnidadActive(id))
    return result
  }, [dispatch])

  // ==================== PROVEEDORES ====================
  
  const loadProveedores = useCallback(async (filters?: ProveedorFilters) => {
    const result = await dispatch(fetchProveedoresEntity(filters))
    return result
  }, [dispatch])

  const addProveedor = useCallback(async (data: CreateProveedorData) => {
    const result = await dispatch(createProveedorEntity(data))
    return result
  }, [dispatch])

  const editProveedor = useCallback(async (id: number, data: UpdateProveedorData) => {
    const result = await dispatch(updateProveedorEntity({ id, data }))
    return result
  }, [dispatch])

  const loadProveedor = useCallback(async (id: number) => {
    try {
      await dispatch(fetchProveedor(id)).unwrap()
      return true
    } catch (error) {
      console.error('Error loading proveedor:', error)
      return false
    }
  }, [dispatch])

  const removeProveedor = useCallback(async (id: number) => {
    try {
      await dispatch(deleteProveedor(id)).unwrap()
      return true
    } catch (error) {
      console.error('Error deleting proveedor:', error)
      return false
    }
  }, [dispatch])

  const toggleProveedorStatus = useCallback(async (id: number) => {
    try {
      await dispatch(toggleProveedorActive(id)).unwrap()
      return true
    } catch (error) {
      console.error('Error toggling proveedor status:', error)
      return false
    }
  }, [dispatch])

  const loadProveedoresActivos = useCallback(async () => {
    const result = await dispatch(fetchProveedoresActivos())
    return result
  }, [dispatch])

  // ==================== ERROR HANDLING ====================
  
  const clearErrors = useCallback(() => {
    dispatch(clearEntitiesErrors())
  }, [dispatch])

  const clearClienteErrors = useCallback(() => {
    dispatch(clearClientesError())
  }, [dispatch])

  const clearUnidadErrors = useCallback(() => {
    dispatch(clearUnidadesError())
  }, [dispatch])

  const clearProveedorErrors = useCallback(() => {
    dispatch(clearProveedoresError())
  }, [dispatch])

  return {
    // State
    entities,
    clientes: entities.clientes,
    unidades: entities.unidades,
    proveedores: entities.proveedores,

    // Cliente operations
    loadClientes,
    loadCliente,
    addCliente,
    editCliente,
    removeCliente,
    toggleClienteStatus,
    loadClienteUnidades,
    loadClientesActivos,

    // Unidad operations
    loadUnidades,
    loadUnidad,
    addUnidad,
    editUnidad,
    removeUnidad,
    toggleUnidadStatus,

    // Proveedor operations
    loadProveedores,
    loadProveedor,
    addProveedor,
    editProveedor,
    removeProveedor,
    toggleProveedorStatus,
    loadProveedoresActivos,

    // Error handling
    clearErrors,
    clearClienteErrors,
    clearUnidadErrors,
    clearProveedorErrors,
  }
}

/**
 * Hook específico para clientes
 */
export const useClientes = () => {
  const dispatch = useAppDispatch()
  const clientes = useAppSelector((state) => state.entities.clientes)

  const loadClientes = useCallback(async (filters?: ClienteFilters) => {
    return await dispatch(fetchClientes(filters))
  }, [dispatch])

  const loadCliente = useCallback(async (id: number) => {
    return await dispatch(fetchCliente(id))
  }, [dispatch])

  const createClienteAction = useCallback(async (data: CreateClienteData) => {
    return await dispatch(createCliente(data))
  }, [dispatch])

  const updateClienteAction = useCallback(async (id: number, data: UpdateClienteData) => {
    return await dispatch(updateCliente({ id, data }))
  }, [dispatch])

  const deleteClienteAction = useCallback(async (id: number) => {
    return await dispatch(deleteCliente(id))
  }, [dispatch])

  const toggleActiveAction = useCallback(async (id: number) => {
    return await dispatch(toggleClienteActive(id))
  }, [dispatch])

  const loadUnidades = useCallback(async (id: number) => {
    return await dispatch(fetchClienteUnidades(id))
  }, [dispatch])

  const loadActivos = useCallback(async () => {
    return await dispatch(fetchClientesActivos())
  }, [dispatch])

  const clearErrors = useCallback(() => {
    dispatch(clearClientesError())
  }, [dispatch])

  return {
    clientes,
    items: clientes.items,
    isLoading: clientes.isLoading,
    error: clientes.error,
    loadClientes,
    loadCliente,
    createCliente: createClienteAction,
    updateCliente: updateClienteAction,
    deleteCliente: deleteClienteAction,
    toggleActive: toggleActiveAction,
    loadUnidades,
    loadActivos,
    clearErrors,
  }
}

/**
 * Hook específico para unidades vehiculares
 */
export const useUnidades = () => {
  const dispatch = useAppDispatch()
  const unidades = useAppSelector((state) => state.entities.unidades)

  const loadUnidades = useCallback(async (filters?: UnidadFilters) => {
    return await dispatch(fetchUnidades(filters))
  }, [dispatch])

  const loadUnidad = useCallback(async (id: number) => {
    return await dispatch(fetchUnidad(id))
  }, [dispatch])

  const createUnidadAction = useCallback(async (data: CreateUnidadData) => {
    return await dispatch(createUnidad(data))
  }, [dispatch])

  const editUnidad = useCallback(async (id: number, data: UpdateUnidadData) => {
    return await dispatch(updateUnidad({ id, data }))
  }, [dispatch])

  const removeUnidad = useCallback(async (id: number) => {
    return await dispatch(deleteUnidad(id))
  }, [dispatch])

  const toggleActive = useCallback(async (id: number) => {
    return await dispatch(toggleUnidadActive(id))
  }, [dispatch])

  const clearErrors = useCallback(() => {
    dispatch(clearUnidadesError())
  }, [dispatch])

  return {
    unidades,
    items: unidades.items,
    isLoading: unidades.isLoading,
    error: unidades.error,
    loadUnidades,
    loadUnidad,
    createUnidad: createUnidadAction,
    editUnidad,
    removeUnidad,
    toggleActive,
    clearErrors,
  }
}

/**
 * Hook específico para proveedores
 */
export const useProveedores = () => {
  const dispatch = useAppDispatch()
  const proveedores = useAppSelector((state) => state.entities.proveedores)

  const loadProveedores = useCallback(async (filters?: ProveedorFilters) => {
    return await dispatch(fetchProveedoresEntity(filters))
  }, [dispatch])

  const createProveedorAction = useCallback(async (data: CreateProveedorData) => {
    return await dispatch(createProveedorEntity(data))
  }, [dispatch])

  const editProveedor = useCallback(async (id: number, data: UpdateProveedorData) => {
    return await dispatch(updateProveedorEntity({ id, data }))
  }, [dispatch])

  const removeProveedor = useCallback(async (id: number) => {
    return await dispatch(deleteProveedor(id))
  }, [dispatch])

  const toggleActive = useCallback(async (id: number) => {
    return await dispatch(toggleProveedorActive(id))
  }, [dispatch])

  const loadActivos = useCallback(async () => {
    return await dispatch(fetchProveedoresActivos())
  }, [dispatch])

  const clearErrors = useCallback(() => {
    dispatch(clearProveedoresError())
  }, [dispatch])

  return {
    proveedores,
    items: proveedores.items,
    isLoading: proveedores.isLoading,
    error: proveedores.error,
    loadProveedores,
    createProveedor: createProveedorAction,
    editProveedor,
    removeProveedor,
    toggleActive,
    loadActivos,
    clearErrors,
  }
}

/**
 * Hook para obtener listas de entidades activas (para selects)
 */
export const useEntitiesSelectors = () => {
  const dispatch = useAppDispatch()
  const { clientes, proveedores } = useAppSelector((state) => state.entities)

  const loadClientesActivos = useCallback(async () => {
    return await dispatch(fetchClientesActivos())
  }, [dispatch])

  const loadProveedoresActivos = useCallback(async () => {
    return await dispatch(fetchProveedoresActivos())
  }, [dispatch])

  return {
    clientesActivos: clientes.items.filter(cliente => cliente.is_active),
    proveedoresActivos: proveedores.items.filter(proveedor => proveedor.is_active),
    loadClientesActivos,
    loadProveedoresActivos,
  }
}

/**
 * Hook para estadísticas de entidades
 */
export const useEntitiesStats = () => {
  const { clientes, unidades, proveedores } = useAppSelector((state) => state.entities)

  return {
    totalClientes: clientes.items.length,
    totalUnidades: unidades.items.length,
    totalProveedores: proveedores.items.length,
    clientesActivos: clientes.items.filter(c => c.is_active).length,
    unidadesActivas: unidades.items.filter(u => u.is_active).length,
    proveedoresActivos: proveedores.items.filter(p => p.is_active).length,
  }
}