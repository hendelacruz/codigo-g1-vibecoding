/**
 * Auth API - Funciones para interactuar con el backend de autenticación
 * 
 * Este módulo maneja todas las llamadas a la API relacionadas con autenticación:
 * - Login/Logout
 * - Refresh de tokens
 * - Gestión de perfil de usuario
 * - Cambio de contraseña
 * - Verificación de estado de autenticación
 */

import axios from 'axios'
import type { AxiosResponse } from 'axios'
import { api } from '../../shared/lib/api'
import { AUTH_ENDPOINTS } from './authConstants'
import type { 
  LoginCredentials, 
  LoginResponse, 
  RefreshTokenResponse, 
  User,
  ChangePasswordData,
  AuthStatusResponse 
} from './authTypes'

// Using centralized API configuration
const authAxios = api

/**
 * Auth API - Conjunto de funciones para manejar autenticación
 */
export const authAPI = {
  /**
   * Iniciar sesión con credenciales de usuario
   * @param credentials - Username y password del usuario
   * @returns Promise con tokens de acceso y datos del usuario
   */
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response: AxiosResponse<LoginResponse> = await authAxios.post(
        AUTH_ENDPOINTS.LOGIN, 
        credentials
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       error.response?.data?.message || 
                       'Error de autenticación'
        throw new Error(message)
      }
      throw new Error('Error de conexión')
    }
  },

  /**
   * Cerrar sesión del usuario
   * @param refreshToken - Token de refresh para invalidar
   * @returns Promise void
   */
  logout: async (refreshToken?: string): Promise<void> => {
    try {
      const payload = refreshToken ? { refresh: refreshToken } : {}
      await authAxios.post(AUTH_ENDPOINTS.LOGOUT, payload)
    } catch (error) {
      // El logout puede fallar si el token ya expiró, pero no es crítico
      console.warn('Logout request failed:', error)
    }
  },

  /**
   * Renovar token de acceso usando refresh token
   * @param refreshToken - Token de refresh válido
   * @returns Promise con nuevo token de acceso
   */
  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    try {
      const response: AxiosResponse<RefreshTokenResponse> = await authAxios.post(
        AUTH_ENDPOINTS.REFRESH, 
        { refresh: refreshToken }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       'Token de refresh inválido o expirado'
        throw new Error(message)
      }
      throw new Error('Error al renovar token')
    }
  },

  /**
   * Obtener estado de autenticación actual
   * @param token - Token de acceso para verificar
   * @returns Promise con datos del usuario autenticado
   */
  getAuthStatus: async (token: string): Promise<AuthStatusResponse> => {
    try {
      const response: AxiosResponse<AuthStatusResponse> = await authAxios.get(
        AUTH_ENDPOINTS.STATUS,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       'Token inválido o expirado'
        throw new Error(message)
      }
      throw new Error('Error al verificar estado de autenticación')
    }
  },

  /**
   * Obtener perfil completo del usuario autenticado
   * @param token - Token de acceso
   * @returns Promise con datos completos del usuario
   */
  getProfile: async (token: string): Promise<User> => {
    try {
      const response: AxiosResponse<User> = await authAxios.get(
        AUTH_ENDPOINTS.PROFILE,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       'Error al obtener perfil de usuario'
        throw new Error(message)
      }
      throw new Error('Error de conexión')
    }
  },

  /**
   * Cambiar contraseña del usuario autenticado
   * @param data - Contraseña actual y nueva contraseña
   * @param token - Token de acceso
   * @returns Promise void
   */
  changePassword: async (data: ChangePasswordData, token: string): Promise<void> => {
    try {
      await authAxios.post(
        AUTH_ENDPOINTS.CHANGE_PASSWORD, 
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       error.response?.data?.old_password?.[0] ||
                       error.response?.data?.new_password?.[0] ||
                       'Error al cambiar contraseña'
        throw new Error(message)
      }
      throw new Error('Error de conexión')
    }
  },

  /**
   * Verificar si un token es válido
   * @param token - Token a verificar
   * @returns Promise<boolean> - true si el token es válido
   */
  verifyToken: async (token: string): Promise<boolean> => {
    try {
      await authAxios.post(
        AUTH_ENDPOINTS.VERIFY_TOKEN,
        { token },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      return true
    } catch (_) {
      return false
    }
  },

  /**
   * Obtener información de roles y permisos del usuario
   * @param token - Token de acceso
   * @returns Promise con roles y permisos del usuario
   */
  getUserPermissions: async (token: string): Promise<{ roles: string[], permissions: string[] }> => {
    try {
      const response: AxiosResponse<{ roles: string[], permissions: string[] }> = await authAxios.get(
        AUTH_ENDPOINTS.PERMISSIONS,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 
                       'Error al obtener permisos de usuario'
        throw new Error(message)
      }
      throw new Error('Error de conexión')
    }
  }
}

/**
 * NOTA: Los interceptores de autenticación y manejo de errores 401
 * están configurados en la API centralizada (shared/lib/api.ts).
 * No es necesario configurarlos aquí ya que authAxios usa la misma instancia.
 */

/**
 * Configurar interceptor de autenticación (delegado a API centralizada)
 * @param _getToken - Función para obtener el token (no utilizada, delegada a API centralizada)
 */
export const setupAuthInterceptor = (_getToken: () => string | null): void => {
  // Los interceptores están configurados en shared/lib/api.ts
  console.log('Auth interceptor setup delegated to centralized API')
}

/**
 * Configurar interceptor de respuesta de autenticación (delegado a API centralizada)
 * @param _onUnauthorized - Callback para manejar errores 401 (no utilizado, delegado a API centralizada)
 */
export const setupAuthResponseInterceptor = (_onUnauthorized: () => void): void => {
  // Los interceptores están configurados en shared/lib/api.ts
  console.log('Auth response interceptor setup delegated to centralized API')
}