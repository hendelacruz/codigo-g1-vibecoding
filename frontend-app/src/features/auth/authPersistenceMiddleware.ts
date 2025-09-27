import type { Middleware } from '@reduxjs/toolkit'
import type { RootState } from '../../app/store'
import type { AnyAction } from '@reduxjs/toolkit'

/**
 * Middleware to automatically persist authentication tokens to localStorage
 * This ensures tokens are available across browser sessions and page reloads
 */
export const authPersistenceMiddleware: Middleware<object, RootState> = (store) => (next) => (action: unknown) => {
  // Execute the action first
  const result = next(action)
  
  // Get the updated state
  const state = store.getState()
  const { auth } = state
  
  // Sync tokens with localStorage after any auth state change
  if (typeof action === 'object' && action !== null && 'type' in action && 
      typeof (action as AnyAction).type === 'string' && 
      (action as AnyAction).type.startsWith('auth/')) {
    try {
      if (auth.token) {
        localStorage.setItem('authToken', auth.token)
        console.log('🔄 Token synced to localStorage')
      } else {
        localStorage.removeItem('authToken')
        console.log('🗑️ Token removed from localStorage')
      }
      
      if (auth.refreshToken) {
        localStorage.setItem('refreshToken', auth.refreshToken)
        console.log('🔄 Refresh token synced to localStorage')
      } else {
        localStorage.removeItem('refreshToken')
        console.log('🗑️ Refresh token removed from localStorage')
      }
      
      // Store user data for quick access
      if (auth.user) {
        localStorage.setItem('userData', JSON.stringify(auth.user))
        console.log('🔄 User data synced to localStorage')
      } else {
        localStorage.removeItem('userData')
        console.log('🗑️ User data removed from localStorage')
      }
      
      // Store authentication status
      localStorage.setItem('isAuthenticated', auth.isAuthenticated.toString())
      
    } catch (error) {
      console.error('❌ Error syncing auth state to localStorage:', error)
    }
  }
  
  return result
}

/**
 * Load initial auth state from localStorage
 * This should be called when initializing the store
 */
export const loadAuthFromStorage = () => {
  try {
    const token = localStorage.getItem('authToken')
    const refreshToken = localStorage.getItem('refreshToken')
    const userData = localStorage.getItem('userData')
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
    
    if (token && refreshToken && userData && isAuthenticated) {
      return {
        token,
        refreshToken,
        user: JSON.parse(userData),
        isAuthenticated,
        isLoading: false,
        error: null
      }
    }
  } catch (error) {
    console.error('❌ Error loading auth state from localStorage:', error)
    // Clear corrupted data
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userData')
    localStorage.removeItem('isAuthenticated')
  }
  
  return null
}

/**
 * Clear all auth data from localStorage
 * Useful for logout or when tokens are invalid
 */
export const clearAuthFromStorage = () => {
  try {
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userData')
    localStorage.removeItem('isAuthenticated')
    console.log('🗑️ All auth data cleared from localStorage')
  } catch (error) {
    console.error('❌ Error clearing auth data from localStorage:', error)
  }
}

/**
 * Check if stored tokens are still valid (not expired)
 * Returns true if tokens exist and are not expired
 */
export const validateStoredTokens = (): boolean => {
  try {
    const token = localStorage.getItem('authToken')
    
    if (!token) {
      return false
    }
    
    // Decode JWT token to check expiry
    const tokenParts = token.split('.')
    if (tokenParts.length !== 3 || !tokenParts[1]) {
      return false
    }
    const payload = JSON.parse(atob(tokenParts[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    
    // Check if token is expired (with 5 minute buffer)
    if (payload.exp && payload.exp < currentTime + 300) {
      console.warn('⚠️ Stored token is expired or expiring soon')
      return false
    }
    
    return true
  } catch (error) {
    console.error('❌ Error validating stored tokens:', error)
    return false
  }
}