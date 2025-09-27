/**
 * useAuthWithPermissions Hook - Integrated authentication and permissions hook
 * 
 * This hook combines the functionality of useAuthOptimized and usePermissions
 * to provide a complete authentication and authorization solution in a single hook.
 * 
 * Features:
 * - Complete authentication state and actions
 * - Full permissions and role checking capabilities
 * - Optimized performance with memoization
 * - Type-safe interface
 * - Convenient utility functions
 * 
 * @author Frontend Team
 * @version 1.0.0
 */

import { useMemo, useCallback } from 'react'
import { useAuthOptimized } from './useAuthOptimized'
import { usePermissionsCorrect } from './usePermissionsCorrect'
import type { User, LoginCredentials, ChangePasswordData } from '../features/auth/authTypes'

// Types for permissions and roles
type Permission = string
type Role = 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores'
type Module = 'users' | 'inventory' | 'services' | 'sales' | 'reports'
type Action = 'create' | 'read' | 'update' | 'delete'

/**
 * Combined authentication and permissions interface
 */
interface UseAuthWithPermissionsReturn {
  // Authentication state
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  token: string | null
  refreshToken: string | null
  
  // Computed user data
  userDisplayName: string
  userRole: string | null
  hasValidToken: boolean
  
  // Authentication actions
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshAuth: () => Promise<void>
  checkStatus: () => Promise<void>
  getProfile: () => Promise<void>
  changePassword: (data: ChangePasswordData) => Promise<void>
  verifyToken: () => Promise<void>
  clearError: () => void
  
  // Permission checking functions
  hasPermission: (permission: Permission) => boolean
  hasRole: (role: Role) => boolean
  hasAnyRole: (roles: Role[]) => boolean
  canAccess: (module: Module, action: Action) => boolean
  canAccessMultiple: (module: Module, actions: Action[], requireAll?: boolean) => boolean
  
  // Role convenience properties
  isAdmin: boolean
  isSupervisor: boolean
  isTechnician: boolean
  isOperator: boolean
  isAdminOrSupervisor: boolean
  isTechnicianOrAbove: boolean
  
  // User data arrays
  userRoles: string[]
  userPermissions: string[]
  
  // Utility functions
  canManageUsers: boolean
  canViewInventory: boolean
  canEditInventory: boolean
  canDeleteInventory: boolean
  canViewSales: boolean
  canEditSales: boolean
  canViewReports: boolean
  
  // Advanced utility functions
  checkMultiplePermissions: (permissions: Permission[], requireAll?: boolean) => boolean
  getAccessLevel: (module: Module) => {
    canCreate: boolean
    canRead: boolean
    canUpdate: boolean
    canDelete: boolean
  }
  getUserSummary: () => {
    displayName: string
    role: string | null
    permissions: string[]
    accessLevel: 'admin' | 'supervisor' | 'technician' | 'operator' | 'none'
  }
}

/**
 * Integrated authentication and permissions hook
 * 
 * Combines useAuthOptimized and usePermissions for complete auth/authz functionality
 * 
 * @returns {UseAuthWithPermissionsReturn} Complete authentication and permissions interface
 * 
 * @example
 * ```tsx
 * const {
 *   user,
 *   isAuthenticated,
 *   login,
 *   logout,
 *   hasPermission,
 *   canAccess,
 *   isAdmin,
 *   canManageUsers,
 *   getUserSummary
 * } = useAuthWithPermissions()
 * 
 * // Check authentication
 * if (!isAuthenticated) {
 *   return <LoginForm onLogin={login} />
 * }
 * 
 * // Check permissions
 * if (!canAccess('users', 'read')) {
 *   return <AccessDenied />
 * }
 * 
 * // Get user summary
 * const summary = getUserSummary()
 * console.log(`User: ${summary.displayName}, Level: ${summary.accessLevel}`)
 * ```
 */
export const useAuthWithPermissions = (): UseAuthWithPermissionsReturn => {
  // Get authentication state and actions
  const auth = useAuthOptimized()
  
  // Get permissions state and functions
  const permissions = usePermissionsCorrect()

  // Advanced utility function to check multiple permissions
  const checkMultiplePermissions = useCallback((
    permissionList: Permission[], 
    requireAll: boolean = false
  ): boolean => {
    if (!auth.user) return false
    
    if (requireAll) {
      return permissionList.every(permission => permissions.hasPermission(permission))
    }
    return permissionList.some(permission => permissions.hasPermission(permission))
  }, [auth.user, permissions])

  // Get access level for a specific module
  const getAccessLevel = useCallback((module: Module) => ({
    canCreate: permissions.canAccess(module, 'create'),
    canRead: permissions.canAccess(module, 'read'),
    canUpdate: permissions.canAccess(module, 'update'),
    canDelete: permissions.canAccess(module, 'delete')
  }), [permissions])

  // Get comprehensive user summary
  const getUserSummary = useCallback(() => {
    const accessLevel = permissions.isAdmin ? 'admin' :
                       permissions.isSupervisor ? 'supervisor' :
                       permissions.isTechnician ? 'technician' :
                       permissions.isOperator ? 'operator' : 'none'

    return {
      displayName: auth.userDisplayName,
      role: auth.userRole,
      permissions: permissions.userPermissions,
      accessLevel: accessLevel as 'admin' | 'supervisor' | 'technician' | 'operator' | 'none'
    }
  }, [
    auth.userDisplayName, 
    auth.userRole, 
    permissions.userPermissions,
    permissions.isAdmin,
    permissions.isSupervisor,
    permissions.isTechnician,
    permissions.isOperator
  ])

  // Quick permission checks for common operations
  const quickPermissions = useMemo(() => ({
    canManageUsers: permissions.canAccess('users', 'create'),
    canViewInventory: permissions.canAccess('inventory', 'read'),
    canEditInventory: permissions.canAccess('inventory', 'update'),
    canDeleteInventory: permissions.canAccess('inventory', 'delete'),
    canViewSales: permissions.canAccess('sales', 'read'),
    canEditSales: permissions.canAccess('sales', 'update'),
    canViewReports: permissions.canAccess('reports', 'read')
  }), [permissions])

  // Return combined interface
  return {
    // Authentication state
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    error: auth.error,
    token: auth.token,
    refreshToken: auth.refreshToken,
    
    // Computed user data
    userDisplayName: auth.userDisplayName,
    userRole: auth.userRole,
    hasValidToken: auth.hasValidToken,
    
    // Authentication actions
    login: auth.login,
    logout: auth.logout,
    refreshAuth: auth.refreshAuth,
    checkStatus: auth.checkStatus,
    getProfile: auth.getProfile,
    changePassword: auth.changePassword,
    verifyToken: auth.verifyToken,
    clearError: auth.clearError,
    
    // Permission checking functions
    hasPermission: permissions.hasPermission,
    hasRole: permissions.hasRole,
    hasAnyRole: permissions.hasAnyRole,
    canAccess: permissions.canAccess,
    canAccessMultiple: useCallback((module: Module, actions: Action[], requireAll: boolean = false): boolean => {
      if (requireAll) {
        return actions.every(action => permissions.canAccess(module, action))
      } else {
        return actions.some(action => permissions.canAccess(module, action))
      }
    }, [permissions]),
    
    // Role convenience properties
    isAdmin: permissions.isAdmin,
    isSupervisor: permissions.isSupervisor,
    isTechnician: permissions.isTechnician,
    isOperator: permissions.isOperator,
    isAdminOrSupervisor: permissions.isAdminOrSupervisor,
    isTechnicianOrAbove: permissions.isTechnicianOrAbove,
    
    // User data arrays
    userRoles: permissions.userRole ? [permissions.userRole] : [],
    userPermissions: permissions.userPermissions,
    
    // Quick permission checks
    ...quickPermissions,
    
    // Advanced utility functions
    checkMultiplePermissions,
    getAccessLevel,
    getUserSummary
  }
}

/**
 * Lightweight version for components that only need basic auth + permission checks
 * Optimized for minimal re-renders
 */
export const useAuthWithPermissionsLite = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    userDisplayName,
    userRole,
    hasValidToken,
    hasPermission,
    hasRole,
    canAccess,
    isAdmin,
    isSupervisor,
    isAdminOrSupervisor,
    canManageUsers,
    canViewInventory,
    canViewSales,
    canViewReports
  } = useAuthWithPermissions()

  return {
    user,
    isAuthenticated,
    isLoading,
    userDisplayName,
    userRole,
    hasValidToken,
    hasPermission,
    hasRole,
    canAccess,
    isAdmin,
    isSupervisor,
    isAdminOrSupervisor,
    canManageUsers,
    canViewInventory,
    canViewSales,
    canViewReports
  }
}

export default useAuthWithPermissions