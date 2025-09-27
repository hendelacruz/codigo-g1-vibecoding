import React from 'react'
import { Sidebar } from '../shared/components/layout/Sidebar'
import { UserManagement } from '../components/auth/UserManagement'
import { usePermissionsCorrect } from '../hooks/usePermissionsCorrect'

export const UsersPage: React.FC = () => {
  const { hasPermission, isAdmin } = usePermissionsCorrect()

  // Permission checks
  const canViewUsers = hasPermission('auth.view_user') || isAdmin

  if (!canViewUsers) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar onModuleChange={() => {}} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Acceso Denegado</h2>
            <p className="text-gray-600">No tienes permisos para ver esta página.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar onModuleChange={() => {}} />
      
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <UserManagement />
        </div>
      </div>
    </div>
  )
}