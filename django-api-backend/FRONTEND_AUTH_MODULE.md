# Módulo de Autenticación para Frontend React + Vite

## 🎯 Objetivo
Esta documentación proporciona una guía completa para implementar el módulo de autenticación en React utilizando los endpoints del backend Django REST Framework.

## 📋 Tabla de Contenidos
1. [Configuración Inicial](#configuración-inicial)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Endpoints Disponibles](#endpoints-disponibles)
4. [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
5. [Implementación del Context](#implementación-del-context)
6. [Componentes de Autenticación](#componentes-de-autenticación)
7. [Hooks Personalizados](#hooks-personalizados)
8. [Protección de Rutas](#protección-de-rutas)
9. [Manejo de Errores](#manejo-de-errores)
10. [Interceptores de Axios](#interceptores-de-axios)

---

## 🚀 Configuración Inicial

### Dependencias Requeridas
```bash
npm install axios react-router-dom @tanstack/react-query
npm install -D @types/node # Si usas TypeScript
```

### Variables de Entorno
Crear archivo `.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_TOKEN_STORAGE_KEY=auth_tokens
```

---

## 📁 Estructura del Proyecto

```
src/
├── auth/
│   ├── components/
│   │   ├── LoginForm.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── RoleGuard.jsx
│   │   └── UserProfile.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── usePermissions.js
│   │   └── useRoles.js
│   ├── services/
│   │   └── authService.js
│   └── types/
│       └── auth.types.js
├── utils/
│   ├── api.js
│   └── storage.js
└── App.jsx
```

---

## 🔗 Endpoints Disponibles

### Base URL
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/auth'
```

### Endpoints de Autenticación

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `POST` | `/login/` | Iniciar sesión | No |
| `POST` | `/logout/` | Cerrar sesión | Sí |
| `POST` | `/token/refresh/` | Renovar token | No |
| `GET` | `/auth/status/` | Estado de autenticación | No |

### Endpoints de Perfil

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/profile/` | Obtener perfil | Sí |
| `PATCH` | `/profile/` | Actualizar perfil | Sí |
| `POST` | `/change-password/` | Cambiar contraseña | Sí |

### Endpoints de Gestión (Solo Administradores)

| Método | Endpoint | Descripción | Autenticación | Permisos |
|--------|----------|-------------|---------------|----------|
| `GET` | `/users/` | Listar usuarios | Sí | Admin |
| `POST` | `/users/` | Crear usuario | Sí | Admin |
| `GET` | `/users/{id}/` | Obtener usuario | Sí | Admin |
| `PATCH` | `/users/{id}/` | Actualizar usuario | Sí | Admin |
| `DELETE` | `/users/{id}/` | Eliminar usuario | Sí | Admin |
| `GET` | `/roles/` | Listar roles | Sí | Todos |

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

## 🔧 Implementación del Context

### AuthContext.jsx
```javascript
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';
import { getStoredTokens, removeStoredTokens } from '../../utils/storage';

// Estados del contexto
const initialState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Tipos de acciones
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REFRESH_TOKEN: 'REFRESH_TOKEN',
  UPDATE_USER: 'UPDATE_USER',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_LOADING: 'SET_LOADING'
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    default:
      return state;
  }
}

// Context
const AuthContext = createContext();

// Provider
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Verificar autenticación al cargar
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const tokens = getStoredTokens();
      if (!tokens) {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        return;
      }

      const response = await authService.getAuthStatus();
      if (response.authenticated) {
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: response.user,
            tokens
          }
        });
      } else {
        removeStoredTokens();
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
      }
    } catch (error) {
      removeStoredTokens();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authService.login(credentials);
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user: response.user,
          tokens: {
            access: response.access,
            refresh: response.refresh
          }
        }
      });
      
      return { success: true };
    } catch (error) {
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: error.message || 'Error al iniciar sesión'
      });
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      if (state.tokens?.refresh) {
        await authService.logout(state.tokens.refresh);
      }
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      removeStoredTokens();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  const updateProfile = async (userData) => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      dispatch({
        type: AUTH_ACTIONS.UPDATE_USER,
        payload: updatedUser
      });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await authService.changePassword(passwordData);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const value = {
    ...state,
    login,
    logout,
    updateProfile,
    changePassword,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};
```

---

## 🛠️ Servicios de API

### authService.js
```javascript
import { api } from '../../utils/api';
import { storeTokens, getStoredTokens, removeStoredTokens } from '../../utils/storage';

export const authService = {
  // Iniciar sesión
  async login(credentials) {
    try {
      const response = await api.post('/auth/login/', credentials);
      
      // Almacenar tokens
      const tokens = {
        access: response.data.access,
        refresh: response.data.refresh
      };
      storeTokens(tokens);
      
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message || 
        'Error al iniciar sesión'
      );
    }
  },

  // Cerrar sesión
  async logout(refreshToken) {
    try {
      await api.post('/auth/logout/', { refresh: refreshToken });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      removeStoredTokens();
    }
  },

  // Renovar token
  async refreshToken() {
    try {
      const tokens = getStoredTokens();
      if (!tokens?.refresh) {
        throw new Error('No hay refresh token disponible');
      }

      const response = await api.post('/auth/token/refresh/', {
        refresh: tokens.refresh
      });

      const newTokens = {
        access: response.data.access,
        refresh: tokens.refresh
      };
      storeTokens(newTokens);

      return newTokens;
    } catch (error) {
      removeStoredTokens();
      throw new Error('Error al renovar token');
    }
  },

  // Verificar estado de autenticación
  async getAuthStatus() {
    try {
      const response = await api.get('/auth/auth/status/');
      return response.data;
    } catch (error) {
      throw new Error('Error al verificar estado de autenticación');
    }
  },

  // Obtener perfil
  async getProfile() {
    try {
      const response = await api.get('/auth/profile/');
      return response.data;
    } catch (error) {
      throw new Error('Error al obtener perfil');
    }
  },

  // Actualizar perfil
  async updateProfile(userData) {
    try {
      const response = await api.patch('/auth/profile/', userData);
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al actualizar perfil'
      );
    }
  },

  // Cambiar contraseña
  async changePassword(passwordData) {
    try {
      const response = await api.post('/auth/change-password/', passwordData);
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al cambiar contraseña'
      );
    }
  },

  // Gestión de usuarios (Solo administradores)
  async getUsers(params = {}) {
    try {
      const response = await api.get('/auth/users/', { params });
      return response.data;
    } catch (error) {
      throw new Error('Error al obtener usuarios');
    }
  },

  async createUser(userData) {
    try {
      const response = await api.post('/auth/users/', userData);
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al crear usuario'
      );
    }
  },

  async updateUser(userId, userData) {
    try {
      const response = await api.patch(`/auth/users/${userId}/`, userData);
      return response.data;
    } catch (error) {
      throw new Error('Error al actualizar usuario');
    }
  },

  async deleteUser(userId) {
    try {
      await api.delete(`/auth/users/${userId}/`);
    } catch (error) {
      throw new Error('Error al eliminar usuario');
    }
  },

  // Obtener roles
  async getRoles() {
    try {
      const response = await api.get('/auth/roles/');
      return response.data;
    } catch (error) {
      throw new Error('Error al obtener roles');
    }
  }
};
```

---

## 🔐 Hooks Personalizados

### usePermissions.js
```javascript
import { useAuth } from '../context/AuthContext';

export function usePermissions() {
  const { user } = useAuth();

  const hasPermission = (permission) => {
    if (!user || !user.rol) return false;
    
    // Los administradores tienen todos los permisos
    if (user.rol.nombre === 'administrador') return true;
    
    // Verificar permisos específicos del rol
    return user.rol.permisos?.[permission] || false;
  };

  const hasRole = (role) => {
    return user?.rol?.nombre === role;
  };

  const hasAnyRole = (roles) => {
    return roles.includes(user?.rol?.nombre);
  };

  const canAccess = (module, action) => {
    const permissionMap = {
      users: {
        create: 'can_manage_users',
        read: 'can_manage_users',
        update: 'can_manage_users',
        delete: 'can_manage_users'
      },
      inventory: {
        create: 'can_manage_inventory',
        read: 'can_read',
        update: 'can_manage_inventory',
        delete: 'can_delete'
      },
      services: {
        create: 'can_manage_services',
        read: 'can_read',
        update: 'can_manage_services',
        delete: 'can_delete'
      },
      sales: {
        create: 'can_manage_sales',
        read: 'can_read',
        update: 'can_manage_sales',
        delete: 'can_delete'
      },
      reports: {
        read: 'can_view_reports'
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
    isAdmin: hasRole('administrador'),
    isOperator: hasRole('operador'),
    isTechnician: hasRole('tecnico')
  };
}
```

---

## 🛡️ Componentes de Protección

### ProtectedRoute.jsx
```javascript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function ProtectedRoute({ children, requireAuth = true }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!requireAuth && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
```

### RoleGuard.jsx
```javascript
import React from 'react';
import { usePermissions } from '../hooks/usePermissions';

export function RoleGuard({ 
  children, 
  roles = [], 
  permissions = [], 
  fallback = null,
  requireAll = false 
}) {
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

  return children;
}
```

---

## 📱 Componentes de UI

### LoginForm.jsx
```javascript
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

export function LoginForm() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  
  const { login, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    const result = await login(credentials);
    if (result.success) {
      navigate(from, { replace: true });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
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
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Usuario
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={credentials.username}
                onChange={handleChange}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Ingresa tu usuario"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Contraseña
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={credentials.password}
                  onChange={handleChange}
                  className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Ingresa tu contraseña"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## 🔧 Utilidades

### api.js
```javascript
import axios from 'axios';
import { getStoredTokens, removeStoredTokens, storeTokens } from './storage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

// Crear instancia de axios
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const tokens = getStoredTokens();
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y renovar tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const tokens = getStoredTokens();
        if (tokens?.refresh) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: tokens.refresh
          });

          const newTokens = {
            access: response.data.access,
            refresh: tokens.refresh
          };
          storeTokens(newTokens);

          // Reintentar petición original con nuevo token
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        removeStoredTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### storage.js
```javascript
const TOKEN_STORAGE_KEY = import.meta.env.VITE_TOKEN_STORAGE_KEY || 'auth_tokens';

export const storeTokens = (tokens) => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
  } catch (error) {
    console.error('Error al almacenar tokens:', error);
  }
};

export const getStoredTokens = () => {
  try {
    const tokens = localStorage.getItem(TOKEN_STORAGE_KEY);
    return tokens ? JSON.parse(tokens) : null;
  } catch (error) {
    console.error('Error al obtener tokens:', error);
    return null;
  }
};

export const removeStoredTokens = () => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch (error) {
    console.error('Error al eliminar tokens:', error);
  }
};
```

---

## 🚦 Configuración de Rutas

### App.jsx
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './auth/context/AuthContext';
import { ProtectedRoute } from './auth/components/ProtectedRoute';
import { RoleGuard } from './auth/components/RoleGuard';
import { LoginForm } from './auth/components/LoginForm';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Inventory from './pages/Inventory';
import Services from './pages/Services';
import Sales from './pages/Sales';
import Reports from './pages/Reports';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Rutas públicas */}
            <Route 
              path="/login" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <LoginForm />
                </ProtectedRoute>
              } 
            />

            {/* Rutas protegidas */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />

            {/* Gestión de usuarios - Solo administradores */}
            <Route 
              path="/users/*" 
              element={
                <ProtectedRoute>
                  <RoleGuard roles={['administrador']}>
                    <Users />
                  </RoleGuard>
                </ProtectedRoute>
              } 
            />

            {/* Inventario - Administradores y Operadores */}
            <Route 
              path="/inventory/*" 
              element={
                <ProtectedRoute>
                  <RoleGuard 
                    roles={['administrador', 'operador']}
                    permissions={['can_manage_inventory']}
                  >
                    <Inventory />
                  </RoleGuard>
                </ProtectedRoute>
              } 
            />

            {/* Servicios - Todos los roles */}
            <Route 
              path="/services/*" 
              element={
                <ProtectedRoute>
                  <RoleGuard permissions={['can_read']}>
                    <Services />
                  </RoleGuard>
                </ProtectedRoute>
              } 
            />

            {/* Ventas - Administradores y Operadores */}
            <Route 
              path="/sales/*" 
              element={
                <ProtectedRoute>
                  <RoleGuard 
                    roles={['administrador', 'operador']}
                    permissions={['can_manage_sales']}
                  >
                    <Sales />
                  </RoleGuard>
                </ProtectedRoute>
              } 
            />

            {/* Reportes - Administradores y Operadores */}
            <Route 
              path="/reports/*" 
              element={
                <ProtectedRoute>
                  <RoleGuard permissions={['can_view_reports']}>
                    <Reports />
                  </RoleGuard>
                </ProtectedRoute>
              } 
            />

            {/* Redirección por defecto */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

## 🎨 Ejemplo de Uso en Componentes

### Dashboard con información del usuario
```javascript
import React from 'react';
import { useAuth } from '../auth/context/AuthContext';
import { usePermissions } from '../auth/hooks/usePermissions';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { hasPermission, isAdmin, isOperator, isTechnician } = usePermissions();

  const handleLogout = async () => {
    await logout();
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
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card para Gestión de Usuarios */}
          {isAdmin && (
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <h3 className="text-lg font-medium text-gray-900">
                  Gestión de Usuarios
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Administrar usuarios del sistema
                </p>
              </div>
            </div>
          )}

          {/* Card para Inventario */}
          {hasPermission('can_manage_inventory') && (
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <h3 className="text-lg font-medium text-gray-900">
                  Inventario
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Gestionar GPS y SIM Cards
                </p>
              </div>
            </div>
          )}

          {/* Card para Servicios */}
          {hasPermission('can_manage_services') && (
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <h3 className="text-lg font-medium text-gray-900">
                  Servicios
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {isTechnician ? 'Mis servicios asignados' : 'Gestionar servicios'}
                </p>
              </div>
            </div>
          )}

          {/* Card para Ventas */}
          {hasPermission('can_manage_sales') && (
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <h3 className="text-lg font-medium text-gray-900">
                  Ventas
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Gestionar ventas y cotizaciones
                </p>
              </div>
            </div>
          )}

          {/* Card para Reportes */}
          {hasPermission('can_view_reports') && (
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <h3 className="text-lg font-medium text-gray-900">
                  Reportes
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Ver reportes y estadísticas
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
```

---

## 🚨 Manejo de Errores

### Tipos de errores comunes
```javascript
export const AUTH_ERRORS = {
  INVALID_CREDENTIALS: 'Credenciales inválidas',
  TOKEN_EXPIRED: 'Sesión expirada',
  INSUFFICIENT_PERMISSIONS: 'Permisos insuficientes',
  NETWORK_ERROR: 'Error de conexión',
  VALIDATION_ERROR: 'Error de validación'
};

export const handleAuthError = (error) => {
  if (error.response?.status === 401) {
    return AUTH_ERRORS.INVALID_CREDENTIALS;
  }
  
  if (error.response?.status === 403) {
    return AUTH_ERRORS.INSUFFICIENT_PERMISSIONS;
  }
  
  if (error.response?.status === 400) {
    return error.response.data?.detail || AUTH_ERRORS.VALIDATION_ERROR;
  }
  
  if (!error.response) {
    return AUTH_ERRORS.NETWORK_ERROR;
  }
  
  return 'Error desconocido';
};
```

---

## 📝 Validaciones del Frontend

### Validaciones de formularios
```javascript
export const authValidations = {
  username: {
    required: 'El usuario es requerido',
    minLength: {
      value: 3,
      message: 'El usuario debe tener al menos 3 caracteres'
    }
  },
  
  password: {
    required: 'La contraseña es requerida',
    minLength: {
      value: 8,
      message: 'La contraseña debe tener al menos 8 caracteres'
    }
  },
  
  dni: {
    required: 'El DNI es requerido',
    pattern: {
      value: /^\d{8}$/,
      message: 'El DNI debe tener exactamente 8 dígitos'
    }
  },
  
  email: {
    required: 'El email es requerido',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Email inválido'
    }
  },
  
  celular: {
    required: 'El celular es requerido',
    pattern: {
      value: /^9\d{8}$/,
      message: 'El celular debe empezar con 9 y tener 9 dígitos'
    }
  }
};
```

---

## 🔄 Rate Limiting en Frontend

### Implementación de rate limiting
```javascript
class RateLimiter {
  constructor() {
    this.attempts = new Map();
  }

  canAttempt(key, maxAttempts = 5, windowMs = 15 * 60 * 1000) {
    const now = Date.now();
    const attempts = this.attempts.get(key) || [];
    
    // Filtrar intentos dentro de la ventana de tiempo
    const recentAttempts = attempts.filter(time => now - time < windowMs);
    
    if (recentAttempts.length >= maxAttempts) {
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