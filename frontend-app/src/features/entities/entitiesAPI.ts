/**
 * Entities API - Funciones para interactuar con el backend de entidades
 * 
 * Este módulo maneja todas las llamadas a la API relacionadas con entidades:
 * - Clientes (CRUD completo)
 * - Unidades Vehiculares (Crear, Listar, Detalle)
 * - Proveedores (Crear, Listar)
 */

import { api } from '../../shared/lib/api'
import { AxiosError } from 'axios'
import type {
  Cliente,
  UnidadVehicular,
  ProveedorEntity,
  CreateClienteData,
  CreateUnidadData,
  CreateProveedorData,
  UpdateClienteData,
  UpdateUnidadData,
  UpdateProveedorData,
  ClienteFilters,
  UnidadFilters,
  ProveedorFilters,
  PaginatedResponse,
  APIError,
  EntitiesStats
} from './entitiesTypes'

/**
 * Entities API - Conjunto de funciones para manejar entidades
 */
export const entitiesAPI = {
  // ==================== CLIENTES ENDPOINTS ====================
  
  /**
   * Obtener todos los clientes
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de clientes
   */
  getClientes: async (filters?: ClienteFilters): Promise<Cliente[]> => {
    try {
      const queryString = filters ? new URLSearchParams(
        Object.entries(filters).filter(([_, value]) => value !== undefined && value !== '')
          .map(([key, value]) => [key, String(value)])
      ).toString() : ''
      
      const url = queryString ? `/api/entities/clientes/?${queryString}` : '/api/entities/clientes/'
      
      const response = await api.get<Cliente[] | { results: Cliente[] }>(url)
      
      // Handle both direct array and paginated response
      if (Array.isArray(response.data)) {
        return response.data
      } else {
        return response.data.results || []
      }
    } catch (error) {
      console.error('❌ Error fetching clientes:', error)
      throw handleEntitiesAPIError(error)
    }
  },

  /**
   * Obtener un cliente específico por ID
   * @param id - ID del cliente
   * @returns Promise con datos del cliente
   */
  getCliente: async (id: number): Promise<Cliente> => {
    try {
      const response = await api.get<Cliente>(`/api/entities/clientes/${id}/`)
      return response.data
    } catch (_) {
      throw new Error(`Error al obtener cliente con ID ${id}`)
    }
  },

  /**
   * Crear un nuevo cliente
   * @param data - Datos del cliente a crear
   * @returns Promise con el cliente creado
   */
  createCliente: async (data: CreateClienteData): Promise<Cliente> => {
    try {
      const response = await api.post<Cliente>('/api/entities/clientes/', data)
      return response.data
    } catch (_) {
      throw new Error('Error al crear cliente')
    }
  },

  /**
   * Actualizar un cliente existente
   * @param id - ID del cliente a actualizar
   * @param data - Datos a actualizar
   * @returns Promise con el cliente actualizado
   */
  updateCliente: async (id: number, data: UpdateClienteData): Promise<Cliente> => {
    try {
      const response = await api.put<Cliente>(`/api/entities/clientes/${id}/`, data)
      return response.data
    } catch (_) {
      throw new Error(`Error al actualizar cliente con ID ${id}`)
    }
  },

  /**
   * Eliminar un cliente
   * @param id - ID del cliente a eliminar
   * @returns Promise void
   */
  deleteCliente: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/entities/clientes/${id}/`)
    } catch (_) {
      throw new Error(`Error al eliminar cliente con ID ${id}`)
    }
  },

  /**
   * Cambiar estado activo/inactivo de un cliente
   * @param id - ID del cliente
   * @returns Promise con el cliente actualizado
   */
  toggleClienteActive: async (id: number): Promise<Cliente> => {
    try {
      // First, get the current cliente to know its current state
      const currentCliente = await api.get<Cliente>(`/api/entities/clientes/${id}/`)
      const newActiveState = !currentCliente.data.is_active
      
      console.log('🔄 toggleClienteActive: Cambiando estado', {
        id,
        currentState: currentCliente.data.is_active,
        newState: newActiveState
      })
      
      // Try different approaches
      let response;
      
      // Approach 1: PATCH with is_active field
      try {
        response = await api.patch<Cliente>(`/api/entities/clientes/${id}/`, {
          is_active: newActiveState
        })
      } catch (_: unknown) {
        console.log('❌ PATCH normal falló, intentando endpoint específico...')
        
        // Approach 2: POST to toggle endpoint
        try {
          response = await api.post<Cliente>(`/api/entities/clientes/${id}/toggle_active/`, {})
        } catch (_: unknown) {
          console.log('❌ POST toggle_active falló, intentando PATCH toggle_active...')
          
          // Approach 3: PATCH to toggle endpoint with empty body
          response = await api.patch<Cliente>(`/api/entities/clientes/${id}/toggle_active/`, {})
        }
      }
      
      return response.data
    } catch (error: unknown) {
      const axiosError = error as AxiosError
      console.error('❌ toggleClienteActive: Error detallado:', {
        id,
        error,
        status: axiosError.response?.status,
        statusText: axiosError.response?.statusText,
        data: axiosError.response?.data,
        message: axiosError.message,
        config: {
          url: axiosError.config?.url,
          method: axiosError.config?.method,
          headers: axiosError.config?.headers
        }
      })
      
      // Log específico para errores 400
      if (axiosError.response?.status === 400) {
        console.error('🔍 Error 400 - Detalles específicos:', {
          responseData: axiosError.response.data,
          responseText: JSON.stringify(axiosError.response.data, null, 2),
          requestUrl: axiosError.config?.url,
          requestMethod: axiosError.config?.method,
          requestHeaders: axiosError.config?.headers
        })
      }
      
      // Proporcionar un mensaje de error más específico
      if (axiosError.response?.status === 401) {
        throw new Error('No autorizado. Por favor, inicia sesión nuevamente.')
      } else if (axiosError.response?.status === 403) {
        throw new Error('No tienes permisos para realizar esta acción.')
      } else if (axiosError.response?.status === 404) {
        throw new Error(`Cliente con ID ${id} no encontrado.`)
      } else if (axiosError.response?.status && axiosError.response.status >= 500) {
        throw new Error('Error del servidor. Por favor, intenta más tarde.')
      } else if (axiosError.response?.data && typeof axiosError.response.data === 'object' && 'detail' in axiosError.response.data) {
        throw new Error(String(axiosError.response.data.detail))
      } else {
        throw new Error(`Error al cambiar estado del cliente con ID ${id}: ${axiosError.message}`)
      }
    }
  },

  /**
   * Obtener unidades del cliente
   * @param id - ID del cliente
   * @returns Promise con lista de unidades del cliente
   */
  getClienteUnidades: async (id: number): Promise<UnidadVehicular[]> => {
    try {
      const response = await api.get<UnidadVehicular[]>(`/api/entities/clientes/${id}/unidades/`)
      return response.data
    } catch (_) {
      throw new Error(`Error al obtener unidades del cliente con ID ${id}`)
    }
  },

  // ==================== UNIDADES VEHICULARES ENDPOINTS ====================

  /**
   * Obtener todas las unidades vehiculares
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de unidades
   */
  getUnidades: async (filters?: UnidadFilters): Promise<UnidadVehicular[]> => {
    try {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.cliente_id) params.append('cliente_id', filters.cliente_id.toString())
      if (filters?.placa) params.append('placa', filters.placa)
      if (filters?.is_active) params.append('is_active', filters.is_active.toString())
      if (filters?.marca) params.append('marca', filters.marca)
      
      const queryString = params.toString()
      const url = queryString ? `/api/entities/unidades/?${queryString}` : '/api/entities/unidades/'
      
      const response = await api.get<PaginatedResponse<UnidadVehicular> | UnidadVehicular[]>(url)
      
      // Verificar si la respuesta es paginada o un array directo
      if (Array.isArray(response.data)) {
        return response.data
      } else if (response.data && typeof response.data === 'object' && 'results' in response.data) {
        return response.data.results
      } else {
        console.warn('⚠️ getUnidades: Estructura de respuesta inesperada:', response.data)
        return []
      }
    } catch (error) {
      console.error('❌ getUnidades: Error en petición:', error)
      throw new Error('Error al obtener unidades vehiculares')
    }
  },

  /**
   * Obtener una unidad vehicular específica por ID
   * @param id - ID de la unidad
   * @returns Promise con datos de la unidad
   */
  getUnidad: async (id: number): Promise<UnidadVehicular> => {
    try {
      const response = await api.get<UnidadVehicular>(`/api/entities/unidades/${id}/`)
      return response.data
    } catch (_) {
      throw new Error(`Error al obtener unidad con ID ${id}`)
    }
  },

  /**
   * Crear una nueva unidad vehicular
   * @param data - Datos de la unidad a crear
   * @returns Promise con la unidad creada
   */
  createUnidad: async (data: CreateUnidadData): Promise<UnidadVehicular> => {
    try {
      // Transform data for backend compatibility - backend expects 'cliente' field
      const backendData = {
        ...data,
        cliente: data.cliente_id,
      }
      // Remove cliente_id as backend doesn't expect it
      delete (backendData as Record<string, unknown>).cliente_id
      
      const response = await api.post<UnidadVehicular>('/api/entities/unidades/', backendData)
      return response.data
    } catch (error: unknown) {
      console.error('❌ createUnidad: Error detallado:', error)
      
      // Type guard para AxiosError
      if (error instanceof AxiosError) {
        if (error.response) {
          console.error('❌ createUnidad: Error de respuesta del servidor:', {
            status: error.response.status,
            statusText: error.response.statusText,
            data: error.response.data
          })
          
          const backendError = error.response.data as { detail?: string; message?: string; error?: string; details?: Record<string, unknown> }
          
          // Para errores 400, mostrar detalles específicos de validación
          if (error.response.status === 400) {
            console.error('❌ createUnidad: Detalles del error 400:', backendError)
            
            // Si hay errores de validación específicos
            if (backendError?.details) {
              const validationErrors = Object.entries(backendError.details)
                .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
                .join('; ')
              throw new Error(`Errores de validación: ${validationErrors}`)
            }
            
            // Si hay un mensaje específico del servidor
            if (backendError?.message) {
              throw new Error(`Error de validación: ${backendError.message}`)
            }
            
            // Si hay un error específico
            if (backendError?.error) {
              throw new Error(`Error de validación: ${backendError.error}`)
            }
            
            // Si los datos son un string
            if (typeof error.response.data === 'string') {
              throw new Error(`Error de validación: ${error.response.data}`)
            }
            
            // Error 400 genérico con datos del servidor
            throw new Error(`Error de validación (400): ${JSON.stringify(error.response.data)}`)
          }
          
          // Si el servidor devuelve un mensaje específico, usarlo
          if (backendError?.message) {
            throw new Error(backendError.message)
          } else if (backendError?.error) {
            throw new Error(backendError.error)
          } else if (typeof error.response.data === 'string') {
            throw new Error(error.response.data)
          } else {
            throw new Error(`Error del servidor (${error.response.status}): ${error.response.statusText}`)
          }
        } else if (error.request) {
          console.error('❌ createUnidad: Error de red - no se recibió respuesta:', error.request)
          throw new Error('Error de conexión: No se pudo conectar con el servidor')
        } else {
          console.error('❌ createUnidad: Error de configuración:', error.message)
          throw new Error(`Error de configuración: ${error.message}`)
        }
      } else {
        // Error no es AxiosError
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
        console.error('❌ createUnidad: Error no identificado:', errorMessage)
        throw new Error(`Error inesperado: ${errorMessage}`)
      }
    }
  },

  /**
   * Actualizar una unidad vehicular existente
   * @param id - ID de la unidad a actualizar
   * @param data - Datos a actualizar
   * @returns Promise con la unidad actualizada
   */
  updateUnidad: async (id: number, data: UpdateUnidadData): Promise<UnidadVehicular> => {
    try {
      // Transform data for backend compatibility - backend expects 'cliente' field
      const backendData = {
        ...data,
        cliente: data.cliente_id,
      }
      // Remove cliente_id as backend doesn't expect it
      delete (backendData as Record<string, unknown>).cliente_id
      
      const response = await api.put<UnidadVehicular>(`/api/entities/unidades/${id}/`, backendData)
      return response.data
    } catch (error: unknown) {
      console.error('❌ updateUnidad: Error detallado:', error)
      
      // Type guard para AxiosError
      if (error instanceof AxiosError) {
        if (error.response) {
          console.error('❌ updateUnidad: Error de respuesta del servidor:', {
            status: error.response.status,
            statusText: error.response.statusText,
            data: error.response.data
          })
          
          // Si el servidor devuelve un mensaje específico, usarlo
          if (error.response.data?.message) {
            throw new Error(error.response.data.message)
          } else if (error.response.data?.error) {
            throw new Error(error.response.data.error)
          } else if (typeof error.response.data === 'string') {
            throw new Error(error.response.data)
          } else {
            throw new Error(`Error del servidor (${error.response.status}): ${error.response.statusText}`)
          }
        } else if (error.request) {
          console.error('❌ updateUnidad: Error de red - no se recibió respuesta:', error.request)
          throw new Error('Error de conexión: No se pudo conectar con el servidor')
        } else {
          console.error('❌ updateUnidad: Error de configuración:', error.message)
          throw new Error(`Error de configuración: ${error.message}`)
        }
      } else if (error instanceof Error) {
        throw new Error(`Error inesperado: ${error.message}`)
      } else {
        throw new Error('Error desconocido al actualizar unidad')
      }
    }
  },

  /**
   * Eliminar una unidad vehicular
   * @param id - ID de la unidad a eliminar
   * @returns Promise void
   */
  deleteUnidad: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/entities/unidades/${id}/`)
    } catch (_) {
      throw new Error(`Error al eliminar unidad vehicular con ID ${id}`)
    }
  },

  /**
   * Activar/Desactivar una unidad vehicular
   * @param id - ID de la unidad
   * @returns Promise con la unidad actualizada
   */
  toggleUnidadActive: async (id: number): Promise<UnidadVehicular> => {
    try {
      const response = await api.patch<UnidadVehicular>(`/api/entities/unidades/${id}/toggle_active/`)
      return response.data
    } catch (_) {
      throw new Error(`Error al cambiar estado de unidad vehicular con ID ${id}`)
    }
  },

  // ==================== PROVEEDORES ENDPOINTS ====================

  /**
   * Obtener todos los proveedores
   * @param filters - Filtros opcionales para la búsqueda
   * @returns Promise con lista de proveedores
   */
  getProveedores: async (filters?: ProveedorFilters): Promise<ProveedorEntity[]> => {
    try {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString())
      if (filters?.ruc) params.append('ruc', filters.ruc)
      
      const queryString = params.toString()
      const url = queryString ? `/api/entities/proveedores/?${queryString}` : '/api/entities/proveedores/'
      
      const response = await api.get<PaginatedResponse<ProveedorEntity> | ProveedorEntity[]>(url)
      
      // Verificar si la respuesta es paginada o un array directo
      if (Array.isArray(response.data)) {
        return response.data
      } else if (response.data && typeof response.data === 'object' && 'results' in response.data) {
        return response.data.results
      } else {
        console.warn('⚠️ getProveedores: Estructura de respuesta inesperada:', response.data)
        return []
      }
    } catch (error) {
      console.error('❌ getProveedores: Error en petición:', error)
      throw new Error('Error al obtener proveedores')
    }
  },

  /**
   * Obtener un proveedor específico por ID
   * @param id - ID del proveedor
   * @returns Promise con datos del proveedor
   */
  getProveedor: async (id: number): Promise<ProveedorEntity> => {
    try {
      const response = await api.get<ProveedorEntity>(`/api/entities/proveedores/${id}/`)
      return response.data
    } catch (_) {
      throw new Error(`Error al obtener proveedor con ID ${id}`)
    }
  },

  /**
   * Crear un nuevo proveedor
   * @param data - Datos del proveedor a crear
   * @returns Promise con el proveedor creado
   */
  createProveedor: async (data: CreateProveedorData): Promise<ProveedorEntity> => {
    try {
      const response = await api.post<ProveedorEntity>('/api/entities/proveedores/', data)
      return response.data
    } catch (_) {
      throw new Error('Error al crear proveedor')
    }
  },

  /**
   * Actualizar un proveedor existente
   * @param id - ID del proveedor a actualizar
   * @param data - Datos del proveedor a actualizar
   * @returns Promise con el proveedor actualizado
   */
  updateProveedor: async (id: number, data: UpdateProveedorData): Promise<ProveedorEntity> => {
    try {
      const response = await api.put<ProveedorEntity>(`/api/entities/proveedores/${id}/`, data)
      return response.data
    } catch (error: unknown) {
      console.error('❌ updateProveedor API: Error detallado:', error)
      
      // Type guard para AxiosError
      if (error instanceof AxiosError) {
        if (error.response) {
          const status = error.response.status
          const errorData = error.response.data
          console.error('❌ Error response:', { status, data: errorData })
          
          if (status === 400) {
            // Manejar errores de validación específicos
            if (errorData && typeof errorData === 'object') {
              const validationErrors: string[] = []
              
              // Extraer errores específicos de cada campo
              Object.entries(errorData).forEach(([field, messages]) => {
                if (Array.isArray(messages)) {
                  messages.forEach((message: string) => {
                    validationErrors.push(`${field}: ${message}`)
                  })
                } else if (typeof messages === 'string') {
                  validationErrors.push(`${field}: ${messages}`)
                }
              })
              
              if (validationErrors.length > 0) {
                throw new Error(`Errores de validación:\n${validationErrors.join('\n')}`)
              }
            }
            
            // Fallback para errores de validación genéricos
            const errorMessage = errorData?.detail || errorData?.message || 'Datos inválidos'
            throw new Error(`Error de validación: ${errorMessage}`)
          } else if (status === 404) {
            throw new Error(`Proveedor con ID ${id} no encontrado`)
          } else if (status === 403) {
            throw new Error('No tienes permisos para actualizar este proveedor')
          } else if (status === 401) {
            throw new Error('No estás autenticado')
          } else {
            throw new Error(`Error del servidor (${status}): ${errorData?.detail || 'Error desconocido'}`)
          }
        } else if (error.request) {
          throw new Error('Error de conexión: No se pudo conectar con el servidor')
        } else {
          throw new Error(`Error inesperado: ${error.message}`)
        }
      } else if (error instanceof Error) {
        throw new Error(`Error inesperado: ${error.message}`)
      } else {
        throw new Error('Error desconocido al actualizar proveedor')
      }
    }
  },

  /**
   * Eliminar un proveedor
   * @param id - ID del proveedor a eliminar
   * @returns Promise void
   */
  deleteProveedor: async (id: number): Promise<void> => {
    try {
      await api.delete(`/api/entities/proveedores/${id}/`)
    } catch (_) {
      throw new Error(`Error al eliminar proveedor con ID ${id}`)
    }
  },

  /**
   * Activar/Desactivar un proveedor
   * @param id - ID del proveedor
   * @returns Promise con el proveedor actualizado
   */
  toggleProveedorActive: async (id: number): Promise<ProveedorEntity> => {
    try {
      // First, get the current proveedor to know its current state
      const currentProveedor = await api.get<ProveedorEntity>(`/api/entities/proveedores/${id}/`)
      const newActiveState = !currentProveedor.data.is_active
      
      console.log('🔄 toggleProveedorActive: Cambiando estado', {
        id,
        currentState: currentProveedor.data.is_active,
        newState: newActiveState
      })
      
      // Try different approaches
      let response;
      
      // Approach 1: PATCH with is_active field
      try {
        response = await api.patch<ProveedorEntity>(`/api/entities/proveedores/${id}/`, {
          is_active: newActiveState
        })
      } catch (_: unknown) {
        console.log('❌ PATCH normal falló, intentando endpoint específico...')
        
        // Approach 2: POST to toggle endpoint
        try {
          response = await api.post<ProveedorEntity>(`/api/entities/proveedores/${id}/toggle_active/`, {})
        } catch (_: unknown) {
          console.log('❌ POST toggle_active falló, intentando PATCH toggle_active...')
          
          // Approach 3: PATCH to toggle endpoint with empty body
          response = await api.patch<ProveedorEntity>(`/api/entities/proveedores/${id}/toggle_active/`, {})
        }
      }
      
      return response.data
    } catch (error: unknown) {
      console.error('❌ toggleProveedorActive: Error detallado:', {
        id,
        error,
        status: error instanceof AxiosError ? error.response?.status : undefined,
        statusText: error instanceof AxiosError ? error.response?.statusText : undefined,
        data: error instanceof AxiosError ? error.response?.data : undefined,
        message: error instanceof Error ? error.message : 'Error desconocido'
      })
      
      // Proporcionar un mensaje de error más específico
      if (error instanceof AxiosError) {
        if (error.response?.status === 401) {
          throw new Error('No autorizado. Por favor, inicia sesión nuevamente.')
        } else if (error.response?.status === 403) {
          throw new Error('No tienes permisos para realizar esta acción.')
        } else if (error.response?.status === 404) {
          throw new Error(`Proveedor con ID ${id} no encontrado.`)
        } else if (error.response?.status && error.response.status >= 500) {
          throw new Error('Error del servidor. Por favor, intenta más tarde.')
        } else if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        } else {
          throw new Error(`Error al cambiar estado del proveedor con ID ${id}: ${error.message}`)
        }
      } else {
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
        throw new Error(`Error al cambiar estado del proveedor con ID ${id}: ${errorMessage}`)
      }
    }
  },

  // ==================== UTILITY ENDPOINTS ====================

  /**
   * Buscar entidades por término de búsqueda
   * @param searchTerm - Término de búsqueda
   * @param entityType - Tipo de entidad a buscar
   * @returns Promise con resultados de búsqueda
   */
  searchEntities: async (
    searchTerm: string, 
    entityType: 'clientes' | 'unidades' | 'proveedores'
  ): Promise<Cliente[] | UnidadVehicular[] | ProveedorEntity[]> => {
    try {
      const response = await api.get(`/api/entities/${entityType}/search/`, {
        params: { search: searchTerm }
      })
      return response.data.results || []
    } catch (_) {
      throw new Error(`Error al buscar ${entityType}`)
    }
  },

  /**
   * Obtener estadísticas de entidades
   * @returns Promise con estadísticas
   */
  getEntitiesStats: async (): Promise<EntitiesStats> => {
    try {
      const response = await api.get<EntitiesStats>('/api/entities/stats/')
      return response.data
    } catch (_) {
      throw new Error('Error al obtener estadísticas de entidades')
    }
  },

  /**
   * Obtener clientes activos para selects
   * @returns Promise con lista de clientes activos
   */
  getClientesActivos: async (): Promise<Cliente[]> => {
    try {
      const response = await api.get<Cliente[]>('/api/entities/clientes/?is_active=true')
      
      // Handle both direct array and paginated response
      if (Array.isArray(response.data)) {
        return response.data
      } else if (response.data && typeof response.data === 'object' && 'results' in response.data) {
        return (response.data as PaginatedResponse<Cliente>).results
      } else {
        console.warn('⚠️ getClientesActivos: Estructura de respuesta inesperada:', response.data)
        return []
      }
    } catch (error) {
      console.error('❌ getClientesActivos: Error en petición:', error)
      throw new Error('Error al obtener clientes activos')
    }
  },

  /**
   * Obtener proveedores activos para selects
   * @returns Promise con lista de proveedores activos
   */
  getProveedoresActivos: async (): Promise<Pick<ProveedorEntity, 'id' | 'nombre'>[]> => {
    try {
      const response = await api.get<ProveedorEntity[]>('/api/entities/proveedores/?is_active=true')
      
      // Handle both direct array and paginated response
      let proveedores: ProveedorEntity[] = []
      if (Array.isArray(response.data)) {
        proveedores = response.data
      } else if (response.data && typeof response.data === 'object' && 'results' in response.data) {
        proveedores = (response.data as PaginatedResponse<ProveedorEntity>).results
      }
      
      // Return only id and nombre
      return proveedores.map(p => ({ id: p.id, nombre: p.nombre }))
    } catch (error) {
      console.error('❌ getProveedoresActivos: Error en petición:', error)
      throw new Error('Error al obtener proveedores activos')
    }
  },

  /**
   * Validar si una placa ya existe
   * @param placa - Placa a validar
   * @param excludeId - ID a excluir de la validación (para edición)
   * @returns Promise con resultado de validación
   */
  validatePlaca: async (placa: string, excludeId?: number): Promise<{ exists: boolean }> => {
    try {
      const response = await api.get('/api/entities/unidades/validate-placa/', {
        params: { placa, exclude_id: excludeId }
      })
      return response.data
    } catch (_) {
      throw new Error('Error al validar placa')
    }
  },

  /**
   * Validar si un RUC ya existe
   * @param ruc - RUC a validar
   * @param entityType - Tipo de entidad (clientes o proveedores)
   * @param excludeId - ID a excluir de la validación (para edición)
   * @returns Promise con resultado de validación
   */
  validateRUC: async (
    ruc: string, 
    entityType: 'clientes' | 'proveedores', 
    excludeId?: number
  ): Promise<{ exists: boolean }> => {
    try {
      const response = await api.get(`/api/entities/validate/ruc/`, {
        params: { ruc, entity_type: entityType, exclude_id: excludeId }
      })
      return response.data
    } catch (_) {
      throw new Error('Error al validar RUC')
    }
  }
}

/**
 * Manejo de errores de la API de entidades
 * @param error - Error capturado
 * @returns APIError formateado
 */
export const handleEntitiesAPIError = (error: unknown): APIError => {
  if (error instanceof AxiosError) {
    const status = error.response?.status || 500
    const message = error.response?.data?.detail || error.message || 'Error de conexión'
    
    const result: APIError = {
      message,
      status,
    }
    
    if (error.response?.data) {
      result.details = { server: [JSON.stringify(error.response.data)] }
    }
    
    return result
  }
  
  if (error instanceof Error) {
    const result: APIError = {
      message: error.message,
      status: 500,
    }
    
    if (error.stack) {
      result.details = { stack: [error.stack] }
    }
    
    return result
  }
  
  return {
    message: 'Error desconocido',
    status: 500,
    details: { error: [String(error)] }
  }
}

export default entitiesAPI