/**
 * useAuthErrorHandler - Hook para manejo avanzado de errores de autenticación
 * 
 * Proporciona funcionalidades para:
 * - Manejo de errores de autenticación con retry automático
 * - Recuperación de sesión con múltiples estrategias
 * - Notificaciones de errores contextuales
 * - Logging y monitoreo de errores
 * - Fallbacks y estrategias de recuperación
 */

import { useCallback, useRef, useState, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from '../app/store'
import { 
  refreshAuthToken, 
  clearAuth, 
  clearError as clearAuthError,
  checkAuthStatus 
} from '../features/auth/authSlice'
import { authAPI } from '../features/auth/authAPI'

// Types for error handling
export interface AuthError {
  code: string
  message: string
  type: 'network' | 'auth' | 'server' | 'validation' | 'unknown'
  timestamp: number
  context?: Record<string, unknown> | undefined
  recoverable: boolean
}

export interface RecoveryStrategy {
  name: string
  execute: () => Promise<boolean>
  priority: number
  maxRetries: number
}

export interface AuthErrorHandlerOptions {
  enableAutoRecovery?: boolean
  maxRetryAttempts?: number
  retryDelay?: number
  enableLogging?: boolean
  onError?: (error: AuthError) => void
  onRecovery?: (strategy: string) => void
}

const DEFAULT_OPTIONS: Required<AuthErrorHandlerOptions> = {
  enableAutoRecovery: true,
  maxRetryAttempts: 3,
  retryDelay: 1000,
  enableLogging: true,
  onError: () => {},
  onRecovery: () => {}
}

/**
 * Hook principal para manejo de errores de autenticación
 */
export const useAuthErrorHandler = (options: AuthErrorHandlerOptions = {}) => {
  const dispatch = useDispatch<AppDispatch>()
  const authState = useSelector((state: RootState) => state.auth)
  
  const config = useMemo(() => ({ ...DEFAULT_OPTIONS, ...options }), [options])
  const retryCountRef = useRef<Record<string, number>>({})
  const [isRecovering, setIsRecovering] = useState(false)
  const [lastError, setLastError] = useState<AuthError | null>(null)

  /**
   * Utility function for delay
   */
  const delay = useCallback((ms: number) => 
    new Promise(resolve => setTimeout(resolve, ms)), [])

  /**
   * Parse and categorize errors
   */
  const parseError = useCallback((error: unknown, context?: Record<string, unknown>): AuthError => {
    let authError: AuthError = {
      code: 'UNKNOWN_ERROR',
      message: 'An unknown error occurred',
      type: 'unknown',
      timestamp: Date.now(),
      context,
      recoverable: false
    }

    // Type guard for axios-like error
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response: { status: number; data: unknown } }
      const { status, data } = axiosError.response
      
      // Type guard for data with detail property
      const dataWithDetail = data && typeof data === 'object' && 'detail' in data ? data as { detail: string } : null
      
      switch (status) {
        case 401:
          authError = {
            code: 'UNAUTHORIZED',
            message: dataWithDetail?.detail || 'Authentication required',
            type: 'auth',
            timestamp: Date.now(),
            context,
            recoverable: true
          }
          break
          
        case 403:
          authError = {
            code: 'FORBIDDEN',
            message: dataWithDetail?.detail || 'Access denied',
            type: 'auth',
            timestamp: Date.now(),
            context,
            recoverable: false
          }
          break
          
        case 422:
          authError = {
            code: 'VALIDATION_ERROR',
            message: dataWithDetail?.detail || 'Invalid data provided',
            type: 'validation',
            timestamp: Date.now(),
            context,
            recoverable: false
          }
          break
          
        case 429:
          authError = {
            code: 'RATE_LIMITED',
            message: 'Too many requests. Please try again later.',
            type: 'server',
            timestamp: Date.now(),
            context,
            recoverable: true
          }
          break
          
        case 500:
        case 502:
        case 503:
        case 504:
          authError = {
            code: 'SERVER_ERROR',
            message: 'Server error. Please try again later.',
            type: 'server',
            timestamp: Date.now(),
            context,
            recoverable: true
          }
          break
          
        default:
          authError = {
            code: `HTTP_${status}`,
            message: dataWithDetail?.detail || `HTTP ${status} error`,
            type: 'server',
            timestamp: Date.now(),
            context,
            recoverable: status >= 500
          }
      }
    } else if (error && typeof error === 'object' && ('code' in error || 'message' in error)) {
      const errorObj = error as { code?: string; message?: string }
      if (errorObj.code === 'NETWORK_ERROR' || (errorObj.message && errorObj.message.includes('Network'))) {
        authError = {
          code: 'NETWORK_ERROR',
          message: 'Network connection error',
          type: 'network',
          timestamp: Date.now(),
          context,
          recoverable: true
        }
      } else if (errorObj.message) {
        authError = {
          code: 'CLIENT_ERROR',
          message: errorObj.message,
          type: 'unknown',
          timestamp: Date.now(),
          context,
          recoverable: false
        }
      }
    }

    return authError
  }, [])

  /**
   * Log errors for monitoring
   */
  const logError = useCallback((error: AuthError) => {
    if (!config.enableLogging) return

    console.group(`🔐 Auth Error [${error.code}]`)
    console.error('Message:', error.message)
    console.error('Type:', error.type)
    console.error('Recoverable:', error.recoverable)
    console.error('Timestamp:', new Date(error.timestamp).toISOString())
    if (error.context) {
      console.error('Context:', error.context)
    }
    console.groupEnd()

    // Here you could integrate with external logging services
    // Example: Sentry, LogRocket, etc.
  }, [config.enableLogging])

  /**
   * Recovery strategies ordered by priority
   */
  const recoveryStrategies: RecoveryStrategy[] = useMemo(() => [
    {
      name: 'token_refresh',
      priority: 1,
      maxRetries: 2,
      execute: async (): Promise<boolean> => {
        if (!authState.refreshToken) return false
        
        try {
          const result = await dispatch(refreshAuthToken(authState.refreshToken))
          return refreshAuthToken.fulfilled.match(result)
        } catch {
          return false
        }
      }
    },
    {
      name: 'auth_status_check',
      priority: 2,
      maxRetries: 1,
      execute: async (): Promise<boolean> => {
        if (!authState.token) return false
        
        try {
          const result = await dispatch(checkAuthStatus(authState.token))
          return checkAuthStatus.fulfilled.match(result)
        } catch {
          return false
        }
      }
    },
    {
      name: 'silent_reauth',
      priority: 3,
      maxRetries: 1,
      execute: async (): Promise<boolean> => {
        // Try to get fresh auth status from server
        try {
          if (authState.token) {
            const authStatus = await authAPI.getAuthStatus(authState.token)
            return !!authStatus.user
          }
          return false
        } catch {
          return false
        }
      }
    }
  ], [authState, dispatch])

  /**
   * Execute recovery strategies
   */
  const executeRecovery = useCallback(async (error: AuthError): Promise<boolean> => {
    if (!error.recoverable || !config.enableAutoRecovery) return false

    setIsRecovering(true)
    
    try {
      // Sort strategies by priority
      const sortedStrategies = [...recoveryStrategies].sort((a, b) => a.priority - b.priority)
      
      for (const strategy of sortedStrategies) {
        const retryKey = `${strategy.name}_${error.code}`
        const currentRetries = retryCountRef.current[retryKey] || 0
        
        if (currentRetries >= strategy.maxRetries) continue
        
        try {
          retryCountRef.current[retryKey] = currentRetries + 1
          
          const success = await strategy.execute()
          
          if (success) {
            config.onRecovery(strategy.name)
            logError({
              ...error,
              message: `Recovered using strategy: ${strategy.name}`,
              code: 'RECOVERY_SUCCESS'
            })
            return true
          }
        } catch (strategyError) {
          logError({
            code: 'RECOVERY_STRATEGY_FAILED',
            message: `Strategy ${strategy.name} failed`,
            type: 'unknown',
            timestamp: Date.now(),
            context: { strategy: strategy.name, error: strategyError },
            recoverable: false
          })
        }
        
        // Delay between strategies
        await delay(config.retryDelay)
      }
      
      return false
    } finally {
      setIsRecovering(false)
    }
  }, [config, delay, logError, recoveryStrategies])

  /**
   * Main error handling function
   */
  const handleAuthError = useCallback(async (
    error: unknown, 
    context?: Record<string, unknown>
  ): Promise<boolean> => {
    const authError = parseError(error, context)
    setLastError(authError)
    
    // Log the error
    logError(authError)
    
    // Update Redux state - using a custom error state since setAuthError doesn't exist
    // We'll use the existing error field in auth state through other actions
    
    // Call custom error handler
    config.onError(authError)
    
    // Attempt recovery if possible
    if (authError.recoverable) {
      const recovered = await executeRecovery(authError)
      
      if (!recovered) {
        // All recovery strategies failed
        if (authError.type === 'auth') {
          dispatch(clearAuth())
          // Redirect to login will be handled by the router
        }
      }
      
      return recovered
    }
    
    return false
  }, [parseError, logError, dispatch, config, executeRecovery])

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setLastError(null)
    dispatch(clearAuthError())
  }, [dispatch])

  /**
   * Reset retry counters
   */
  const resetRetryCounters = useCallback(() => {
    retryCountRef.current = {}
  }, [])

  /**
   * Check if a specific error type is recoverable
   */
  const isRecoverable = useCallback((error: unknown): boolean => {
    const authError = parseError(error)
    return authError.recoverable
  }, [parseError])

  /**
   * Get error statistics
   */
  const getErrorStats = useCallback(() => {
    return {
      lastError,
      isRecovering,
      retryCount: Object.values(retryCountRef.current).reduce((sum, count) => sum + count, 0),
      hasActiveError: !!lastError && !!authState.error
    }
  }, [lastError, isRecovering, authState.error])

  return {
    // Main functions
    handleAuthError,
    clearError,
    resetRetryCounters,
    
    // Utilities
    isRecoverable,
    parseError,
    
    // State
    isRecovering,
    lastError,
    getErrorStats,
    
    // Configuration
    config
  }
}

/**
 * Lightweight version for simple error handling
 */
export const useAuthErrorHandlerLite = () => {
  const dispatch = useDispatch<AppDispatch>()
  
  const handleError = useCallback((error: unknown) => {
    // Log error for debugging
    console.error('Auth Error:', error)
    
    // Type guard for axios-like error
    const hasResponse = error && typeof error === 'object' && 'response' in error
    const axiosError = hasResponse ? error as { response: { status: number } } : null
    
    // Clear auth on 401 errors
    if (axiosError?.response?.status === 401) {
      dispatch(clearAuth())
    }
  }, [dispatch])
  
  const clearError = useCallback(() => {
    dispatch(clearAuthError())
  }, [dispatch])
  
  return {
    handleError,
    clearError
  }
}

export default useAuthErrorHandler