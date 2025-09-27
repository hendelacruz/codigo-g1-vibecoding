/**
 * usePermissionsFixed Hook - Fixed version that handles both singular and plural roles
 * 
 * This hook provides a unified interface for checking user permissions
 * with support for both singular and plural role names to handle backend inconsistencies.
 * 
 * Features:
 * - Role verification with fallback (administrador -> Administradores)
 * - Specific permission verification (auth.add_user, inventory.view_dispositivo, etc.)
 * - Module and action access verification
 * - Compatibility with existing Redux state
 * - Safe fallback when no authenticated user
 */

import { useAppSelector } from '../app/hooks'

// Types for permission system
type Permission = string
type RoleSingular = 'administrador' | 'supervisor' | 'tecnico' | 'operador' | 'admin'
type RolePlural = 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores'
type Role = RoleSingular | RolePlural
type Module = 'users' | 'inventory' | 'services' | 'sales' | 'reports'
type Action = 'create' | 'read' | 'update' | 'delete'

/**
 * Role mapping between singular and plural forms
 */
const ROLE_MAPPING: Record<RoleSingular, RolePlural> = {
  'administrador': 'Administradores',
  'admin': 'Administradores',
  'supervisor': 'Supervisores',
  'tecnico': 'Técnicos',
  'operador': 'Operadores'
}

/**
 * Normalize role name to handle both singular and plural forms
 */
const normalizeRole = (role: Role): RolePlural => {
  // If it's already plural, return as is
  if (['Administradores', 'Supervisores', 'Técnicos', 'Operadores'].includes(role as RolePlural)) {
    return role as RolePlural
  }
  
  // If it's singular, convert to plural
  return ROLE_MAPPING[role as RoleSingular] || role as RolePlural
}

/**
 * Check if user has a specific role, handling both singular and plural forms
 */
const checkUserRole = (userGroups: string[] | undefined, role: Role): boolean => {
  if (!userGroups || userGroups.length === 0) return false
  
  const normalizedRole = normalizeRole(role)
  
  // Check exact match first
  if (userGroups.includes(normalizedRole)) return true
  
  // Check if user has the singular form
  const singularForms = Object.keys(ROLE_MAPPING) as RoleSingular[]
  for (const singular of singularForms) {
    if (ROLE_MAPPING[singular] === normalizedRole && userGroups.includes(singular)) {
      return true
    }
  }
  
  // Check rol_nombre field as fallback
  return false
}

/**
 * Main hook for permission management
 * Integrated with existing Redux authentication state
 */
export function usePermissionsFixed() {
  const { user } = useAppSelector((state) => state.auth)

  /**
   * Check if user has a specific permission
   * @param permission - Permission in Django format (e.g., 'auth.add_user')
   * @returns boolean - true if user has permission
   */
  const hasPermission = (permission: Permission): boolean => {
    if (!user) return false
    
    // Administrators have all permissions
    if (hasRole('administrador') || hasRole('Administradores')) return true
    
    // Check specific user permissions
    return user.user_permissions?.includes(permission) || false
  }

  /**
   * Check if user has a specific role (handles both singular and plural)
   * @param role - User role/group
   * @returns boolean - true if user has role
   */
  const hasRole = (role: Role): boolean => {
    if (!user) return false
    
    // Check groups array
    if (checkUserRole(user.groups, role)) return true
    
    // Fallback: check rol_nombre field
    if (user.rol_nombre) {
      const normalizedRole = normalizeRole(role)
      const normalizedRolNombre = normalizeRole(user.rol_nombre as Role)
      return normalizedRole === normalizedRolNombre
    }
    
    return false
  }

  /**
   * Check if user has any of the specified roles
   * @param roles - Array of roles to check
   * @returns boolean - true if user has at least one role
   */
  const hasAnyRole = (roles: Role[]): boolean => {
    if (!user) return false
    return roles.some(role => hasRole(role))
  }

  /**
   * Check if user can access a module with specific action
   * @param module - System module (users, inventory, etc.)
   * @param action - Action to perform (create, read, update, delete)
   * @returns boolean - true if user can access
   */
  const canAccess = (module: Module, action: Action): boolean => {
    if (!user) return false

    // Permission mapping for modules and actions to Django permissions
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
   * Check if user can perform multiple actions on a module
   * @param module - System module
   * @param actions - Array of actions to check
   * @param requireAll - If true, requires all permissions. If false, requires at least one
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

  // Convenience properties for common roles (using both forms)
  const isAdmin = hasRole('administrador') || hasRole('Administradores')
  const isSupervisor = hasRole('supervisor') || hasRole('Supervisores')
  const isTechnician = hasRole('tecnico') || hasRole('Técnicos')
  const isOperator = hasRole('operador') || hasRole('Operadores')

  // Common access level checks
  const isAdminOrSupervisor = isAdmin || isSupervisor
  const isTechnicianOrAbove = isAdmin || isSupervisor || isTechnician

  // Get user's actual roles for debugging
  const getUserRoles = (): string[] => {
    if (!user) return []
    
    const roles: string[] = []
    
    // Add groups
    if (user.groups) {
      roles.push(...user.groups)
    }
    
    // Add rol_nombre if different
    if (user.rol_nombre && !roles.includes(user.rol_nombre)) {
      roles.push(user.rol_nombre)
    }
    
    return roles
  }

  return {
    // Main functions
    hasPermission,
    hasRole,
    hasAnyRole,
    canAccess,
    canAccessMultiple,
    
    // Convenience properties
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    isAdminOrSupervisor,
    isTechnicianOrAbove,
    
    // User data
    user,
    
    // Authentication state
    isAuthenticated: !!user,
    userRoles: getUserRoles(),
    userPermissions: user?.user_permissions || [],
    
    // Debug helpers
    normalizeRole,
    checkUserRole: (role: Role) => checkUserRole(user?.groups, role),
    rawGroups: user?.groups || [],
    rolNombre: user?.rol_nombre || null
  }
}

/**
 * Quick permissions hook with fixed role handling
 * Useful for components that only need to check specific permissions
 */
export function useQuickPermissionsFixed() {
  const {
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    canAccess,
    hasRole,
    isAuthenticated
  } = usePermissionsFixed()

  return {
    // Quick role checks
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    
    // Quick access checks
    canManageUsers: isAdmin || isSupervisor,
    canViewInventory: canAccess('inventory', 'read'),
    canManageInventory: canAccess('inventory', 'create'),
    canViewReports: canAccess('reports', 'read'),
    canViewSales: canAccess('sales', 'read'),
    
    // Utilities
    hasRole,
    canAccess,
    isAuthenticated
  }
}