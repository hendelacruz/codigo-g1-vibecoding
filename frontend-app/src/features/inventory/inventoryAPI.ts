/**
 * Inventory API - Funciones para interactuar con el backend de inventario
 * 
 * Este módulo maneja todas las llamadas a la API relacionadas con inventario:
 * - GPS devices (CRUD completo)
 * - SIM Cards (CRUD completo)
 * - Otros Productos (CRUD completo + ajuste de stock)
 * - Proveedores (lectura)
 */

import { api } from '../../shared/lib/api'
import { AxiosError } from 'axios'
import type {
  GPS,
  SIMCard,
  OtroProducto,
  Proveedor,
  CreateGPSData,
  CreateSIMCardData,
  CreateOtroProductoData,
  AdjustStockData,
  InventoryFilters,
  APIError
} from './inventoryTypes'

/**
 * Inventory API - Conjunto de funciones para manejar inventario
 */
export const inventoryAPI = {
  // ==================== GPS ENDPOINTS ====================
  
  /**
   * Obtener todos los dispositivos GPS
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de dispositivos GPS
   */
  getGPSDevices: async (filters?: InventoryFilters): Promise<GPS[]> => {
    try {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.proveedor) params.append('proveedor', filters.proveedor.toString())
      
      const queryString = params.toString()
      const url = queryString ? `/api/inventory/gps/?${queryString}` : '/api/inventory/gps/'
      
      const response = await api.get<GPS[]>(url)
      
      return response.data
    } catch (error: unknown) {
      console.error('❌ inventoryAPI.getGPSDevices - Error:', error)
      
      const axiosError = error as AxiosError
      
      // Handle specific API errors
      if (axiosError.response?.data) {
        const errorData = axiosError.response.data as { error?: string; message?: string; retry_after?: number };
        if (errorData.error === 'Rate limit exceeded' && errorData.retry_after) {
          throw new Error(`Límite de solicitudes excedido. Intenta nuevamente en ${Math.ceil(errorData.retry_after / 60)} minutos.`)
        } else if (errorData.message) {
          throw new Error(errorData.message)
        }
      }
      
      // Handle network errors
      if (axiosError.code === 'ECONNREFUSED' || axiosError.message?.includes('Network Error')) {
        throw new Error('No se puede conectar con el servidor. Verifica que el backend esté ejecutándose.')
      }
      
      throw new Error('Error al obtener dispositivos GPS')
    }
  },

  /**
   * Obtener un dispositivo GPS por ID
   * @param id - ID del dispositivo GPS
   * @returns Promise con datos del dispositivo GPS
   */
  getGPS: async (id: number): Promise<GPS> => {
    try {
      const response = await api.get<GPS>(`/api/inventory/gps/${id}/`)
      return response.data
    } catch {
      throw new Error('Error al obtener dispositivo GPS')
    }
  },

  /**
   * Crear un nuevo dispositivo GPS
   * @param data - Datos del dispositivo GPS a crear
   * @returns Promise con el dispositivo GPS creado
   */
  createGPS: async (data: CreateGPSData): Promise<GPS> => {
    try {
      const response = await api.post<GPS>('/api/inventory/gps/', data)
      return response.data
    } catch {
      throw new Error('Error al crear dispositivo GPS')
    }
  },

  /**
   * Actualizar un dispositivo GPS existente
   * @param id - ID del dispositivo GPS
   * @param data - Datos parciales a actualizar
   * @returns Promise con el dispositivo GPS actualizado
   */
  updateGPS: async (id: number, data: Partial<CreateGPSData>): Promise<GPS> => {
    try {
      const response = await api.put<GPS>(`/api/inventory/gps/${id}/`, data)
      return response.data
    } catch (error: unknown) {
      console.error('❌ inventoryAPI.updateGPS - Error:', error)
      
      // Preserve specific error details from backend
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as AxiosError
        if (axiosError.response?.data) {
          const backendError = axiosError.response.data
          if (typeof backendError === 'string') {
            throw new Error(backendError)
          } else if (backendError && typeof backendError === 'object') {
            if ('detail' in backendError && typeof backendError.detail === 'string') {
              throw new Error(backendError.detail)
            } else if ('message' in backendError && typeof backendError.message === 'string') {
              throw new Error(backendError.message)
            } else {
              // Handle validation errors
              const validationErrors = Object.entries(backendError)
                .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
                .join('; ')
              throw new Error(validationErrors || 'Error de validación')
            }
          }
        }
      }
      
      throw new Error('Error al actualizar dispositivo GPS')
    }
  },

  /**
   * Eliminar un dispositivo GPS
   * @param id - ID del dispositivo GPS a eliminar
   * @returns Promise void
   */
  deleteGPS: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/inventory/gps/${id}/`)
    } catch {
      throw new Error('Error al eliminar dispositivo GPS')
    }
  },

  /**
   * Cambiar estado de un dispositivo GPS (activar/desactivar)
   * @param id - ID del dispositivo GPS
   * @returns Promise con el dispositivo GPS actualizado
   */
  toggleGPSState: async (id: number, isActive?: boolean, observaciones?: string): Promise<GPS> => {
    try {
      // First get current state if isActive is not provided
      let targetState = isActive
      if (targetState === undefined) {
        const currentDevice = await api.get<GPS>(`/api/inventory/gps/${id}/`)
        // Toggle the current state - assuming 'no_asignado' means active
        targetState = currentDevice.data.estado !== 'no_asignado'
      }

      const response = await api.patch<GPS>(`/api/inventory/gps/${id}/cambiar_estado/`, {
        is_active: targetState,
        observaciones: observaciones || `${targetState ? 'Activando' : 'Desactivando'} GPS desde la interfaz`
      })
      return response.data
    } catch (error: unknown) {
      console.error('❌ inventoryAPI.toggleGPSState - Error:', error)
      
      // Preserve specific error details from backend
      if (error instanceof AxiosError && error.response?.data) {
        const backendError = error.response.data as { detail?: string; message?: string }
        if (typeof backendError === 'string') {
          throw new Error(backendError)
        } else if (backendError.detail) {
          throw new Error(backendError.detail)
        } else if (backendError.message) {
          throw new Error(backendError.message)
        }
      }
      
      throw new Error('Error al cambiar estado del dispositivo GPS')
    }
  },

  // ==================== SIM CARDS ENDPOINTS ====================

  /**
   * Obtener todas las tarjetas SIM
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de tarjetas SIM
   */
  getSIMCards: async (filters?: InventoryFilters): Promise<SIMCard[]> => {
    try {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.proveedor) params.append('proveedor', filters.proveedor.toString())
      
      const queryString = params.toString()
      const url = queryString ? `/api/inventory/simcards/?${queryString}` : '/api/inventory/simcards/'
      
      const response = await api.get<SIMCard[]>(url)
      return response.data
    } catch {
      throw new Error('Error al obtener tarjetas SIM')
    }
  },

  /**
   * Obtener una tarjeta SIM por ID
   * @param id - ID de la tarjeta SIM
   * @returns Promise con datos de la tarjeta SIM
   */
  getSIMCard: async (id: number): Promise<SIMCard> => {
    try {
      const response = await api.get<SIMCard>(`/api/inventory/simcards/${id}/`)
      return response.data
    } catch {
      throw new Error('Error al obtener tarjeta SIM')
    }
  },

  /**
   * Crear una nueva tarjeta SIM
   * @param data - Datos de la tarjeta SIM a crear
   * @returns Promise con la tarjeta SIM creada
   */
  createSIMCard: async (data: CreateSIMCardData): Promise<SIMCard> => {
    try {
      const response = await api.post<SIMCard>('/api/inventory/simcards/', data)
      return response.data
    } catch {
      throw new Error('Error al crear tarjeta SIM')
    }
  },

  /**
   * Actualizar una tarjeta SIM existente
   * @param id - ID de la tarjeta SIM
   * @param data - Datos parciales a actualizar
   * @returns Promise con la tarjeta SIM actualizada
   */
  updateSIMCard: async (id: number, data: Partial<CreateSIMCardData>): Promise<SIMCard> => {
    try {
      const response = await api.patch<SIMCard>(`/api/inventory/simcards/${id}/`, data)
      return response.data
    } catch {
      throw new Error('Error al actualizar tarjeta SIM')
    }
  },

  /**
   * Eliminar una tarjeta SIM
   * @param id - ID de la tarjeta SIM a eliminar
   * @returns Promise void
   */
  deleteSIMCard: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/inventory/simcards/${id}/`)
    } catch {
      throw new Error('Error al eliminar tarjeta SIM')
    }
  },

  // ==================== OTROS PRODUCTOS ENDPOINTS ====================

  /**
   * Obtener todos los otros productos
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de otros productos
   */
  getOtrosProductos: async (filters?: InventoryFilters): Promise<OtroProducto[]> => {
    try {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.proveedor) params.append('proveedor', filters.proveedor.toString())
      
      const queryString = params.toString()
      const url = queryString ? `/api/inventory/otros/?${queryString}` : '/api/inventory/otros/'
      
      const response = await api.get<OtroProducto[]>(url)
      return response.data
    } catch {
      throw new Error('Error al obtener otros productos')
    }
  },

  /**
   * Obtener un producto por ID
   * @param id - ID del producto
   * @returns Promise con datos del producto
   */
  getOtroProducto: async (id: number): Promise<OtroProducto> => {
    try {
      const response = await api.get<OtroProducto>(`/api/inventory/otros/${id}/`)
      return response.data
    } catch {
      throw new Error('Error al obtener producto')
    }
  },

  /**
   * Crear un nuevo producto
   * @param data - Datos del producto a crear
   * @returns Promise con el producto creado
   */
  createOtroProducto: async (data: CreateOtroProductoData): Promise<OtroProducto> => {
    try {
      const response = await api.post<OtroProducto>('/api/inventory/otros/', data)
      return response.data
    } catch {
      throw new Error('Error al crear producto')
    }
  },

  /**
   * Actualizar un producto existente
   * @param id - ID del producto
   * @param data - Datos parciales a actualizar
   * @returns Promise con el producto actualizado
   */
  updateOtroProducto: async (id: number, data: Partial<CreateOtroProductoData>): Promise<OtroProducto> => {
    try {
      const response = await api.patch<OtroProducto>(`/api/inventory/otros/${id}/`, data)
      return response.data
    } catch {
      throw new Error('Error al actualizar producto')
    }
  },

  /**
   * Eliminar un producto
   * @param id - ID del producto a eliminar
   * @returns Promise void
   */
  deleteOtroProducto: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/inventory/otros/${id}/`)
    } catch {
      throw new Error('Error al eliminar producto')
    }
  },

  /**
   * Ajustar stock de un producto
   * @param id - ID del producto
   * @param data - Datos del ajuste de stock
   * @returns Promise con el producto actualizado
   */
  adjustStock: async (id: number, data: AdjustStockData): Promise<OtroProducto> => {
    try {
      const response = await api.patch<OtroProducto>(`/api/inventory/otros/${id}/adjust-stock/`, data)
      return response.data
    } catch {
      throw new Error('Error al ajustar stock')
    }
  },

  // ==================== PROVEEDORES ENDPOINTS ====================

  /**
   * Obtener todos los proveedores
   * @returns Promise con lista de proveedores
   */
  getProveedores: async (): Promise<Proveedor[]> => {
    try {
      const response = await api.get<Proveedor[]>('/api/entities/proveedores/')
      return response.data
    } catch {
      throw new Error('Error al obtener proveedores')
    }
  },

  /**
   * Obtener un proveedor por ID
   * @param id - ID del proveedor
   * @returns Promise con datos del proveedor
   */
  getProveedor: async (id: number): Promise<Proveedor> => {
    try {
      const response = await api.get<Proveedor>(`/api/entities/proveedores/${id}/`)
      return response.data
    } catch {
      throw new Error('Error al obtener proveedor')
    }
  },

  // ==================== UTILITY FUNCTIONS ====================

  /**
   * Buscar productos por término de búsqueda
   * @param searchTerm - Término de búsqueda
   * @param productType - Tipo de producto ('gps' | 'simcard' | 'otros')
   * @returns Promise con resultados de búsqueda
   */
  searchProducts: async (
    searchTerm: string, 
    productType: 'gps' | 'simcard' | 'otros'
  ): Promise<GPS[] | SIMCard[] | OtroProducto[]> => {
    try {
      const filters: InventoryFilters = { search: searchTerm }
      
      switch (productType) {
        case 'gps':
          return await inventoryAPI.getGPSDevices(filters)
        case 'simcard':
          return await inventoryAPI.getSIMCards(filters)
        case 'otros':
          return await inventoryAPI.getOtrosProductos(filters)
        default:
          throw new Error('Tipo de producto no válido')
      }
    } catch (error) {
      throw new Error(`Error al buscar productos: ${error}`)
    }
  },

  /**
   * Obtener estadísticas de inventario
   * @returns Promise con estadísticas generales
   */
  getInventoryStats: async (): Promise<{
    totalGPS: number
    totalSIMCards: number
    totalOtrosProductos: number
    lowStockProducts: number
  }> => {
    try {
      const response = await api.get('/api/inventory/stats/')
      return response.data
    } catch {
      throw new Error('Error al obtener estadísticas de inventario')
    }
  }
}

/**
 * Función helper para manejar errores de API de inventario
 * @param error - Error capturado
 * @returns APIError formateado
 */
export const handleInventoryAPIError = (error: unknown): APIError => {
  if (error instanceof Error) {
    return {
      message: error.message,
      code: 'INVENTORY_ERROR'
    }
  }
  
  return {
    message: 'Error desconocido en inventario',
    code: 'UNKNOWN_ERROR'
  }
}

export default inventoryAPI