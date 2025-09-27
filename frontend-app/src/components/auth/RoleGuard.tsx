/**
 * RoleGuard Component - Control de acceso basado en roles y permisos
 * 
 * Este componente proporciona control granular de acceso a nivel de componente,
 * complementando al ProtectedRoute que maneja autenticación a nivel de ruta.
 * 
 * Características:
 * - Verificación de roles específicos (Administradores, Supervisores, etc.)
 * - Verificación de permisos específicos (auth.add_user, inventory.view_dispositivo, etc.)
 * - Soporte para múltiples roles/permisos con lógica AND/OR
 * - Fallback personalizable para acceso denegado
 * - Integración completa con usePermissions hook
 * - TypeScript estricto para type safety
 */

import type { ReactNode } from 'react'
import { usePermissionsCorrect } from '../../hooks/usePermissionsCorrect'

// Tipos específicos para roles y permisos del sistema
type Role = 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores'
type Permission = string

interface RoleGuardProps {
  children: ReactNode
  /** Roles requeridos para acceder al contenido */
  roles?: Role[]
  /** Permisos específicos requeridos */
  permissions?: Permission[]
  /** Componente a mostrar cuando no se tienen permisos */
  fallback?: ReactNode
  /** Si true, requiere TODOS los roles/permisos. Si false, requiere AL MENOS UNO */
  requireAll?: boolean
  /** Mensaje personalizado para mostrar en el fallback por defecto */
  deniedMessage?: string
  /** Título personalizado para el fallback por defecto */
  deniedTitle?: string
}

/**
 * RoleGuard - Componente de control de acceso granular
 * 
 * Diferencias con ProtectedRoute:
 * - ProtectedRoute: Maneja autenticación (¿está logueado?)
 * - RoleGuard: Maneja autorización (¿puede hacer esto?)
 * 
 * Diferencias con AuthGuard:
 * - AuthGuard: Verificación básica de autenticación con redirección
 * - RoleGuard: Control granular de permisos sin redirección
 */
export function RoleGuard({ 
  children, 
  roles = [], 
  permissions = [], 
  fallback = null,
  requireAll = false,
  deniedMessage = "No tienes permisos para acceder a esta sección.",
  deniedTitle = "Acceso Denegado"
}: RoleGuardProps) {
  const { hasRole, hasPermission, hasAnyRole, isAuthenticated } = usePermissionsCorrect()

  // Si no está autenticado, no mostrar nada (esto debería manejarse en ProtectedRoute)
  if (!isAuthenticated) {
    return null
  }

  // Verificar roles si se especificaron
  let hasRequiredRole = true
  if (roles.length > 0) {
    hasRequiredRole = requireAll 
      ? roles.every(role => hasRole(role))
      : hasAnyRole(roles)
  }

  // Verificar permisos si se especificaron
  let hasRequiredPermission = true
  if (permissions.length > 0) {
    hasRequiredPermission = requireAll
      ? permissions.every(permission => hasPermission(permission))
      : permissions.some(permission => hasPermission(permission))
  }

  // Si no tiene los permisos requeridos, mostrar fallback
  if (!hasRequiredRole || !hasRequiredPermission) {
    return fallback || <DefaultAccessDenied title={deniedTitle} message={deniedMessage} />
  }

  // Si tiene permisos, mostrar el contenido
  return <>{children}</>
}

/**
 * Componente por defecto para mostrar cuando se deniega el acceso
 */
const DefaultAccessDenied: React.FC<{ title: string; message: string }> = ({ 
  title, 
  message 
}) => (
  <div className="text-center p-8 bg-gray-50 rounded-lg border border-gray-200">
    <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
      <svg 
        className="w-8 h-8 text-red-600" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
        />
      </svg>
    </div>
    <h3 className="text-lg font-semibold text-gray-700 mb-2">
      {title}
    </h3>
    <p className="text-gray-500 text-sm max-w-md mx-auto">
      {message}
    </p>
  </div>
)

export default RoleGuard