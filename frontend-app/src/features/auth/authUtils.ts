/**
 * Auth Utilities - Helper functions for authentication and authorization
 */

import type { User, UserRole, RolePermissions, TokenPayload } from './authTypes'

/**
 * Get user role permissions based on role name
 */
export const getRolePermissions = (roleName: string): RolePermissions => {
  const role = roleName.toLowerCase() as UserRole

  const permissions: Record<UserRole, RolePermissions> = {
    admin: {
      canViewInventory: true,
      canEditInventory: true,
      canDeleteInventory: true,
      canViewSales: true,
      canEditSales: true,
      canDeleteSales: true,
      canViewReports: true,
      canManageUsers: true,
    },
    supervisor: {
      canViewInventory: true,
      canEditInventory: true,
      canDeleteInventory: false,
      canViewSales: true,
      canEditSales: true,
      canDeleteSales: false,
      canViewReports: true,
      canManageUsers: false,
    },
    vendedor: {
      canViewInventory: true,
      canEditInventory: false,
      canDeleteInventory: false,
      canViewSales: true,
      canEditSales: true,
      canDeleteSales: false,
      canViewReports: false,
      canManageUsers: false,
    },
    tecnico: {
      canViewInventory: true,
      canEditInventory: true,
      canDeleteInventory: false,
      canViewSales: false,
      canEditSales: false,
      canDeleteSales: false,
      canViewReports: false,
      canManageUsers: false,
    },
  }

  return permissions[role] || permissions.vendedor // Default to vendedor permissions
}

/**
 * Check if user has specific permission
 */
export const hasPermission = (
  user: User | null,
  permission: keyof RolePermissions
): boolean => {
  if (!user || !user.is_active) return false
  
  const permissions = getRolePermissions(user.rol_nombre)
  return permissions[permission]
}

/**
 * Check if user has any of the specified roles
 */
export const hasRole = (user: User | null, roles: UserRole[]): boolean => {
  if (!user || !user.is_active) return false
  
  const userRole = user.rol_nombre.toLowerCase() as UserRole
  return roles.includes(userRole)
}

/**
 * Get user full name
 */
export const getUserFullName = (user: User | null): string => {
  if (!user) return ''
  
  const firstName = user.first_name?.trim() || ''
  const lastName = user.last_name?.trim() || ''
  
  if (firstName && lastName) {
    return `${firstName} ${lastName}`
  }
  
  return firstName || lastName || user.username
}

/**
 * Get user display name (full name or username)
 */
export const getUserDisplayName = (user: User | null): string => {
  if (!user) return ''
  
  const fullName = getUserFullName(user)
  return fullName !== user.username ? fullName : user.username
}

/**
 * Check if token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = decodeToken(token)
    const currentTime = Math.floor(Date.now() / 1000)
    return payload.exp < currentTime
  } catch {
    return true
  }
}

/**
 * Decode JWT token payload
 */
export const decodeToken = (token: string): TokenPayload => {
  try {
    const base64Url = token.split('.')[1]
    if (!base64Url) {
      throw new Error('Invalid token format')
    }
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload) as TokenPayload
  } catch (_) {
    throw new Error('Invalid token format')
  }
}

/**
 * Get token expiration time in milliseconds
 */
export const getTokenExpirationTime = (token: string): number => {
  try {
    const payload = decodeToken(token)
    return payload.exp * 1000 // Convert to milliseconds
  } catch {
    return 0
  }
}

/**
 * Check if user is active and authenticated
 */
export const isUserActive = (user: User | null): boolean => {
  return user !== null && user.is_active
}

/**
 * Format user role for display
 */
export const formatUserRole = (roleName: string): string => {
  const roleMap: Record<string, string> = {
    admin: 'Administrador',
    supervisor: 'Supervisor',
    vendedor: 'Vendedor',
    tecnico: 'Técnico',
  }
  
  return roleMap[roleName.toLowerCase()] || roleName
}

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9]([a-zA-Z0-9._+-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$/
  return emailRegex.test(email) && !email.includes('..')
}

/**
 * Validate DNI format (Argentina)
 */
export const isValidDNI = (dni: string): boolean => {
  const dniRegex = /^\d{7,8}$/
  return dniRegex.test(dni.replace(/\D/g, ''))
}

/**
 * Format DNI for display
 */
export const formatDNI = (dni: string): string => {
  const cleanDNI = dni.replace(/\D/g, '')
  if (cleanDNI.length === 8) {
    return cleanDNI.replace(/(\d{2})(\d{3})(\d{3})/, '$1.$2.$3')
  }
  if (cleanDNI.length === 7) {
    return cleanDNI.replace(/(\d{1})(\d{3})(\d{3})/, '$1.$2.$3')
  }
  return cleanDNI
}