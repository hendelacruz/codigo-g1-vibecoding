/**
 * Auth Types - Complete TypeScript definitions for authentication system
 * Implements JWT authentication with user management and role-based access
 */

export interface User {
  // Campos heredados de Django User
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  password?: string  // Solo para creación/actualización, no se devuelve en consultas
  is_staff: boolean
  is_active: boolean
  is_superuser: boolean
  date_joined: string  // ISO string format
  last_login?: string | null  // ISO string format, puede ser null
  
  // Campos personalizados (si los tienes)
  dni?: string
  celular?: string  // Número de celular peruano
  licencia?: string  // Licencia de conducir (formato A12345678)
  rol_nombre?: string
  
  // Campos para sistema de permisos basado en Django
  groups?: string[]  // Grupos/roles del usuario (ej: ['Administradores', 'Supervisores'])
  user_permissions?: string[]  // Permisos específicos del usuario (ej: ['auth.add_user', 'inventory.view_dispositivo'])
}

export interface CreateUserData {
  username: string
  email: string
  first_name: string
  last_name: string
  dni: string
  celular: string
  password: string
  password_confirm: string
  rol: number
  licencia?: string
  is_active: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

// Backend response type (different from frontend User interface)
export interface BackendLoginResponse {
  access: string
  refresh: string
  user: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    dni: string
    rol?: {
      id: number
      nombre: string
      permisos: Record<string, any>
    }
    is_staff?: boolean
    is_superuser?: boolean
    is_active?: boolean
    groups?: string[]
    user_permissions?: string[]
  }
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface RefreshTokenResponse {
  access: string
}

export interface ChangePasswordData {
  old_password: string
  new_password: string
}

export interface AuthStatusResponse {
  user: User
}

// API Error types
export interface AuthError {
  message: string
  field?: string
  code?: string
}

export interface ValidationError {
  [key: string]: string[]
}

// Form validation types
export interface LoginFormData {
  username: string
  password: string
}

export interface ChangePasswordFormData {
  old_password: string
  new_password: string
  confirm_password: string
}

// Role-based access types
export type UserRole = 'admin' | 'vendedor' | 'tecnico' | 'supervisor'

export interface RolePermissions {
  canViewInventory: boolean
  canEditInventory: boolean
  canDeleteInventory: boolean
  canViewSales: boolean
  canEditSales: boolean
  canDeleteSales: boolean
  canViewReports: boolean
  canManageUsers: boolean
}

// Auth context types
export interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  clearError: () => void
  checkAuthStatus: () => Promise<void>
}

// Protected route types
export interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: UserRole
  fallback?: React.ReactNode
}

// Token payload types (for JWT decoding)
export interface TokenPayload {
  user_id: number
  username: string
  exp: number
  iat: number
  jti: string
  token_type: string
}