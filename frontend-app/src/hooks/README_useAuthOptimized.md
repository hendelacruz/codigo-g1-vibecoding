# useAuthOptimized Hook

Hook optimizado para la gestión de autenticación con mejoras de rendimiento y funcionalidades avanzadas.

## 🚀 Características

- **Optimización de rendimiento**: Selectores memoizados para prevenir re-renders innecesarios
- **Valores computados**: Propiedades derivadas del estado de autenticación
- **Gestión completa de tokens**: Manejo de access y refresh tokens
- **Acciones memoizadas**: Callbacks optimizados con `useCallback`
- **Validación de estado**: Verificaciones automáticas de tokens y estado de autenticación
- **Versión lite**: Hook ligero para componentes que solo necesitan leer el estado

## 📦 Instalación

El hook está disponible en `src/hooks/useAuthOptimized.ts` y se integra automáticamente con el sistema Redux existente.

## 🔧 Uso Básico

### Hook Principal

```tsx
import { useAuthOptimized } from '@/hooks/useAuthOptimized'

function UserProfile() {
  const {
    user,
    isAuthenticated,
    userDisplayName,
    userRole,
    hasValidToken,
    login,
    logout,
    getProfile
  } = useAuthOptimized()

  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />
  }

  return (
    <div>
      <h1>Bienvenido, {userDisplayName}</h1>
      <p>Rol: {userRole}</p>
      <button onClick={logout}>Cerrar Sesión</button>
    </div>
  )
}
```

### Hook Lite (Solo Lectura)

```tsx
import { useAuthOptimizedLite } from '@/hooks/useAuthOptimized'

function Header() {
  const { isAuthenticated, userDisplayName, userRole } = useAuthOptimizedLite()

  if (!isAuthenticated) {
    return <div>No autenticado</div>
  }

  return (
    <header>
      <span>{userDisplayName} ({userRole})</span>
    </header>
  )
}
```

## 📋 API Reference

### useAuthOptimized()

Retorna un objeto con las siguientes propiedades y métodos:

#### Estado de Usuario
- `user: User | null` - Datos del usuario autenticado
- `isAuthenticated: boolean` - Estado de autenticación
- `isLoading: boolean` - Estado de carga
- `error: string | null` - Error actual si existe

#### Gestión de Tokens
- `token: string | null` - Token de acceso actual
- `refreshToken: string | null` - Token de renovación
- `hasValidToken: boolean` - Indica si hay un token válido

#### Valores Computados
- `userDisplayName: string` - Nombre completo del usuario o username
- `userRole: string | null` - Rol del usuario actual

#### Acciones de Autenticación
- `login(credentials: LoginCredentials): Promise<void>` - Iniciar sesión
- `logout(): Promise<void>` - Cerrar sesión
- `refreshAuth(): Promise<void>` - Renovar token de acceso
- `checkStatus(): Promise<void>` - Verificar estado de autenticación
- `getProfile(): Promise<void>` - Obtener perfil del usuario
- `changePassword(data: ChangePasswordData): Promise<void>` - Cambiar contraseña
- `verifyToken(): Promise<void>` - Verificar validez del token

#### Gestión de Estado
- `clearError(): void` - Limpiar errores
- `updateUserData(userData: Partial<User>): void` - Actualizar datos del usuario
- `setAuthToken(token: string): void` - Establecer token de acceso
- `setAuthRefreshToken(refreshToken: string): void` - Establecer token de renovación
- `clearAuthData(): void` - Limpiar todos los datos de autenticación
- `setLoadingState(loading: boolean): void` - Establecer estado de carga

### useAuthOptimizedLite()

Versión ligera que solo retorna:
- `user: User | null`
- `isAuthenticated: boolean`
- `isLoading: boolean`
- `userDisplayName: string`
- `userRole: string | null`
- `hasValidToken: boolean`

## 🎯 Propiedades de Conveniencia

### userDisplayName
Combina `first_name` y `last_name` del usuario, o usa `username` como fallback:

```tsx
const { userDisplayName } = useAuthOptimized()
// "John Doe" o "username" si no hay nombres
```

### hasValidToken
Verifica si existe un token válido y el usuario está autenticado:

```tsx
const { hasValidToken } = useAuthOptimized()
if (hasValidToken) {
  // Realizar operaciones que requieren autenticación
}
```

## 🔄 Ejemplos de Uso

### Login con Manejo de Errores

```tsx
function LoginForm() {
  const { login, isLoading, error, clearError } = useAuthOptimized()
  const [credentials, setCredentials] = useState({ username: '', password: '' })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      clearError()
      await login(credentials)
      // Redireccionar después del login exitoso
    } catch (err) {
      // El error se maneja automáticamente en el estado
      console.error('Login failed:', err)
    }
  }

  return (
    <form onSubmit={handleLogin}>
      {error && <div className="error">{error}</div>}
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
        placeholder="Usuario"
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
        placeholder="Contraseña"
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  )
}
```

### Renovación Automática de Token

```tsx
function TokenManager() {
  const { refreshAuth, hasValidToken, token } = useAuthOptimized()

  useEffect(() => {
    if (!hasValidToken) return

    // Renovar token cada 14 minutos (tokens expiran en 15 min)
    const interval = setInterval(async () => {
      try {
        await refreshAuth()
      } catch (error) {
        console.error('Token refresh failed:', error)
      }
    }, 14 * 60 * 1000)

    return () => clearInterval(interval)
  }, [refreshAuth, hasValidToken])

  return null
}
```

### Cambio de Contraseña

```tsx
function ChangePasswordForm() {
  const { changePassword, isLoading, error } = useAuthOptimized()
  const [passwords, setPasswords] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwords.new_password !== passwords.confirm_password) {
      alert('Las contraseñas no coinciden')
      return
    }

    try {
      await changePassword({
        old_password: passwords.old_password,
        new_password: passwords.new_password
      })
      alert('Contraseña cambiada exitosamente')
      setPasswords({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      console.error('Password change failed:', err)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <input
        type="password"
        value={passwords.old_password}
        onChange={(e) => setPasswords(prev => ({ ...prev, old_password: e.target.value }))}
        placeholder="Contraseña actual"
      />
      <input
        type="password"
        value={passwords.new_password}
        onChange={(e) => setPasswords(prev => ({ ...prev, new_password: e.target.value }))}
        placeholder="Nueva contraseña"
      />
      <input
        type="password"
        value={passwords.confirm_password}
        onChange={(e) => setPasswords(prev => ({ ...prev, confirm_password: e.target.value }))}
        placeholder="Confirmar nueva contraseña"
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Cambiando...' : 'Cambiar Contraseña'}
      </button>
    </form>
  )
}
```

## ⚡ Consideraciones de Rendimiento

### Optimizaciones Implementadas

1. **Selectores Memoizados**: Los valores computados usan `useMemo` para evitar recálculos innecesarios
2. **Callbacks Memoizados**: Todas las acciones usan `useCallback` para prevenir re-renders
3. **Suscripción Selectiva**: Solo se suscribe a las partes necesarias del estado Redux

### Cuándo Usar Cada Versión

- **`useAuthOptimized`**: Para componentes que necesitan realizar acciones de autenticación
- **`useAuthOptimizedLite`**: Para componentes que solo necesitan leer el estado (headers, guards, etc.)

### Ejemplo de Optimización

```tsx
// ❌ Malo - Re-render en cada cambio del store
function BadComponent() {
  const authState = useAppSelector(state => state.auth)
  return <div>{authState.user?.first_name}</div>
}

// ✅ Bueno - Solo re-render cuando cambia userDisplayName
function GoodComponent() {
  const { userDisplayName } = useAuthOptimizedLite()
  return <div>{userDisplayName}</div>
}
```

## 🔒 Estructura de Datos Esperada

### User Interface
```typescript
interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  dni: string
  rol_nombre: string
  is_active: boolean
  groups?: string[]
  user_permissions?: string[]
}
```

### LoginCredentials Interface
```typescript
interface LoginCredentials {
  username: string
  password: string
}
```

### ChangePasswordData Interface
```typescript
interface ChangePasswordData {
  old_password: string
  new_password: string
}
```

## 🧪 Testing

El hook incluye tests comprehensivos que cubren:

- Estado inicial y autenticado
- Valores computados (userDisplayName, userRole, hasValidToken)
- Todas las acciones disponibles
- Manejo de errores
- Acciones de gestión de estado
- Funcionalidad del hook lite

Para ejecutar los tests:

```bash
npm test useAuthOptimized.test.ts
```

## 🔧 Troubleshooting

### Errores Comunes

1. **"No token available"**: Asegúrate de que el usuario esté autenticado antes de llamar acciones que requieren token
2. **"No refresh token available"**: Verifica que el refresh token esté presente antes de intentar renovar
3. **Re-renders excesivos**: Usa `useAuthOptimizedLite` para componentes que solo leen estado

### Debugging

```tsx
function DebugAuth() {
  const auth = useAuthOptimized()
  
  console.log('Auth State:', {
    isAuthenticated: auth.isAuthenticated,
    hasValidToken: auth.hasValidToken,
    userRole: auth.userRole,
    userDisplayName: auth.userDisplayName
  })
  
  return null
}
```

## 🔄 Migración desde useAuth

Para migrar desde el hook `useAuth` básico:

```tsx
// Antes
const { user, isAuthenticated, login, logout } = useAuth()

// Después
const { user, isAuthenticated, login, logout, userDisplayName, hasValidToken } = useAuthOptimized()
```

El hook es completamente compatible con el anterior, pero añade optimizaciones y nuevas funcionalidades.

## 📝 Notas Técnicas

- Compatible con React 18+ y Concurrent Features
- Integrado con Redux Toolkit y Redux Persist
- Manejo automático de errores con try/catch
- Validaciones de estado antes de ejecutar acciones
- Soporte completo para TypeScript con tipos estrictos