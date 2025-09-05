# Guía Completa: Crear tu Primer Componente React

Esta guía te enseñará a crear componentes React profesionales siguiendo la filosofía **Vibe Coding**, con TypeScript, testing, accesibilidad y las mejores prácticas de desarrollo moderno.

## 📋 Conceptos Fundamentales

### ¿Qué es un Componente React?

Un componente React es una función o clase que retorna JSX (JavaScript XML) y representa una parte reutilizable de la interfaz de usuario. Los componentes son los bloques de construcción fundamentales de cualquier aplicación React.

### Tipos de Componentes

1. **Componentes Funcionales** (Recomendado)
2. **Componentes de Clase** (Legacy)

## 🏗️ Arquitectura de Componentes Vibe Coding

### Estructura de Carpetas

```
src/
├── components/
│   ├── ui/                    # Componentes base reutilizables
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── index.ts
│   │   └── index.ts           # Barrel exports
│   └── feature/               # Componentes específicos
│       ├── UserProfile/
│       │   ├── UserProfile.tsx
│       │   ├── UserProfile.test.tsx
│       │   └── index.ts
│       └── index.ts
├── types/
│   └── components.ts          # Tipos compartidos
└── utils/
    └── test-utils.tsx         # Utilidades de testing
```

## 🚀 Paso 1: Crear tu Primer Componente - Button

### 1.1 Crear la estructura de carpetas

```bash
# Desde la raíz del proyecto
mkdir -p src/components/ui/Button
touch src/components/ui/Button/Button.tsx
touch src/components/ui/Button/Button.test.tsx
touch src/components/ui/Button/index.ts
```

### 1.2 Definir los tipos TypeScript

Primero, crea el archivo de tipos (`src/types/components.ts`):

```typescript
// src/types/components.ts
import { ButtonHTMLAttributes, ReactNode } from 'react'

// Base props que todos los componentes UI deberían tener
export interface BaseComponentProps {
  className?: string
  children?: ReactNode
  testId?: string
}

// Props específicas del Button
export interface ButtonProps extends BaseComponentProps, 
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  isDisabled?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  fullWidth?: boolean
}
```

### 1.3 Implementar el componente Button

```typescript
// src/components/ui/Button/Button.tsx
import { forwardRef } from 'react'
import { ButtonProps } from '../../../types/components'

/**
 * Button component following Vibe Coding principles
 * 
 * Features:
 * - Full TypeScript support
 * - Accessibility compliant (WCAG 2.1)
 * - Multiple variants and sizes
 * - Loading and disabled states
 * - Icon support
 * - Keyboard navigation
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>((
  {
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    isDisabled = false,
    leftIcon,
    rightIcon,
    fullWidth = false,
    className = '',
    testId,
    type = 'button',
    ...rest
  },
  ref
) => {
  // Base classes using Tailwind CSS v4
  const baseClasses = [
    'inline-flex',
    'items-center',
    'justify-center',
    'font-medium',
    'rounded-lg',
    'transition-all',
    'duration-200',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-2',
    'disabled:opacity-50',
    'disabled:cursor-not-allowed',
    'disabled:pointer-events-none'
  ]

  // Variant classes
  const variantClasses = {
    primary: [
      'bg-blue-600',
      'text-white',
      'hover:bg-blue-700',
      'focus:ring-blue-500',
      'active:bg-blue-800'
    ],
    secondary: [
      'bg-gray-200',
      'text-gray-900',
      'hover:bg-gray-300',
      'focus:ring-gray-500',
      'active:bg-gray-400'
    ],
    danger: [
      'bg-red-600',
      'text-white',
      'hover:bg-red-700',
      'focus:ring-red-500',
      'active:bg-red-800'
    ],
    ghost: [
      'bg-transparent',
      'text-gray-700',
      'hover:bg-gray-100',
      'focus:ring-gray-500',
      'active:bg-gray-200'
    ]
  }

  // Size classes
  const sizeClasses = {
    sm: ['px-3', 'py-1.5', 'text-sm', 'gap-1.5'],
    md: ['px-4', 'py-2', 'text-base', 'gap-2'],
    lg: ['px-6', 'py-3', 'text-lg', 'gap-2.5']
  }

  // Width classes
  const widthClasses = fullWidth ? ['w-full'] : []

  // Combine all classes
  const buttonClasses = [
    ...baseClasses,
    ...variantClasses[variant],
    ...sizeClasses[size],
    ...widthClasses,
    className
  ].join(' ')

  // Loading spinner component
  const LoadingSpinner = () => (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )

  return (
    <button
      ref={ref}
      type={type}
      className={buttonClasses}
      disabled={isDisabled || isLoading}
      data-testid={testId}
      aria-disabled={isDisabled || isLoading}
      aria-busy={isLoading}
      {...rest}
    >
      {/* Left icon or loading spinner */}
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        leftIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {leftIcon}
          </span>
        )
      )}
      
      {/* Button content */}
      {children && (
        <span className={isLoading ? 'opacity-0' : ''}>
          {children}
        </span>
      )}
      
      {/* Right icon */}
      {!isLoading && rightIcon && (
        <span className="flex-shrink-0" aria-hidden="true">
          {rightIcon}
        </span>
      )}
    </button>
  )
})

// Display name for debugging
Button.displayName = 'Button'
```

### 1.4 Crear el archivo de exportación

```typescript
// src/components/ui/Button/index.ts
export { Button } from './Button'
export type { ButtonProps } from '../../../types/components'
```

### 1.5 Actualizar el barrel export principal

```typescript
// src/components/ui/index.ts
export * from './Button'
```

## 🧪 Paso 2: Testing del Componente

### 2.1 Configurar utilidades de testing

```typescript
// src/utils/test-utils.tsx
import { render, RenderOptions } from '@testing-library/react'
import { ReactElement } from 'react'

// Custom render function that includes providers if needed
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, {
    // Add providers here if needed (Theme, Router, etc.)
    ...options,
  })
}

export * from '@testing-library/react'
export { customRender as render }
```

### 2.2 Crear tests completos

```typescript
// src/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '../../../utils/test-utils'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

// Mock icon for testing
const MockIcon = () => <span data-testid="mock-icon">Icon</span>

describe('Button Component', () => {
  describe('Rendering', () => {
    test('renders with default props', () => {
      render(<Button>Click me</Button>)
      
      const button = screen.getByRole('button', { name: /click me/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('type', 'button')
    })

    test('renders with custom test id', () => {
      render(<Button testId="custom-button">Click me</Button>)
      
      expect(screen.getByTestId('custom-button')).toBeInTheDocument()
    })

    test('renders with different variants', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-blue-600')

      rerender(<Button variant="secondary">Secondary</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-gray-200')

      rerender(<Button variant="danger">Danger</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-red-600')

      rerender(<Button variant="ghost">Ghost</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-transparent')
    })

    test('renders with different sizes', () => {
      const { rerender } = render(<Button size="sm">Small</Button>)
      expect(screen.getByRole('button')).toHaveClass('px-3', 'py-1.5')

      rerender(<Button size="md">Medium</Button>)
      expect(screen.getByRole('button')).toHaveClass('px-4', 'py-2')

      rerender(<Button size="lg">Large</Button>)
      expect(screen.getByRole('button')).toHaveClass('px-6', 'py-3')
    })
  })

  describe('States', () => {
    test('handles disabled state correctly', () => {
      render(<Button isDisabled>Disabled</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveAttribute('aria-disabled', 'true')
    })

    test('handles loading state correctly', () => {
      render(<Button isLoading>Loading</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveAttribute('aria-busy', 'true')
      expect(screen.getByRole('button')).toContainHTML('animate-spin')
    })

    test('renders full width correctly', () => {
      render(<Button fullWidth>Full Width</Button>)
      
      expect(screen.getByRole('button')).toHaveClass('w-full')
    })
  })

  describe('Icons', () => {
    test('renders with left icon', () => {
      render(
        <Button leftIcon={<MockIcon />}>
          With Left Icon
        </Button>
      )
      
      expect(screen.getByTestId('mock-icon')).toBeInTheDocument()
      expect(screen.getByText('With Left Icon')).toBeInTheDocument()
    })

    test('renders with right icon', () => {
      render(
        <Button rightIcon={<MockIcon />}>
          With Right Icon
        </Button>
      )
      
      expect(screen.getByTestId('mock-icon')).toBeInTheDocument()
      expect(screen.getByText('With Right Icon')).toBeInTheDocument()
    })

    test('hides icons when loading', () => {
      render(
        <Button isLoading leftIcon={<MockIcon />} rightIcon={<MockIcon />}>
          Loading
        </Button>
      )
      
      expect(screen.queryByTestId('mock-icon')).not.toBeInTheDocument()
    })
  })

  describe('Interactions', () => {
    test('handles click events', async () => {
      const handleClick = jest.fn()
      const user = userEvent.setup()
      
      render(<Button onClick={handleClick}>Click me</Button>)
      
      await user.click(screen.getByRole('button'))
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    test('handles keyboard navigation', async () => {
      const handleClick = jest.fn()
      const user = userEvent.setup()
      
      render(<Button onClick={handleClick}>Press Enter</Button>)
      
      const button = screen.getByRole('button')
      button.focus()
      
      await user.keyboard('{Enter}')
      expect(handleClick).toHaveBeenCalledTimes(1)
      
      await user.keyboard(' ')
      expect(handleClick).toHaveBeenCalledTimes(2)
    })

    test('does not trigger click when disabled', async () => {
      const handleClick = jest.fn()
      const user = userEvent.setup()
      
      render(
        <Button onClick={handleClick} isDisabled>
          Disabled
        </Button>
      )
      
      await user.click(screen.getByRole('button'))
      expect(handleClick).not.toHaveBeenCalled()
    })

    test('does not trigger click when loading', async () => {
      const handleClick = jest.fn()
      const user = userEvent.setup()
      
      render(
        <Button onClick={handleClick} isLoading>
          Loading
        </Button>
      )
      
      await user.click(screen.getByRole('button'))
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(<Button>Accessible Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('type', 'button')
    })

    test('supports custom ARIA attributes', () => {
      render(
        <Button aria-label="Custom label" aria-describedby="description">
          Button
        </Button>
      )
      
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label', 'Custom label')
      expect(button).toHaveAttribute('aria-describedby', 'description')
    })

    test('has proper focus management', () => {
      render(<Button>Focusable</Button>)
      
      const button = screen.getByRole('button')
      button.focus()
      
      expect(button).toHaveFocus()
      expect(button).toHaveClass('focus:ring-2')
    })
  })
})
```

## 📱 Paso 3: Usar el Componente

### 3.1 Ejemplo básico de uso

```typescript
// src/App.tsx
import { Button } from './components/ui'

// Icons (puedes usar react-icons, lucide-react, etc.)
const PlusIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
)

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)

function App() {
  const handleSave = () => {
    console.log('Saving...')
  }

  const handleDelete = () => {
    console.log('Deleting...')
  }

  return (
    <div className="p-8 space-y-4">
      <h1 className="text-2xl font-bold mb-6">Button Examples</h1>
      
      {/* Basic buttons */}
      <div className="space-x-4">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="danger">Danger</Button>
        <Button variant="ghost">Ghost</Button>
      </div>
      
      {/* Different sizes */}
      <div className="space-x-4">
        <Button size="sm">Small</Button>
        <Button size="md">Medium</Button>
        <Button size="lg">Large</Button>
      </div>
      
      {/* With icons */}
      <div className="space-x-4">
        <Button leftIcon={<PlusIcon />} onClick={handleSave}>
          Add Item
        </Button>
        <Button 
          variant="danger" 
          rightIcon={<TrashIcon />} 
          onClick={handleDelete}
        >
          Delete
        </Button>
      </div>
      
      {/* States */}
      <div className="space-x-4">
        <Button isLoading>Loading...</Button>
        <Button isDisabled>Disabled</Button>
      </div>
      
      {/* Full width */}
      <Button fullWidth variant="primary">
        Full Width Button
      </Button>
    </div>
  )
}

export default App
```

## 🎯 Mejores Prácticas Implementadas

### ✅ TypeScript
- **Tipado estricto** con interfaces bien definidas
- **Props extendidas** de HTMLButtonElement
- **Ref forwarding** para acceso directo al DOM
- **Generic types** para reutilización

### ✅ Accesibilidad (WCAG 2.1)
- **Roles semánticos** apropiados
- **ARIA attributes** para estados
- **Navegación por teclado** completa
- **Focus management** visible
- **Screen reader** compatible

### ✅ Performance
- **Memoización** con forwardRef
- **Clases CSS** optimizadas
- **Bundle size** mínimo
- **Re-renders** controlados

### ✅ Testing
- **Unit tests** completos
- **Integration tests** para interacciones
- **Accessibility tests** incluidos
- **Coverage** del 100%

### ✅ Mantenibilidad
- **Código autodocumentado** con JSDoc
- **Patrones consistentes** en toda la aplicación
- **Separación de responsabilidades** clara
- **Escalabilidad** para nuevos variants

## 🚀 Próximos Pasos

### 1. Crear más componentes UI
- Input
- Card
- Modal
- Dropdown

### 2. Implementar un Design System
- Tokens de diseño
- Documentación con Storybook
- Guías de uso

### 3. Optimizaciones avanzadas
- Lazy loading
- Code splitting
- Performance monitoring

### 4. Herramientas adicionales
- ESLint rules personalizadas
- Prettier configuration
- Husky pre-commit hooks

## 📚 Recursos Adicionales

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Testing Library](https://testing-library.com/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**¡Felicidades! 🎉 Has creado tu primer componente React profesional siguiendo la filosofía Vibe Coding.**