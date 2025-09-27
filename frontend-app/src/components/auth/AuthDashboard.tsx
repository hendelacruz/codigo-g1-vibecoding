import React, { useState } from 'react'
import { useAuth } from '../../features/auth/hooks/useAuth'
import { usePermissionsCorrect } from '../../hooks/usePermissionsCorrect'
import { UserProfile } from './UserProfile'
import { RoleGuard } from './RoleGuard'
import { Button } from '../../shared/components/ui/Button'
import { UserManagement } from './UserManagement'

interface AuthDashboardProps {
  className?: string
}

export const AuthDashboard: React.FC<AuthDashboardProps> = ({ className = '' }) => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const { hasRole, canAccess } = usePermissionsCorrect()
  const [showUserProfile, setShowUserProfile] = useState(false)
  const [showUserManagement, setShowUserManagement] = useState(false)

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Sesión no válida
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>Tu sesión ha expirado. Por favor, inicia sesión nuevamente.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const getPermissionsSummary = () => {
    const permissions = []
    
    if (canAccess('users', 'read')) permissions.push('Ver usuarios')
    if (canAccess('users', 'create')) permissions.push('Crear usuarios')
    if (canAccess('inventory', 'read')) permissions.push('Ver inventario')
    if (canAccess('inventory', 'create')) permissions.push('Gestionar inventario')
    if (canAccess('services', 'read')) permissions.push('Ver servicios')
    if (canAccess('services', 'create')) permissions.push('Gestionar servicios')
    if (canAccess('sales', 'read')) permissions.push('Ver ventas')
    if (canAccess('reports', 'read')) permissions.push('Ver reportes')

    return permissions
  }

  const getAccessLevelColor = () => {
    if (hasRole('Administradores')) return 'bg-red-100 text-red-800'
    if (hasRole('Supervisores')) return 'bg-yellow-100 text-yellow-800'
    if (hasRole('Técnicos')) return 'bg-blue-100 text-blue-800'
    if (hasRole('Operadores')) return 'bg-green-100 text-green-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header de autenticación */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white text-lg font-semibold">
              {user.first_name?.charAt(0) || user.username.charAt(0)}
              {user.last_name?.charAt(0) || ''}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                ¡Bienvenido, {user.first_name || user.username}!
              </h2>
              <p className="text-sm text-gray-600">
                Sesión activa como {user.rol_nombre || 'Usuario'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getAccessLevelColor()}`}>
              {hasRole('Administradores') && 'Acceso Total'}
              {hasRole('Supervisores') && 'Supervisor'}
              {hasRole('Técnicos') && 'Técnico'}
              {hasRole('Operadores') && 'Operador'}
              {!hasRole('Administradores') && !hasRole('Supervisores') && !hasRole('Técnicos') && !hasRole('Operadores') && 'Usuario'}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowUserProfile(!showUserProfile)}
            >
              {showUserProfile ? 'Ocultar perfil' : 'Ver perfil'}
            </Button>
          </div>
        </div>
      </div>

      {/* Perfil de usuario expandido */}
      {showUserProfile && (
        <UserProfile showFullProfile={true} />
      )}

      {/* Gestión de usuarios */}
      {showUserManagement && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Gestión de Usuarios</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowUserManagement(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
          <UserManagement />
        </div>
      )}

      {/* Panel de permisos y accesos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Módulos disponibles */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Módulos disponibles</h3>
          <div className="space-y-2">
            {canAccess('inventory', 'read') && (
              <div className="flex items-center text-sm text-green-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Inventario
              </div>
            )}
            {canAccess('services', 'read') && (
              <div className="flex items-center text-sm text-green-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Servicios
              </div>
            )}
            {canAccess('sales', 'read') && (
              <div className="flex items-center text-sm text-green-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Ventas
              </div>
            )}
            {canAccess('reports', 'read') && (
              <div className="flex items-center text-sm text-green-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Reportes
              </div>
            )}
          </div>
        </div>

        {/* Permisos específicos */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Permisos activos</h3>
          <div className="space-y-2">
            {getPermissionsSummary().slice(0, 5).map((permission, index) => (
              <div key={index} className="flex items-center text-sm text-blue-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {permission}
              </div>
            ))}
            {getPermissionsSummary().length > 5 && (
              <div className="text-sm text-gray-500">
                +{getPermissionsSummary().length - 5} permisos más
              </div>
            )}
          </div>
        </div>

        {/* Acciones rápidas */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Acciones rápidas</h3>
          <div className="space-y-3">
            <RoleGuard roles={['Administradores', 'Supervisores']}>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full justify-start"
                onClick={() => setShowUserManagement(!showUserManagement)}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                {showUserManagement ? 'Ocultar gestión' : 'Gestionar usuarios'}
              </Button>
            </RoleGuard>
            
            {canAccess('inventory', 'create') && (
              <Button variant="outline" size="sm" className="w-full justify-start">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Agregar producto
              </Button>
            )}
            
            {canAccess('reports', 'read') && (
              <Button variant="outline" size="sm" className="w-full justify-start">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Ver reportes
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}