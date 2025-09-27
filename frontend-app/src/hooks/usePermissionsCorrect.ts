import { useMemo } from 'react'
import { useAuth } from '../features/auth/hooks/useAuth'

// Extended User type to match backend structure
interface ExtendedUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  dni: string
  rol?: {
    id: number
    nombre: string
    permisos: Record<string, unknown>
  }
  rol_nombre?: string // Fallback field
  groups?: string[]   // Fallback field
  user_permissions?: string[] // Fallback field
  is_staff: boolean
  is_superuser: boolean
  is_active?: boolean
}

// Role mapping from backend format to frontend format
const ROLE_MAPPING: Record<string, string> = {
  // Backend singular -> Frontend plural
  'administrador': 'Administradores',
  'supervisor': 'Supervisores', 
  'tecnico': 'Técnicos',
  'operador': 'Operadores',
  'admin': 'Administradores',
  'tech': 'Técnicos',
  'op': 'Operadores',
  // Already correct formats
  'Administradores': 'Administradores',
  'Supervisores': 'Supervisores',
  'Técnicos': 'Técnicos',
  'Operadores': 'Operadores'
}

// Roles that should have full admin privileges
const ADMIN_ROLES = ['administrador', 'admin', 'Administradores']

// Default permissions for each role when rol.permisos is empty
const DEFAULT_ROLE_PERMISSIONS: Record<string, string[]> = {
  'Administradores': [
    'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
    'inventory.add_dispositivo', 'inventory.change_dispositivo', 'inventory.delete_dispositivo', 'inventory.view_dispositivo',
    'services.add_servicio', 'services.change_servicio', 'services.delete_servicio', 'services.view_servicio',
    'reports.view_report', 'reports.generate_report'
  ],
  'Supervisores': [
    'auth.view_user', 'auth.change_user',
    'inventory.add_dispositivo', 'inventory.change_dispositivo', 'inventory.view_dispositivo',
    'services.add_servicio', 'services.change_servicio', 'services.view_servicio',
    'reports.view_report'
  ],
  'Técnicos': [
    'inventory.view_dispositivo', 'inventory.change_dispositivo',
    'services.view_servicio', 'services.change_servicio'
  ],
  'Operadores': [
    'inventory.view_dispositivo',
    'services.view_servicio'
  ]
}

// Module to permission mapping
const MODULE_PERMISSIONS: Record<string, Record<string, string[]>> = {
  users: {
    read: ['auth.view_user'],
    create: ['auth.add_user'],
    update: ['auth.change_user'],
    delete: ['auth.delete_user']
  },
  inventory: {
    read: ['inventory.view_dispositivo'],
    create: ['inventory.add_dispositivo'],
    update: ['inventory.change_dispositivo'],
    delete: ['inventory.delete_dispositivo']
  },
  services: {
    read: ['services.view_servicio'],
    create: ['services.add_servicio'],
    update: ['services.change_servicio'],
    delete: ['services.delete_servicio']
  },
  reports: {
    read: ['reports.view_report'],
    generate: ['reports.generate_report']
  }
}

/**
 * Normalize role name from backend format to frontend format
 */
const normalizeRole = (role: string): string => {
  return ROLE_MAPPING[role] || role
}

/**
 * Extract user role from the user object
 */
const getUserRole = (user: ExtendedUser | null): string | null => {
  if (!user) return null
  
  // Priority 1: rol.nombre (new backend structure)
  if (user.rol?.nombre) {
    return normalizeRole(user.rol.nombre)
  }
  
  // Priority 2: rol_nombre (fallback)
  if (user.rol_nombre) {
    return normalizeRole(user.rol_nombre)
  }
  
  // Priority 3: groups array (legacy)
  if (user.groups && user.groups.length > 0 && user.groups[0]) {
    return normalizeRole(user.groups[0])
  }
  
  return null
}

/**
 * Extract user permissions from the user object
 */
const getUserPermissions = (user: ExtendedUser | null): string[] => {
  if (!user) return []
  
  const userRole = getUserRole(user)
  
  // Check if user is admin - admins get ALL permissions
  const isAdmin = ADMIN_ROLES.some(adminRole => {
    return userRole === adminRole || 
           user.rol?.nombre === adminRole ||
           user.rol_nombre === adminRole ||
           (user.groups && user.groups.includes(adminRole))
  })
  
  if (isAdmin) {
    // Return ALL possible permissions for administrators
    return [
      // Auth permissions
      'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
      // Inventory permissions
      'inventory.add_dispositivo', 'inventory.change_dispositivo', 'inventory.delete_dispositivo', 'inventory.view_dispositivo',
      // Services permissions
      'services.add_servicio', 'services.change_servicio', 'services.delete_servicio', 'services.view_servicio',
      // Reports permissions
      'reports.view_report', 'reports.generate_report',
      // Additional admin permissions
      'admin.full_access', 'admin.manage_all'
    ]
  }
  
  // Priority 1: rol.permisos (new backend structure)
  if (user.rol?.permisos && Object.keys(user.rol.permisos).length > 0) {
    // Convert permisos object to array of permission strings
    const permisos = user.rol.permisos
    const permissions: string[] = []
    
    Object.entries(permisos).forEach(([module, actions]) => {
      if (typeof actions === 'object' && actions !== null) {
        Object.entries(actions).forEach(([action, hasPermission]) => {
          if (hasPermission) {
            permissions.push(`${module}.${action}`)
          }
        })
      }
    })
    
    return permissions
  }
  
  // Priority 2: Default permissions based on role
  if (userRole && DEFAULT_ROLE_PERMISSIONS[userRole]) {
    return DEFAULT_ROLE_PERMISSIONS[userRole]
  }
  
  // Priority 3: user_permissions (legacy)
  if (user.user_permissions && user.user_permissions.length > 0) {
    return user.user_permissions
  }
  
  return []
}

/**
 * Check if user has a specific role
 */
const checkUserRole = (user: ExtendedUser | null, targetRole: string): boolean => {
  const userRole = getUserRole(user)
  if (!userRole) return false
  
  const normalizedTarget = normalizeRole(targetRole)
  return userRole === normalizedTarget
}

/**
 * Enhanced permissions hook that handles the real backend structure
 */
export const usePermissionsCorrect = () => {
  const { user: authUser, isAuthenticated } = useAuth()
  const user = authUser as ExtendedUser | null

  const userRole = useMemo(() => getUserRole(user), [user])
  const userPermissions = useMemo(() => getUserPermissions(user), [user])

  const hasPermission = useMemo(() => (permission: string): boolean => {
    if (!isAuthenticated || !user) return false
    
    // Superuser has all permissions
    if (user.is_superuser) return true
    
    return userPermissions.includes(permission)
  }, [isAuthenticated, user, userPermissions])

  const hasRole = useMemo(() => (role: string): boolean => {
    return checkUserRole(user, role)
  }, [user])

  const hasAnyRole = useMemo(() => (roles: string[]): boolean => {
    return roles.some(role => hasRole(role))
  }, [hasRole])

  const canAccess = useMemo(() => (module: string, action: string): boolean => {
    if (!isAuthenticated || !user) return false
    
    // Superuser has all access
    if (user.is_superuser) return true
    
    const modulePerms = MODULE_PERMISSIONS[module]
    if (!modulePerms || !modulePerms[action]) return false
    
    return modulePerms[action].some(permission => hasPermission(permission))
  }, [isAuthenticated, user, hasPermission])

  const canAccessMultiple = useMemo(() => (checks: Array<{ module: string; action: string }>): boolean => {
    return checks.every(({ module, action }) => canAccess(module, action))
  }, [canAccess])

  // Convenience role checks
  const isAdmin = useMemo(() => hasRole('Administradores'), [hasRole])
  const isSupervisor = useMemo(() => hasRole('Supervisores'), [hasRole])
  const isTechnician = useMemo(() => hasRole('Técnicos'), [hasRole])
  const isOperator = useMemo(() => hasRole('Operadores'), [hasRole])

  // Combined role checks
  const isAdminOrSupervisor = useMemo(() => isAdmin || isSupervisor, [isAdmin, isSupervisor])
  const isTechnicianOrAbove = useMemo(() => isAdmin || isSupervisor || isTechnician, [isAdmin, isSupervisor, isTechnician])

  // Convenience permission checks for common actions
  const canViewUsers = useMemo(() => canAccess('users', 'read'), [canAccess])
  const canCreateUsers = useMemo(() => canAccess('users', 'create'), [canAccess])
  const canEditUsers = useMemo(() => canAccess('users', 'update'), [canAccess])
  const canDeleteUsers = useMemo(() => canAccess('users', 'delete'), [canAccess])

  return {
    // Core functions
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
    
    // Convenience permission checks
    canViewUsers,
    canCreateUsers,
    canEditUsers,
    canDeleteUsers,
    
    // User data
    user,
    isAuthenticated,
    userRole,
    userPermissions,
    
    // Debug helpers
    getUserRole: () => getUserRole(user),
    getUserPermissions: () => getUserPermissions(user),
    normalizeRole: (role: string) => normalizeRole(role)
  }
}

/**
 * Quick permissions hook for common use cases
 */
export const useQuickPermissionsCorrect = () => {
  const {
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    isAdminOrSupervisor,
    isTechnicianOrAbove,
    canAccess,
    isAuthenticated
  } = usePermissionsCorrect()

  return {
    isAdmin,
    isSupervisor,
    isTechnician,
    isOperator,
    isAdminOrSupervisor,
    isTechnicianOrAbove,
    canAccess,
    isAuthenticated
  }
}