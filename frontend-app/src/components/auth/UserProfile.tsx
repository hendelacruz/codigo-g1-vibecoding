import React, { useState } from 'react';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { usePermissionsCorrect } from '../../hooks/usePermissionsCorrect';
import { LogoutButton } from './LogoutButton';

interface UserProfileProps {
  className?: string
  showFullProfile?: boolean
}

export const UserProfile: React.FC<UserProfileProps> = ({ 
  className = '', 
  showFullProfile = false 
}) => {
  const { user } = useAuth()
  const { hasRole, hasPermission } = usePermissionsCorrect()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  if (!user) {
    return null
  }



  const getUserRoleDisplay = () => {
    if (hasRole('Administradores')) return 'Administrador'
    if (hasRole('Supervisores')) return 'Supervisor'
    if (hasRole('Técnicos')) return 'Técnico'
    if (hasRole('Operadores')) return 'Operador'
    return user.rol_nombre || 'Usuario'
  }

  const getUserInitials = () => {
    const firstName = user.first_name || user.username
    const lastName = user.last_name || ''
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  if (showFullProfile) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-xl font-semibold">
            {getUserInitials()}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user.username
              }
            </h3>
            <p className="text-sm text-gray-600">{user.email}</p>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {getUserRoleDisplay()}
            </span>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Información de la cuenta</h4>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Usuario:</span>
                <span className="font-medium">{user.username}</span>
              </div>
              <div className="flex justify-between">
                <span>Email:</span>
                <span className="font-medium">{user.email}</span>
              </div>
              <div className="flex justify-between">
                <span>Estado:</span>
                <span className={`font-medium ${user.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {user.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>DNI:</span>
                <span className="font-medium">{user.dni || 'No especificado'}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Permisos principales</h4>
            <div className="flex flex-wrap gap-1">
              {hasPermission('auth.view_user') && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                  Ver usuarios
                </span>
              )}
              {hasPermission('auth.add_user') && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                  Crear usuarios
                </span>
              )}
              {hasPermission('auth.change_user') && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800">
                  Editar usuarios
                </span>
              )}
              {hasPermission('auth.delete_user') && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                  Eliminar usuarios
                </span>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <LogoutButton
              variant="secondary"
              size="sm"
              className="w-full"
              showConfirmation={true}
            />
          </div>
        </div>
      </div>
    )
  }

  // Compact profile for header
  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md p-2"
      >
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
          {getUserInitials()}
        </div>
        <div className="hidden sm:block text-left">
          <div className="font-medium">
            {user.first_name && user.last_name 
              ? `${user.first_name} ${user.last_name}`
              : user.username
            }
          </div>
          <div className="text-xs text-gray-500">{getUserRoleDisplay()}</div>
        </div>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isDropdownOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsDropdownOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-20">
            <div className="p-4">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {getUserInitials()}
                </div>
                <div>
                  <div className="font-medium text-gray-900">
                    {user.first_name && user.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user.username
                    }
                  </div>
                  <div className="text-sm text-gray-500">{user.email}</div>
                </div>
              </div>
              
              <div className="mb-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {getUserRoleDisplay()}
                </span>
              </div>

              <div className="border-t border-gray-200 pt-3">
                <LogoutButton
                  variant="secondary"
                  size="sm"
                  className="w-full"
                  showConfirmation={true}
                />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}