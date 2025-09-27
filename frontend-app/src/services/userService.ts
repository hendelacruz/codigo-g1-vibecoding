import { api } from '../shared/lib/api'
import { AUTH_ENDPOINTS } from '../features/auth/authConstants'
import type { User } from '../shared/types/common'
import type { CreateUserData } from '../features/auth/authTypes'

// API Response types
interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

interface GetUsersParams {
  page?: number
  limit?: number
  search?: string
  role?: string
  status?: 'active' | 'inactive'
  sortBy?: keyof User
  sortOrder?: 'asc' | 'desc'
}

// User Service Class
export class UserService {
  private static readonly BASE_URL = AUTH_ENDPOINTS.USERS

  /**
   * Get all users with optional filtering and pagination
   */
  static async getUsers(params: GetUsersParams = {}): Promise<PaginatedResponse<User>> {
    try {
      console.log('🔄 UserService.getUsers: Starting request with params:', params)
      console.log('🔄 UserService.getUsers: BASE_URL:', UserService.BASE_URL)
      
      const searchParams = new URLSearchParams()
      
      if (params.page) searchParams.append('page', params.page.toString())
      if (params.limit) searchParams.append('limit', params.limit.toString())
      if (params.search) searchParams.append('search', params.search)
      if (params.role) searchParams.append('role', params.role)
      if (params.status) searchParams.append('status', params.status)
      if (params.sortBy) searchParams.append('sortBy', params.sortBy)
      if (params.sortOrder) searchParams.append('sortOrder', params.sortOrder)

      const queryString = searchParams.toString()
      const url = queryString ? `${UserService.BASE_URL}?${queryString}` : UserService.BASE_URL
      
      console.log('🔄 UserService.getUsers: Final URL:', url)
      console.log('🔄 UserService.getUsers: Making API request...')

      const response = await api.get<User[] | PaginatedResponse<User>>(url)
      
      console.log('📥 UserService.getUsers: Response received:', response)
      console.log('📥 UserService.getUsers: Response status:', response.status)
      console.log('📥 UserService.getUsers: Response data:', response.data)
      
      // Adaptador: El backend devuelve una estructura de paginación específica
      let adaptedResponse: PaginatedResponse<User>
      
      if (Array.isArray(response.data)) {
        // Si el backend devuelve directamente un array, lo adaptamos
        adaptedResponse = {
          data: response.data,
          total: response.data.length,
          page: params.page || 1,
          limit: params.limit || response.data.length,
          totalPages: 1
        }
      } else if (response.data && 'results' in response.data) {
        // El backend devuelve estructura con results y adaptive_info
        const backendData = response.data as any
        const users = backendData.results || []
        adaptedResponse = {
          data: users,
          total: backendData.count || users.length,
          page: backendData.current_page || params.page || 1,
          limit: backendData.page_size || params.limit || users.length,
          totalPages: backendData.total_pages || 1
        }
      } else {
        // Si el backend ya devuelve una respuesta paginada en el formato esperado
        adaptedResponse = response.data as PaginatedResponse<User>
      }

      return adaptedResponse
    } catch (error: unknown) {
      console.error('❌ Error fetching users:', error)
      
      // Handle specific error cases
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number; data?: { message?: string; detail?: string } } }
        
        // Handle rate limiting
        if (axiosError.response?.status === 429) {
          throw new Error('Demasiadas solicitudes. Intenta de nuevo en unos momentos.')
        }
        
        // Handle authentication errors
        if (axiosError.response?.status === 401) {
          throw new Error('No tienes autorización para ver usuarios. Por favor, inicia sesión.')
        }
        
        // Handle permission errors
        if (axiosError.response?.status === 403) {
          throw new Error('No tienes permisos para ver usuarios.')
        }
        
        // Handle not found errors
        if (axiosError.response?.status === 404) {
          throw new Error('El endpoint de usuarios no fue encontrado.')
        }
        
        // Handle server errors
        if (axiosError.response?.status && axiosError.response.status >= 500) {
          throw new Error('Error del servidor. Por favor, intenta más tarde.')
        }
        
        const message = axiosError.response?.data?.detail || 
                       axiosError.response?.data?.message || 
                       'Error al cargar usuarios'
        throw new Error(message)
      }
      
      // Handle network errors
      if (error && typeof error === 'object' && 'code' in error) {
        const networkError = error as { code?: string }
        if (networkError.code === 'NETWORK_ERROR' || !navigator.onLine) {
          throw new Error('Error de conexión. Verifica tu conexión a internet.')
        }
      }
      
      throw new Error('Error al cargar usuarios')
    }
  }

  /**
   * Get a single user by ID
   */
  static async getUserById(id: number): Promise<User> {
    try {
      const response = await api.get<ApiResponse<User>>(`${UserService.BASE_URL}/${id}`)
      return response.data.data
    } catch (error) {
      console.error(`Error fetching user ${id}:`, error)
      throw new Error(`Failed to fetch user with ID ${id}`)
    }
  }

  /**
   * Create a new user
   */
  static async createUser(userData: CreateUserData): Promise<User> {
    try {
      // Validate required fields
      this.validateUserData(userData)

      console.log('🔍 UserService: Sending createUser request with data:', userData)
      const response = await api.post<ApiResponse<User>>(UserService.BASE_URL, userData)
      
      console.log('🔍 UserService: Full response received:', response)
      console.log('🔍 UserService: Response data:', response.data)
      console.log('🔍 UserService: Response data.data:', response.data?.data)
      
      // Check if response.data.data exists, otherwise use response.data directly
      const user = response.data?.data || response.data
      console.log('🔍 UserService: Final user object:', user)
      
      if (!user || typeof user !== 'object') {
        throw new Error('Invalid response format from server')
      }
      
      return user as User
    } catch (error: unknown) {
      console.error('Error creating user:', error)
      
      // Handle validation errors first
      if (error instanceof Error && error.message.includes('validation')) {
        throw error
      }
      
      // Handle HTTP errors
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number; data?: { message?: string } } }
        
        if (axiosError.response?.status === 401) {
          throw new Error('No tienes autorización para crear usuarios. Por favor, inicia sesión.')
        }
        if (axiosError.response?.status === 403) {
          throw new Error('No tienes permisos para crear usuarios.')
        }
        if (axiosError.response?.status === 400) {
          throw new Error(axiosError.response?.data?.message || 'Datos de usuario inválidos.')
        }
        if (axiosError.response?.status && axiosError.response.status >= 500) {
          throw new Error('Error del servidor. Por favor, intenta más tarde.')
        }
        
        throw new Error(axiosError.response?.data?.message || 'Error al crear usuario')
      }
      
      throw new Error('Error al crear usuario')
    }
  }

  /**
   * Update an existing user
   */
  static async updateUser(id: number, userData: Partial<CreateUserData>): Promise<User> {
    try {
      // Remove empty fields to avoid sending unnecessary data
      const cleanedData = this.cleanUserData(userData)

      console.log('🔄 UserService.updateUser: Sending request for user ID:', id)
      console.log('🔄 UserService.updateUser: Request data:', cleanedData)
      console.log('🔄 UserService.updateUser: BASE_URL:', UserService.BASE_URL)
      
      // Construct URL properly to avoid double slashes
      const url = `${UserService.BASE_URL.replace(/\/$/, '')}/${id}/`
      console.log('🔄 UserService.updateUser: Final URL:', url)

      const response = await api.put<ApiResponse<User>>(url, cleanedData)
      
      console.log('📥 UserService.updateUser: Full response:', response)
      console.log('📥 UserService.updateUser: Response data:', response.data)
      console.log('📥 UserService.updateUser: Response data.data:', response.data?.data)

      // Handle different response structures from backend
      const updatedUser = response.data?.data || response.data
      
      if (!updatedUser || typeof updatedUser !== 'object' || !('id' in updatedUser)) {
        console.error('❌ UserService.updateUser: Invalid response format:', response.data)
        throw new Error('Invalid response format from server')
      }

      console.log('✅ UserService.updateUser: User updated successfully:', updatedUser)
      return updatedUser as User
    } catch (error) {
      console.error(`❌ UserService.updateUser: Error updating user ${id}:`, error)
      if (error instanceof Error) {
        throw error
      }
      throw new Error(`Failed to update user with ID ${id}`)
    }
  }

  /**
   * Delete a user
   */
  static async deleteUser(id: number): Promise<void> {
    try {
      // Prevent deletion of admin user (ID 1)
      if (id === 1) {
        throw new Error('Cannot delete the main administrator user')
      }

      // Fix double slash issue: remove trailing slash from BASE_URL before concatenating
      const baseUrl = UserService.BASE_URL.endsWith('/') ? UserService.BASE_URL.slice(0, -1) : UserService.BASE_URL
      const deleteUrl = `${baseUrl}/${id}`
      
      console.log('🗑️ Deleting user with URL:', deleteUrl)
      await api.delete(deleteUrl)
      console.log('✅ User deleted successfully:', id)
    } catch (error) {
      console.error(`❌ Error deleting user ${id}:`, error)
      if (error instanceof Error) {
        throw error
      }
      throw new Error(`Failed to delete user with ID ${id}`)
    }
  }

  /**
   * Toggle user active status
   */
  static async toggleUserStatus(id: number): Promise<User> {
    try {
      const response = await api.patch<ApiResponse<User>>(`${UserService.BASE_URL}/${id}/toggle-status`)
      return response.data.data
    } catch (error) {
      console.error(`Error toggling user status ${id}:`, error)
      throw new Error(`Failed to toggle status for user with ID ${id}`)
    }
  }

  /**
   * Change user password
   */
  static async changeUserPassword(id: number, newPassword: string): Promise<void> {
    try {
      if (!newPassword || newPassword.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }

      await api.patch(`${UserService.BASE_URL}/${id}/change-password`, {
        password: newPassword
      })
    } catch (error) {
      console.error(`Error changing password for user ${id}:`, error)
      if (error instanceof Error) {
        throw error
      }
      throw new Error(`Failed to change password for user with ID ${id}`)
    }
  }

  /**
   * Get available roles for user creation/editing
   */
  static async getAvailableRoles(): Promise<Array<{ id: number; name: string; description?: string }>> {
    try {
      const response = await api.get<ApiResponse<Array<{ id: number; name: string; description?: string }>>>('/roles')
      return response.data.data
    } catch (error) {
      console.error('Error fetching roles:', error)
      throw new Error('Failed to fetch available roles')
    }
  }

  /**
   * Validate user data before sending to API
   */
  private static validateUserData(userData: CreateUserData): void {
    const errors: string[] = []

    if (!userData.username?.trim()) {
      errors.push('Username is required')
    }

    if (!userData.email?.trim()) {
      errors.push('Email is required')
    } else if (!this.isValidEmail(userData.email)) {
      errors.push('Invalid email format')
    }

    if (!userData.first_name?.trim()) {
      errors.push('First name is required')
    }

    if (!userData.last_name?.trim()) {
      errors.push('Last name is required')
    }

    if (!userData.dni?.trim()) {
      errors.push('DNI is required')
    } else if (!/^\d{8}$/.test(userData.dni)) {
      errors.push('DNI must be exactly 8 digits')
    }

    if (!userData.celular?.trim()) {
      errors.push('Celular is required')
    } else if (!/^(\+51)?9\d{8}$/.test(userData.celular.replace(/[\s\-()]/g, ''))) {
      errors.push('Celular must be a valid Peruvian mobile number (format: +51987654321 or 987654321)')
    }

    if (!userData.password?.trim()) {
      errors.push('Password is required')
    } else if (userData.password.length < 8) {
      errors.push('Password must be at least 8 characters long')
    }

    if (!userData.rol) {
      errors.push('Role is required')
    }

    // Validate license format if provided
    if (userData.licencia && userData.licencia.trim() && !/^[A-Z]\d{8}$/.test(userData.licencia)) {
      errors.push('License must follow format A12345678 (one letter followed by 8 digits)')
    }

    if (errors.length > 0) {
      throw new Error(`Validation errors: ${errors.join(', ')}`)
    }
  }

  /**
   * Clean user data by removing empty/undefined fields
   */
  private static cleanUserData(userData: Partial<CreateUserData>): Partial<CreateUserData> {
    const cleaned: Partial<CreateUserData> = {}

    Object.entries(userData).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        (cleaned as Record<string, unknown>)[key] = value
      }
    })

    return cleaned
  }

  /**
   * Validate email format
   */
  private static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }
}

// Export individual functions for easier usage
export const {
  getUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
  changeUserPassword,
  getAvailableRoles
} = UserService

// Export default service
export default UserService