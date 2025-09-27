# Auth Slice - Redux Toolkit State Management

## Descripción General

El Auth Slice es el núcleo del manejo de estado de autenticación en la aplicación, implementado con Redux Toolkit. Proporciona un estado global centralizado para la autenticación de usuarios, incluyendo async thunks para operaciones asíncronas y reducers para actualizaciones de estado síncronas.

## Características Principales

### 🔄 Async Thunks
- **loginUser**: Autenticación de usuario con credenciales
- **logoutUser**: Cierre de sesión con limpieza de tokens
- **refreshAuthToken**: Renovación automática de tokens
- **checkAuthStatus**: Verificación del estado de autenticación
- **getUserProfile**: Obtención del perfil de usuario
- **changeUserPassword**: Cambio de contraseña
- **verifyUserToken**: Verificación de validez de tokens

### 🎛️ Reducers Síncronos
- **clearError**: Limpia errores del estado
- **setToken**: Establece token de acceso
- **setRefreshToken**: Establece token de renovación
- **updateUser**: Actualiza datos del usuario
- **clearAuth**: Limpia completamente el estado de autenticación
- **setLoading**: Controla el estado de carga

### 📊 Estado Global
```typescript
interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
```

## API Reference

### Async Thunks

#### `loginUser(credentials: LoginCredentials)`
```typescript
// Uso
dispatch(loginUser({ username: 'user', password: 'pass' }))

// Estados manejados:
// - pending: isLoading = true, error = null
// - fulfilled: user, token, refreshToken establecidos, isAuthenticated = true
// - rejected: error establecido, isAuthenticated = false
```

#### `logoutUser(refreshToken?: string)`
```typescript
// Uso
dispatch(logoutUser(refreshToken))

// Estados manejados:
// - pending: isLoading = true
// - fulfilled/rejected: Estado completamente limpiado
```

#### `refreshAuthToken(refreshToken: string)`
```typescript
// Uso
dispatch(refreshAuthToken(refreshToken))

// Estados manejados:
// - pending: isLoading = true
// - fulfilled: Nuevo token establecido
// - rejected: Estado de auth completamente limpiado
```

#### `checkAuthStatus(token: string)`
```typescript
// Uso
dispatch(checkAuthStatus(token))

// Estados manejados:
// - pending: isLoading = true
// - fulfilled: user establecido, isAuthenticated = true
// - rejected: Estado de auth limpiado
```

#### `getUserProfile(token: string)`
```typescript
// Uso
dispatch(getUserProfile(token))

// Estados manejados:
// - pending: isLoading = true
// - fulfilled: user actualizado
// - rejected: error establecido
```

#### `changeUserPassword({ passwordData, token })`
```typescript
// Uso
dispatch(changeUserPassword({
  passwordData: { old_password: 'old', new_password: 'new' },
  token: 'jwt-token'
}))

// Estados manejados:
// - pending: isLoading = true, error = null
// - fulfilled: isLoading = false, error = null
// - rejected: error establecido
```

#### `verifyUserToken(token: string)`
```typescript
// Uso
dispatch(verifyUserToken(token))

// Estados manejados:
// - pending: isLoading = true
// - fulfilled: Si token inválido, limpia estado de auth
// - rejected: Estado de auth limpiado
```

### Reducers Síncronos

#### `clearError()`
```typescript
// Uso
dispatch(clearError())
// Resultado: state.error = null
```

#### `setToken(token: string)`
```typescript
// Uso
dispatch(setToken('new-jwt-token'))
// Resultado: state.token = 'new-jwt-token'
```

#### `setRefreshToken(refreshToken: string)`
```typescript
// Uso
dispatch(setRefreshToken('new-refresh-token'))
// Resultado: state.refreshToken = 'new-refresh-token'
```

#### `updateUser(updates: Partial<User>)`
```typescript
// Uso
dispatch(updateUser({ first_name: 'Nuevo Nombre' }))
// Resultado: state.user = { ...state.user, first_name: 'Nuevo Nombre' }
```

#### `clearAuth()`
```typescript
// Uso
dispatch(clearAuth())
// Resultado: Estado completamente reiniciado
```

#### `setLoading(isLoading: boolean)`
```typescript
// Uso
dispatch(setLoading(true))
// Resultado: state.isLoading = true
```

## Integración con React

### Hook Personalizado
```typescript
// hooks/useAuth.ts
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store'
import { loginUser, logoutUser, clearError } from '../features/auth/authSlice'

export const useAuth = () => {
  const dispatch = useDispatch()
  const auth = useSelector((state: RootState) => state.auth)

  const login = async (credentials: LoginCredentials) => {
    await dispatch(loginUser(credentials))
  }

  const logout = async () => {
    await dispatch(logoutUser(auth.refreshToken))
  }

  const clearAuthError = () => {
    dispatch(clearError())
  }

  return {
    ...auth,
    login,
    logout,
    clearError: clearAuthError,
  }
}
```

### Componente de Login
```typescript
// components/LoginForm.tsx
import { useAuth } from '../hooks/useAuth'

export const LoginForm = () => {
  const { login, isLoading, error } = useAuth()

  const handleSubmit = async (credentials: LoginCredentials) => {
    await login(credentials)
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      {error && <div className="error">{error}</div>}
      <button disabled={isLoading}>
        {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  )
}
```

## Manejo de Errores

### Estrategias de Error Handling
1. **Errores de Red**: Capturados en async thunks y almacenados en `state.error`
2. **Tokens Expirados**: Automáticamente limpian el estado de autenticación
3. **Errores de Validación**: Propagados desde la API y mostrados al usuario
4. **Errores de Servidor**: Manejados con mensajes user-friendly

### Ejemplo de Manejo de Errores
```typescript
// En el componente
const { error, clearError } = useAuth()

useEffect(() => {
  if (error) {
    // Mostrar notificación de error
    toast.error(error)
    // Limpiar error después de mostrar
    setTimeout(() => clearError(), 5000)
  }
}, [error, clearError])
```

## Configuración del Store

### Store Setup
```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### Provider Setup
```typescript
// App.tsx
import { Provider } from 'react-redux'
import { store } from './store'

function App() {
  return (
    <Provider store={store}>
      {/* App components */}
    </Provider>
  )
}
```

## Persistencia de Estado

### Redux Persist Integration
```typescript
// store/persistConfig.ts
import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import authReducer from '../features/auth/authSlice'

const authPersistConfig = {
  key: 'auth',
  storage,
  whitelist: ['user', 'token', 'refreshToken', 'isAuthenticated'],
}

export const persistedAuthReducer = persistReducer(authPersistConfig, authReducer)
```

## Testing

### Test Coverage
- ✅ Reducers síncronos
- ✅ Async thunks (pending, fulfilled, rejected)
- ✅ Estado inicial
- ✅ Action creators
- ✅ Edge cases (usuario null, tokens inválidos)

### Ejemplo de Test
```typescript
// __tests__/authSlice.test.ts
describe('authSlice', () => {
  it('should handle loginUser.fulfilled', () => {
    const payload = {
      user: mockUser,
      access: 'access-token',
      refresh: 'refresh-token',
    }
    
    const action = { type: loginUser.fulfilled.type, payload }
    const result = authReducer(initialState, action)
    
    expect(result.isAuthenticated).toBe(true)
    expect(result.user).toEqual(mockUser)
    expect(result.token).toBe('access-token')
  })
})
```

## Mejores Prácticas

### Performance
- **Memoización**: Usar `useSelector` con selectores memoizados
- **Actualizaciones Parciales**: `updateUser` solo actualiza campos específicos
- **Estado Inmutable**: Redux Toolkit usa Immer internamente

### Seguridad
- **Token Management**: Tokens almacenados de forma segura
- **Auto-logout**: Limpieza automática en caso de tokens inválidos
- **Error Sanitization**: Errores sanitizados antes de mostrar al usuario

### Maintainability
- **TypeScript Estricto**: Tipado completo en todos los thunks y reducers
- **Separación de Responsabilidades**: Lógica de API separada del estado
- **Documentación**: Comentarios y documentación comprehensiva

## Roadmap de Mejoras

### Próximas Funcionalidades
1. **Refresh Token Automático**: Interceptor para renovación automática
2. **Multi-device Logout**: Invalidación de sesiones en múltiples dispositivos
3. **Session Timeout**: Timeout automático por inactividad
4. **Audit Logging**: Registro de eventos de autenticación
5. **Two-Factor Authentication**: Soporte para 2FA
6. **Social Login**: Integración con proveedores OAuth

### Optimizaciones
1. **Selective Persistence**: Persistir solo datos necesarios
2. **Background Sync**: Sincronización en background
3. **Offline Support**: Manejo de estado offline
4. **Performance Monitoring**: Métricas de rendimiento

## Integración con Otras Features

### Rutas Protegidas
```typescript
// components/ProtectedRoute.tsx
import { useAuth } from '../hooks/useAuth'

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <LoadingSpinner />
  if (!isAuthenticated) return <Navigate to="/login" />
  
  return <>{children}</>
}
```

### API Interceptors
```typescript
// lib/apiInterceptors.ts
import { store } from '../store'
import { refreshAuthToken, clearAuth } from '../features/auth/authSlice'

// Response interceptor para manejo automático de tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const { auth } = store.getState()
      if (auth.refreshToken) {
        await store.dispatch(refreshAuthToken(auth.refreshToken))
      } else {
        store.dispatch(clearAuth())
      }
    }
    return Promise.reject(error)
  }
)
```

---

**Nota**: Este Auth Slice está diseñado para ser el núcleo del sistema de autenticación, proporcionando una base sólida y escalable para el manejo de estado de autenticación en toda la aplicación.