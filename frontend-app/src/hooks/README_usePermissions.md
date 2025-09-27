# usePermissions Hook

Hook personalizado para gestionar permisos de usuario en la aplicación React con Redux.

## Características

- ✅ **Type-safe**: Completamente tipado con TypeScript
- ✅ **Redux Integration**: Se integra perfectamente con el estado de autenticación
- ✅ **Performance**: Optimizado con memoización para evitar re-renders innecesarios
- ✅ **Flexible**: Soporta verificación de permisos específicos, roles y módulos
- ✅ **Convenience Methods**: Incluye métodos de conveniencia para roles comunes

## Instalación

El hook ya está disponible en `src/hooks/usePermissions.ts` y listo para usar.

## Uso Básico

```typescript
import { usePermissions } from '@/hooks/usePermissions'

function MyComponent() {
  const {
    hasPermission,
    hasRole,
    hasAnyRole,
    canAccessModule,
    isAdmin,
    isStaff,
    isSuperuser,
    canRead,
    canWrite,
    canDelete
  } = usePermissions()

  if (!canRead) {
    return <div>No tienes permisos para ver este contenido</div>
  }

  return (
    <div>
      {canWrite && <button>Editar</button>}
      {canDelete && <button>Eliminar</button>}
      {isAdmin && <button>Panel Admin</button>}
    </div>
  )
}
```

## API Reference

### hasPermission(permission: string): boolean

Verifica si el usuario tiene un permiso específico.

```typescript
const canEditUsers = hasPermission('auth.change_user')
const canViewReports = hasPermission('reports.view_report')
```

### hasRole(role: string): boolean

Verifica si el usuario tiene un rol específico.

```typescript
const isManager = hasRole('manager')
const isEditor = hasRole('editor')
```

### hasAnyRole(roles: string[]): boolean

Verifica si el usuario tiene al menos uno de los roles especificados.

```typescript
const canModerate = hasAnyRole(['admin', 'moderator', 'staff'])
```

### canAccessModule(module: string): boolean

Verifica si el usuario puede acceder a un módulo específico basado en sus permisos.

```typescript
const canAccessAuth = canAccessModule('auth')
const canAccessReports = canAccessModule('reports')
```

### Propiedades de Conveniencia

#### Roles Comunes
- `isAdmin`: Verifica si el usuario es administrador
- `isStaff`: Verifica si el usuario es staff
- `isSuperuser`: Verifica si el usuario es superusuario

#### Permisos Básicos
- `canRead`: Verifica permisos de lectura generales
- `canWrite`: Verifica permisos de escritura generales  
- `canDelete`: Verifica permisos de eliminación generales

## Hook de Conveniencia: useQuickPermissions

Para casos simples, puedes usar `useQuickPermissions`:

```typescript
import { useQuickPermissions } from '@/hooks/usePermissions'

function QuickComponent() {
  const { isAdmin, canWrite, canDelete } = useQuickPermissions()
  
  return (
    <div>
      {isAdmin && <AdminPanel />}
      {canWrite && <EditButton />}
      {canDelete && <DeleteButton />}
    </div>
  )
}
```

## Ejemplos de Uso

### Protección de Rutas

```typescript
import { usePermissions } from '@/hooks/usePermissions'
import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isStaff } = usePermissions()
  
  if (!isStaff) {
    return <Navigate to="/unauthorized" replace />
  }
  
  return <>{children}</>
}
```

### Renderizado Condicional

```typescript
function UserActions({ userId }: { userId: string }) {
  const { hasPermission, isAdmin } = usePermissions()
  
  const canEditUser = hasPermission('auth.change_user')
  const canDeleteUser = hasPermission('auth.delete_user')
  
  return (
    <div>
      {canEditUser && <EditUserButton userId={userId} />}
      {canDeleteUser && <DeleteUserButton userId={userId} />}
      {isAdmin && <ViewUserLogsButton userId={userId} />}
    </div>
  )
}
```

### Verificación de Módulos

```typescript
function Navigation() {
  const { canAccessModule } = usePermissions()
  
  return (
    <nav>
      <Link to="/">Inicio</Link>
      {canAccessModule('auth') && <Link to="/users">Usuarios</Link>}
      {canAccessModule('reports') && <Link to="/reports">Reportes</Link>}
      {canAccessModule('settings') && <Link to="/settings">Configuración</Link>}
    </nav>
  )
}
```

## Consideraciones de Performance

- El hook utiliza `useMemo` para optimizar las verificaciones de permisos
- Solo se recalcula cuando cambia el usuario en el estado de Redux
- Las funciones de verificación son estables y no causan re-renders innecesarios

## Estructura de Datos Esperada

El hook espera que el usuario tenga la siguiente estructura:

```typescript
interface User {
  id: string
  username: string
  email: string
  is_staff: boolean
  is_superuser: boolean
  groups: string[]
  user_permissions: string[]
}
```

## Testing

El hook incluye tests completos que verifican:
- Comportamiento con usuario nulo
- Verificación de permisos para usuarios admin
- Verificación de permisos específicos
- Funcionalidad de roles múltiples
- Hook de conveniencia `useQuickPermissions`

Para ejecutar los tests:

```bash
npm test src/hooks/__tests__/usePermissions.test.ts
```

## Troubleshooting

### El hook siempre devuelve false

Verifica que:
1. El usuario esté autenticado y presente en el estado de Redux
2. Los campos `groups` y `user_permissions` estén presentes en el objeto usuario
3. Los permisos tengan el formato correcto (ej: 'app.permission_name')

### Performance Issues

Si experimentas problemas de performance:
1. Verifica que no estés llamando al hook en componentes que se re-renderizan frecuentemente
2. Considera usar `useQuickPermissions` para casos simples
3. Implementa memoización en componentes padre si es necesario