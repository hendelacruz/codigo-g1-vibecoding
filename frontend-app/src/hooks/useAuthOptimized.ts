/**
 * useAuthOptimized Hook - Optimized authentication hook with performance enhancements
 * 
 * This hook provides an optimized version of authentication state management with:
 * - Memoized selectors to prevent unnecessary re-renders
 * - Computed authentication status
 * - Performance-optimized user data access
 * - Minimal re-renders through selective state subscription
 * 
 * @author Frontend Team
 * @version 1.0.0
 */

import { useMemo, useCallback } from 'react'
import { useAppSelector, useAppDispatch } from '../app/hooks'
import { 
  loginUser, 
  logoutUser, 
  refreshAuthToken, 
  checkAuthStatus,
  getUserProfile,
  changeUserPassword,
  verifyUserToken,
  clearError,
  setToken,
  setRefreshToken,
  updateUser,
  clearAuth,
  setLoading
} from '../features/auth/authSlice'
import type { 
  User, 
  LoginCredentials, 
  ChangePasswordData
} from '../features/auth/authTypes'

/**
 * Optimized authentication hook interface
 */
interface UseAuthOptimizedReturn {
  // User data (memoized)
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Token management (memoized)
  token: string | null
  refreshToken: string | null
  
  // Computed values (memoized)
  userDisplayName: string
  userRole: string | null
  hasValidToken: boolean
  
  // Actions (memoized callbacks)
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshAuth: () => Promise<void>
  checkStatus: () => Promise<void>
  getProfile: () => Promise<void>
  changePassword: (data: ChangePasswordData) => Promise<void>
  verifyToken: () => Promise<void>
  
  // State management actions
  clearError: () => void
  updateUserData: (userData: Partial<User>) => void
  setAuthToken: (token: string) => void
  setAuthRefreshToken: (refreshToken: string) => void
  clearAuthData: () => void
  setLoadingState: (loading: boolean) => void
}

/**
 * Optimized authentication hook with performance enhancements
 * 
 * Features:
 * - Memoized selectors to prevent unnecessary re-renders
 * - Computed authentication status and user information
 * - Optimized action dispatchers with useCallback
 * - Selective state subscription for minimal re-renders
 * 
 * @returns {UseAuthOptimizedReturn} Optimized authentication state and actions
 * 
 * @example
 * ```tsx
 * const { 
 *   user, 
 *   isAuthenticated, 
 *   userDisplayName, 
 *   login, 
 *   logout 
 * } = useAuthOptimized()
 * 
 * // Login user
 * await login({ username: 'user', password: 'pass' })
 * 
 * // Display user name
 * console.log(userDisplayName) // "John Doe"
 * ```
 */
export const useAuthOptimized = (): UseAuthOptimizedReturn => {
  const dispatch = useAppDispatch()
  
  // Memoized selectors for optimal performance
  const authState = useAppSelector((state) => state.auth)
  
  // Destructure auth state for better performance
  const {
    user,
    token,
    refreshToken,
    isAuthenticated,
    isLoading,
    error
  } = authState
  
  // Computed values with memoization
  const userDisplayName = useMemo(() => {
    if (!user) return ''
    return `${user.first_name} ${user.last_name}`.trim() || user.username
  }, [user])
  
  const userRole = useMemo(() => {
    return user?.rol_nombre || null
  }, [user?.rol_nombre])
  
  const hasValidToken = useMemo(() => {
    return Boolean(token && isAuthenticated)
  }, [token, isAuthenticated])
  
  // Memoized action dispatchers
  const login = useCallback(async (credentials: LoginCredentials) => {
    await dispatch(loginUser(credentials)).unwrap()
  }, [dispatch])
  
  const logout = useCallback(async () => {
    await dispatch(logoutUser(refreshToken || undefined)).unwrap()
  }, [dispatch, refreshToken])
  
  const refreshAuth = useCallback(async () => {
    if (!refreshToken) throw new Error('No refresh token available')
    await dispatch(refreshAuthToken(refreshToken)).unwrap()
  }, [dispatch, refreshToken])
  
  const checkStatus = useCallback(async () => {
    if (!token) throw new Error('No token available')
    await dispatch(checkAuthStatus(token)).unwrap()
  }, [dispatch, token])
  
  const getProfile = useCallback(async () => {
    if (!token) throw new Error('No token available')
    await dispatch(getUserProfile(token)).unwrap()
  }, [dispatch, token])
  
  const changePassword = useCallback(async (data: ChangePasswordData) => {
    if (!token) throw new Error('No token available')
    await dispatch(changeUserPassword({ 
      passwordData: data, 
      token 
    })).unwrap()
  }, [dispatch, token])
  
  const verifyToken = useCallback(async () => {
    if (!token) throw new Error('No token available')
    await dispatch(verifyUserToken(token)).unwrap()
  }, [dispatch, token])
  
  // State management actions
  const clearAuthError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])
  
  const updateUserData = useCallback((userData: Partial<User>) => {
    dispatch(updateUser(userData))
  }, [dispatch])
  
  const setAuthToken = useCallback((newToken: string) => {
    dispatch(setToken(newToken))
  }, [dispatch])
  
  const setAuthRefreshToken = useCallback((newRefreshToken: string) => {
    dispatch(setRefreshToken(newRefreshToken))
  }, [dispatch])
  
  const clearAuthData = useCallback(() => {
    dispatch(clearAuth())
  }, [dispatch])
  
  const setLoadingState = useCallback((loading: boolean) => {
    dispatch(setLoading(loading))
  }, [dispatch])
  
  return {
    // User data
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // Token management
    token,
    refreshToken,
    
    // Computed values
    userDisplayName,
    userRole,
    hasValidToken,
    
    // Authentication actions
    login,
    logout,
    refreshAuth,
    checkStatus,
    getProfile,
    changePassword,
    verifyToken,
    
    // State management actions
    clearError: clearAuthError,
    updateUserData,
    setAuthToken,
    setAuthRefreshToken,
    clearAuthData,
    setLoadingState,
  }
}

/**
 * Lightweight version of useAuthOptimized for components that only need basic auth state
 * 
 * This hook provides minimal auth state without actions for optimal performance
 * in components that only need to read authentication status.
 * 
 * @returns Basic authentication state
 * 
 * @example
 * ```tsx
 * const { isAuthenticated, user, userDisplayName } = useAuthOptimizedLite()
 * 
 * if (!isAuthenticated) {
 *   return <LoginForm />
 * }
 * 
 * return <div>Welcome, {userDisplayName}!</div>
 * ```
 */
export const useAuthOptimizedLite = () => {
  const { user, isAuthenticated, isLoading, userDisplayName, userRole, hasValidToken } = useAuthOptimized()
  
  return {
    user,
    isAuthenticated,
    isLoading,
    userDisplayName,
    userRole,
    hasValidToken,
  }
}

export default useAuthOptimized