/**
 * Auth Constants - Configuration values and constants for authentication
 */

import type { UserRole } from './authTypes'

// API Endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: '/api/auth/login/',
  LOGOUT: '/api/auth/logout/',
  REFRESH: '/api/auth/token/refresh/',
  STATUS: '/api/auth/auth/status/',
  PROFILE: '/api/auth/profile/',
  CHANGE_PASSWORD: '/api/auth/change-password/',
  USERS: '/api/auth/users/',
  ROLES: '/api/auth/roles/',
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  REMEMBER_ME: 'remember_me',
} as const

// User Roles
export const USER_ROLES: Record<string, UserRole> = {
  ADMIN: 'admin',
  SUPERVISOR: 'supervisor',
  VENDEDOR: 'vendedor',
  TECNICO: 'tecnico',
} as const

// Role Display Names
export const ROLE_DISPLAY_NAMES: Record<UserRole, string> = {
  admin: 'Administrador',
  supervisor: 'Supervisor',
  vendedor: 'Vendedor',
  tecnico: 'Técnico',
} as const

// Auth Error Messages
export const AUTH_ERROR_MESSAGES = {
  INVALID_CREDENTIALS: 'Credenciales inválidas',
  TOKEN_EXPIRED: 'Sesión expirada',
  UNAUTHORIZED: 'No autorizado',
  FORBIDDEN: 'Acceso denegado',
  NETWORK_ERROR: 'Error de conexión',
  UNKNOWN_ERROR: 'Error desconocido',
  USER_INACTIVE: 'Usuario inactivo',
  INVALID_TOKEN: 'Token inválido',
} as const

// Validation Rules
export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 150,
    PATTERN: /^[a-zA-Z0-9._-]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBERS: true,
    REQUIRE_SPECIAL_CHARS: false,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  DNI: {
    PATTERN: /^\d{7,8}$/,
    MIN_LENGTH: 7,
    MAX_LENGTH: 8,
  },
} as const

// Token Configuration
export const TOKEN_CONFIG = {
  REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes before expiry
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const

// Session Configuration
export const SESSION_CONFIG = {
  IDLE_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  WARNING_TIMEOUT: 5 * 60 * 1000, // 5 minutes before idle timeout
  CHECK_INTERVAL: 60 * 1000, // Check every minute
} as const

// Form Field Names
export const FORM_FIELDS = {
  USERNAME: 'username',
  PASSWORD: 'password',
  OLD_PASSWORD: 'old_password',
  NEW_PASSWORD: 'new_password',
  CONFIRM_PASSWORD: 'confirm_password',
  REMEMBER_ME: 'remember_me',
} as const

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const

// Redux Action Types (for reference)
export const AUTH_ACTION_TYPES = {
  LOGIN_REQUEST: 'auth/login/pending',
  LOGIN_SUCCESS: 'auth/login/fulfilled',
  LOGIN_FAILURE: 'auth/login/rejected',
  LOGOUT: 'auth/logout',
  REFRESH_TOKEN: 'auth/refreshToken',
  CHECK_STATUS: 'auth/checkStatus',
  CLEAR_ERROR: 'auth/clearError',
  SET_TOKEN: 'auth/setToken',
  CLEAR_AUTH: 'auth/clearAuth',
} as const

// Permission Keys
export const PERMISSIONS = {
  VIEW_INVENTORY: 'canViewInventory',
  EDIT_INVENTORY: 'canEditInventory',
  DELETE_INVENTORY: 'canDeleteInventory',
  VIEW_SALES: 'canViewSales',
  EDIT_SALES: 'canEditSales',
  DELETE_SALES: 'canDeleteSales',
  VIEW_REPORTS: 'canViewReports',
  MANAGE_USERS: 'canManageUsers',
} as const

// Route Paths
export const AUTH_ROUTES = {
  LOGIN: '/login',
  LOGOUT: '/logout',
  DASHBOARD: '/dashboard',
  PROFILE: '/profile',
  CHANGE_PASSWORD: '/change-password',
} as const