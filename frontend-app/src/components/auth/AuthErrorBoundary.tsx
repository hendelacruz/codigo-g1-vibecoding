import React, { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { Button } from '../../shared/components/ui/Button'
import { useAuthError } from '../../hooks/useAuthError'

/**
 * AuthErrorBoundary - Error Boundary específico para errores de autenticación
 * 
 * Características:
 * - Captura errores específicos del sistema de autenticación
 * - Integración con useAuthError hook para manejo centralizado
 * - Fallback UI personalizable
 * - Logging automático de errores
 * - Recuperación automática con retry
 * - Redirección a login en casos críticos
 * 
 * @author Frontend Team
 * @version 1.0.0
 */

interface AuthErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  enableRetry?: boolean
  redirectOnCriticalError?: boolean
}

interface AuthErrorBoundaryState {
  hasError: boolean
  error?: Error | null
  errorInfo?: ErrorInfo | null
  retryCount: number
}

// Hook wrapper para usar useAuthError en class component
const AuthErrorHandler: React.FC<{
  error: Error
  onRetry: () => void
  enableRetry: boolean
  redirectOnCriticalError: boolean
}> = ({ error, onRetry, enableRetry, redirectOnCriticalError }) => {
  const { handleAuthError } = useAuthError()

  React.useEffect(() => {
    // Manejar el error usando el hook centralizado
    if (redirectOnCriticalError && isAuthCriticalError(error)) {
      handleAuthError({
        response: { status: 401 },
        message: error.message
      })
    }
  }, [error, handleAuthError, redirectOnCriticalError])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
        <div className="mb-4">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg
              className="h-6 w-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
        </div>
        
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Error de Autenticación
        </h2>
        
        <p className="text-gray-600 mb-6">
          {getErrorMessage(error)}
        </p>
        
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {enableRetry && (
            <Button
              onClick={onRetry}
              variant="default"
              className="w-full sm:w-auto"
            >
              Intentar Nuevamente
            </Button>
          )}
          
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="w-full sm:w-auto"
          >
            Recargar Página
          </Button>
        </div>
        
        <div className="mt-4 text-xs text-gray-500">
          Si el problema persiste, contacta al administrador del sistema.
        </div>
      </div>
    </div>
  )
}

// Función para determinar si es un error crítico de autenticación
const isAuthCriticalError = (error: Error): boolean => {
  const criticalPatterns = [
    'token',
    'auth',
    'login',
    'session',
    'unauthorized',
    'forbidden',
    'expired'
  ]
  
  const errorMessage = error.message.toLowerCase()
  return criticalPatterns.some(pattern => errorMessage.includes(pattern))
}

// Función para obtener mensaje de error user-friendly
const getErrorMessage = (error: Error): string => {
  const message = error.message.toLowerCase()
  
  if (message.includes('token') || message.includes('expired')) {
    return 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
  }
  
  if (message.includes('unauthorized') || message.includes('forbidden')) {
    return 'No tienes permisos para acceder a esta sección.'
  }
  
  if (message.includes('network') || message.includes('connection')) {
    return 'Error de conexión. Verifica tu conexión a internet.'
  }
  
  if (message.includes('server') || message.includes('500')) {
    return 'Error interno del servidor. Intenta nuevamente en unos minutos.'
  }
  
  return 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.'
}

export class AuthErrorBoundary extends Component<AuthErrorBoundaryProps, AuthErrorBoundaryState> {
  private readonly maxRetries = 3

  constructor(props: AuthErrorBoundaryProps) {
    super(props)
    this.state = { 
      hasError: false, 
      retryCount: 0 
    }
  }

  static getDerivedStateFromError(error: Error): Partial<AuthErrorBoundaryState> {
    return { hasError: true, error }
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log del error para debugging
    console.error('AuthErrorBoundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      retryCount: this.state.retryCount
    })

    // Actualizar estado con información del error
    this.setState({
      error,
      errorInfo
    })

    // Callback personalizado si se proporciona
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Reportar error a servicio de monitoreo (si está configurado)
    if (typeof window !== 'undefined' && 'Sentry' in window) {
      const sentry = (window as { Sentry?: { captureException: (error: Error, options?: Record<string, unknown>) => void } }).Sentry
      sentry?.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        },
        tags: {
          section: 'auth',
          retryCount: this.state.retryCount
        }
      })
    }
  }

  handleRetry = () => {
    if (this.state.retryCount < this.maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1
      }))
    } else {
      // Máximo de reintentos alcanzado, recargar página
      window.location.reload()
    }
  }

  override render() {
    if (this.state.hasError && this.state.error) {
      // Usar fallback personalizado si se proporciona
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Renderizar UI de error por defecto
      return (
        <AuthErrorHandler
          error={this.state.error}
          onRetry={this.handleRetry}
          enableRetry={this.props.enableRetry !== false && this.state.retryCount < this.maxRetries}
          redirectOnCriticalError={this.props.redirectOnCriticalError !== false}
        />
      )
    }

    return this.props.children
  }
}

// Export por defecto para facilitar importación
export default AuthErrorBoundary

// Export de tipos para uso externo
export type { AuthErrorBoundaryProps, AuthErrorBoundaryState }