/**
 * usePermissions Hook - Sistema de permisos basado en roles y permisos específicos
 * 
 * Este hook proporciona una interfaz unificada para verificar permisos de usuario
 * basado en el sistema de autenticación Django con grupos y permisos específicos.
 * 
 * Características:
 * - Verificación de roles/grupos (Administradores, Supervisores, etc.)
 * - Verificación de permisos específicos (auth.add_user, inventory.view_dispositivo, etc.)
 * - Verificación de acceso por módulo y acción
 * - Compatibilidad con el estado Redux existente
 * - Fallback seguro cuando no hay usuario autenticado
 */

import { useAppSelector } from '../app/hooks'

// Tipos para el sistema de permisos
type Permission = string
type Role = 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores'
type Module = 'users' | 'inventory' | 'services' | 'sales' | 'reports'
type Action = 'create' | 'read' | 'update' | 'delete'

/**
 * Hook principal para manejo de permisos
 * Integrado con el estado Redux de autenticación existente
 */
export function usePermissions() {
  const { user } = useAppSelector((state) => state.auth)

  /**
   * Verifica si el usuario tiene un permiso específico
   * @param permission - Permiso en formato Django (ej: 'auth.add_user')
   * @returns boolean - true si tiene el permiso
   */
  const hasPermission = (permission: Permission): boolean => {
    if (!user) return false
    
    // Los Administradores tienen todos los permisos
    if (user.groups?.includes('Administradores')) return true
    
    // Verificar permisos específicos del usuario
    return user.user_permissions?.includes(permission) || false
  }

  /**
   * Verifica si el usuario tiene un rol específico
   * @param role - Rol/grupo del usuario
   * @returns boolean - true si tiene el rol
   */
  const hasRole = (role: Role): boolean => {
    if (!user) return false
    return user.groups?.includes(role) || false
  }

  /**
   * Verifica si el usuario tiene alguno de los roles especificados
   * @param roles - Array de roles a verificar
   * @returns boolean - true si tiene al menos uno de los roles
   */
  const hasAnyRole = (roles: Role[]): boolean => {
    if (!user) return false
    return roles.some(role => hasRole(role))
  }

  /**
   * Verifica si el usuario puede acceder a un módulo con una acción específica
   * @param module - Módulo del sistema (users, inventory, etc.)
   * @param action - Acción a realizar (create, read, update, delete)
   * @returns boolean - true si puede acceder
   */
  const canAccess = (module: Module, action: Action): boolean => {
    if (!user) return false

    // Mapeo de módulos y acciones a permisos Django
    const permissionMap: Record<Module, Record<Action, Permission>> = {
      users: {
        create: 'auth.add_user',
        read: 'auth.view_user',
        update: 'auth.change_user',
        delete: 'auth.delete_user'
      },
      inventory: {
        create: 'inventory.add_dispositivo',
        read: 'inventory.view_dispositivo',
        update: 'inventory.change_dispositivo',
        delete: 'inventory.delete_dispositivo'
      },
      services: {
        create: 'services.add_servicio',
        read: 'services.view_servicio',
        update: 'services.change_servicio',
        delete: 'services.delete_servicio'
      },
      sales: {
        create: 'sales.add_venta',
        read: 'sales.view_venta',
        update: 'sales.change_venta',
        delete: 'sales.delete_venta'
      },
      reports: {
        create: 'reports.add_report',
        read: 'reports.view_reports',
        update: 'reports.change_report',
        delete: 'reports.delete_report'
      }
    }

    const permission = permissionMap[module]?.[action]
    return permission ? hasPermission(permission) : false
  }

  /**
   * Verifica si el usuario puede realizar múltiples acciones en un módulo
   * @param module - Módulo del sistema
   * @param actions - Array de acciones a verificar
   * @param requireAll - Si true, requiere todos los permisos. Si false, requiere al menos uno
   * @returns boolean
   */
  const canAccessMultiple = (
    module: Module, 
    actions: Action[], 
    requireAll: boolean = false
  ): boolean => {
    if (requireAll) {
      return actions.every(action => canAccess(module, action))
    }
    return actions.some(action => canAccess(module, action))
  }

  // Propiedades de conveniencia para roles comunes
  const isAdmin = hasRole('Administradores')
  const isSupervisor = hasRole('Supervisores')
  const isTechnician = hasRole('Técnicos')
  const isOperator = hasRole('Operadores')

  // Verificaciones de nivel de acceso comunes
  const isAdminOrSupervisor = hasAnyRole(['Administradores', 'Supervisores'])
  const isTechnicianOrAbove = hasAnyRole(['Administradores', 'Supervisores', 'Técnicos'])

  return {
    // Funciones principales
    hasPermission,
    hasRole,
    hasAnyRole,
    canAccess,
    canAccessMultiple,
    
    // Propiedades de conveniencia
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    isAdminOrSupervisor,
    isTechnicianOrAbove,
    
    // Datos del usuario
    user,
    
    // Estado de autenticación
    isAuthenticated: !!user,
    userRoles: user?.groups || [],
    userPermissions: user?.user_permissions || []
  }
}

/**
 * Hook de conveniencia para verificaciones rápidas de permisos
 * Útil para componentes que solo necesitan verificar permisos específicos
 */
export function useQuickPermissions() {
  const permissions = usePermissions()

  return {
    // Permisos de usuarios
    canManageUsers: permissions.canAccess('users', 'create'),
    canViewUsers: permissions.canAccess('users', 'read'),
    canEditUsers: permissions.canAccess('users', 'update'),
    canDeleteUsers: permissions.canAccess('users', 'delete'),

    // Permisos de inventario
    canManageInventory: permissions.canAccess('inventory', 'create'),
    canViewInventory: permissions.canAccess('inventory', 'read'),
    canEditInventory: permissions.canAccess('inventory', 'update'),
    canDeleteInventory: permissions.canAccess('inventory', 'delete'),

    // Permisos de servicios
    canManageServices: permissions.canAccess('services', 'create'),
    canViewServices: permissions.canAccess('services', 'read'),
    canEditServices: permissions.canAccess('services', 'update'),
    canDeleteServices: permissions.canAccess('services', 'delete'),

    // Permisos de ventas
    canManageSales: permissions.canAccess('sales', 'create'),
    canViewSales: permissions.canAccess('sales', 'read'),
    canEditSales: permissions.canAccess('sales', 'update'),
    canDeleteSales: permissions.canAccess('sales', 'delete'),

    // Permisos de reportes
    canViewReports: permissions.canAccess('reports', 'read'),
    canManageReports: permissions.canAccess('reports', 'create'),

    // Roles
    ...permissions
  }
}