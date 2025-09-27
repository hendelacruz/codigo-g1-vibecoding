import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { authAPI } from './authAPI'
import type { AuthState, LoginCredentials, User, BackendLoginResponse } from './authTypes'

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials) as BackendLoginResponse
      
      // Transform backend response to match frontend User interface
      const transformedUser: User = {
        id: response.user.id,
        username: response.user.username,
        email: response.user.email,
        first_name: response.user.first_name,
        last_name: response.user.last_name,
        dni: response.user.dni,
        rol_nombre: response.user.rol?.nombre || 'USER', // Transform rol.nombre to rol_nombre
        is_active: response.user.is_active ?? true, // Default to true if not provided
        is_staff: response.user.is_staff ?? false,
        is_superuser: response.user.is_superuser ?? false,
        date_joined: new Date().toISOString(), // Default to current date since not provided by backend
        groups: response.user.groups || [],
        user_permissions: response.user.user_permissions || []
      }
      
      return {
        user: transformedUser,
        access: response.access,
        refresh: response.refresh
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Login failed')
    }
  }
)

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (refreshToken: string | undefined, { rejectWithValue }) => {
    try {
      await authAPI.logout(refreshToken)
      return { success: true }
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Logout failed')
    }
  }
)

export const refreshAuthToken = createAsyncThunk(
  'auth/refreshToken',
  async (refreshToken: string, { rejectWithValue }) => {
    try {
      const response = await authAPI.refreshToken(refreshToken)
      return response.access
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Token refresh failed')
    }
  }
)

export const checkAuthStatus = createAsyncThunk(
  'auth/checkStatus',
  async (token: string, { rejectWithValue }) => {
    try {
      const response = await authAPI.getAuthStatus(token)
      return response.user
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Auth status check failed')
    }
  }
)

export const getUserProfile = createAsyncThunk(
  'auth/getProfile',
  async (token: string, { rejectWithValue }) => {
    try {
      const user = await authAPI.getProfile(token)
      return user
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Get profile failed')
    }
  }
)

export const changeUserPassword = createAsyncThunk(
  'auth/changePassword',
  async (
    { passwordData, token }: { 
      passwordData: { old_password: string; new_password: string }
      token: string 
    }, 
    { rejectWithValue }
  ) => {
    try {
      await authAPI.changePassword(passwordData, token)
      return 'Password changed successfully'
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Password change failed')
    }
  }
)

export const verifyUserToken = createAsyncThunk(
  'auth/verifyToken',
  async (token: string, { rejectWithValue }) => {
    try {
      const isValid = await authAPI.verifyToken(token)
      return isValid
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Token verification failed')
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload
    },
    setRefreshToken: (state, action: PayloadAction<string>) => {
      state.refreshToken = action.payload
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload }
      }
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
    },
    clearAuth: (state) => {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = null
      state.isLoading = false
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload.user
        state.token = action.payload.access
        state.refreshToken = action.payload.refresh
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
        state.isAuthenticated = false
      })
      
      // Logout
      .addCase(logoutUser.pending, (state) => {
        state.isLoading = true
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.error = null
        state.isLoading = false
      })
      .addCase(logoutUser.rejected, (state, action) => {
        // Even if logout fails on server, clear local state
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Refresh Token
      .addCase(refreshAuthToken.pending, (state) => {
        state.isLoading = true
      })
      .addCase(refreshAuthToken.fulfilled, (state, action) => {
        state.token = action.payload
        state.isLoading = false
        state.error = null
      })
      .addCase(refreshAuthToken.rejected, (state, action) => {
        // If refresh fails, clear auth state
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Check Auth Status
      .addCase(checkAuthStatus.pending, (state) => {
        state.isLoading = true
      })
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.user = action.payload
        state.isAuthenticated = true
        state.isLoading = false
        state.error = null
      })
      .addCase(checkAuthStatus.rejected, (state, action) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Get Profile
      .addCase(getUserProfile.pending, (state) => {
        state.isLoading = true
      })
      .addCase(getUserProfile.fulfilled, (state, action) => {
        state.user = action.payload
        state.isLoading = false
        state.error = null
      })
      .addCase(getUserProfile.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Change Password
      .addCase(changeUserPassword.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(changeUserPassword.fulfilled, (state) => {
        state.isLoading = false
        state.error = null
      })
      .addCase(changeUserPassword.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      
      // Verify Token
      .addCase(verifyUserToken.pending, (state) => {
        state.isLoading = true
      })
      .addCase(verifyUserToken.fulfilled, (state, action) => {
        state.isLoading = false
        state.error = null
        // If token is invalid, clear auth state
        if (!action.payload) {
          state.user = null
          state.token = null
          state.refreshToken = null
          state.isAuthenticated = false
        }
      })
      .addCase(verifyUserToken.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
        // Clear auth state on verification failure
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
      })
  },
})

export const { 
  clearError, 
  setToken, 
  setRefreshToken, 
  updateUser,
  setUser, 
  clearAuth, 
  setLoading,
  setAuthenticated 
} = authSlice.actions

export default authSlice.reducer