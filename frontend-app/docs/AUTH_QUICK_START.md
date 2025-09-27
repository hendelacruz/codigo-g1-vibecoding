# 🚀 Guía de Inicio Rápido - Sistema de Autenticación

## 📋 Tabla de Contenidos

1. [Instalación y Configuración](#instalación-y-configuración)
2. [Uso Básico](#uso-básico)
3. [Hooks Disponibles](#hooks-disponibles)
4. [Ejemplos Comunes](#ejemplos-comunes)
5. [Troubleshooting](#troubleshooting)

## 🛠️ Instalación y Configuración

### 1. Dependencias Requeridas

```bash
npm install @reduxjs/toolkit react-redux
npm install @types/react-redux # Si usas TypeScript
```

### 2. Configuración del Store

```typescript
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### 3. Configuración del Provider

```typescript
// src/App.tsx
import { Provider } from 'react-redux'
import { store } from './store'

function App() {
  return (
    <Provider store={store}>
      {/* Tu aplicación */}
    </Provider>
  )
}
```

## 🎯 Uso Básico

### 1. Hook Principal: useAuthOptimized

```typescript
import { useAuthOptimized } from '@/hooks/useAuthOptimized'

const MyComponent = () => {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    login, 
    logout 
  } = useAuthOptimized()

  if (isLoading) return <div>Loading...</div>
  
  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />
  }

  return (
    <div>
      <h1>Welcome, {user?.first_name}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

### 2. Hook de Permisos: useAuthWithPermissions

```typescript
import { useAuthWithPermissions } from '@/hooks/useAuthWithPermissions'

const AdminPanel = () => {
  const { hasRole, canAccess } = useAuthWithPermissions()

  const isAdmin = hasRole('Administradores')
  const canManageUsers = canAccess('users', 'create')

  if (!isAdmin) {
    return <div>Access denied</div>
  }

  return (
    <div>
      <h1>Admin Panel</h1>
      {canManageUsers && <UserManagement />}
    </div>
  )
}
```

### 3. Hook de Errores: useAuthErrorHandler

```typescript
import { useAuthErrorHandler } from '@/hooks/useAuthErrorHandler'

const ApiComponent = () => {
  const { handleAuthError, lastError } = useAuthErrorHandler()

  const fetchData = async () => {
    try {
      const response = await api.get('/data')
      return response.data
    } catch (error) {
      await handleAuthError(error)
    }
  }

  return (
    <div>
      {lastError && <ErrorAlert error={lastError} />}
      <button onClick={fetchData}>Fetch Data</button>
    </div>
  )
}
```

## 🎣 Hooks Disponibles

### useAuthOptimized

**Propósito**: Hook principal optimizado para performance

```typescript
const {
  // Estado básico
  user,                    // Usuario actual
  token,                   // JWT token
  isAuthenticated,         // Estado de autenticación
  isLoading,              // Estado de carga
  error,                  // Errores de autenticación

  // Valores computados
  userDisplayName,        // Nombre completo del usuario
  userRole,              // Rol del usuario
  hasValidToken,         // Si el token es válido

  // Acciones
  login,                 // Función de login
  logout,                // Función de logout
  refreshAuth,           // Renovar token
  checkStatus,           // Verificar estado
  
  // Gestión de estado
  setAuthToken,          // Establecer token
  updateUserData,        // Actualizar datos del usuario
  clearAuthError         // Limpiar errores
} = useAuthOptimized()
```

### useAuthWithPermissions

**Propósito**: Hook con funcionalidades de permisos y roles

```typescript
const {
  // Todo lo de useAuthOptimized +
  
  // Verificación de permisos
  hasPermission,         // (permission: string) => boolean
  hasRole,              // (role: string) => boolean
  canAccess,            // (resource: string, action: string) => boolean
  
  // Utilidades avanzadas
  checkMultiplePermissions,  // (permissions: string[]) => boolean
  getAccessLevel,           // (resource: string) => AccessLevel
  getUserSummary,          // () => UserSummary
  quickPermissions         // Permisos comunes pre-calculados
} = useAuthWithPermissions()
```

### useAuthErrorHandler

**Propósito**: Manejo centralizado de errores de autenticación

```typescript
const {
  // Manejo de errores
  handleAuthError,       // (error: any) => Promise<void>
  clearError,           // () => void
  resetRetryCounters,   // () => void
  
  // Estado
  lastError,            // Último error procesado
  isRecovering,         // Si está en proceso de recuperación
  
  // Utilidades
  isRecoverable,        // (error: any) => boolean
  parseError,           // (error: any) => AuthError
  getErrorStats         // () => ErrorStats
} = useAuthErrorHandler(options?)
```

## 💡 Ejemplos Comunes

### 1. Formulario de Login

```typescript
import { useState } from 'react'
import { useAuthOptimized } from '@/hooks/useAuthOptimized'

const LoginForm = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  
  const { login, isLoading, error } = useAuthOptimized()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await login(credentials)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Username"
        value={credentials.username}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          username: e.target.value
        }))}
      />
      
      <input
        type="password"
        placeholder="Password"
        value={credentials.password}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          password: e.target.value
        }))}
      />
      
      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
```

### 2. Ruta Protegida

```typescript
import { Navigate } from 'react-router-dom'
import { useAuthWithPermissions } from '@/hooks/useAuthWithPermissions'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
  requiredPermission?: string
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermission
}) => {
  const { 
    isAuthenticated, 
    hasRole, 
    hasPermission 
  } = useAuthWithPermissions()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
}

// Uso
<ProtectedRoute requiredRole="Administradores">
  <AdminDashboard />
</ProtectedRoute>
```

### 3. Componente con Permisos Condicionales

```typescript
import { useAuthWithPermissions } from '@/hooks/useAuthWithPermissions'

const UserTable = () => {
  const { canAccess, getAccessLevel } = useAuthWithPermissions()
  
  const userAccess = getAccessLevel('users')

  return (
    <div>
      <h2>Users</h2>
      
      {userAccess.canCreate && (
        <button>Add New User</button>
      )}
      
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            {userAccess.canUpdate && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              {userAccess.canUpdate && (
                <td>
                  <button>Edit</button>
                  {userAccess.canDelete && (
                    <button>Delete</button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### 4. Manejo de Errores Automático

```typescript
import { useAuthErrorHandler } from '@/hooks/useAuthErrorHandler'

const DataFetcher = () => {
  const [data, setData] = useState(null)
  const { handleAuthError, lastError } = useAuthErrorHandler({
    maxRetries: 3,
    enableAutoRecovery: true
  })

  const fetchData = async () => {
    try {
      const response = await fetch('/api/data', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const result = await response.json()
      setData(result)
    } catch (error) {
      // El error handler se encarga de la lógica de recuperación
      await handleAuthError(error)
    }
  }

  return (
    <div>
      {lastError && (
        <div className="error-banner">
          Error: {lastError.message}
          {lastError.recoverable && " (Attempting recovery...)"}
        </div>
      )}
      
      <button onClick={fetchData}>Fetch Data</button>
      
      {data && <DataDisplay data={data} />}
    </div>
  )
}
```

### 5. Verificación de Múltiples Permisos

```typescript
import { useAuthWithPermissions } from '@/hooks/useAuthWithPermissions'

const ComplexComponent = () => {
  const { checkMultiplePermissions, quickPermissions } = useAuthWithPermissions()

  // Verificar múltiples permisos a la vez
  const hasUserManagementAccess = checkMultiplePermissions([
    'users.read',
    'users.edit'
  ])

  // Usar permisos pre-calculados para mejor performance
  const { canManageUsers, canViewReports } = quickPermissions

  return (
    <div>
      {hasUserManagementAccess && <UserManagement />}
      {canViewReports && <ReportsSection />}
    </div>
  )
}
```

## 🔧 Troubleshooting

### Problema: "Cannot read properties of null"

**Causa**: El hook se está ejecutando antes de que el store esté inicializado.

**Solución**:
```typescript
// Asegúrate de que el Provider esté correctamente configurado
<Provider store={store}>
  <App />
</Provider>

// O usa un loading state
const { user, isLoading } = useAuthOptimized()

if (isLoading) {
  return <LoadingSpinner />
}
```

### Problema: "Hook is not updating"

**Causa**: El componente no está suscrito a los cambios del store.

**Solución**:
```typescript
// Verifica que estés usando el hook correctamente
const { isAuthenticated } = useAuthOptimized() // ✅ Correcto

// No hagas esto:
const auth = useSelector(state => state.auth) // ❌ No optimizado
```

### Problema: "Permission check always returns false"

**Causa**: Los permisos no están cargados o el formato es incorrecto.

**Solución**:
```typescript
// Verifica que el usuario tenga permisos cargados
const { user, hasPermission } = useAuthWithPermissions()

console.log('User permissions:', user?.permissions) // Debug

// Asegúrate de usar el formato correcto
const canEdit = hasPermission('users.edit') // ✅ Correcto
const canEdit = hasPermission('edit users') // ❌ Formato incorrecto
```

### Problema: "Token refresh not working"

**Causa**: El interceptor de Axios no está configurado correctamente.

**Solución**:
```typescript
// Verifica la configuración del API
// src/features/auth/authAPI.ts
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Lógica de refresh token
      await store.dispatch(refreshAuthToken())
    }
    return Promise.reject(error)
  }
)
```

## 📚 Recursos Adicionales

- [Documentación Completa](./AUTHENTICATION_ARCHITECTURE.md)
- [Ejemplos de Testing](../src/hooks/__tests__/)
- [Configuración de TypeScript](../tsconfig.json)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)

---

**¿Necesitas ayuda?** Consulta la documentación completa o contacta al equipo de desarrollo.

**Última actualización**: Enero 2024