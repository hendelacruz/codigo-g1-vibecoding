# Auth Types Documentation

## Overview
Complete TypeScript definitions for the authentication system, implementing JWT authentication with user management and role-based access control.

## Core Types

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
}
```

**Usage:**
```typescript
import type { User } from './authTypes'

const user: User = {
  id: 1,
  username: 'jdoe',
  email: 'john@example.com',
  first_name: 'John',
  last_name: 'Doe',
  dni: '12345678',
  rol_nombre: 'admin',
  is_active: true
}
```

### Authentication State
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

### Login Credentials
```typescript
interface LoginCredentials {
  username: string
  password: string
}
```

## Role-Based Access Control

### User Roles
```typescript
type UserRole = 'admin' | 'vendedor' | 'tecnico' | 'supervisor'
```

### Role Permissions
```typescript
interface RolePermissions {
  canViewInventory: boolean
  canEditInventory: boolean
  canDeleteInventory: boolean
  canViewSales: boolean
  canEditSales: boolean
  canDeleteSales: boolean
  canViewReports: boolean
  canManageUsers: boolean
}
```

## Utility Functions

### Permission Checking
```typescript
import { hasPermission, hasRole } from './authUtils'

// Check specific permission
const canEdit = hasPermission(user, 'canEditInventory')

// Check role
const isAdmin = hasRole(user, ['admin'])
```

### User Information
```typescript
import { getUserFullName, getUserDisplayName, formatUserRole } from './authUtils'

const fullName = getUserFullName(user) // "John Doe"
const displayName = getUserDisplayName(user) // "John Doe" or username
const roleDisplay = formatUserRole(user.rol_nombre) // "Administrador"
```

### Token Management
```typescript
import { isTokenExpired, decodeToken, getTokenExpirationTime } from './authUtils'

const expired = isTokenExpired(token)
const payload = decodeToken(token)
const expTime = getTokenExpirationTime(token)
```

### Validation
```typescript
import { isValidEmail, isValidDNI, formatDNI } from './authUtils'

const emailValid = isValidEmail('test@example.com') // true
const dniValid = isValidDNI('12345678') // true
const formattedDNI = formatDNI('12345678') // "12.345.678"
```

## Role Permissions Matrix

| Role       | View Inventory | Edit Inventory | Delete Inventory | View Sales | Edit Sales | Delete Sales | View Reports | Manage Users |
|------------|----------------|----------------|------------------|------------|------------|--------------|--------------|--------------|
| Admin      | ✅             | ✅             | ✅               | ✅         | ✅         | ✅           | ✅           | ✅           |
| Supervisor | ✅             | ✅             | ❌               | ✅         | ✅         | ❌           | ✅           | ❌           |
| Vendedor   | ✅             | ❌             | ❌               | ✅         | ✅         | ❌           | ❌           | ❌           |
| Técnico    | ✅             | ✅             | ❌               | ❌         | ❌         | ❌           | ❌           | ❌           |

## Constants

### API Endpoints
```typescript
import { AUTH_ENDPOINTS } from './authConstants'

// Usage
const loginUrl = AUTH_ENDPOINTS.LOGIN // '/auth/login/'
```

### Storage Keys
```typescript
import { STORAGE_KEYS } from './authConstants'

// Usage
localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
```

### Validation Rules
```typescript
import { VALIDATION_RULES } from './authConstants'

// Usage
const minPasswordLength = VALIDATION_RULES.PASSWORD.MIN_LENGTH // 8
```

## Form Types

### Login Form
```typescript
interface LoginFormData {
  username: string
  password: string
}
```

### Change Password Form
```typescript
interface ChangePasswordFormData {
  old_password: string
  new_password: string
  confirm_password: string
}
```

## Error Handling

### Auth Errors
```typescript
interface AuthError {
  message: string
  field?: string
  code?: string
}
```

### Validation Errors
```typescript
interface ValidationError {
  [key: string]: string[]
}
```

## Protected Routes

### Protected Route Props
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: UserRole
  fallback?: React.ReactNode
}
```

**Usage:**
```typescript
<ProtectedRoute requiredRole="admin">
  <AdminPanel />
</ProtectedRoute>
```

## Best Practices

### 1. Type Safety
Always use the provided types instead of `any`:
```typescript
// ✅ Good
const user: User = await fetchUser()

// ❌ Bad
const user: any = await fetchUser()
```

### 2. Permission Checking
Use utility functions for consistent permission checking:
```typescript
// ✅ Good
if (hasPermission(user, 'canEditInventory')) {
  // Show edit button
}

// ❌ Bad
if (user?.rol_nombre === 'admin') {
  // Show edit button
}
```

### 3. Role-Based Rendering
```typescript
// ✅ Good
{hasRole(user, ['admin', 'supervisor']) && (
  <AdminFeature />
)}

// ❌ Bad
{user?.rol_nombre === 'admin' || user?.rol_nombre === 'supervisor' && (
  <AdminFeature />
)}
```

### 4. Error Handling
```typescript
// ✅ Good
try {
  const result = await login(credentials)
} catch (error) {
  if (error instanceof AuthError) {
    setError(error.message)
  }
}
```

## Integration with Redux

The types are designed to work seamlessly with Redux Toolkit:

```typescript
// In authSlice.ts
const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

// In components
const { user, isAuthenticated } = useSelector((state: RootState) => state.auth)
```

## Testing

Comprehensive tests are provided in `__tests__/authTypes.test.ts` covering:
- Type validation
- Utility functions
- Permission checking
- Role-based access
- Token handling
- Validation functions

Run tests with:
```bash
npm run test auth
```