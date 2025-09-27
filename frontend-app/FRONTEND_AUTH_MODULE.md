# Módulo de Autenticación - React + Vite + TypeScript

## 🎯 Objetivo
Esta documentación actualizada proporciona una guía completa para trabajar con el módulo de autenticación ya implementado en tu proyecto React + Vite + TypeScript, utilizando Redux Toolkit y las mejores prácticas modernas.

## 📋 Tabla de Contenidos
1. [Estado Actual del Proyecto](#estado-actual-del-proyecto)
2. [Arquitectura Implementada](#arquitectura-implementada)
3. [Endpoints Disponibles](#endpoints-disponibles)
4. [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
5. [Redux Toolkit Implementation](#redux-toolkit-implementation)
6. [Componentes de Autenticación](#componentes-de-autenticación)
7. [Hooks y Servicios](#hooks-y-servicios)
8. [Protección de Rutas](#protección-de-rutas)
9. [Testing Strategy](#testing-strategy)
10. [Mejoras y Optimizaciones](#mejoras-y-optimizaciones)

---

## 🚀 Estado Actual del Proyecto

### ✅ Dependencias Ya Instaladas
Tu proyecto ya cuenta con todas las dependencias necesarias:

```json
{
  "dependencies": {
    "@hookform/resolvers": "^5.2.2",
    "@reduxjs/toolkit": "^2.9.0",
    "@tanstack/react-query": "^5.89.0",
    "axios": "^1.12.2",
    "react-hook-form": "^7.63.0",
    "react-redux": "^9.2.0",
    "react-router-dom": "^7.9.1",
    "redux-persist": "^6.0.0",
    "zod": "^4.1.9"
  }
}
```

### 🔧 Configuración TypeScript Estricta
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  }
}
```

### 🛠️ Variables de Entorno
```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## 📁 Arquitectura Implementada

### Estructura Actual del Proyecto
```
src/
├── features/
│   └── auth/
│       ├── components/
│       │   ├── AuthLayout.tsx
│       │   ├── LoginForm.tsx
│       │   └── ProtectedRoute.tsx
│       ├── hooks/
│       │   └── useAuth.ts
│       ├── services/
│       │   └── authApi.ts
│       ├── __tests__/
│       │   ├── authAPI.test.ts
│       │   └── ProtectedRoute.test.tsx
│       ├── authAPI.ts
│       ├── authConstants.ts
│       ├── authSlice.ts
│       ├── authTypes.ts
│       └── README_AUTH_API.md
├── shared/
│   ├── lib/
│   │   └── api.ts
│   └── types/
├── app/
│   ├── store.ts
│   └── rootReducer.ts
└── pages/
    └── LoginPage.tsx
```

---

## 🔗 Endpoints Disponibles

### Base URL
```typescript
const API_BASE_URL = 'http://127.0.0.1:8000/api/auth'
```

### Endpoints de Autenticación (Implementados en authAPI.ts)

| Método | Endpoint | Descripción | Autenticación | Implementado |
|--------|----------|-------------|---------------|-------------|
| `POST` | `/login/` | Iniciar sesión | No | ✅ |
| `POST` | `/logout/` | Cerrar sesión | Sí | ✅ |
| `POST` | `/token/refresh/` | Renovar token | No | ✅ |
| `GET` | `/auth/status/` | Estado de autenticación | No | ✅ |

### Endpoints de Perfil (Implementados)

| Método | Endpoint | Descripción | Autenticación | Implementado |
|--------|----------|-------------|---------------|-------------|
| `GET` | `/profile/` | Obtener perfil | Sí | ✅ |
| `PATCH` | `/profile/` | Actualizar perfil | Sí | ✅ |
| `POST` | `/change-password/` | Cambiar contraseña | Sí | ✅ |

### Endpoints de Gestión (Solo Administradores)

| Método | Endpoint | Descripción | Autenticación | Permisos | Implementado |
|--------|----------|-------------|---------------|----------|-------------|
| `GET` | `/users/` | Listar usuarios | Sí | Admin | ✅ |
| `POST` | `/users/` | Crear usuario | Sí | Admin | ✅ |
| `GET` | `/users/{id}/` | Obtener usuario | Sí | Admin | ✅ |
| `PATCH` | `/users/{id}/` | Actualizar usuario | Sí | Admin | ✅ |
| `DELETE` | `/users/{id}/` | Eliminar usuario | Sí | Admin | ✅ |
| `GET` | `/roles/` | Listar roles | Sí | Todos | ✅ |

---

## 👥 Sistema de Roles y Permisos

### Roles Disponibles

#### 🔴 Administrador
```javascript
const ADMIN_PERMISSIONS = {
  can_create: true,
  can_read: true,
  can_update: true,
  can_delete: true,
  can_manage_users: true,
  can_view_reports: true,
  can_manage_inventory: true,
  can_manage_services: true,
  can_manage_sales: true
}
```

#### 🟡 Operador
```javascript
const OPERATOR_PERMISSIONS = {
  can_create: true,
  can_read: true,
  can_update: true,
  can_delete: false,
  can_manage_users: false,
  can_view_reports: true,
  can_manage_inventory: true,
  can_manage_services: true,
  can_manage_sales: true
}
```

#### 🟢 Técnico
```javascript
const TECHNICIAN_PERMISSIONS = {
  can_create: true,        // Solo en servicios
  can_read: true,
  can_update: true,        // Solo en servicios
  can_delete: false,
  can_manage_users: false,
  can_view_reports: false,
  can_manage_inventory: false,  // Solo lectura
  can_manage_services: true,    // Acceso completo
  can_manage_sales: false       // Solo lectura
}
```

---

## 🔄 Redux Toolkit Implementation

### authSlice.ts (Implementación Actual)
```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from './authAPI';
import type { User, LoginCredentials, AuthState } from './authTypes';

// Async Thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Login failed');
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.refreshToken();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Token refresh failed');
    }
  }
);

export const fetchUserProfile = createAsyncThunk(
  'auth/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authAPI.getProfile();
      return user;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch profile');
    }
  }
);

// Initial State
const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Auth Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      authAPI.logout();
    },
    clearError: (state) => {
      state.error = null;
    },
    setCredentials: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      })
      // Refresh Token
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.token = action.payload.access;
      })
      // Fetch Profile
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      });
  },
});

export const { logout, clearError, setCredentials } = authSlice.actions;
export default authSlice.reducer;
```

### Store Configuration (app/store.ts)
```typescript
import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import authReducer from '@/features/auth/authSlice';

const authPersistConfig = {
  key: 'auth',
  storage,
  whitelist: ['user', 'token', 'refreshToken', 'isAuthenticated'],
};

const persistedAuthReducer = persistReducer(authPersistConfig, authReducer);

export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

---

## 🛠️ Servicios de API

### authAPI.ts (Implementación Actual)
```typescript
import axios, { AxiosResponse } from 'axios';
import type { 
  LoginCredentials, 
  LoginResponse, 
  RefreshTokenResponse, 
  User,
  UpdateProfileData,
  ChangePasswordData 
} from './authTypes';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Axios instance with interceptors
const authAPI = axios.create({
  baseURL: `${API_BASE_URL}/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
authAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
authAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authAPI.post('/token/refresh/', {
            refresh: refreshToken
          });
          
          const newToken = response.data.access;
          localStorage.setItem('access_token', newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          return authAPI(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export const authAPIService = {
  // Authentication
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await authAPI.post('/login/', credentials);
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    
    return response.data;
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    try {
      if (refreshToken) {
        await authAPI.post('/logout/', { refresh: refreshToken });
      }
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  async refreshToken(): Promise<RefreshTokenResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response: AxiosResponse<RefreshTokenResponse> = await authAPI.post('/token/refresh/', {
      refresh: refreshToken
    });

    localStorage.setItem('access_token', response.data.access);
    return response.data;
  },

  async getAuthStatus(): Promise<{ authenticated: boolean; user?: User }> {
    const response = await authAPI.get('/auth/status/');
    return response.data;
  },

  // Profile Management
  async getProfile(): Promise<User> {
    const response: AxiosResponse<User> = await authAPI.get('/profile/');
    return response.data;
  },

  async updateProfile(userData: UpdateProfileData): Promise<User> {
    const response: AxiosResponse<User> = await authAPI.patch('/profile/', userData);
    return response.data;
  },

  async changePassword(passwordData: ChangePasswordData): Promise<void> {
    await authAPI.post('/change-password/', passwordData);
  },

  // User Management (Admin only)
  async getUsers(params: Record<string, any> = {}): Promise<User[]> {
    const response: AxiosResponse<User[]> = await authAPI.get('/users/', { params });
    return response.data;
  },

  async createUser(userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await authAPI.post('/users/', userData);
    return response.data;
  },

  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await authAPI.patch(`/users/${userId}/`, userData);
    return response.data;
  },

  async deleteUser(userId: number): Promise<void> {
    await authAPI.delete(`/users/${userId}/`);
  },

  // Roles
  async getRoles(): Promise<string[]> {
    const response: AxiosResponse<string[]> = await authAPI.get('/roles/');
    return response.data;
  }
};

export default authAPIService;
```

---

## 🔐 Hooks y Servicios

### useAuth.ts (Implementación Actual)
```typescript
import { useAppSelector, useAppDispatch } from '@/app/hooks';
import { loginUser, logout, fetchUserProfile } from '@/features/auth/authSlice';
import type { LoginCredentials } from '@/features/auth/authTypes';

export function useAuth() {
  const dispatch = useAppDispatch();
  const { user, token, isAuthenticated, isLoading, error } = useAppSelector(
    (state) => state.auth
  );

  const login = async (credentials: LoginCredentials) => {
    return dispatch(loginUser(credentials)).unwrap();
  };

  const logoutUser = () => {
    dispatch(logout());
  };

  const refreshProfile = async () => {
    return dispatch(fetchUserProfile()).unwrap();
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout: logoutUser,
    refreshProfile,
  };
}
```

### usePermissions.ts (Implementación Mejorada)
```typescript
import { useAppSelector } from '@/app/hooks';
import type { User } from '@/features/auth/authTypes';

type Permission = string;
type Role = 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores';
type Module = 'users' | 'inventory' | 'services' | 'sales' | 'reports';
type Action = 'create' | 'read' | 'update' | 'delete';

export function usePermissions() {
  const { user } = useAppSelector((state) => state.auth);

  const hasPermission = (permission: Permission): boolean => {
    if (!user) return false;
    
    // Administradores tienen todos los permisos
    if (user.groups?.includes('Administradores')) return true;
    
    // Verificar permisos específicos
    return user.user_permissions?.includes(permission) || false;
  };

  const hasRole = (role: Role): boolean => {
    return user?.groups?.includes(role) || false;
  };

  const hasAnyRole = (roles: Role[]): boolean => {
    return roles.some(role => hasRole(role));
  };

  const canAccess = (module: Module, action: Action): boolean => {
    const permissionMap: Record<Module, Record<Action, Permission>> = {
      users: {
        create: 'auth.add_user',
        read: 'auth.view_user',
        update: 'auth.change_user',
        delete: 'auth.delete_user'
      },
      inventory: {
        create: 'inventory.add_dispositivo',
        read: 'inventory.view_dispositivo',
        update: 'inventory.change_dispositivo',
        delete: 'inventory.delete_dispositivo'
      },
      services: {
        create: 'services.add_servicio',
        read: 'services.view_servicio',
        update: 'services.change_servicio',
        delete: 'services.delete_servicio'
      },
      sales: {
        create: 'sales.add_venta',
        read: 'sales.view_venta',
        update: 'sales.change_venta',
        delete: 'sales.delete_venta'
      },
      reports: {
        create: 'reports.add_report',
        read: 'reports.view_reports',
        update: 'reports.change_report',
        delete: 'reports.delete_report'
      }
    };

    const permission = permissionMap[module]?.[action];
    return permission ? hasPermission(permission) : false;
  };

  return {
    hasPermission,
    hasRole,
    hasAnyRole,
    canAccess,
    isAdmin: hasRole('Administradores'),
    isSupervisor: hasRole('Supervisores'),
    isTechnician: hasRole('Técnicos'),
    isOperator: hasRole('Operadores'),
    user,
  };
}
```

---

## 🛡️ Componentes de Protección

### ProtectedRoute.tsx (Implementación Actual)
```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '@/app/hooks';
import { usePermissions } from '@/hooks/usePermissions';
import type { ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermission?: string;
  requiredRole?: 'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores';
  fallback?: ReactNode;
}

export function ProtectedRoute({ 
  children, 
  requiredPermission, 
  requiredRole,
  fallback = <Navigate to="/login" replace />
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAppSelector((state) => state.auth);
  const { hasPermission, hasRole } = usePermissions();
  const location = useLocation();

  // Mostrar loading mientras se verifica la autenticación
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Redirigir al login si no está autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Verificar permisos específicos
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Verificar roles específicos
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
```

### RoleGuard.tsx (Implementación Mejorada)
```typescript
import type { ReactNode } from 'react';
import { usePermissions } from '@/hooks/usePermissions';

interface RoleGuardProps {
  children: ReactNode;
  roles?: Array<'Administradores' | 'Supervisores' | 'Técnicos' | 'Operadores'>;
  permissions?: string[];
  fallback?: ReactNode;
  requireAll?: boolean;
}

export function RoleGuard({ 
  children, 
  roles = [], 
  permissions = [], 
  fallback = null,
  requireAll = false 
}: RoleGuardProps) {
  const { hasRole, hasPermission, hasAnyRole } = usePermissions();

  // Verificar roles
  const hasRequiredRole = roles.length === 0 || 
    (requireAll ? roles.every(role => hasRole(role)) : hasAnyRole(roles));

  // Verificar permisos
  const hasRequiredPermission = permissions.length === 0 || 
    (requireAll ? 
      permissions.every(permission => hasPermission(permission)) : 
      permissions.some(permission => hasPermission(permission))
    );

  if (!hasRequiredRole || !hasRequiredPermission) {
    return fallback || (
      <div className="text-center p-8">
        <h3 className="text-lg font-semibold text-gray-700">
          Acceso Denegado
        </h3>
        <p className="text-gray-500 mt-2">
          No tienes permisos para acceder a esta sección.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
```

---

## 📱 Componentes de UI

### LoginForm.tsx (Implementación Actual)
```typescript
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Button } from '@/shared/components/ui/Button';
import { Input } from '@/shared/components/ui/Input';
import { useNavigate } from 'react-router-dom';

const loginSchema = z.object({
  username: z.string().min(1, 'Username es requerido'),
  password: z.string().min(1, 'Password es requerido')
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm: React.FC = () => {
  const { login, isLoading, error, isAuthenticated, clearError } = useAuth();
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  const onSubmit = async (data: LoginFormData) => {
    await login(data);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Iniciar Sesión
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sistema de Gestión Logística
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              Error: {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <Input
                {...register('username')}
                placeholder="Username"
                error={errors.username?.message}
              />
            </div>
            
            <div>
              <Input
                {...register('password')}
                type="password"
                placeholder="Password"
                error={errors.password?.message}
              />
            </div>
          </div>

          <div>
            <Button
              type="submit"
              isLoading={isLoading}
              className="w-full"
            >
              {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

---

## 🔧 Utilidades y Configuración

### authAPI.ts (Implementación Actual)
```typescript
import axios, { type AxiosResponse } from 'axios';
import type { 
  LoginCredentials, 
  LoginResponse, 
  User, 
  RefreshTokenResponse 
} from '@/features/auth/authTypes';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

// Crear instancia de axios con configuración base
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar respuestas y renovar tokens automáticamente
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post<RefreshTokenResponse>(
            `${API_BASE_URL}/auth/token/refresh/`,
            { refresh: refreshToken }
          );

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Reintentar petición original con nuevo token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Token refresh falló, limpiar storage y redirigir
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Funciones de autenticación
export const authAPI = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await api.post('/auth/login/', credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh: refreshToken });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async refreshToken(): Promise<RefreshTokenResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response: AxiosResponse<RefreshTokenResponse> = await api.post(
      '/auth/token/refresh/',
      { refresh: refreshToken }
    );
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response: AxiosResponse<User> = await api.get('/auth/profile/');
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
};
```

---

## 🚦 Configuración de Rutas

### App.tsx (Implementación Actual)
```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from '@/app/store';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { RoleGuard } from '@/features/auth/components/RoleGuard';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { UsersPage } from '@/pages/UsersPage';
import { InventoryPage } from '@/pages/InventoryPage';
import { ServicesPage } from '@/pages/ServicesPage';
import { SalesPage } from '@/pages/SalesPage';
import { ReportsPage } from '@/pages/ReportsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

function App(): JSX.Element {
  return (
    <Provider store={store}>
      <PersistGate loading={<div>Loading...</div>} persistor={persistor}>
        <QueryClientProvider client={queryClient}>
          <Router>
            <Routes>
              {/* Rutas públicas */}
              <Route path="/login" element={<LoginPage />} />

              {/* Rutas protegidas */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                } 
              />

              {/* Gestión de usuarios - Solo administradores */}
              <Route 
                path="/users/*" 
                element={
                  <ProtectedRoute>
                    <RoleGuard roles={['Administradores']}>
                      <UsersPage />
                    </RoleGuard>
                  </ProtectedRoute>
                } 
              />

              {/* Inventario - Administradores y Supervisores */}
              <Route 
                path="/inventory/*" 
                element={
                  <ProtectedRoute>
                    <RoleGuard 
                      roles={['Administradores', 'Supervisores']}
                      permissions={['inventory.view_dispositivo']}
                    >
                      <InventoryPage />
                    </RoleGuard>
                  </ProtectedRoute>
                } 
              />

              {/* Servicios - Todos los roles autenticados */}
              <Route 
                path="/services/*" 
                element={
                  <ProtectedRoute>
                    <RoleGuard permissions={['services.view_servicio']}>
                      <ServicesPage />
                    </RoleGuard>
                  </ProtectedRoute>
                } 
              />

              {/* Ventas - Administradores y Supervisores */}
              <Route 
                path="/sales/*" 
                element={
                  <ProtectedRoute>
                    <RoleGuard 
                      roles={['Administradores', 'Supervisores']}
                      permissions={['sales.view_venta']}
                    >
                      <SalesPage />
                    </RoleGuard>
                  </ProtectedRoute>
                } 
              />

              {/* Reportes - Administradores y Supervisores */}
              <Route 
                path="/reports/*" 
                element={
                  <ProtectedRoute>
                    <RoleGuard 
                      roles={['Administradores', 'Supervisores']}
                      permissions={['reports.view_reports']}
                    >
                      <ReportsPage />
                    </RoleGuard>
                  </ProtectedRoute>
                } 
              />

              {/* Página no autorizada */}
              <Route path="/unauthorized" element={<div>No autorizado</div>} />

              {/* Redirección por defecto */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Ruta 404 */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Router>
        </QueryClientProvider>
      </PersistGate>
    </Provider>
  );
}

export default App;
```

---

## 🎨 Ejemplo de Uso en Componentes

### Dashboard con información del usuario (Implementación Actual)
```typescript
import React from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { usePermissions } from '@/features/auth/hooks/usePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

interface DashboardCardProps {
  title: string;
  description: string;
  href?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, description, href }) => (
  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
    <CardHeader>
      <CardTitle className="text-lg">{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
  </Card>
);

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const { hasPermission, isAdmin, isSupervisor, isTechnician } = usePermissions();

  const handleLogout = (): void => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Hola, {user?.first_name || user?.username}
              </span>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                {user?.rol?.nombre}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700"
              >
                Cerrar Sesión
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card para Gestión de Usuarios - Solo Administradores */}
          {isAdmin && (
            <DashboardCard
              title="Gestión de Usuarios"
              description="Administrar usuarios del sistema"
              href="/users"
            />
          )}

          {/* Card para Inventario - Administradores y Supervisores */}
          {hasPermission('inventory.view_dispositivo') && (
            <DashboardCard
              title="Inventario"
              description="Gestionar dispositivos GPS y SIM Cards"
              href="/inventory"
            />
          )}

          {/* Card para Servicios - Todos los roles */}
          {hasPermission('services.view_servicio') && (
            <DashboardCard
              title="Servicios"
              description={isTechnician ? 'Mis servicios asignados' : 'Gestionar servicios'}
              href="/services"
            />
          )}

          {/* Card para Ventas - Administradores y Supervisores */}
          {hasPermission('sales.view_venta') && (
            <DashboardCard
              title="Ventas"
              description="Gestionar ventas y cotizaciones"
              href="/sales"
            />
          )}

          {/* Card para Reportes - Administradores y Supervisores */}
          {hasPermission('reports.view_reports') && (
            <DashboardCard
              title="Reportes"
              description="Ver reportes y estadísticas del sistema"
              href="/reports"
            />
          )}

          {/* Card para Proveedores - Administradores y Supervisores */}
          {(isAdmin || isSupervisor) && (
            <DashboardCard
              title="Proveedores"
              description="Gestionar proveedores y contactos"
              href="/providers"
            />
          )}
        </div>
      </main>
    </div>
  );
};
```

---

## 🚨 Manejo de Errores

### Tipos de errores comunes (Implementación Actual)
```typescript
// types/auth.ts
export interface AuthError {
  code: string;
  message: string;
  details?: string;
}

export interface ApiError {
  response?: {
    status: number;
    data?: {
      detail?: string;
      message?: string;
      errors?: Record<string, string[]>;
    };
  };
  message: string;
}

// lib/auth-errors.ts
export const AUTH_ERRORS = {
  INVALID_CREDENTIALS: 'Credenciales inválidas',
  TOKEN_EXPIRED: 'Sesión expirada',
  INSUFFICIENT_PERMISSIONS: 'Permisos insuficientes',
  NETWORK_ERROR: 'Error de conexión',
  VALIDATION_ERROR: 'Error de validación',
  USER_NOT_FOUND: 'Usuario no encontrado',
  ACCOUNT_DISABLED: 'Cuenta deshabilitada',
  SERVER_ERROR: 'Error interno del servidor'
} as const;

export type AuthErrorType = typeof AUTH_ERRORS[keyof typeof AUTH_ERRORS];

export const handleAuthError = (error: ApiError): AuthErrorType => {
  // Error de red
  if (!error.response) {
    return AUTH_ERRORS.NETWORK_ERROR;
  }

  const { status, data } = error.response;

  switch (status) {
    case 401:
      return data?.detail === 'Token has expired' 
        ? AUTH_ERRORS.TOKEN_EXPIRED 
        : AUTH_ERRORS.INVALID_CREDENTIALS;
    
    case 403:
      return AUTH_ERRORS.INSUFFICIENT_PERMISSIONS;
    
    case 400:
      return data?.detail || data?.message || AUTH_ERRORS.VALIDATION_ERROR;
    
    case 404:
      return AUTH_ERRORS.USER_NOT_FOUND;
    
    case 500:
    case 502:
    case 503:
      return AUTH_ERRORS.SERVER_ERROR;
    
    default:
      return data?.detail || data?.message || 'Error desconocido';
  }
};

// Hook para manejo de errores
export const useAuthErrorHandler = () => {
  const handleError = (error: ApiError): string => {
    const errorMessage = handleAuthError(error);
    
    // Log del error para debugging
    console.error('Auth Error:', {
      status: error.response?.status,
      message: errorMessage,
      details: error.response?.data
    });
    
    return errorMessage;
  };

  return { handleError };
};
```

---

## 📝 Validaciones del Frontend

### Validaciones con Zod (Implementación Actual)
```typescript
// lib/validations/auth.ts
import { z } from 'zod';

// Schema para login
export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'El usuario es requerido')
    .min(3, 'El usuario debe tener al menos 3 caracteres')
    .max(150, 'El usuario no puede exceder 150 caracteres'),
  
  password: z
    .string()
    .min(1, 'La contraseña es requerida')
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
});

export type LoginFormData = z.infer<typeof loginSchema>;

// Schema para registro de usuario
export const userRegistrationSchema = z.object({
  username: z
    .string()
    .min(3, 'El usuario debe tener al menos 3 caracteres')
    .max(150, 'El usuario no puede exceder 150 caracteres')
    .regex(/^[a-zA-Z0-9_]+$/, 'Solo se permiten letras, números y guiones bajos'),
  
  email: z
    .string()
    .email('Email inválido')
    .max(254, 'El email no puede exceder 254 caracteres'),
  
  password: z
    .string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'La contraseña debe contener al menos una mayúscula, una minúscula y un número'),
  
  confirmPassword: z.string(),
  
  first_name: z
    .string()
    .min(1, 'El nombre es requerido')
    .max(30, 'El nombre no puede exceder 30 caracteres'),
  
  last_name: z
    .string()
    .min(1, 'El apellido es requerido')
    .max(30, 'El apellido no puede exceder 30 caracteres'),
  
  dni: z
    .string()
    .regex(/^\d{8}$/, 'El DNI debe tener exactamente 8 dígitos'),
  
  celular: z
    .string()
    .regex(/^9\d{8}$/, 'El celular debe empezar con 9 y tener 9 dígitos'),
  
  rol: z.number().min(1, 'Debe seleccionar un rol')
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword']
});

export type UserRegistrationFormData = z.infer<typeof userRegistrationSchema>;

// Schema para cambio de contraseña
export const changePasswordSchema = z.object({
  currentPassword: z
    .string()
    .min(1, 'La contraseña actual es requerida'),
  
  newPassword: z
    .string()
    .min(8, 'La nueva contraseña debe tener al menos 8 caracteres')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'La contraseña debe contener al menos una mayúscula, una minúscula y un número'),
  
  confirmNewPassword: z.string()
}).refine((data) => data.newPassword === data.confirmNewPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmNewPassword']
});

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

// Schema para perfil de usuario
export const userProfileSchema = z.object({
  first_name: z
    .string()
    .min(1, 'El nombre es requerido')
    .max(30, 'El nombre no puede exceder 30 caracteres'),
  
  last_name: z
    .string()
    .min(1, 'El apellido es requerido')
    .max(30, 'El apellido no puede exceder 30 caracteres'),
  
  email: z
    .string()
    .email('Email inválido')
    .max(254, 'El email no puede exceder 254 caracteres'),
  
  celular: z
    .string()
    .regex(/^9\d{8}$/, 'El celular debe empezar con 9 y tener 9 dígitos')
});

export type UserProfileFormData = z.infer<typeof userProfileSchema>;

// Validaciones personalizadas
export const customValidations = {
  // Validar que el username no esté en uso
  validateUniqueUsername: async (username: string): Promise<boolean> => {
    try {
      // Aquí iría la llamada a la API para verificar disponibilidad
      const response = await fetch(`/api/auth/check-username/${username}`);
      const data = await response.json();
      return data.available;
    } catch {
      return false;
    }
  },
  
  // Validar que el email no esté en uso
  validateUniqueEmail: async (email: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/auth/check-email/${email}`);
      const data = await response.json();
      return data.available;
    } catch {
      return false;
    }
  }
};
```

---

## 🚀 Mejoras Específicas del Proyecto

### 1. Optimizaciones de Performance
```typescript
// hooks/useAuthOptimized.ts
import { useMemo } from 'react';
import { useAppSelector } from '@/app/hooks';
import { selectAuth } from '@/features/auth/authSlice';

export const useAuthOptimized = () => {
  const auth = useAppSelector(selectAuth);
  
  // Memoizar valores computados para evitar re-renders innecesarios
  const authData = useMemo(() => ({
    isAuthenticated: !!auth.token && !!auth.user,
    user: auth.user,
    token: auth.token,
    isLoading: auth.isLoading,
    error: auth.error
  }), [auth.token, auth.user, auth.isLoading, auth.error]);
  
  return authData;
};
```

### 2. Interceptores Mejorados para Axios
```typescript
// lib/api-interceptors.ts
import { store } from '@/app/store';
import { logout, refreshToken } from '@/features/auth/authSlice';

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: string) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });
  
  failedQueue = [];
};

// Interceptor para manejar múltiples requests simultáneos
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const result = await store.dispatch(refreshToken()).unwrap();
        processQueue(null, result.access);
        originalRequest.headers.Authorization = `Bearer ${result.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        store.dispatch(logout());
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
```

### 3. Componente de Error Boundary para Auth
```typescript
// components/auth/AuthErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class AuthErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Auth Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <h2 className="text-xl font-semibold mb-4">Error de Autenticación</h2>
          <p className="text-gray-600 mb-4">
            Ha ocurrido un error inesperado. Por favor, intenta nuevamente.
          </p>
          <Button onClick={() => window.location.reload()}>
            Recargar Página
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 4. Hook para Persistencia Offline
```typescript
// hooks/useOfflineAuth.ts
import { useEffect, useState } from 'react';
import { useAuth } from './useAuth';

export const useOfflineAuth = () => {
  const { isAuthenticated, user } = useAuth();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState<any>(null);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated && user && isOnline) {
      // Guardar datos para uso offline
      localStorage.setItem('offline_user_data', JSON.stringify({
        user,
        timestamp: Date.now()
      }));
    }
  }, [isAuthenticated, user, isOnline]);

  const getOfflineUserData = () => {
    try {
      const data = localStorage.getItem('offline_user_data');
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  };

  return {
      isOnline,
      isAuthenticated: isOnline ? isAuthenticated : !!getOfflineUserData(),
      user: isOnline ? user : getOfflineUserData()?.user,
      offlineData: getOfflineUserData()
    };
  };
```

---

## 📋 Checklist de Implementación

### ✅ Completado
- [x] **Redux Toolkit** configurado con persistencia
- [x] **Autenticación JWT** con refresh tokens
- [x] **Componentes TypeScript** con tipado estricto
- [x] **React Hook Form + Zod** para validaciones
- [x] **Interceptores Axios** para manejo automático de tokens
- [x] **Rutas protegidas** con control de roles y permisos
- [x] **Hooks personalizados** para auth y permisos
- [x] **Manejo de errores** robusto
- [x] **Componentes UI** con Radix UI y Tailwind CSS

### 🔄 En Progreso
- [ ] Tests unitarios completos
- [ ] Tests de integración
- [ ] Documentación de componentes con Storybook
- [ ] Optimizaciones de performance avanzadas

### 📈 Próximas Mejoras
- [ ] Implementar 2FA (Two-Factor Authentication)
- [ ] Agregar logs de auditoría
- [ ] Implementar rate limiting en frontend
- [ ] Agregar notificaciones push
- [ ] Mejorar accesibilidad (ARIA labels)

---

## 🎯 Conclusiones

Este módulo de autenticación implementa las **mejores prácticas modernas** para aplicaciones React enterprise:

### 🏆 Fortalezas
1. **Arquitectura Escalable**: Estructura modular con separación clara de responsabilidades
2. **Type Safety**: TypeScript estricto en toda la aplicación
3. **Performance Optimizada**: Memoización, lazy loading y code splitting
4. **UX Excelente**: Manejo fluido de estados de carga y errores
5. **Seguridad Robusta**: JWT con refresh tokens y manejo seguro de credenciales
6. **Mantenibilidad**: Código limpio, documentado y testeable

### 🔧 Stack Tecnológico Utilizado
- **React 18+** con Concurrent Features
- **Redux Toolkit** para estado global
- **React Hook Form + Zod** para formularios
- **Axios** con interceptores inteligentes
- **Radix UI + Tailwind CSS** para UI moderna
- **Vite** para desarrollo y build optimizado
- **TypeScript** con configuración estricta

### 📚 Recursos Adicionales
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [React Hook Form Guide](https://react-hook-form.com/)
- [Zod Schema Validation](https://zod.dev/)
- [Radix UI Components](https://www.radix-ui.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

---

**Última actualización**: Diciembre 2024  
**Versión del documento**: 2.0  
**Estado**: ✅ Implementado y Actualizado
      return false;
    }
    
    // Agregar intento actual
    recentAttempts.push(now);
    this.attempts.set(key, recentAttempts);
    
    return true;
  }

  getRemainingTime(key, windowMs = 15 * 60 * 1000) {
    const attempts = this.attempts.get(key) || [];
    if (attempts.length === 0) return 0;
    
    const oldestAttempt = Math.min(...attempts);
    const remaining = windowMs - (Date.now() - oldestAttempt);
    
    return Math.max(0, remaining);
  }
}

export const rateLimiter = new RateLimiter();
```

---

## 🎯 Mejores Prácticas

### 1. Seguridad
- ✅ Nunca almacenar información sensible en localStorage
- ✅ Validar permisos en frontend Y backend
- ✅ Implementar rate limiting para login
- ✅ Usar HTTPS en producción
- ✅ Limpiar tokens al cerrar sesión

### 2. UX/UI
- ✅ Mostrar estados de carga
- ✅ Manejar errores de forma amigable
- ✅ Implementar auto-logout por inactividad
- ✅ Guardar estado de navegación para redirección post-login

### 3. Performance
- ✅ Usar React.memo para componentes pesados
- ✅ Implementar lazy loading para rutas
- ✅ Cachear datos de usuario y permisos
- ✅ Minimizar re-renders innecesarios

### 4. Mantenibilidad
- ✅ Separar lógica de negocio en hooks
- ✅ Usar TypeScript para mejor tipado
- ✅ Documentar componentes y funciones
- ✅ Implementar tests unitarios

---

## 🧪 Testing

### Ejemplo de test para AuthContext
```javascript
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe('AuthContext', () => {
  test('should login successfully', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      const response = await result.current.login({
        username: 'testuser',
        password: 'testpass123'
      });
      expect(response.success).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeDefined();
  });
});
```

---

## 📚 Recursos Adicionales

### Documentación de referencia
- [React Router](https://reactrouter.com/)
- [Axios](https://axios-http.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com/)

### Herramientas recomendadas
- **Estado global**: Zustand o Redux Toolkit
- **Formularios**: React Hook Form
- **UI Components**: Headless UI o Radix UI
- **Testing**: Vitest + Testing Library

---

## 🎉 Conclusión

Este módulo de autenticación proporciona una base sólida para implementar autenticación y autorización en React con Django REST Framework. Incluye:

- ✅ Autenticación JWT completa
- ✅ Sistema de roles y permisos granular
- ✅ Protección de rutas
- ✅ Manejo de errores robusto
- ✅ Interceptores para renovación automática de tokens
- ✅ Componentes reutilizables
- ✅ Hooks personalizados para lógica de negocio

¡Ahora puedes implementar un sistema de autenticación completo y seguro en tu aplicación React!