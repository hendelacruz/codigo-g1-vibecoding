/**
 * AuthProvider - Proveedor de contexto de autenticación global
 * 
 * Proporciona un contexto de autenticación robusto que integra Redux con React Context
 * para manejar el estado de autenticación de manera eficiente y escalable.
 * 
 * Características:
 * - Integración con Redux para estado global
 * - Manejo automático de tokens y renovación
 * - Interceptores de Axios configurados automáticamente
 * - Funciones optimizadas para login, logout y verificación
 * - Manejo de errores y recuperación de sesión
 * - TypeScript estricto para type safety
 */

import React, { createContext, useContext, useEffect, useCallback, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '../../app/store'
import { 
  loginUser, 
  logoutUser, 
  refreshAuthToken, 
  checkAuthStatus,
  clearError
} from '../../features/auth/authSlice'
import { setupAuthResponseInterceptor } from '../../features/auth/authAPI'
import type { LoginCredentials, User } from '../../features/auth/authTypes'

/**
 * Tipo para el contexto de autenticación
 */
interface AuthContextType {
  // Estado de autenticación
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  isInitialized: boolean

  // Funciones de autenticación
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  checkAuth: () => Promise<void>
  clearAuthError: () => void

  // Funciones de utilidad
  hasRole: (role: string) => boolean
  hasPermission: (permission: string) => boolean
  getAuthHeaders: () => Record<string, string>
}

/**
 * Props para el AuthProvider
 */
interface AuthProviderProps {
  children: React.ReactNode
}

/**
 * Contexto de autenticación
 */
const AuthContext = createContext<AuthContextType | null>(null)

/**
 * Hook para usar el contexto de autenticación
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  return context
}

/**
 * Proveedor de contexto de autenticación
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useDispatch<AppDispatch>()
  const authState = useSelector((state: RootState) => state.auth)
  const [isInitialized, setIsInitialized] = React.useState(false)

  // Setup interceptors for automatic token handling
  useEffect(() => {
    setupAuthResponseInterceptor(() => {
      if (authState.refreshToken) {
        dispatch(refreshAuthToken(authState.refreshToken))
          .catch(() => {
            if (authState.refreshToken) {
              dispatch(logoutUser(authState.refreshToken))
            }
          })
      }
    })
  }, [dispatch, authState.refreshToken])

  // Initialize authentication state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('authToken')
      
      if (storedToken) {
        try {
          // Verify token is still valid
          await dispatch(checkAuthStatus(storedToken)).unwrap()
        } catch {
          // Token invalid, clear storage
          localStorage.removeItem('authToken')
          localStorage.removeItem('refreshToken')
        }
      }
      
      setIsInitialized(true)
    }

    initializeAuth()
  }, [dispatch])

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      await dispatch(loginUser(credentials)).unwrap()
    } catch (error) {
      console.error('Error during login:', error)
      throw error
    }
  }, [dispatch])

  // Logout function
  const logout = useCallback(async () => {
    try {
      if (authState.refreshToken) {
        await dispatch(logoutUser(authState.refreshToken)).unwrap()
      }
    } catch (error) {
      console.error('Error during logout:', error)
    } finally {
      localStorage.removeItem('authToken')
      localStorage.removeItem('refreshToken')
    }
  }, [dispatch, authState.refreshToken])

  // Refresh token function
  const refreshToken = useCallback(async () => {
    try {
      if (authState.refreshToken) {
        await dispatch(refreshAuthToken(authState.refreshToken)).unwrap()
      }
    } catch (error) {
      console.error('Error refreshing token:', error)
      await logout()
    }
  }, [dispatch, authState.refreshToken, logout])

  // Check authentication status
  const checkAuth = useCallback(async () => {
    try {
      if (authState.token) {
        await dispatch(checkAuthStatus(authState.token)).unwrap()
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      await logout()
    }
  }, [dispatch, authState.token, logout])

  // Clear authentication errors
  const clearAuthError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  // Check if user has specific role
  const hasRole = useCallback((role: string): boolean => {
    return authState.user?.groups?.includes(role) ?? false
  }, [authState.user])

  // Check if user has specific permission
  const hasPermission = useCallback((permission: string): boolean => {
    return authState.user?.user_permissions?.includes(permission) ?? false
  }, [authState.user])

  // Get authentication headers for API calls
  const getAuthHeaders = useCallback((): Record<string, string> => {
    if (authState.token) {
      return {
        'Authorization': `Bearer ${authState.token}`,
        'Content-Type': 'application/json'
      }
    }
    return {
      'Content-Type': 'application/json'
    }
  }, [authState.token])

  // Memoized context value
  const contextValue = useMemo<AuthContextType>(() => ({
    // Estado
    user: authState.user,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    error: authState.error,
    isInitialized,

    // Funciones
    login,
    logout,
    refreshToken,
    checkAuth,
    clearAuthError,

    // Utilidades
    hasRole,
    hasPermission,
    getAuthHeaders
  }), [
    authState.user,
    authState.token,
    authState.isAuthenticated,
    authState.isLoading,
    authState.error,
    isInitialized,
    login,
    logout,
    refreshToken,
    checkAuth,
    clearAuthError,
    hasRole,
    hasPermission,
    getAuthHeaders
  ])

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * HOC para componentes que requieren autenticación
 */
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  const AuthenticatedComponent: React.FC<P> = (props) => {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
      return <div>Cargando...</div>
    }

    if (!isAuthenticated) {
      return <div>No autorizado</div>
    }

    return <Component {...props} />
  }

  AuthenticatedComponent.displayName = `withAuth(${Component.displayName || Component.name})`
  
  return AuthenticatedComponent
}

export default AuthProvider