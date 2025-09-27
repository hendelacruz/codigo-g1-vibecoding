import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import type { RootState } from '../../../app/store'

interface AuthGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

/**
 * AuthGuard - Componente que verifica autenticación antes de mostrar contenido
 * 
 * Características:
 * - Verifica si el usuario está autenticado
 * - Redirige a login si no hay autenticación
 * - Muestra fallback mientras verifica
 * - Maneja tokens expirados
 */
export const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  fallback = <AuthFallback /> 
}) => {
  const navigate = useNavigate()
  const { isAuthenticated, token, isLoading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    // Si no está cargando y no está autenticado, redirigir a login
    if (!isLoading && !isAuthenticated) {
      navigate('/login', { 
        replace: true,
        state: { 
          from: window.location.pathname,
          message: 'Debes iniciar sesión para acceder a esta función'
        }
      })
    }
  }, [isAuthenticated, isLoading, navigate])

  // Mostrar loading mientras verifica autenticación
  if (isLoading) {
    return <AuthLoadingState />
  }

  // Si no está autenticado, mostrar fallback
  if (!isAuthenticated || !token) {
    return <>{fallback}</>
  }

  // Si está autenticado, mostrar contenido
  return <>{children}</>
}

/**
 * Componente de loading para verificación de autenticación
 */
const AuthLoadingState: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-2 text-gray-600">Verificando autenticación...</p>
    </div>
  </div>
)

/**
 * Componente fallback cuando no hay autenticación
 */
const AuthFallback: React.FC = () => (
  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
    <div className="flex">
      <div className="flex-shrink-0">
        <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
      <div className="ml-3">
        <h3 className="text-sm font-medium text-yellow-800">
          Autenticación Requerida
        </h3>
        <div className="mt-2 text-sm text-yellow-700">
          <p>
            Debes iniciar sesión para acceder a esta función. 
            Serás redirigido a la página de login.
          </p>
        </div>
      </div>
    </div>
  </div>
)

export default AuthGuard