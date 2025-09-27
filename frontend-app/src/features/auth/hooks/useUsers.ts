/**
 * Custom hook for managing users data and operations
 * 
 * This hook provides a centralized way to manage user-related state and operations,
 * including fetching, creating, updating, and deleting users.
 * It follows the same pattern as the inventory module for consistency.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { UserService } from '../../../services/userService'
import type { User } from '../../../shared/types/common'
import type { CreateUserData } from '../authTypes'

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
  retryCount?: number
}

interface UseUsersState {
  users: User[]
  loading: boolean
  error: string | null
  isRateLimited: boolean
  retryAfter: number | null
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

interface UseUsersActions {
  fetchUsers: (params?: GetUsersParams) => Promise<void>
  createUser: (userData: CreateUserData) => Promise<User>
  updateUser: (id: number, userData: Partial<CreateUserData>) => Promise<User>
  deleteUser: (id: number) => Promise<void>
  toggleUserStatus: (id: number) => Promise<User>
  changeUserPassword: (id: number, newPassword: string) => Promise<void>
  refreshUsers: () => Promise<void>
  clearError: () => void
}

interface UseUsersReturn extends UseUsersState, UseUsersActions {}

/**
 * Custom hook for users management
 */
export const useUsers = (initialParams?: GetUsersParams): UseUsersReturn => {
  const [state, setState] = useState<UseUsersState>({
    users: [],
    loading: false,
    error: null,
    isRateLimited: false,
    retryAfter: null,
    pagination: {
      page: 1,
      limit: 50,
      total: 0,
      totalPages: 0
    }
  })

  const [lastParams, setLastParams] = useState<GetUsersParams>(initialParams || {})

  // Debouncing ref
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastRequestRef = useRef<string>('')

  /**
   * Fetch users with optional parameters
   */
  const fetchUsers = useCallback(async (params: GetUsersParams = {}) => {
    // Create request key for debouncing
    const requestKey = JSON.stringify(params)
    
    // Clear previous debounce timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }
    
    // If same request is already in progress, skip
    if (lastRequestRef.current === requestKey && state.loading) {
      console.log('🔄 useUsers: Skipping duplicate request')
      return
    }
    
    lastRequestRef.current = requestKey
    setState(prev => ({ ...prev, loading: true, error: null, isRateLimited: false, retryAfter: null }))
    
    try {
      console.log('🔄 useUsers: Fetching users from backend with params:', params)
      
      const response: PaginatedResponse<User> = await UserService.getUsers(params)
      
      setState(prev => ({
        ...prev,
        users: response.data || [],
        loading: false,
        isRateLimited: false,
        retryAfter: null,
        pagination: {
          page: response.page || 1,
          limit: response.limit || 50,
          total: response.total || 0,
          totalPages: response.totalPages || 0
        }
      }))
      
      setLastParams(params)
      console.log('✅ useUsers: Users fetched successfully from backend API')
      
    } catch (error) {
      console.error('❌ useUsers: Error fetching users from backend:', error)
      
      let errorMessage = 'Error al conectar con el servidor'
      let isRateLimited = false
      let retryAfter: number | null = null
      
      if (error instanceof Error) {
        if (error.message.includes('429')) {
          errorMessage = 'Demasiadas peticiones. El sistema reintentará automáticamente.'
          isRateLimited = true
          // Extract retry-after from error message if available
           const retryMatch = error.message.match(/retry.*?(\d+)/i)
           retryAfter = retryMatch && retryMatch[1] ? parseInt(retryMatch[1]) : 60
        } else if (error.message.includes('401')) {
          errorMessage = 'No tienes autorización para ver esta información. Por favor, inicia sesión.'
        } else if (error.message.includes('403')) {
          errorMessage = 'No tienes permisos para acceder a esta información.'
        } else if (error.message.includes('500')) {
          errorMessage = 'Error interno del servidor. Por favor, contacta al administrador.'
        } else {
          errorMessage = error.message
        }
      }
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        isRateLimited,
        retryAfter,
        users: isRateLimited ? prev.users : [] // Keep users on rate limit, clear on other errors
      }))
      
      // Auto-retry on rate limit (max 3 attempts)
      if (isRateLimited && retryAfter && (params.retryCount || 0) < 3) {
        const retryCount = (params.retryCount || 0) + 1
        console.log(`🔄 useUsers: Auto-retrying in ${retryAfter} seconds due to rate limit (attempt ${retryCount}/3)`)
        debounceTimeoutRef.current = setTimeout(() => {
          fetchUsers({ ...params, retryCount })
        }, retryAfter * 1000)
      } else if (isRateLimited && (params.retryCount || 0) >= 3) {
        console.error('❌ useUsers: Max retry attempts reached for rate limit')
      }
    }
  }, [])

  /**
   * Create a new user
   */
  const createUser = useCallback(async (userData: CreateUserData): Promise<User> => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      console.log('🔄 useUsers: Creating user:', userData.username)
      
      const newUser = await UserService.createUser(userData)
      
      // Validate that newUser is properly defined
      if (!newUser || typeof newUser !== 'object' || !newUser.id) {
        console.error('❌ useUsers: Invalid user object received:', newUser)
        throw new Error('Invalid user data received from server')
      }
      
      setState(prev => ({
        ...prev,
        loading: false,
        users: [newUser, ...prev.users],
        pagination: {
          ...prev.pagination,
          total: prev.pagination.total + 1
        }
      }))
      
      console.log('✅ useUsers: User created successfully:', newUser.id)
      return newUser
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al crear usuario'
      console.error('❌ useUsers: Error creating user:', errorMessage)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  /**
   * Update an existing user
   */
  const updateUser = useCallback(async (id: number, userData: Partial<CreateUserData>): Promise<User> => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      console.log('🔄 useUsers: Updating user:', id)
      
      const updatedUser = await UserService.updateUser(id, userData)
      
      // Validate that updatedUser is properly defined
      if (!updatedUser || typeof updatedUser !== 'object' || !('id' in updatedUser)) {
        console.error('❌ useUsers: Invalid updated user data:', updatedUser)
        throw new Error('Datos de usuario actualizados inválidos recibidos del servidor')
      }
      
      setState(prev => ({
        ...prev,
        loading: false,
        users: prev.users.map(user => 
          user.id === id ? updatedUser : user
        )
      }))
      
      console.log('✅ useUsers: User updated successfully:', updatedUser)
      return updatedUser
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al actualizar usuario'
      console.error('❌ useUsers: Error updating user:', errorMessage)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  /**
   * Delete a user
   */
  const deleteUser = useCallback(async (id: number): Promise<void> => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      console.log('🔄 useUsers: Deleting user:', id)
      
      await UserService.deleteUser(id)
      
      setState(prev => ({
        ...prev,
        loading: false,
        users: prev.users.filter(user => user.id !== id),
        pagination: {
          ...prev.pagination,
          total: Math.max(0, prev.pagination.total - 1)
        }
      }))
      
      console.log('✅ useUsers: User deleted successfully:', id)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar usuario'
      console.error('❌ useUsers: Error deleting user:', errorMessage)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  /**
   * Toggle user status (active/inactive)
   */
  const toggleUserStatus = useCallback(async (id: number): Promise<User> => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      console.log('🔄 useUsers: Toggling user status:', id)
      
      const updatedUser = await UserService.toggleUserStatus(id)
      
      setState(prev => ({
        ...prev,
        loading: false,
        users: prev.users.map(user => 
          user.id === id ? updatedUser : user
        )
      }))
      
      console.log('✅ useUsers: User status toggled successfully:', id)
      return updatedUser
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al cambiar estado del usuario'
      console.error('❌ useUsers: Error toggling user status:', errorMessage)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  /**
   * Change user password
   */
  const changeUserPassword = useCallback(async (id: number, newPassword: string): Promise<void> => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      console.log('🔄 useUsers: Changing user password:', id)
      
      await UserService.changeUserPassword(id, newPassword)
      
      setState(prev => ({ ...prev, loading: false }))
      
      console.log('✅ useUsers: User password changed successfully:', id)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al cambiar contraseña'
      console.error('❌ useUsers: Error changing user password:', errorMessage)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  /**
   * Refresh users with last used parameters
   */
  const refreshUsers = useCallback(async () => {
    await fetchUsers(lastParams)
  }, []) // Removed all dependencies to prevent infinite loops

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  // Auto-fetch users on mount if initial params are provided
  useEffect(() => {
    if (initialParams) {
      fetchUsers(initialParams)
    }
    
    // Cleanup timeout on unmount
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }
    }
  }, []) // Only run on mount

  return {
    // State
    users: state.users,
    loading: state.loading,
    error: state.error,
    isRateLimited: state.isRateLimited,
    retryAfter: state.retryAfter,
    pagination: state.pagination,
    
    // Actions
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    toggleUserStatus,
    changeUserPassword,
    refreshUsers,
    clearError
  }
}

export default useUsers