# Auth API Documentation

## Descripción General

El módulo `authAPI.ts` proporciona una interfaz completa para manejar todas las operaciones de autenticación con el backend. Incluye funciones para login, logout, gestión de tokens, perfiles de usuario y un sistema robusto de interceptores para manejo automático de tokens.

## Características Principales

### 🔐 Funciones de Autenticación
- **Login/Logout**: Autenticación segura con JWT tokens
- **Refresh Token**: Renovación automática de tokens expirados
- **Token Verification**: Validación de tokens en tiempo real
- **Auth Status**: Verificación del estado de autenticación

### 🛡️ Interceptores Automáticos
- **Request Interceptor**: Inyección automática de tokens en headers
- **Response Interceptor**: Manejo automático de errores 401 y refresh de tokens
- **Error Handling**: Gestión centralizada de errores de autenticación

### 👤 Gestión de Usuario
- **Profile Management**: Obtención y actualización de perfiles
- **Password Change**: Cambio seguro de contraseñas
- **Permissions**: Sistema de permisos basado en roles

## API Reference

### Core Authentication Functions

#### `authAPI.login(credentials: LoginCredentials): Promise<LoginResponse>`

Autentica un usuario con credenciales.

```typescript
import { authAPI } from '@/features/auth/authAPI'

try {
  const response = await authAPI.login({
    username: 'usuario@example.com',
    password: 'password123'
  })
  
  console.log('Login exitoso:', response.user)
  // Guardar tokens
  localStorage.setItem('access_token', response.access)
  localStorage.setItem('refresh_token', response.refresh)
} catch (error) {
  console.error('Error de login:', error.message)
}
```

#### `authAPI.logout(refreshToken?: string): Promise<void>`

Cierra sesión del usuario y revoca tokens.

```typescript
try {
  const refreshToken = localStorage.getItem('refresh_token')
  await authAPI.logout(refreshToken)
  
  // Limpiar tokens locales
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
} catch (error) {
  console.warn('Error en logout:', error)
  // Limpiar tokens aunque falle la petición
}
```

#### `authAPI.refreshToken(refreshToken: string): Promise<RefreshTokenResponse>`

Renueva el access token usando el refresh token.

```typescript
try {
  const refreshToken = localStorage.getItem('refresh_token')
  const response = await authAPI.refreshToken(refreshToken)
  
  localStorage.setItem('access_token', response.access)
} catch (error) {
  // Token refresh falló, redirigir a login
  window.location.href = '/login'
}
```

### User Management Functions

#### `authAPI.getProfile(token: string): Promise<User>`

Obtiene el perfil completo del usuario autenticado.

```typescript
try {
  const token = localStorage.getItem('access_token')
  const user = await authAPI.getProfile(token)
  
  console.log('Perfil del usuario:', user)
} catch (error) {
  console.error('Error obteniendo perfil:', error)
}
```

#### `authAPI.changePassword(data: ChangePasswordData, token: string): Promise<void>`

Cambia la contraseña del usuario.

```typescript
try {
  const token = localStorage.getItem('access_token')
  await authAPI.changePassword({
    old_password: 'contraseñaActual',
    new_password: 'nuevaContraseña123'
  }, token)
  
  console.log('Contraseña cambiada exitosamente')
} catch (error) {
  console.error('Error cambiando contraseña:', error)
}
```

### Token Management Functions

#### `authAPI.verifyToken(token: string): Promise<boolean>`

Verifica si un token es válido.

```typescript
const token = localStorage.getItem('access_token')
const isValid = await authAPI.verifyToken(token)

if (!isValid) {
  // Token inválido, intentar refresh o redirigir a login
}
```

#### `authAPI.getAuthStatus(token: string): Promise<AuthStatusResponse>`

Obtiene el estado de autenticación actual.

```typescript
try {
  const token = localStorage.getItem('access_token')
  const status = await authAPI.getAuthStatus(token)
  
  console.log('Usuario autenticado:', status.user)
} catch (error) {
  console.log('Usuario no autenticado')
}
```

#### `authAPI.getUserPermissions(token: string): Promise<any>`

Obtiene los permisos del usuario autenticado.

```typescript
try {
  const token = localStorage.getItem('access_token')
  const permissions = await authAPI.getUserPermissions(token)
  
  console.log('Permisos del usuario:', permissions)
} catch (error) {
  console.error('Error obteniendo permisos:', error)
}
```

## Interceptores

### Setup Request Interceptor

Configura el interceptor de requests para inyectar automáticamente tokens.

```typescript
import { setupAuthInterceptor } from '@/features/auth/authAPI'

// Función que retorna el token actual
const getToken = () => localStorage.getItem('access_token')

// Configurar interceptor
setupAuthInterceptor(getToken)
```

### Setup Response Interceptor

Configura el interceptor de responses para manejar errores 401 automáticamente.

```typescript
import { setupAuthResponseInterceptor } from '@/features/auth/authAPI'

const onTokenExpired = () => {
  // Limpiar tokens y redirigir a login
  localStorage.clear()
  window.location.href = '/login'
}

const onRefreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token')
    const response = await authAPI.refreshToken(refreshToken)
    localStorage.setItem('access_token', response.access)
    return response.access
  } catch (error) {
    onTokenExpired()
    throw error
  }
}

setupAuthResponseInterceptor(onTokenExpired, onRefreshToken)
```

## Integración con React

### Hook personalizado para autenticación

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react'
import { authAPI } from '@/features/auth/authAPI'
import type { User } from '@/features/auth/authTypes'

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          const status = await authAPI.getAuthStatus(token)
          setUser(status.user)
        }
      } catch (error) {
        console.error('Auth check failed:', error)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    const response = await authAPI.login(credentials)
    localStorage.setItem('access_token', response.access)
    localStorage.setItem('refresh_token', response.refresh)
    setUser(response.user)
    return response
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      await authAPI.logout(refreshToken)
    } finally {
      localStorage.clear()
      setUser(null)
    }
  }

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  }
}
```

### Componente de Login

```typescript
// components/LoginForm.tsx
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

export const LoginForm = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await login(credentials)
      // Redirigir al dashboard
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          username: e.target.value
        }))}
        placeholder="Usuario"
        required
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          password: e.target.value
        }))}
        placeholder="Contraseña"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  )
}
```

## Manejo de Errores

### Tipos de Errores Comunes

```typescript
// Manejo específico de errores de autenticación
try {
  await authAPI.login(credentials)
} catch (error) {
  if (error.message.includes('Invalid credentials')) {
    // Credenciales incorrectas
    setError('Usuario o contraseña incorrectos')
  } else if (error.message.includes('Network Error')) {
    // Error de conexión
    setError('Error de conexión. Intenta nuevamente.')
  } else {
    // Error genérico
    setError('Error inesperado. Contacta soporte.')
  }
}
```

### Retry Logic

```typescript
const loginWithRetry = async (credentials: LoginCredentials, maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await authAPI.login(credentials)
    } catch (error) {
      if (attempt === maxRetries) throw error
      
      // Esperar antes del siguiente intento
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
    }
  }
}
```

## Configuración de Desarrollo

### Variables de Entorno

```env
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_AUTH_TOKEN_KEY=access_token
VITE_REFRESH_TOKEN_KEY=refresh_token
```

### Mock para Testing

```typescript
// __mocks__/authAPI.ts
export const authAPI = {
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  getAuthStatus: vi.fn(),
  getProfile: vi.fn(),
  changePassword: vi.fn(),
  verifyToken: vi.fn(),
  getUserPermissions: vi.fn()
}

export const setupAuthInterceptor = vi.fn()
export const setupAuthResponseInterceptor = vi.fn()
```

## Mejores Prácticas

### 1. Seguridad de Tokens
- Nunca almacenar tokens en localStorage en producción
- Usar httpOnly cookies cuando sea posible
- Implementar token rotation
- Validar tokens en cada request crítico

### 2. Performance
- Implementar cache para permisos de usuario
- Usar debounce para verificaciones de token
- Lazy loading para funciones no críticas

### 3. UX
- Mostrar loading states durante autenticación
- Implementar auto-logout por inactividad
- Guardar estado de navegación para redirect post-login

### 4. Error Handling
- Logs detallados para debugging
- Fallbacks graceful para errores de red
- Mensajes de error user-friendly

## Integración con Estado Global

### Con Zustand

```typescript
// stores/authStore.ts
import { create } from 'zustand'
import { authAPI } from '@/features/auth/authAPI'
import type { User } from '@/features/auth/authTypes'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: false,

  login: async (credentials) => {
    set({ loading: true })
    try {
      const response = await authAPI.login(credentials)
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)
      set({ 
        user: response.user, 
        isAuthenticated: true,
        loading: false 
      })
    } catch (error) {
      set({ loading: false })
      throw error
    }
  },

  logout: async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      await authAPI.logout(refreshToken)
    } finally {
      localStorage.clear()
      set({ user: null, isAuthenticated: false })
    }
  },

  checkAuth: async () => {
    set({ loading: true })
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const status = await authAPI.getAuthStatus(token)
        set({ 
          user: status.user, 
          isAuthenticated: true,
          loading: false 
        })
      } else {
        set({ loading: false })
      }
    } catch (error) {
      set({ user: null, isAuthenticated: false, loading: false })
    }
  }
}))
```

## Testing

### Unit Tests

Los tests están ubicados en `__tests__/authAPI.test.ts` y cubren:

- ✅ Estructura y tipos del API
- ✅ Validación de interfaces TypeScript
- ✅ Existencia de todas las funciones requeridas
- ✅ Configuración de interceptores

### Integration Tests

```typescript
// Ejemplo de test de integración
describe('Auth Flow Integration', () => {
  it('should complete full auth flow', async () => {
    // 1. Login
    const loginResponse = await authAPI.login(mockCredentials)
    expect(loginResponse.access).toBeDefined()
    
    // 2. Get Profile
    const profile = await authAPI.getProfile(loginResponse.access)
    expect(profile.id).toBeDefined()
    
    // 3. Logout
    await authAPI.logout(loginResponse.refresh)
  })
})
```

## Roadmap

### Próximas Mejoras
- [ ] Implementación de 2FA
- [ ] Biometric authentication
- [ ] Session management avanzado
- [ ] Audit logs de autenticación
- [ ] Rate limiting client-side
- [ ] Offline authentication cache

### Optimizaciones Pendientes
- [ ] Token encryption en storage
- [ ] Background token refresh
- [ ] Connection pooling
- [ ] Request deduplication
- [ ] Automatic retry con exponential backoff

---

## Soporte

Para reportar bugs o solicitar features relacionadas con el Auth API, crear un issue en el repositorio del proyecto con la etiqueta `auth-api`.