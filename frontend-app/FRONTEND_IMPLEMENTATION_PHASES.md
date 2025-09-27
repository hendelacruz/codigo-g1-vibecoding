# Implementación Frontend por Fases - React + Vite + Redux Toolkit

Esta guía define la implementación por fases de la aplicación frontend React + Vite con Redux Toolkit y persistencia, incluyendo pruebas exhaustivas en cada fase contra el backend Django en puerto 8000.

## 🎯 Principios de Implementación

- **Desarrollo incremental**: Cada fase debe completarse y probarse antes de continuar
- **Pruebas exhaustivas**: Autenticación y CRUD completo en cada fase
- **TypeScript estricto**: Sin uso de `any`, tipado completo
- **Redux Toolkit**: Gestión de estado moderna con persistencia
- **Arquitectura modular**: Componentes reutilizables y mantenibles
- **Testing directo**: Pruebas contra backend en puerto 8000

## 📋 Estructura de Fases

### Fase 1: Configuración Base y Autenticación ✅
### Fase 2: Módulo de Inventario (GPS, SIM Cards, Otros) ✅
### Fase 3: Módulo de Ventas y Entidades ✅
### Fase 4: Dashboard y Servicios ✅

---

## 🚀 FASE 1: Configuración Base y Autenticación

### Objetivos
- Configurar proyecto React + Vite + TypeScript
- Implementar Redux Toolkit con persistencia
- Sistema de autenticación JWT completo
- Pruebas de login, logout, refresh token

### 1.1 Configuración Inicial

```bash
# Crear proyecto
npm create vite@latest frontend-app -- --template react-ts
cd frontend-app

# Dependencias principales
npm install @reduxjs/toolkit react-redux redux-persist
npm install axios @tanstack/react-query
npm install react-hook-form @hookform/resolvers zod
npm install react-router-dom

# UI y Styling
npm install tailwindcss postcss autoprefixer
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-toast @radix-ui/react-select
npm install clsx tailwind-merge class-variance-authority

# Utilidades
npm install date-fns

# Development
npm install -D @types/node vitest @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event jsdom
```

### 1.2 Configuración de Tailwind

```bash
npx tailwindcss init -p
```

**tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: {
          500: '#10b981',
          600: '#059669',
        },
        error: {
          500: '#ef4444',
          600: '#dc2626',
        }
      }
    },
  },
  plugins: [],
}
```

### 1.3 Estructura del Proyecto

```
src/
├── app/
│   ├── store.ts              # Redux store configuration
│   ├── rootReducer.ts        # Root reducer
│   └── providers/
│       ├── ReduxProvider.tsx
│       ├── QueryProvider.tsx
│       └── AppProviders.tsx
├── features/
│   ├── auth/
│   │   ├── authSlice.ts
│   │   ├── authAPI.ts
│   │   ├── authTypes.ts
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── AuthLayout.tsx
│   │   └── hooks/
│   │       └── useAuth.ts
│   ├── inventory/           # Fase 2
│   ├── sales/              # Fase 3
│   └── dashboard/          # Fase 4
├── shared/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Layout.tsx
│   ├── hooks/
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   └── useApi.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── utils.ts
│   │   └── validations.ts
│   └── types/
│       ├── api.ts
│       ├── common.ts
│       └── index.ts
├── pages/
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   └── NotFoundPage.tsx
└── tests/
    ├── setup.ts
    ├── utils.tsx
    └── __mocks__/
```

### 1.4 Redux Store Configuration

**src/app/store.ts**
```typescript
import { configureStore } from '@reduxjs/toolkit'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { rootReducer } from './rootReducer'

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth'], // Only persist auth state
}

const persistedReducer = persistReducer(persistConfig, rootReducer)

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
})

export const persistor = persistStore(store)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

**src/app/rootReducer.ts**
```typescript
import { combineReducers } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'

export const rootReducer = combineReducers({
  auth: authReducer,
  // inventory: inventoryReducer, // Fase 2
  // sales: salesReducer,         // Fase 3
  // dashboard: dashboardReducer, // Fase 4
})
```

### 1.5 Auth Types

**src/features/auth/authTypes.ts**
```typescript
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  dni: string
  rol_nombre: string
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
```

### 1.6 Auth API

**src/features/auth/authAPI.ts**
```typescript
import { api } from '../../shared/lib/api'
import { LoginCredentials, LoginResponse, RefreshTokenResponse, User } from './authTypes'

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login/', credentials)
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout/')
  },

  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const response = await api.post<RefreshTokenResponse>('/auth/token/refresh/', {
      refresh: refreshToken
    })
    return response.data
  },

  getAuthStatus: async (): Promise<{ user: User }> => {
    const response = await api.get<{ user: User }>('/auth/status/')
    return response.data
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get<User>('/auth/profile/')
    return response.data
  },

  changePassword: async (data: { old_password: string; new_password: string }): Promise<void> => {
    await api.put('/auth/change-password/', data)
  }
}
```

### 1.7 Auth Slice

**src/features/auth/authSlice.ts**
```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authAPI } from './authAPI'
import { AuthState, LoginCredentials, User } from './authTypes'

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
      const response = await authAPI.login(credentials)
      return response
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
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout()
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
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getAuthStatus()
      return response.user
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Auth status check failed')
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
    clearAuth: (state) => {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.error = null
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
      })
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
        state.error = null
      })
      // Refresh Token
      .addCase(refreshAuthToken.fulfilled, (state, action) => {
        state.token = action.payload
      })
      .addCase(refreshAuthToken.rejected, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
      })
      // Check Auth Status
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.user = action.payload
        state.isAuthenticated = true
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.user = null
        state.token = null
        state.refreshToken = null
        state.isAuthenticated = false
      })
  },
})

export const { clearError, setToken, clearAuth } = authSlice.actions
export default authSlice.reducer
```

### 1.8 API Configuration

**src/shared/lib/api.ts**
```typescript
import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { store } from '../../app/store'
import { refreshAuthToken, clearAuth } from '../../features/auth/authSlice'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const state = store.getState()
    const token = state.auth.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      
      const state = store.getState()
      const refreshToken = state.auth.refreshToken
      
      if (refreshToken) {
        try {
          const resultAction = await store.dispatch(refreshAuthToken(refreshToken))
          
          if (refreshAuthToken.fulfilled.match(resultAction)) {
            const newToken = resultAction.payload
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          }
        } catch (refreshError) {
          store.dispatch(clearAuth())
          window.location.href = '/login'
        }
      } else {
        store.dispatch(clearAuth())
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
```

### 1.9 Auth Hook

**src/features/auth/hooks/useAuth.ts**
```typescript
import { useSelector, useDispatch } from 'react-redux'
import { useCallback } from 'react'
import { RootState, AppDispatch } from '../../../app/store'
import { loginUser, logoutUser, checkAuthStatus, clearError } from '../authSlice'
import { LoginCredentials } from '../authTypes'

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>()
  const auth = useSelector((state: RootState) => state.auth)

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const result = await dispatch(loginUser(credentials))
      return result
    },
    [dispatch]
  )

  const logout = useCallback(async () => {
    await dispatch(logoutUser())
  }, [dispatch])

  const checkStatus = useCallback(async () => {
    await dispatch(checkAuthStatus())
  }, [dispatch])

  const clearAuthError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  return {
    ...auth,
    login,
    logout,
    checkStatus,
    clearError: clearAuthError,
  }
}
```

### 1.10 Login Form Component

**src/features/auth/components/LoginForm.tsx**
```typescript
import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

const loginSchema = z.object({
  username: z.string().min(1, 'Username es requerido'),
  password: z.string().min(1, 'Password es requerido')
})

type LoginFormData = z.infer<typeof loginSchema>

export const LoginForm: React.FC = () => {
  const { login, isLoading, error, isAuthenticated, clearError } = useAuth()
  const navigate = useNavigate()
  
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    return () => {
      clearError()
    }
  }, [clearError])

  const onSubmit = async (data: LoginFormData) => {
    await login(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Iniciar Sesión
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <Input
                {...register('username')}
                type="text"
                placeholder="Username"
                error={errors.username?.message}
                className="relative block w-full"
              />
            </div>
            
            <div>
              <Input
                {...register('password')}
                type="password"
                placeholder="Password"
                error={errors.password?.message}
                className="relative block w-full"
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">
                Error: {error}
              </div>
            </div>
          )}

          <div>
            <Button
              type="submit"
              isLoading={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

### 1.11 Protected Route Component

**src/features/auth/components/ProtectedRoute.tsx**
```typescript
import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { LoadingSpinner } from '../../../shared/components/ui/LoadingSpinner'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading, checkStatus, token } = useAuth()
  const location = useLocation()

  useEffect(() => {
    if (token && !isAuthenticated) {
      checkStatus()
    }
  }, [token, isAuthenticated, checkStatus])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
```

### 1.12 UI Components

**src/shared/components/ui/Button.tsx**
```typescript
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary-600 text-white hover:bg-primary-700",
        destructive: "bg-error-500 text-white hover:bg-error-600",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary-600",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = "Button"
```

**src/shared/components/ui/Input.tsx**
```typescript
import React from 'react'
import { cn } from '../../lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-error-500 focus-visible:ring-error-500",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-error-500">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = "Input"
```

**src/shared/components/ui/LoadingSpinner.tsx**
```typescript
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const spinnerVariants = cva(
  "animate-spin rounded-full border-2 border-gray-300 border-t-primary-600",
  {
    variants: {
      size: {
        sm: "h-4 w-4",
        md: "h-6 w-6",
        lg: "h-8 w-8",
        xl: "h-12 w-12",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
)

export interface LoadingSpinnerProps extends VariantProps<typeof spinnerVariants> {
  className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size, 
  className 
}) => {
  return (
    <div className={cn(spinnerVariants({ size }), className)} />
  )
}
```

### 1.13 Utilities

**src/shared/lib/utils.ts**
```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(date))
}

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
  }).format(amount)
}
```

### 1.14 App Providers

**src/app/providers/ReduxProvider.tsx**
```typescript
import React from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { store, persistor } from '../store'
import { LoadingSpinner } from '../../shared/components/ui/LoadingSpinner'

interface ReduxProviderProps {
  children: React.ReactNode
}

export const ReduxProvider: React.FC<ReduxProviderProps> = ({ children }) => {
  return (
    <Provider store={store}>
      <PersistGate 
        loading={
          <div className="min-h-screen flex items-center justify-center">
            <LoadingSpinner size="xl" />
          </div>
        } 
        persistor={persistor}
      >
        {children}
      </PersistGate>
    </Provider>
  )
}
```

**src/app/providers/QueryProvider.tsx**
```typescript
import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

interface QueryProviderProps {
  children: React.ReactNode
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

**src/app/providers/AppProviders.tsx**
```typescript
import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { ReduxProvider } from './ReduxProvider'
import { QueryProvider } from './QueryProvider'

interface AppProvidersProps {
  children: React.ReactNode
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <ReduxProvider>
      <QueryProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryProvider>
    </ReduxProvider>
  )
}
```

### 1.15 Main App Component

**src/App.tsx**
```typescript
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AppProviders } from './app/providers/AppProviders'
import { LoginForm } from './features/auth/components/LoginForm'
import { ProtectedRoute } from './features/auth/components/ProtectedRoute'
import { DashboardPage } from './pages/DashboardPage'
import './index.css'

const App: React.FC = () => {
  return (
    <AppProviders>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AppProviders>
  )
}

export default App
```

**src/pages/DashboardPage.tsx**
```typescript
import React from 'react'
import { useAuth } from '../features/auth/hooks/useAuth'
import { Button } from '../shared/components/ui/Button'

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Bienvenido, {user?.first_name} {user?.last_name}
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Cerrar Sesión
              </Button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                ¡Autenticación Exitosa!
              </h2>
              <p className="text-gray-600">
                Fase 1 completada. Listo para implementar módulos.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
```

### 1.16 Environment Variables

**.env**
```
VITE_API_URL=http://127.0.0.1:8000
```

### 1.17 Vite Configuration

**vite.config.ts**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
  },
})
```

## 🧪 PRUEBAS FASE 1

### 1.18 Test Configuration

**src/tests/setup.ts**
```typescript
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock environment variables
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://127.0.0.1:8000'
  }
}))
```

### 1.19 Manual Testing Script

**tests/phase1-manual-tests.md**
```markdown
# Fase 1 - Pruebas Manuales de Autenticación

## Pre-requisitos
- Backend Django ejecutándose en puerto 8000
- Frontend ejecutándose en puerto 3000
- Usuario de prueba creado en Django

## Pruebas a Realizar

### 1. Configuración Inicial ✅
- [ ] `npm run dev` inicia sin errores
- [ ] Aplicación carga en http://localhost:3000
- [ ] Redux DevTools funciona correctamente
- [ ] Persistencia funciona (refresh mantiene estado)

### 2. Autenticación - Login ✅
- [ ] Navegar a /login muestra formulario
- [ ] Validación de campos vacíos funciona
- [ ] Login con credenciales incorrectas muestra error
- [ ] Login con credenciales correctas:
  - [ ] Redirige a /dashboard
  - [ ] Token se guarda en Redux store
  - [ ] Usuario se guarda en Redux store
  - [ ] Estado persiste después de refresh

### 3. Autenticación - Logout ✅
- [ ] Botón logout en dashboard funciona
- [ ] Limpia estado de Redux
- [ ] Redirige a /login
- [ ] Estado limpio persiste después de refresh

### 4. Rutas Protegidas ✅
- [ ] Acceso directo a /dashboard sin auth redirige a /login
- [ ] Después de login, acceso a /dashboard funciona
- [ ] Refresh en /dashboard mantiene sesión

### 5. Token Refresh ✅
- [ ] Token expira y se renueva automáticamente
- [ ] Requests continúan funcionando después de refresh
- [ ] Si refresh falla, redirige a login

### 6. Manejo de Errores ✅
- [ ] Errores de red se muestran correctamente
- [ ] Errores de autenticación se manejan
- [ ] Loading states funcionan

## Comandos de Prueba

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Ejecutar tests unitarios
npm run test

# Build para producción
npm run build
```

## Criterios de Éxito
- ✅ Todas las pruebas manuales pasan
- ✅ No hay errores en consola
- ✅ Redux DevTools muestra estado correcto
- ✅ Persistencia funciona correctamente
- ✅ Manejo de errores robusto
```

### 1.20 API Testing Script

**tests/api-test.js**
```javascript
// Script para probar endpoints de autenticación
const API_BASE = 'http://127.0.0.1:8000'

async function testAuthEndpoints() {
  console.log('🧪 Iniciando pruebas de API de autenticación...\n')
  
  try {
    // Test 1: Login
    console.log('1. Probando login...')
    const loginResponse = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'Hdelacruz', // Cambiar por usuario real
        password: 'Hygcompe2025' // Cambiar por password real
      })
    })
    
    if (!loginResponse.ok) {
      throw new Error(`Login failed: ${loginResponse.status}`)
    }
    
    const loginData = await loginResponse.json()
    console.log('✅ Login exitoso')
    console.log('   - Access token recibido')
    console.log('   - Refresh token recibido')
    console.log('   - Datos de usuario recibidos\n')
    
    const { access, refresh } = loginData
    
    // Test 2: Auth Status
    console.log('2. Probando auth status...')
    const statusResponse = await fetch(`${API_BASE}/auth/status/`, {
      headers: {
        'Authorization': `Bearer ${access}`
      }
    })
    
    if (!statusResponse.ok) {
      throw new Error(`Auth status failed: ${statusResponse.status}`)
    }
    
    console.log('✅ Auth status exitoso\n')
    
    // Test 3: Token Refresh
    console.log('3. Probando token refresh...')
    const refreshResponse = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: refresh
      })
    })
    
    if (!refreshResponse.ok) {
      throw new Error(`Token refresh failed: ${refreshResponse.status}`)
    }
    
    console.log('✅ Token refresh exitoso\n')
    
    // Test 4: Logout
    console.log('4. Probando logout...')
    const logoutResponse = await fetch(`${API_BASE}/auth/logout/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${access}`
      }
    })
    
    if (!logoutResponse.ok) {
      throw new Error(`Logout failed: ${logoutResponse.status}`)
    }
    
    console.log('✅ Logout exitoso\n')
    
    console.log('🎉 Todas las pruebas de autenticación pasaron!')
    
  } catch (error) {
    console.error('❌ Error en pruebas:', error.message)
  }
}

// Ejecutar pruebas
testAuthEndpoints()
```

## ✅ CRITERIOS DE APROBACIÓN FASE 1

Para pasar a la Fase 2, se debe cumplir:

1. **Configuración Base** ✅
   - Proyecto React + Vite + TypeScript funcional
   - Redux Toolkit configurado correctamente
   - Persistencia funcionando
   - Tailwind CSS configurado

2. **Autenticación Completa** ✅
   - Login/logout funcional
   - Token refresh automático
   - Rutas protegidas
   - Manejo de errores robusto

3. **Pruebas Exitosas** ✅
   - Todas las pruebas manuales pasan
   - API endpoints responden correctamente
   - No hay errores en consola
   - Estado persiste correctamente

4. **Código de Calidad** ✅
   - TypeScript estricto (sin `any`)
   - Componentes modulares
   - Arquitectura escalable
   - Documentación completa

---

## 🚀 FASE 2: Módulo de Inventario

### Objetivos
- Implementar CRUD completo para GPS, SIM Cards y Otros productos
- Gestión de estado con Redux Toolkit
- Componentes reutilizables y formularios
- Validaciones con Zod
- Pruebas exhaustivas de todas las operaciones

### 2.1 Types para Inventario

**src/features/inventory/inventoryTypes.ts**
```typescript
export interface GPS {
  id: number
  fecha_compra: string
  imei: string
  marca: string
  modelo: string
  numero_factura: string
  proveedor: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  estado: 'disponible' | 'activo' | 'asignado' | 'suspendido' | 'en_mantenimiento' | 'dañado' | 'perdido' | 'dado_de_baja'
  estado_display: string
  precio_compra?: number
  observaciones?: string
  created_at: string
  updated_at: string
}

export interface SIMCard {
  id: number
  fecha_compra: string
  numero_factura: string
  numero_chip: string
  icc: string
  proveedor: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  estado: 'disponible' | 'activo' | 'asignado' | 'suspendido' | 'en_mantenimiento' | 'dañado' | 'perdido' | 'dado_de_baja'
  estado_display: string
  operadora?: string
  plan?: string
  precio_compra?: number
  observaciones?: string
  created_at: string
  updated_at: string
}

export interface OtroProducto {
  id: number
  nombre: string
  descripcion?: string
  categoria: string
  precio_unitario: number
  stock_actual: number
  stock_minimo: number
  proveedor: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  estado_stock: 'disponible' | 'agotado' | 'bajo_stock'
  created_at: string
  updated_at: string
}

export interface Proveedor {
  id: number
  nombre: string
  ruc?: string
  telefono?: string
  correo?: string
  direccion?: string
  is_active: boolean
}

export interface InventoryState {
  gps: {
    items: GPS[]
    isLoading: boolean
    error: string | null
  }
  simCards: {
    items: SIMCard[]
    isLoading: boolean
    error: string | null
  }
  otrosProductos: {
    items: OtroProducto[]
    isLoading: boolean
    error: string | null
  }
  proveedores: {
    items: Proveedor[]
    isLoading: boolean
    error: string | null
  }
}

export interface CreateGPSData {
  fecha_compra: string
  imei: string
  marca: string
  modelo: string
  numero_factura: string
  proveedor: number
  estado: GPS['estado']
  precio_compra?: number
  observaciones?: string
}

export interface CreateSIMCardData {
  fecha_compra: string
  numero_factura: string
  numero_chip: string
  icc: string
  proveedor: number
  estado: SIMCard['estado']
  operadora?: string
  plan?: string
  precio_compra?: number
  observaciones?: string
}

export interface CreateOtroProductoData {
  nombre: string
  descripcion?: string
  categoria: string
  precio_unitario: number
  stock_actual: number
  stock_minimo: number
  proveedor: number
}

export interface AdjustStockData {
  cantidad: number
  motivo?: string
}
```

### 2.2 Inventory API

**src/features/inventory/inventoryAPI.ts**
```typescript
import { api } from '../../shared/lib/api'
import { 
  GPS, 
  SIMCard, 
  OtroProducto, 
  Proveedor,
  CreateGPSData,
  CreateSIMCardData,
  CreateOtroProductoData,
  AdjustStockData
} from './inventoryTypes'

export const inventoryAPI = {
  // GPS endpoints
  getGPSDevices: async (): Promise<GPS[]> => {
    const response = await api.get<GPS[]>('/api/inventory/gps/')
    return response.data
  },

  getGPSDevice: async (id: number): Promise<GPS> => {
    const response = await api.get<GPS>(`/api/inventory/gps/${id}/`)
    return response.data
  },

  createGPS: async (data: CreateGPSData): Promise<GPS> => {
    const response = await api.post<GPS>('/api/inventory/gps/', data)
    return response.data
  },

  updateGPS: async (id: number, data: Partial<CreateGPSData>): Promise<GPS> => {
    const response = await api.put<GPS>(`/api/inventory/gps/${id}/`, data)
    return response.data
  },

  deleteGPS: async (id: number): Promise<void> => {
    await api.delete(`/api/inventory/gps/${id}/`)
  },

  // SIM Cards endpoints
  getSIMCards: async (): Promise<SIMCard[]> => {
    const response = await api.get<SIMCard[]>('/api/inventory/simcards/')
    return response.data
  },

  getSIMCard: async (id: number): Promise<SIMCard> => {
    const response = await api.get<SIMCard>(`/api/inventory/simcards/${id}/`)
    return response.data
  },

  createSIMCard: async (data: CreateSIMCardData): Promise<SIMCard> => {
    const response = await api.post<SIMCard>('/api/inventory/simcards/', data)
    return response.data
  },

  updateSIMCard: async (id: number, data: Partial<CreateSIMCardData>): Promise<SIMCard> => {
    const response = await api.put<SIMCard>(`/api/inventory/simcards/${id}/`, data)
    return response.data
  },

  deleteSIMCard: async (id: number): Promise<void> => {
    await api.delete(`/api/inventory/simcards/${id}/`)
  },

  // Otros Productos endpoints
  getOtrosProductos: async (): Promise<OtroProducto[]> => {
    const response = await api.get<OtroProducto[]>('/api/inventory/otros/')
    return response.data
  },

  getOtroProducto: async (id: number): Promise<OtroProducto> => {
    const response = await api.get<OtroProducto>(`/api/inventory/otros/${id}/`)
    return response.data
  },

  createOtroProducto: async (data: CreateOtroProductoData): Promise<OtroProducto> => {
    const response = await api.post<OtroProducto>('/api/inventory/otros/', data)
    return response.data
  },

  updateOtroProducto: async (id: number, data: Partial<CreateOtroProductoData>): Promise<OtroProducto> => {
    const response = await api.put<OtroProducto>(`/api/inventory/otros/${id}/`, data)
    return response.data
  },

  deleteOtroProducto: async (id: number): Promise<void> => {
    await api.delete(`/api/inventory/otros/${id}/`)
  },

  adjustStock: async (id: number, data: AdjustStockData): Promise<OtroProducto> => {
    const response = await api.put<OtroProducto>(`/api/inventory/otros/${id}/adjust-stock/`, data)
    return response.data
  },

  // Proveedores endpoints
  getProveedores: async (): Promise<Proveedor[]> => {
    const response = await api.get<Proveedor[]>('/api/entities/proveedores/')
    return response.data
  }
}
```

### 2.3 Inventory Slice

**src/features/inventory/inventorySlice.ts**
```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { inventoryAPI } from './inventoryAPI'
import { 
  InventoryState, 
  CreateGPSData, 
  CreateSIMCardData, 
  CreateOtroProductoData,
  AdjustStockData
} from './inventoryTypes'

const initialState: InventoryState = {
  gps: {
    items: [],
    isLoading: false,
    error: null,
  },
  simCards: {
    items: [],
    isLoading: false,
    error: null,
  },
  otrosProductos: {
    items: [],
    isLoading: false,
    error: null,
  },
  proveedores: {
    items: [],
    isLoading: false,
    error: null,
  },
}

// GPS Async Thunks
export const fetchGPSDevices = createAsyncThunk(
  'inventory/fetchGPSDevices',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getGPSDevices()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to fetch GPS devices')
    }
  }
)

export const createGPS = createAsyncThunk(
  'inventory/createGPS',
  async (data: CreateGPSData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createGPS(data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to create GPS device')
    }
  }
)

export const updateGPS = createAsyncThunk(
  'inventory/updateGPS',
  async ({ id, data }: { id: number; data: Partial<CreateGPSData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateGPS(id, data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to update GPS device')
    }
  }
)

export const deleteGPS = createAsyncThunk(
  'inventory/deleteGPS',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteGPS(id)
      return id
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to delete GPS device')
    }
  }
)

// SIM Cards Async Thunks
export const fetchSIMCards = createAsyncThunk(
  'inventory/fetchSIMCards',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getSIMCards()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to fetch SIM cards')
    }
  }
)

export const createSIMCard = createAsyncThunk(
  'inventory/createSIMCard',
  async (data: CreateSIMCardData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createSIMCard(data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to create SIM card')
    }
  }
)

export const updateSIMCard = createAsyncThunk(
  'inventory/updateSIMCard',
  async ({ id, data }: { id: number; data: Partial<CreateSIMCardData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateSIMCard(id, data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to update SIM card')
    }
  }
)

export const deleteSIMCard = createAsyncThunk(
  'inventory/deleteSIMCard',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteSIMCard(id)
      return id
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to delete SIM card')
    }
  }
)

// Otros Productos Async Thunks
export const fetchOtrosProductos = createAsyncThunk(
  'inventory/fetchOtrosProductos',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getOtrosProductos()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to fetch otros productos')
    }
  }
)

export const createOtroProducto = createAsyncThunk(
  'inventory/createOtroProducto',
  async (data: CreateOtroProductoData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createOtroProducto(data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to create producto')
    }
  }
)

export const updateOtroProducto = createAsyncThunk(
  'inventory/updateOtroProducto',
  async ({ id, data }: { id: number; data: Partial<CreateOtroProductoData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateOtroProducto(id, data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to update producto')
    }
  }
)

export const deleteOtroProducto = createAsyncThunk(
  'inventory/deleteOtroProducto',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteOtroProducto(id)
      return id
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to delete producto')
    }
  }
)

export const adjustStock = createAsyncThunk(
  'inventory/adjustStock',
  async ({ id, data }: { id: number; data: AdjustStockData }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.adjustStock(id, data)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to adjust stock')
    }
  }
)

// Proveedores Async Thunk
export const fetchProveedores = createAsyncThunk(
  'inventory/fetchProveedores',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getProveedores()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Failed to fetch proveedores')
    }
  }
)

const inventorySlice = createSlice({
  name: 'inventory',
  initialState,
  reducers: {
    clearInventoryErrors: (state) => {
      state.gps.error = null
      state.simCards.error = null
      state.otrosProductos.error = null
      state.proveedores.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // GPS reducers
      .addCase(fetchGPSDevices.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(fetchGPSDevices.fulfilled, (state, action) => {
        state.gps.isLoading = false
        state.gps.items = action.payload
      })
      .addCase(fetchGPSDevices.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      .addCase(createGPS.fulfilled, (state, action) => {
        state.gps.items.push(action.payload)
      })
      .addCase(updateGPS.fulfilled, (state, action) => {
        const index = state.gps.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.gps.items[index] = action.payload
        }
      })
      .addCase(deleteGPS.fulfilled, (state, action) => {
        state.gps.items = state.gps.items.filter(item => item.id !== action.payload)
      })
      // SIM Cards reducers
      .addCase(fetchSIMCards.pending, (state) => {
        state.simCards.isLoading = true
        state.simCards.error = null
      })
      .addCase(fetchSIMCards.fulfilled, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.items = action.payload
      })
      .addCase(fetchSIMCards.rejected, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.error = action.payload as string
      })
      .addCase(createSIMCard.fulfilled, (state, action) => {
        state.simCards.items.push(action.payload)
      })
      .addCase(updateSIMCard.fulfilled, (state, action) => {
        const index = state.simCards.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.simCards.items[index] = action.payload
        }
      })
      .addCase(deleteSIMCard.fulfilled, (state, action) => {
        state.simCards.items = state.simCards.items.filter(item => item.id !== action.payload)
      })
      // Otros Productos reducers
      .addCase(fetchOtrosProductos.pending, (state) => {
        state.otrosProductos.isLoading = true
        state.otrosProductos.error = null
      })
      .addCase(fetchOtrosProductos.fulfilled, (state, action) => {
        state.otrosProductos.isLoading = false
        state.otrosProductos.items = action.payload
      })
      .addCase(fetchOtrosProductos.rejected, (state, action) => {
        state.otrosProductos.isLoading = false
        state.otrosProductos.error = action.payload as string
      })
      .addCase(createOtroProducto.fulfilled, (state, action) => {
        state.otrosProductos.items.push(action.payload)
      })
      .addCase(updateOtroProducto.fulfilled, (state, action) => {
        const index = state.otrosProductos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.otrosProductos.items[index] = action.payload
        }
      })
      .addCase(deleteOtroProducto.fulfilled, (state, action) => {
        state.otrosProductos.items = state.otrosProductos.items.filter(item => item.id !== action.payload)
      })
      .addCase(adjustStock.fulfilled, (state, action) => {
        const index = state.otrosProductos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.otrosProductos.items[index] = action.payload
        }
      })
      // Proveedores reducers
      .addCase(fetchProveedores.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(fetchProveedores.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.items = action.payload
      })
      .addCase(fetchProveedores.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })
  },
})

export const { clearInventoryErrors } = inventorySlice.actions
export default inventorySlice.reducer
```

### 2.4 Inventory Hooks

**src/features/inventory/hooks/useInventory.ts**
```typescript
import { useSelector, useDispatch } from 'react-redux'
import { useCallback } from 'react'
import { RootState, AppDispatch } from '../../../app/store'
import {
  fetchGPSDevices,
  createGPS,
  updateGPS,
  deleteGPS,
  fetchSIMCards,
  createSIMCard,
  updateSIMCard,
  deleteSIMCard,
  fetchOtrosProductos,
  createOtroProducto,
  updateOtroProducto,
  deleteOtroProducto,
  adjustStock,
  fetchProveedores,
  clearInventoryErrors,
} from '../inventorySlice'
import { 
  CreateGPSData, 
  CreateSIMCardData, 
  CreateOtroProductoData,
  AdjustStockData
} from '../inventoryTypes'

export const useInventory = () => {
  const dispatch = useDispatch<AppDispatch>()
  const inventory = useSelector((state: RootState) => state.inventory)

  // GPS operations
  const loadGPSDevices = useCallback(async () => {
    await dispatch(fetchGPSDevices())
  }, [dispatch])

  const addGPS = useCallback(async (data: CreateGPSData) => {
    const result = await dispatch(createGPS(data))
    return result
  }, [dispatch])

  const editGPS = useCallback(async (id: number, data: Partial<CreateGPSData>) => {
    const result = await dispatch(updateGPS({ id, data }))
    return result
  }, [dispatch])

  const removeGPS = useCallback(async (id: number) => {
    const result = await dispatch(deleteGPS(id))
    return result
  }, [dispatch])

  // SIM Cards operations
  const loadSIMCards = useCallback(async () => {
    await dispatch(fetchSIMCards())
  }, [dispatch])

  const addSIMCard = useCallback(async (data: CreateSIMCardData) => {
    const result = await dispatch(createSIMCard(data))
    return result
  }, [dispatch])

  const editSIMCard = useCallback(async (id: number, data: Partial<CreateSIMCardData>) => {
    const result = await dispatch(updateSIMCard({ id, data }))
    return result
  }, [dispatch])

  const removeSIMCard = useCallback(async (id: number) => {
    const result = await dispatch(deleteSIMCard(id))
    return result
  }, [dispatch])

  // Otros Productos operations
  const loadOtrosProductos = useCallback(async () => {
    await dispatch(fetchOtrosProductos())
  }, [dispatch])

  const addOtroProducto = useCallback(async (data: CreateOtroProductoData) => {
    const result = await dispatch(createOtroProducto(data))
    return result
  }, [dispatch])

  const editOtroProducto = useCallback(async (id: number, data: Partial<CreateOtroProductoData>) => {
    const result = await dispatch(updateOtroProducto({ id, data }))
    return result
  }, [dispatch])

  const removeOtroProducto = useCallback(async (id: number) => {
    const result = await dispatch(deleteOtroProducto(id))
    return result
  }, [dispatch])

  const adjustProductStock = useCallback(async (id: number, data: AdjustStockData) => {
    const result = await dispatch(adjustStock({ id, data }))
    return result
  }, [dispatch])

  // Proveedores operations
  const loadProveedores = useCallback(async () => {
    await dispatch(fetchProveedores())
  }, [dispatch])

  const clearErrors = useCallback(() => {
    dispatch(clearInventoryErrors())
  }, [dispatch])

  return {
    ...inventory,
    // GPS
    loadGPSDevices,
    addGPS,
    editGPS,
    removeGPS,
    // SIM Cards
    loadSIMCards,
    addSIMCard,
    editSIMCard,
    removeSIMCard,
    // Otros Productos
    loadOtrosProductos,
    addOtroProducto,
    editOtroProducto,
    removeOtroProducto,
    adjustProductStock,
    // Proveedores
    loadProveedores,
    // Utils
    clearErrors,
  }
}
```

### 2.5 Validations

**src/features/inventory/validations.ts**
```typescript
import { z } from 'zod'

export const gpsSchema = z.object({
  fecha_compra: z.string().min(1, 'Fecha de compra es requerida'),
  imei: z.string().min(15, 'IMEI debe tener al menos 15 caracteres').max(17, 'IMEI no puede tener más de 17 caracteres'),
  marca: z.string().min(1, 'Marca es requerida'),
  modelo: z.string().min(1, 'Modelo es requerido'),
  numero_factura: z.string().min(1, 'Número de factura es requerido'),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja']),
  precio_compra: z.number().min(0, 'Precio debe ser mayor a 0').optional(),
  observaciones: z.string().optional(),
})

export const simCardSchema = z.object({
  fecha_compra: z.string().min(1, 'Fecha de compra es requerida'),
  numero_factura: z.string().min(1, 'Número de factura es requerido'),
  numero_chip: z.string().min(1, 'Número de chip es requerido'),
  icc: z.string().min(1, 'ICC es requerido'),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja']),
  operadora: z.string().optional(),
  plan: z.string().optional(),
  precio_compra: z.number().min(0, 'Precio debe ser mayor a 0').optional(),
  observaciones: z.string().optional(),
})

export const otroProductoSchema = z.object({
  nombre: z.string().min(1, 'Nombre es requerido'),
  descripcion: z.string().optional(),
  categoria: z.string().min(1, 'Categoría es requerida'),
  precio_unitario: z.number().min(0, 'Precio debe ser mayor a 0'),
  stock_actual: z.number().min(0, 'Stock actual debe ser mayor o igual a 0'),
  stock_minimo: z.number().min(0, 'Stock mínimo debe ser mayor o igual a 0'),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
})

export const adjustStockSchema = z.object({
  cantidad: z.number().int('Cantidad debe ser un número entero'),
  motivo: z.string().optional(),
})

export type GPSFormData = z.infer<typeof gpsSchema>
export type SIMCardFormData = z.infer<typeof simCardSchema>
export type OtroProductoFormData = z.infer<typeof otroProductoSchema>
export type AdjustStockFormData = z.infer<typeof adjustStockSchema>
```

## 🧪 PRUEBAS FASE 2

### 2.6 Manual Testing Script

**tests/phase2-manual-tests.md**
```markdown
# Fase 2 - Pruebas Manuales de Inventario

## Pre-requisitos
- Fase 1 completada exitosamente
- Backend Django ejecutándose en puerto 8000
- Usuario autenticado en la aplicación

## Pruebas a Realizar

### 1. GPS Devices - CRUD Completo ✅

#### Crear GPS
- [ ] Formulario de creación se muestra correctamente
- [ ] Validaciones funcionan (IMEI, campos requeridos)
- [ ] Lista de proveedores se carga
- [ ] Crear GPS con datos válidos funciona
- [ ] GPS aparece en la lista inmediatamente
- [ ] Estado se actualiza en Redux

#### Leer GPS
- [ ] Lista de GPS se carga al entrar al módulo
- [ ] Filtros y búsqueda funcionan
- [ ] Paginación funciona (si aplica)
- [ ] Detalles de GPS se muestran correctamente

#### Actualizar GPS
- [ ] Formulario de edición se pre-llena con datos
- [ ] Actualización funciona correctamente
- [ ] Cambios se reflejan inmediatamente en la lista
- [ ] Estado se actualiza en Redux

#### Eliminar GPS
- [ ] Confirmación de eliminación se muestra
- [ ] Eliminación funciona correctamente
- [ ] GPS se remueve de la lista inmediatamente
- [ ] Estado se actualiza en Redux

### 2. SIM Cards - CRUD Completo ✅

#### Crear SIM Card
- [ ] Formulario de creación funciona
- [ ] Validaciones de ICC y número de chip
- [ ] Crear SIM Card exitosamente
- [ ] Aparece en lista inmediatamente

#### Leer SIM Cards
- [ ] Lista se carga correctamente
- [ ] Filtros por operadora funcionan
- [ ] Búsqueda por número funciona

#### Actualizar SIM Card
- [ ] Edición funciona correctamente
- [ ] Cambios se reflejan inmediatamente

#### Eliminar SIM Card
- [ ] Eliminación funciona correctamente
- [ ] Se remueve de la lista

### 3. Otros Productos - CRUD Completo ✅

#### Crear Producto
- [ ] Formulario de creación funciona
- [ ] Validaciones de stock y precio
- [ ] Crear producto exitosamente

#### Leer Productos
- [ ] Lista se carga correctamente
- [ ] Estados de stock se muestran correctamente
- [ ] Filtros por categoría funcionan

#### Actualizar Producto
- [ ] Edición funciona correctamente
- [ ] Ajuste de stock funciona
- [ ] Estados se calculan correctamente

#### Eliminar Producto
- [ ] Eliminación funciona correctamente

### 4. Gestión de Proveedores ✅
- [ ] Lista de proveedores se carga
- [ ] Proveedores aparecen en formularios
- [ ] Filtros por proveedor funcionan

### 5. Manejo de Errores ✅
- [ ] Errores de red se muestran
- [ ] Validaciones de formulario funcionan
- [ ] Loading states se muestran
- [ ] Errores se limpian correctamente

## Comandos de Prueba

```bash
# Ejecutar aplicación
npm run dev

# Ejecutar tests
npm run test

# Verificar tipos
npm run type-check
```

## Criterios de Éxito
- ✅ Todos los CRUD funcionan correctamente
- ✅ Estado de Redux se mantiene sincronizado
- ✅ Validaciones funcionan en todos los formularios
- ✅ Manejo de errores robusto
- ✅ UI responsiva y accesible
```

---

## 🚀 FASE 3: Módulo de Ventas y Entidades

### Objetivos
- Implementar CRUD completo para Ventas
- Gestión de Clientes y Unidades
- Cálculo automático de IGV
- Validaciones de negocio
- Reportes básicos de ventas

### 3.1 Sales Types

**src/features/sales/salesTypes.ts**
```typescript
export interface Cliente {
  id: number
  nombre: string
  apellido: string
  dni?: string
  ruc?: string
  telefono?: string
  correo?: string
  direccion?: string
  tipo_cliente: 'persona' | 'empresa'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Unidad {
  id: number
  nombre: string
  descripcion?: string
  is_active: boolean
}

export interface Venta {
  id: number
  cliente: number
  cliente_info?: Cliente
  unidad: number
  unidad_info?: Unidad
  fecha_venta: string
  tipo_pago: 'efectivo' | 'transferencia' | 'tarjeta' | 'credito'
  tipo_pago_display: string
  subtotal: number
  igv: number
  total: number
  estado: 'pendiente' | 'completada' | 'cancelada'
  estado_display: string
  observaciones?: string
  created_at: string
  updated_at: string
}

export interface CreateVentaData {
  cliente: number
  unidad: number
  fecha_venta: string
  tipo_pago: Venta['tipo_pago']
  subtotal: number
  estado: Venta['estado']
  observaciones?: string
}

export interface CreateClienteData {
  nombre: string
  apellido: string
  dni?: string
  ruc?: string
  telefono?: string
  correo?: string
  direccion?: string
  tipo_cliente: Cliente['tipo_cliente']
}

export interface CreateUnidadData {
  nombre: string
  descripcion?: string
}

export interface SalesState {
  ventas: {
    items: Venta[]
    isLoading: boolean
    error: string | null
  }
  clientes: {
    items: Cliente[]
    isLoading: boolean
    error: string | null
  }
  unidades: {
    items: Unidad[]
    isLoading: boolean
    error: string | null
  }
}
```

### 3.2 Sales API

**src/features/sales/salesAPI.ts**
```typescript
import { api } from '../../shared/lib/api'
import { 
  Venta, 
  Cliente, 
  Unidad,
  CreateVentaData,
  CreateClienteData,
  CreateUnidadData
} from './salesTypes'

export const salesAPI = {
  // Ventas endpoints
  getVentas: async (): Promise<Venta[]> => {
    const response = await api.get<Venta[]>('/api/sales/ventas/')
    return response.data
  },

  getVenta: async (id: number): Promise<Venta> => {
    const response = await api.get<Venta>(`/api/sales/ventas/${id}/`)
    return response.data
  },

  createVenta: async (data: CreateVentaData): Promise<Venta> => {
    const response = await api.post<Venta>('/api/sales/ventas/', data)
    return response.data
  },

  updateVenta: async (id: number, data: Partial<CreateVentaData>): Promise<Venta> => {
    const response = await api.put<Venta>(`/api/sales/ventas/${id}/`, data)
    return response.data
  },

  deleteVenta: async (id: number): Promise<void> => {
    await api.delete(`/api/sales/ventas/${id}/`)
  },

  // Clientes endpoints
  getClientes: async (): Promise<Cliente[]> => {
    const response = await api.get<Cliente[]>('/api/entities/clientes/')
    return response.data
  },

  getCliente: async (id: number): Promise<Cliente> => {
    const response = await api.get<Cliente>(`/api/entities/clientes/${id}/`)
    return response.data
  },

  createCliente: async (data: CreateClienteData): Promise<Cliente> => {
    const response = await api.post<Cliente>('/api/entities/clientes/', data)
    return response.data
  },

  updateCliente: async (id: number, data: Partial<CreateClienteData>): Promise<Cliente> => {
    const response = await api.put<Cliente>(`/api/entities/clientes/${id}/`, data)
    return response.data
  },

  deleteCliente: async (id: number): Promise<void> => {
    await api.delete(`/api/entities/clientes/${id}/`)
  },

  // Unidades endpoints
  getUnidades: async (): Promise<Unidad[]> => {
    const response = await api.get<Unidad[]>('/api/entities/unidades/')
    return response.data
  },

  createUnidad: async (data: CreateUnidadData): Promise<Unidad> => {
    const response = await api.post<Unidad>('/api/entities/unidades/', data)
    return response.data
  },

  updateUnidad: async (id: number, data: Partial<CreateUnidadData>): Promise<Unidad> => {
    const response = await api.put<Unidad>(`/api/entities/unidades/${id}/`, data)
    return response.data
  },

  deleteUnidad: async (id: number): Promise<void> => {
    await api.delete(`/api/entities/unidades/${id}/`)
  }
}
```

## 🧪 PRUEBAS FASE 3

### 3.3 Manual Testing Script

**tests/phase3-manual-tests.md**
```markdown
# Fase 3 - Pruebas Manuales de Ventas y Entidades

## Pre-requisitos
- Fases 1 y 2 completadas exitosamente
- Backend Django ejecutándose en puerto 8000
- Datos de prueba: clientes, unidades, productos

## Pruebas a Realizar

### 1. Gestión de Clientes - CRUD Completo ✅

#### Crear Cliente
- [ ] Formulario de creación funciona
- [ ] Validaciones de DNI/RUC funcionan
- [ ] Tipos de cliente (persona/empresa) funcionan
- [ ] Cliente se crea exitosamente

#### Leer Clientes
- [ ] Lista de clientes se carga
- [ ] Filtros por tipo funcionan
- [ ] Búsqueda por nombre/DNI funciona

#### Actualizar Cliente
- [ ] Edición funciona correctamente
- [ ] Validaciones se mantienen

#### Eliminar Cliente
- [ ] Eliminación funciona (si no tiene ventas)
- [ ] Validación de integridad referencial

### 2. Gestión de Unidades - CRUD Completo ✅

#### Crear Unidad
- [ ] Formulario funciona correctamente
- [ ] Unidad se crea exitosamente

#### Leer Unidades
- [ ] Lista se carga correctamente
- [ ] Filtros funcionan

#### Actualizar Unidad
- [ ] Edición funciona

#### Eliminar Unidad
- [ ] Eliminación funciona

### 3. Gestión de Ventas - CRUD Completo ✅

#### Crear Venta
- [ ] Formulario de venta funciona
- [ ] Selección de cliente funciona
- [ ] Selección de unidad funciona
- [ ] Cálculo automático de IGV funciona
- [ ] Tipos de pago funcionan
- [ ] Venta se crea exitosamente

#### Leer Ventas
- [ ] Lista de ventas se carga
- [ ] Filtros por fecha funcionan
- [ ] Filtros por estado funcionan
- [ ] Totales se muestran correctamente

#### Actualizar Venta
- [ ] Edición funciona
- [ ] Recálculo de totales funciona
- [ ] Estados se actualizan

#### Eliminar Venta
- [ ] Eliminación funciona
- [ ] Confirmación se muestra

### 4. Validaciones de Negocio ✅
- [ ] IGV se calcula automáticamente (18%)
- [ ] Subtotal + IGV = Total
- [ ] Fechas de venta válidas
- [ ] Estados de venta válidos

## Criterios de Éxito
- ✅ Todos los CRUD funcionan
- ✅ Cálculos automáticos correctos
- ✅ Validaciones de negocio funcionan
- ✅ Integridad referencial mantenida
```

---

## 🚀 FASE 4: Dashboard y Servicios

### Objetivos
- Dashboard con KPIs principales
- Módulo de servicios y tipos de trabajo
- Reportes y estadísticas
- Optimización final y testing completo

### 4.1 Dashboard Types

**src/features/dashboard/dashboardTypes.ts**
```typescript
export interface DashboardKPI {
  total_ventas_mes: number
  total_ingresos_mes: number
  total_gps_activos: number
  total_sim_activas: number
  total_clientes_activos: number
  ventas_pendientes: number
  productos_bajo_stock: number
  servicios_pendientes: number
}

export interface VentasPorMes {
  mes: string
  total: number
  cantidad: number
}

export interface ProductosBajoStock {
  id: number
  nombre: string
  stock_actual: number
  stock_minimo: number
}

export interface DashboardState {
  kpis: DashboardKPI | null
  ventasPorMes: VentasPorMes[]
  productosBajoStock: ProductosBajoStock[]
  isLoading: boolean
  error: string | null
}
```

## 🧪 PRUEBAS FASE 4

### 4.2 Final Testing Script

**tests/phase4-final-tests.md**
```markdown
# Fase 4 - Pruebas Finales y Dashboard

## Pre-requisitos
- Todas las fases anteriores completadas
- Datos de prueba suficientes en el sistema

## Pruebas a Realizar

### 1. Dashboard ✅
- [ ] KPIs se cargan correctamente
- [ ] Gráficos se muestran
- [ ] Datos en tiempo real
- [ ] Responsive design

### 2. Servicios ✅
- [ ] CRUD de tipos de trabajo
- [ ] CRUD de servicios
- [ ] Asignación de servicios

### 3. Pruebas de Integración ✅
- [ ] Flujo completo: Cliente → Venta → Inventario
- [ ] Actualizaciones en tiempo real
- [ ] Consistencia de datos

### 4. Pruebas de Performance ✅
- [ ] Carga inicial < 3 segundos
- [ ] Navegación fluida
- [ ] Manejo de listas grandes

### 5. Pruebas de Usabilidad ✅
- [ ] UI intuitiva
- [ ] Mensajes de error claros
- [ ] Feedback visual adecuado

## Criterios de Aprobación Final
- ✅ Todas las funcionalidades implementadas
- ✅ Todas las pruebas pasan
- ✅ Performance aceptable
- ✅ UI/UX de calidad
- ✅ Código mantenible y escalable
```

## 📋 SCRIPTS DE TESTING AUTOMATIZADO

### Testing Script Principal

**scripts/run-all-tests.sh**
```bash
#!/bin/bash

echo "🧪 Ejecutando todas las pruebas del frontend..."

# Verificar que el backend esté ejecutándose
echo "1. Verificando backend en puerto 8000..."
if ! curl -s http://127.0.0.1:8000/api/ > /dev/null; then
    echo "❌ Backend no está ejecutándose en puerto 8000"
    exit 1
fi
echo "✅ Backend disponible"

# Instalar dependencias
echo "2. Instalando dependencias..."
npm install

# Verificar tipos TypeScript
echo "3. Verificando tipos TypeScript..."
npm run type-check
if [ $? -ne 0 ]; then
    echo "❌ Errores de TypeScript encontrados"
    exit 1
fi
echo "✅ Tipos TypeScript correctos"

# Ejecutar tests unitarios
echo "4. Ejecutando tests unitarios..."
npm run test
if [ $? -ne 0 ]; then
    echo "❌ Tests unitarios fallaron"
    exit 1
fi
echo "✅ Tests unitarios pasaron"

# Ejecutar build
echo "5. Ejecutando build de producción..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build falló"
    exit 1
fi
echo "✅ Build exitoso"

# Ejecutar tests de API
echo "6. Ejecutando tests de API..."
node tests/api-test.js
if [ $? -ne 0 ]; then
    echo "❌ Tests de API fallaron"
    exit 1
fi
echo "✅ Tests de API pasaron"

echo "🎉 Todas las pruebas completadas exitosamente!"
echo "✅ Frontend listo para producción"
```

## 🎯 RESUMEN DE IMPLEMENTACIÓN

### Tecnologías Utilizadas
- **React 18** con TypeScript estricto
- **Vite** para desarrollo y build
- **Redux Toolkit** para gestión de estado
- **Redux Persist** para persistencia
- **React Hook Form + Zod** para formularios
- **Tailwind CSS** para estilos
- **Axios** para API calls
- **React Router** para navegación

### Arquitectura
- **Modular**: Cada feature en su propio módulo
- **Escalable**: Fácil agregar nuevas funcionalidades
- **Mantenible**: Código limpio y bien documentado
- **Performante**: Optimizaciones desde el diseño

### Características Principales
- ✅ **Autenticación JWT** completa con refresh automático
- ✅ **CRUD completo** para todos los módulos
- ✅ **Validaciones robustas** con Zod
- ✅ **Estado persistente** con Redux Persist
- ✅ **Manejo de errores** comprehensivo
- ✅ **UI moderna** y responsive
- ✅ **TypeScript estricto** sin uso de `any`
- ✅ **Testing** manual y automatizado

### Próximos Pasos
1. Ejecutar `scripts/run-all-tests.sh`
2. Verificar que todas las pruebas pasen
3. Desplegar en ambiente de staging
4. Realizar pruebas de usuario final
5. Desplegar en producción

---

**¡Implementación por fases completada! 🎉**

Cada fase debe completarse y probarse exhaustivamente antes de continuar con la siguiente. No se permite avanzar si hay errores o funcionalidades incompletas.