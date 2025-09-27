import React, { useState, useEffect } from 'react'
import { usePermissionsCorrect } from '../../hooks/usePermissionsCorrect'
import { useUsers } from '../../features/auth/hooks/useUsers'
import { UserTable } from './UserTable'
import { UserForm, type UserFormData } from './UserForm'
import { DeleteUserModal } from './DeleteUserModal'
import { Button } from '../../shared/components/ui/Button'

import type { User } from '../../shared/types/common'
import type { CreateUserData } from '../../features/auth/authTypes'

// Mapeo de nombres de roles a IDs (basado en el backend Django)
const ROLE_NAME_TO_ID: Record<string, number> = {
  'ADMIN': 1,
  'administrador': 5,
  'supervisor': 11,
  'tecnico': 7,
}

export const UserManagement: React.FC = () => {
  const { canAccess, isAuthenticated } = usePermissionsCorrect()
  const { users, loading, error, createUser, updateUser, deleteUser, fetchUsers } = useUsers()
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  // Permission checks
  const canViewUsers = canAccess('users', 'read')
  const canCreateUsers = canAccess('users', 'create')
  const canEditUsers = canAccess('users', 'update')
  const canDeleteUsers = canAccess('users', 'delete')

  // Debug logs
  console.log('🔍 UserManagement Debug:', {
    isAuthenticated,
    canViewUsers,
    canCreateUsers,
    canEditUsers,
    canDeleteUsers,
    loading,
    error,
    usersCount: users?.length || 0,
    users: users
  })

  // Debug: Log current state
  console.log('🔍 UserManagement render state:', {
    isAuthenticated,
    canViewUsers,
    canCreateUsers,
    canEditUsers,
    canDeleteUsers,
    loading,
    error,
    usersCount: users?.length || 0,
    hasUsers: !!users,
    usersArray: users
  })

  // Load users on component mount
  useEffect(() => {
    console.log('🔄 UserManagement useEffect triggered:', { isAuthenticated, canViewUsers })
    if (isAuthenticated && canViewUsers) {
      console.log('🔄 UserManagement: Loading users on mount')
      fetchUsers()
    } else {
      console.log('❌ UserManagement: Cannot load users', { isAuthenticated, canViewUsers })
    }
  }, [isAuthenticated, canViewUsers])

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Debes iniciar sesión para ver esta página</p>
      </div>
    )
  }

  if (!canViewUsers) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-red-500">No tienes permisos para ver los usuarios</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-red-500">Error al cargar usuarios: {error}</p>
      </div>
    )
  }

  const handleCreateUser = async (userData: UserFormData) => {
    try {
      // Get rol_id from rol_nombre mapping
      const rol_id = ROLE_NAME_TO_ID[userData.rol_nombre]
      
      if (!rol_id) {
        throw new Error(`Rol no válido: ${userData.rol_nombre}`)
      }

      // Clean celular format (remove spaces, hyphens, parentheses)
      const formatCelular = (celular: string): string => {
        return celular.replace(/[\s\-()]/g, '')
      }

      // Transform UserFormData to CreateUserData
      const createData: CreateUserData = {
        username: userData.username,
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        dni: userData.dni,
        celular: formatCelular(userData.celular),
        password: userData.password || '', // Provide default empty string
        password_confirm: userData.confirm_password || userData.password || '', // Use confirm_password from form
        rol: rol_id, // Use 'rol' instead of 'rol_id' as backend expects
        is_active: userData.is_active,
        ...(userData.licencia && userData.licencia.trim() && { licencia: userData.licencia })
      }
      
      // Debug logging
      console.log('🔍 UserFormData received:', userData)
      console.log('🔍 CreateUserData to send:', createData)
      console.log('🔍 Mapped rol_id:', rol_id, 'from rol_nombre:', userData.rol_nombre)
      
      // Create the user
      const newUser = await createUser(createData)
      console.log('✅ Usuario creado exitosamente:', newUser.username)
      
      // Close modal immediately after successful creation
      setIsCreateModalOpen(false)
      
      // Refresh the user list to ensure synchronization
      console.log('🔄 Refreshing user list after creation')
      await fetchUsers()
      
    } catch (err) {
      console.error('❌ Error creating user:', err)
      // Error will be handled by the useUsers hook and displayed in the UI
      // The modal will remain open so user can see the error and retry
    }
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setIsEditModalOpen(true)
  }

  const handleUpdateUser = async (userData: UserFormData) => {
    if (!selectedUser) return
    
    try {
      // Get rol_id from rol_nombre mapping
      const rol_id = ROLE_NAME_TO_ID[userData.rol_nombre]
      
      if (!rol_id) {
        throw new Error(`Rol no válido: ${userData.rol_nombre}`)
      }

      // Clean celular format (remove spaces, hyphens, parentheses)
      const formatCelular = (celular: string): string => {
        return celular.replace(/[\s\-()]/g, '')
      }

      // Transform UserFormData to Partial<CreateUserData>
      const updateData: Partial<CreateUserData> = {
        username: userData.username,
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        dni: userData.dni,
        celular: formatCelular(userData.celular), // ✅ AGREGADO: Campo celular faltante
        rol: rol_id, // Use 'rol' instead of 'rol_nombre'
        is_active: userData.is_active,
        ...(userData.licencia && userData.licencia.trim() && { licencia: userData.licencia }) // ✅ AGREGADO: Campo licencia opcional
      }
      
      // Only include password if it's provided
      if (userData.password && userData.password.trim() !== '') {
        updateData.password = userData.password
        updateData.password_confirm = userData.confirm_password || userData.password
      }
      
      // Debug logging
      console.log('🔍 UserFormData received for update:', userData)
      console.log('🔍 UpdateData to send:', updateData)
      console.log('🔍 Mapped rol_id:', rol_id, 'from rol_nombre:', userData.rol_nombre)
      
      await updateUser(selectedUser.id, updateData)
      console.log('✅ Usuario actualizado exitosamente:', selectedUser.username)
      
      setIsEditModalOpen(false)
      setSelectedUser(null)
      
      // Refresh the user list to ensure synchronization
      console.log('🔄 Refreshing user list after update')
      await fetchUsers()
      
    } catch (err) {
      console.error('❌ Error updating user:', err)
      // Error will be handled by the useUsers hook and displayed in the UI
    }
  }

  const handleDeleteUser = (user: User) => {
    setSelectedUser(user)
    setIsDeleteModalOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (!selectedUser) return
    
    try {
      console.log('🗑️ Deleting user:', selectedUser.username, 'ID:', selectedUser.id)
      await deleteUser(selectedUser.id)
      console.log('✅ Usuario eliminado exitosamente:', selectedUser.username)
      
      setIsDeleteModalOpen(false)
      setSelectedUser(null)
      
      // Refresh the user list to ensure synchronization
      console.log('🔄 Refreshing user list after deletion')
      await fetchUsers()
      
    } catch (err) {
      console.error('❌ Error deleting user:', err)
      // Error will be handled by the useUsers hook and displayed in the UI
    }
  }

  return (
    <div className="space-y-6">

      
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
        {canCreateUsers && (
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Nuevo Usuario
          </Button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* User Table */}
        <UserTable
          users={users}
          loading={loading}
          {...(canEditUsers && { onEdit: handleEditUser })}
          {...(canDeleteUsers && { 
            onDelete: (userId: number) => {
              const user = users.find(u => u.id === userId)
              if (user) handleDeleteUser(user)
            }
          })}
          canEdit={canEditUsers}
          canDelete={canDeleteUsers}
          canView={true}
        />

       {/* Create User Modal */}
       {isCreateModalOpen && (
         <UserForm
           user={null}
           onSubmit={handleCreateUser}
           onCancel={() => setIsCreateModalOpen(false)}
           mode="create"
         />
       )}

       {/* Edit User Modal */}
       {isEditModalOpen && selectedUser && (
         <UserForm
           user={selectedUser}
           onSubmit={handleUpdateUser}
           onCancel={() => {
             setIsEditModalOpen(false)
             setSelectedUser(null)
           }}
           mode="edit"
         />
       )}

       {/* Delete User Modal */}
       {isDeleteModalOpen && selectedUser && (
         <DeleteUserModal
           isOpen={isDeleteModalOpen}
           user={selectedUser}
           onConfirm={handleConfirmDelete}
           onCancel={() => {
             setIsDeleteModalOpen(false)
             setSelectedUser(null)
           }}
         />
       )}
    </div>
  )
}