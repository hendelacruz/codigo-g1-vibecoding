import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { clearAuth } from '../features/auth/authSlice'
import type { RootState } from '../app/store'

/**
 * Hook para manejar errores de autenticación de forma centralizada
 * 
 * Características:
 * - Detecta errores 401, 403 y 429
 * - Maneja logout automático en caso de token expirado
 * - Redirección automática a login
 * - Notificaciones toast apropiadas
 * - Verificación de estado de autenticación
 */
export const useAuthError = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { isAuthenticated, token } = useSelector((state: RootState) => state.auth)

  const handleAuthError = useCallback((error: unknown) => {
    // Type guard for axios-like error
    const hasResponse = error && typeof error === 'object' && 'response' in error
    const axiosError = hasResponse ? error as { response: { status?: number; statusText?: string; data?: { message?: string } } } : null
    
    // Type guard for error with message
    const hasMessage = error && typeof error === 'object' && 'message' in error
    const errorWithMessage = hasMessage ? error as { message: string } : null
    
    const status = axiosError?.response?.status
    const message = axiosError?.response?.data?.message || errorWithMessage?.message

    console.error('Auth Error:', { status, message, error })

    switch (status) {
      case 401:
        // Token expirado o inválido
        toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.')
        dispatch(clearAuth())
        navigate('/login')
        break

      case 403:
        // Sin permisos
        toast.error('No tienes permisos para realizar esta acción.')
        break

      case 429:
        // Rate limiting
        toast.error('Demasiadas solicitudes. Intenta nuevamente en unos minutos.')
        break

      case 400:
        // Bad request - puede ser datos inválidos
        toast.error(message || 'Datos inválidos en la solicitud.')
        break

      case 500:
        // Error del servidor
        toast.error('Error interno del servidor. Intenta nuevamente.')
        break

      default:
        // Otros errores
        if (status && status >= 400) {
          const statusText = axiosError?.response?.statusText || 'Error en la solicitud'
          toast.error(message || `Error ${status}: ${statusText}`)
        } else {
          toast.error(message || 'Error de conexión')
        }
        break
    }
  }, [dispatch, navigate])

  const validateAuth = useCallback(() => {
    if (!isAuthenticated || !token) {
      toast.error('Debes estar autenticado para realizar esta acción.')
      navigate('/login')
      return false
    }
    return true
  }, [isAuthenticated, token, navigate])

  const handleApiCall = useCallback(async <T>(
    apiCall: () => Promise<T>,
    options?: {
      showSuccessToast?: boolean
      successMessage?: string
      skipAuthValidation?: boolean
    }
  ): Promise<T | null> => {
    try {
      // Validar autenticación antes de la llamada
      if (!options?.skipAuthValidation && !validateAuth()) {
        return null
      }

      const result = await apiCall()
      
      if (options?.showSuccessToast) {
        toast.success(options.successMessage || 'Operación exitosa')
      }
      
      return result
    } catch (error) {
      handleAuthError(error)
      throw error
    }
  }, [handleAuthError, validateAuth])

  return { 
    handleAuthError, 
    validateAuth, 
    handleApiCall,
    isAuthenticated,
    hasValidToken: !!token
  }
}

export default useAuthError