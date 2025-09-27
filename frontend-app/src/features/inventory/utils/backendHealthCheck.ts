import { api } from '../../../shared/lib/api';

export interface BackendHealthStatus {
  isOnline: boolean;
  responseTime: number;
  error?: string;
  timestamp: string;
}

export const checkBackendHealth = async (): Promise<BackendHealthStatus & {
  isRateLimited?: boolean;
  retryAfter?: number;
  resetTime?: number;
}> => {
  const startTime = Date.now();
  const timestamp = new Date().toISOString();

  try {
    // Try to make a simple request to test connectivity
    // We'll try the GPS endpoint first as it's likely to exist
    await api.get('/api/inventory/gps/', { 
      timeout: 5000,
      // Add a parameter to make it a lightweight request
      params: { limit: 1 }
    });
    
    const responseTime = Date.now() - startTime;
    
    return {
      isOnline: true,
      responseTime,
      timestamp
    };
  } catch (err: unknown) {
    const responseTime = Date.now() - startTime;
    const error = err as { response?: { status: number; headers: Record<string, string>; data?: { message?: string } }; code?: string; message?: string };
    
    // Check for rate limiting first
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      const resetTime = error.response.headers['x-ratelimit-reset'];
      
      const result: BackendHealthStatus & { isRateLimited?: boolean; retryAfter?: number; resetTime?: number } = {
        isOnline: true, // Backend is online but rate limited
        responseTime,
        isRateLimited: true,
        error: `Rate limit exceeded. ${error.response.data?.message || 'Too many requests'}`,
        timestamp
      };
      
      if (retryAfter) {
        result.retryAfter = parseInt(retryAfter);
      }
      if (resetTime) {
        result.resetTime = parseInt(resetTime);
      }
      
      return result;
    }
    
    // Determine the type of error
    let errorMessage = 'Unknown error';
    
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      errorMessage = 'Backend server is not running or not accessible';
    } else if (error.response?.status === 401) {
      errorMessage = 'Authentication required (backend is online but requires login)';
    } else if (error.response?.status === 404) {
      errorMessage = 'Endpoint not found (backend is online but API structure may have changed)';
    } else if (error.response?.status && error.response.status >= 500) {
      errorMessage = 'Backend server error';
    } else if (error.message?.includes('timeout')) {
      errorMessage = 'Request timeout - backend may be slow or overloaded';
    } else {
      errorMessage = error.message || 'Connection failed';
    }
    
    return {
      isOnline: false,
      responseTime,
      error: errorMessage,
      timestamp
    };
  }
};

export const testSpecificEndpoint = async (endpoint: string): Promise<{
  success: boolean;
  status?: number;
  data?: unknown;
  error?: string;
  responseTime: number;
}> => {
  const startTime = Date.now();
  
  try {
    const response = await api.get(endpoint, { timeout: 5000 });
    const responseTime = Date.now() - startTime;
    
    return {
      success: true,
      status: response.status,
      data: response.data,
      responseTime
    };
  } catch (err: unknown) {
    const responseTime = Date.now() - startTime;
    const error = err as { response?: { status: number }; message?: string };
    
    const result: { success: boolean; status?: number; data?: unknown; error?: string; responseTime: number } = {
      success: false,
      error: error.message || 'Unknown error',
      responseTime
    };
    
    if (error.response?.status) {
      result.status = error.response.status;
    }
    
    return result;
  }
};

export const getBackendInfo = () => {
  const baseURL = api.defaults.baseURL;
  const timeout = api.defaults.timeout;
  
  return {
    baseURL,
    timeout,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  };
};