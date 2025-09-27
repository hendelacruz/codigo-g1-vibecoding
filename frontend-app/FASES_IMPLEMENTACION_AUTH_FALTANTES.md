# 🚀 Fases de Implementación Faltantes - Módulo de Autenticación

## 📊 Análisis del Estado Actual

### ✅ Componentes Implementados
- **Core Auth**: `authSlice.ts`, `authTypes.ts`, `authAPI.ts`, `useAuth.ts`
- **Componentes Base**: `LoginForm.tsx`, `ProtectedRoute.tsx`, `AuthLayout.tsx` (placeholder)
- **UI Components**: `Button.tsx`, `Input.tsx`, `Select.tsx`, `Textarea.tsx`, `LoadingSpinner.tsx`, `Card.tsx`, `Badge.tsx`
- **Utilidades**: `authUtils.ts`, `useAuthError.ts`
- **Testing**: Tests básicos para componentes principales

### ❌ Componentes Faltantes (Documentados pero No Implementados)
- `usePermissions.ts` hook
- `RoleGuard.tsx` component
- `AuthErrorBoundary.tsx` component
- `useAuthOptimized.ts` hook
- Páginas adicionales (`UnauthorizedPage`, `DashboardPage` completo)
- Componentes de UI avanzados (`Modal`, `Toast`, etc.)

---

## 🎯 FASE 1: Hooks y Utilidades de Permisos (Prioridad Alta)

### 1.1 Implementar usePermissions Hook
**Archivo**: `src/hooks/usePermissions.ts`

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

### 1.2 Implementar useAuthOptimized Hook
**Archivo**: `src/hooks/useAuthOptimized.ts`

```typescript
import { useMemo, useCallback } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { usePermissions } from './usePermissions';

export function useAuthOptimized() {
  const auth = useAuth();
  const permissions = usePermissions();

  // Memoizar datos del usuario para evitar re-renders innecesarios
  const userInfo = useMemo(() => ({
    id: auth.user?.id,
    username: auth.user?.username,
    email: auth.user?.email,
    fullName: `${auth.user?.first_name || ''} ${auth.user?.last_name || ''}`.trim(),
    isActive: auth.user?.is_active,
    groups: auth.user?.groups || [],
    permissions: auth.user?.user_permissions || []
  }), [auth.user]);

  // Funciones optimizadas para verificación de permisos
  const checkAccess = useCallback((module: string, action: string) => {
    return permissions.canAccess(module as any, action as any);
  }, [permissions]);

  const hasAnyPermission = useCallback((permissionList: string[]) => {
    return permissionList.some(permission => permissions.hasPermission(permission));
  }, [permissions]);

  return {
    ...auth,
    ...permissions,
    userInfo,
    checkAccess,
    hasAnyPermission,
    isReady: !auth.isLoading && auth.isAuthenticated
  };
}
```

---

## 🛡️ FASE 2: Componentes de Protección y Control de Acceso (Prioridad Alta)

### 2.1 Implementar RoleGuard Component
**Archivo**: `src/components/auth/RoleGuard.tsx`

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

### 2.2 Implementar AuthErrorBoundary Component
**Archivo**: `src/components/auth/AuthErrorBoundary.tsx`

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/shared/components/ui/Button';

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

---

## 📱 FASE 3: Páginas y Layouts Completos (Prioridad Media)

### 3.1 Completar AuthLayout Component
**Archivo**: `src/features/auth/components/AuthLayout.tsx`

```typescript
import React from 'react';
import { Card, CardContent, CardHeader } from '@/shared/components/ui/Card';

interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title = "Iniciar Sesión",
  subtitle = "Accede a tu cuenta para continuar"
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {title}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {subtitle}
          </p>
        </div>
        
        <Card className="mt-8">
          <CardHeader className="space-y-1">
            <div className="flex justify-center">
              {/* Logo aquí */}
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">G1</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {children}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
```

### 3.2 Crear UnauthorizedPage
**Archivo**: `src/pages/UnauthorizedPage.tsx`

```typescript
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/shared/components/ui/Button';
import { Card, CardContent, CardHeader } from '@/shared/components/ui/Card';

export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="max-w-md w-full">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Acceso Denegado</h1>
          <p className="text-gray-600 mt-2">
            No tienes permisos para acceder a esta página.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button 
            onClick={() => navigate('/dashboard')} 
            className="w-full"
          >
            Ir al Dashboard
          </Button>
          <Button 
            onClick={() => navigate(-1)} 
            variant="secondary"
            className="w-full"
          >
            Volver Atrás
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
```

---

## 🎨 FASE 4: Componentes UI Avanzados (Prioridad Media)

### 4.1 Implementar Modal Component
**Archivo**: `src/shared/components/ui/Modal.tsx`

```typescript
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/shared/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlayClick?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  children,
  title,
  size = 'md',
  closeOnOverlayClick = true
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={closeOnOverlayClick ? onClose : undefined}
      />
      <div className={cn(
        "relative bg-white rounded-lg shadow-xl w-full mx-4",
        sizeClasses[size]
      )}>
        {title && (
          <div className="flex items-center justify-between p-6 border-b">
            <h3 className="text-lg font-semibold">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
};
```

### 4.2 Implementar Toast System
**Archivo**: `src/shared/components/ui/Toast.tsx`

```typescript
import React, { createContext, useContext, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/shared/lib/utils';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type: Toast['type'], duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: Toast['type'], duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: Toast = { id, message, type, duration };
    
    setToasts(prev => [...prev, toast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {createPortal(
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {toasts.map(toast => (
            <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
};

const ToastItem: React.FC<{ toast: Toast; onRemove: (id: string) => void }> = ({ toast, onRemove }) => {
  const typeStyles = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white'
  };

  return (
    <div className={cn(
      "px-4 py-3 rounded-lg shadow-lg flex items-center justify-between min-w-80",
      typeStyles[toast.type]
    )}>
      <span>{toast.message}</span>
      <button
        onClick={() => onRemove(toast.id)}
        className="ml-4 text-white hover:text-gray-200"
      >
        ×
      </button>
    </div>
  );
};
```

---

## 🧪 FASE 5: Testing y Validación (Prioridad Media)

### 5.1 Tests para usePermissions
**Archivo**: `src/hooks/__tests__/usePermissions.test.ts`

```typescript
import { renderHook } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { usePermissions } from '../usePermissions';
import authReducer from '@/features/auth/authSlice';

const createMockStore = (authState: any) => {
  return configureStore({
    reducer: { auth: authReducer },
    preloadedState: { auth: authState }
  });
};

describe('usePermissions', () => {
  it('should return false for permissions when user is null', () => {
    const store = createMockStore({ user: null });
    const wrapper = ({ children }: any) => <Provider store={store}>{children}</Provider>;
    
    const { result } = renderHook(() => usePermissions(), { wrapper });
    
    expect(result.current.hasPermission('any.permission')).toBe(false);
    expect(result.current.hasRole('Administradores')).toBe(false);
  });

  it('should return true for admin users', () => {
    const store = createMockStore({
      user: {
        groups: ['Administradores'],
        user_permissions: []
      }
    });
    const wrapper = ({ children }: any) => <Provider store={store}>{children}</Provider>;
    
    const { result } = renderHook(() => usePermissions(), { wrapper });
    
    expect(result.current.hasPermission('any.permission')).toBe(true);
    expect(result.current.isAdmin).toBe(true);
  });
});
```

### 5.2 Tests para RoleGuard
**Archivo**: `src/components/auth/__tests__/RoleGuard.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { RoleGuard } from '../RoleGuard';
import authReducer from '@/features/auth/authSlice';

const createMockStore = (authState: any) => {
  return configureStore({
    reducer: { auth: authReducer },
    preloadedState: { auth: authState }
  });
};

describe('RoleGuard', () => {
  it('should render children when user has required role', () => {
    const store = createMockStore({
      user: { groups: ['Administradores'] }
    });

    render(
      <Provider store={store}>
        <RoleGuard roles={['Administradores']}>
          <div>Protected Content</div>
        </RoleGuard>
      </Provider>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should render fallback when user lacks required role', () => {
    const store = createMockStore({
      user: { groups: ['Operadores'] }
    });

    render(
      <Provider store={store}>
        <RoleGuard roles={['Administradores']}>
          <div>Protected Content</div>
        </RoleGuard>
      </Provider>
    );

    expect(screen.getByText('Acceso Denegado')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});
```

---

## 🔧 FASE 6: Optimizaciones y Mejoras (Prioridad Baja)

### 6.1 Implementar Lazy Loading para Páginas
**Archivo**: `src/app/router/LazyRoutes.tsx`

```typescript
import { lazy } from 'react';

// Lazy loading de páginas principales
export const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
export const UsersPage = lazy(() => import('@/pages/UsersPage'));
export const InventoryPage = lazy(() => import('@/pages/InventoryPage'));
export const ServicesPage = lazy(() => import('@/pages/ServicesPage'));
export const SalesPage = lazy(() => import('@/pages/SalesPage'));
export const ReportsPage = lazy(() => import('@/pages/ReportsPage'));
export const UnauthorizedPage = lazy(() => import('@/pages/UnauthorizedPage'));
```

### 6.2 Implementar Cache de Permisos
**Archivo**: `src/hooks/usePermissionsCache.ts`

```typescript
import { useMemo } from 'react';
import { usePermissions } from './usePermissions';

export function usePermissionsCache() {
  const permissions = usePermissions();

  // Cache de permisos calculados para evitar recálculos
  const permissionCache = useMemo(() => ({
    canManageUsers: permissions.canAccess('users', 'create'),
    canViewInventory: permissions.canAccess('inventory', 'read'),
    canEditInventory: permissions.canAccess('inventory', 'update'),
    canDeleteInventory: permissions.canAccess('inventory', 'delete'),
    canViewSales: permissions.canAccess('sales', 'read'),
    canEditSales: permissions.canAccess('sales', 'update'),
    canViewReports: permissions.canAccess('reports', 'read'),
    isAdminOrSupervisor: permissions.hasAnyRole(['Administradores', 'Supervisores']),
    isTechnicianOrAbove: permissions.hasAnyRole(['Administradores', 'Supervisores', 'Técnicos'])
  }), [permissions]);

  return {
    ...permissions,
    cache: permissionCache
  };
}
```

---

## 📋 Checklist de Implementación

### ✅ Fase 1: Hooks y Utilidades (Crítico)
- [ ] `usePermissions.ts` - Hook principal de permisos
- [ ] `useAuthOptimized.ts` - Hook optimizado para performance
- [ ] Tests unitarios para hooks

### ✅ Fase 2: Componentes de Protección (Crítico)
- [ ] `RoleGuard.tsx` - Componente de control de acceso
- [ ] `AuthErrorBoundary.tsx` - Manejo de errores de auth
- [ ] Tests para componentes de protección

### ✅ Fase 3: Páginas y Layouts (Importante)
- [ ] Completar `AuthLayout.tsx`
- [ ] `UnauthorizedPage.tsx` - Página de acceso denegado
- [ ] Mejorar estructura de routing

### ✅ Fase 4: UI Avanzados (Importante)
- [ ] `Modal.tsx` - Sistema de modales
- [ ] `Toast.tsx` - Sistema de notificaciones
- [ ] Componentes adicionales según necesidad

### ✅ Fase 5: Testing (Importante)
- [ ] Tests de integración completos
- [ ] Tests E2E para flujos de auth
- [ ] Coverage de al menos 80%

### ✅ Fase 6: Optimizaciones (Opcional)
- [ ] Lazy loading de páginas
- [ ] Cache de permisos
- [ ] Performance monitoring
- [ ] Bundle optimization

---

## 🚀 Orden de Implementación Recomendado

1. **INMEDIATO** (Fase 1): Implementar `usePermissions` y `useAuthOptimized`
2. **SIGUIENTE** (Fase 2): Crear `RoleGuard` y `AuthErrorBoundary`
3. **DESPUÉS** (Fase 3): Completar páginas y layouts
4. **LUEGO** (Fase 4): Agregar componentes UI avanzados
5. **FINALMENTE** (Fases 5-6): Testing y optimizaciones

## 🎯 Criterios de Éxito

- ✅ Control de acceso granular funcionando
- ✅ Manejo robusto de errores de autenticación
- ✅ UI/UX consistente en toda la aplicación
- ✅ Performance optimizada (< 100ms para verificaciones de permisos)
- ✅ Cobertura de tests > 80%
- ✅ Documentación completa y actualizada

---

## 📝 Notas Adicionales

### Dependencias Requeridas
```json
{
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.0.0"
}
```

### Variables de Entorno
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_AUTH_TOKEN_KEY=access_token
VITE_REFRESH_TOKEN_KEY=refresh_token
```

### Configuración TypeScript
Asegurar que `tsconfig.json` tenga:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

Este documento proporciona una hoja de ruta clara y detallada para completar la implementación del módulo de autenticación, priorizando los componentes más críticos y proporcionando ejemplos de código listos para implementar.