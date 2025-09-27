import axios, { AxiosError } from 'axios'
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { store } from '../../app/store'
import type { AppDispatch } from '../../app/store'
import { refreshAuthToken, clearAuth } from '../../features/auth/authSlice'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Extend the AxiosRequestConfig to include metadata
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  metadata?: { startTime: number }
  _retry?: boolean
  _retryCount?: number
}

// Request deduplication cache
const pendingRequests = new Map<string, Promise<AxiosResponse>>()

// Create request key for deduplication
const createRequestKey = (config: InternalAxiosRequestConfig): string => {
  const { method, url, params, data } = config
  return `${method?.toUpperCase()}-${url}-${JSON.stringify(params)}-${JSON.stringify(data)}`
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout for better UX
  headers: {
    'Content-Type': 'application/json',
  },
  // Enable request/response compression
  decompress: true,
})

// Request interceptor with deduplication and performance optimizations
api.interceptors.request.use(
  (config: ExtendedAxiosRequestConfig) => {
    const state = store.getState()
    const token = state.auth.token
    
    // Add authorization header if token exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request timestamp for performance monitoring
    config.metadata = { startTime: Date.now() }
    
    // Request deduplication for GET requests
    if (config.method?.toLowerCase() === 'get') {
      const requestKey = createRequestKey(config)
      const pendingRequest = pendingRequests.get(requestKey)
      
      if (pendingRequest) {
        // Return existing pending request
        return pendingRequest.then(() => config)
      }
    }
    
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// Utility function for exponential backoff delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Enhanced response interceptor with better error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Performance monitoring
    const config = response.config as ExtendedAxiosRequestConfig
    if (config.metadata?.startTime) {
      const duration = Date.now() - config.metadata.startTime
      if (duration > 3000) {
        console.warn(`⚠️ Slow API request detected: ${config.url} took ${duration}ms`)
      }
    }
    
    // Clean up request deduplication cache for GET requests
    if (config.method?.toLowerCase() === 'get') {
      const requestKey = createRequestKey(config)
      pendingRequests.delete(requestKey)
    }
    
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig

    // Clean up request deduplication cache on error
    if (originalRequest && originalRequest.method?.toLowerCase() === 'get') {
      const requestKey = createRequestKey(originalRequest)
      pendingRequests.delete(requestKey)
    }

    // Enhanced rate limiting handling (429 errors)
    if (error.response?.status === 429 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1
      
      // Maximum 3 retries with exponential backoff
      if (originalRequest._retryCount <= 3) {
        const retryAfter = error.response.headers['retry-after']
        const backoffDelay = retryAfter 
          ? parseInt(retryAfter) * 1000 
          : Math.min(1000 * Math.pow(2, originalRequest._retryCount), 10000)
        
        console.log(`🔄 Rate limited, retrying in ${backoffDelay}ms (attempt ${originalRequest._retryCount}/3)`)
        
        await delay(backoffDelay)
        return api(originalRequest)
      } else {
        console.error('❌ Rate limit exceeded after 3 retries')
        return Promise.reject(new Error('Rate limit exceeded. Please try again later.'))
      }
    }

    // Enhanced 401 handling with better logging and error recovery
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      
      const state = store.getState()
      const refreshToken = state.auth.refreshToken
      
      console.log('🔐 401 Unauthorized detected:', {
        url: originalRequest.url,
        method: originalRequest.method,
        hasRefreshToken: !!refreshToken,
        isAuthenticated: state.auth.isAuthenticated,
        hasToken: !!state.auth.token
      })
      
      if (refreshToken && state.auth.isAuthenticated) {
        try {
          console.log('🔄 Attempting token refresh...')
          // Properly typed dispatch call
          const resultAction = await (store.dispatch as AppDispatch)(refreshAuthToken(refreshToken))
          
          if (refreshAuthToken.fulfilled.match(resultAction)) {
            const newToken = resultAction.payload
            console.log('✅ Token refresh successful, retrying original request')
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          } else {
            console.error('❌ Token refresh failed:', resultAction.payload)
            store.dispatch(clearAuth())
            
            // Only redirect if not already on login page
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login'
            }
            return Promise.reject(error)
          }
        } catch (refreshError) {
          console.error('❌ Token refresh error:', refreshError)
          store.dispatch(clearAuth())
          
          // Only redirect if not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login'
          }
          return Promise.reject(error)
        }
      } else {
        console.log('🚫 No refresh token available or user not authenticated, clearing auth')
        store.dispatch(clearAuth())
        
        // Only redirect if not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    }

    // Enhanced error logging for debugging
    if (error.response) {
      console.error('🚨 API Error Response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        url: originalRequest?.url,
        method: originalRequest?.method,
        data: error.response.data,
        headers: error.response.headers
      })
    } else if (error.request) {
      console.error('🚨 API Network Error:', {
        url: originalRequest?.url,
        method: originalRequest?.method,
        message: error.message,
        code: error.code
      })
    } else {
      console.error('🚨 API Setup Error:', error.message)
    }

    return Promise.reject(error)
  }
)

// Export API instance and utilities
export default api

// Utility function to clear request cache (useful for testing or manual cache clearing)
export const clearRequestCache = () => {
  pendingRequests.clear()
}

// Utility function to get cache size (for monitoring)
export const getRequestCacheSize = () => {
  return pendingRequests.size
}