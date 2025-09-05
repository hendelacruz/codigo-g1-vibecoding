# Documentación del Componente Button

Esta documentación explica línea por línea el funcionamiento del componente Button implementado siguiendo la filosofía Vibe Coding.

## 📁 Ubicación del Archivo

```
src/components/ui/Button/Button.tsx
```

## 🔍 Análisis Línea por Línea

### Importaciones (Líneas 1-2)

```typescript
import type { ButtonProps } from "../../../types/components";
import { forwardRef } from "react";
```

**Línea 1:** Importa el tipo `ButtonProps` desde el archivo de tipos. El uso de `type` indica que es solo para tipado TypeScript y será eliminado en el build.

**Línea 2:** Importa `forwardRef` de React, que permite pasar referencias del DOM a componentes hijos, esencial para accesibilidad y manipulación directa del elemento.

### Documentación JSDoc (Líneas 4-8)

```typescript
/**
 * Button component following Vibe Coding principles
 * 
 * @param props - ButtonProps interface with all button properties
 * @returns JSX.Element - Rendered button component
 */
```

**Propósito:** Documentación estándar JSDoc que describe:
- Qué hace el componente
- Qué parámetros recibe
- Qué retorna
- Aparece en el IntelliSense del IDE

### Declaración del Componente (Líneas 9-25)

```typescript
export const Button = forwardRef<HTMLButtonElement, ButtonProps>((
  {
    className = "",
    children,
    testId,
    variant = "primary",
    size = "md",
    isLoading = false,
    isDisabled = false,
    leftIcon,
    rightIcon,
    fullWidth = false,
    type = "button",
    ...rest
  },
  ref
) => {
```

**Línea 9:** Declara el componente usando `forwardRef` con tipos genéricos:
- `HTMLButtonElement`: Tipo del elemento DOM al que se refiere
- `ButtonProps`: Tipo de las props del componente

**Líneas 11-23:** Destructuring de props con valores por defecto:
- `className = ""`: Clases CSS adicionales (vacío por defecto)
- `variant = "primary"`: Estilo visual del botón
- `size = "md"`: Tamaño del botón (mediano por defecto)
- `isLoading = false`: Estado de carga
- `isDisabled = false`: Estado deshabilitado
- `fullWidth = false`: Si ocupa todo el ancho disponible
- `type = "button"`: Tipo HTML del botón
- `...rest`: Resto de props HTML nativas

**Línea 24:** Segundo parámetro de `forwardRef` que recibe la referencia

### Clases Base (Líneas 27-40)

```typescript
const baseClasses = [
  "inline-flex",
  "items-center",
  "justify-center",
  "font-medium",
  "rounded-lg",
  "transition-all",
  "duration-200",
  "focus:outline-none",
  "focus:ring-2",
  "focus:ring-offset-2",
  "disabled:opacity-50",
  "disabled:cursor-not-allowed",
  "disabled:pointer-events-none"
];
```

**Propósito:** Define las clases CSS base que todos los botones tendrán:
- `inline-flex`: Display flex en línea
- `items-center`: Centra verticalmente el contenido
- `justify-center`: Centra horizontalmente el contenido
- `font-medium`: Peso de fuente medio
- `rounded-lg`: Bordes redondeados grandes
- `transition-all`: Transiciones suaves en todas las propiedades
- `duration-200`: Duración de 200ms para transiciones
- `focus:outline-none`: Elimina el outline por defecto
- `focus:ring-2`: Añade un anillo de enfoque de 2px
- `focus:ring-offset-2`: Offset del anillo de enfoque
- `disabled:opacity-50`: Opacidad reducida cuando está deshabilitado
- `disabled:cursor-not-allowed`: Cursor de "no permitido" cuando está deshabilitado
- `disabled:pointer-events-none`: Desactiva eventos del mouse cuando está deshabilitado

### Clases de Variantes (Líneas 43-75)

```typescript
const variantClasses = {
  primary: [
    "bg-blue-600",
    "text-white",
    "hover:bg-blue-700",
    "focus:ring-blue-500",
    "active:bg-blue-800",
  ],
  // ... más variantes
};
```

**Propósito:** Define los estilos específicos para cada variante del botón:

**Primary (Líneas 44-50):**
- `bg-blue-600`: Fondo azul
- `text-white`: Texto blanco
- `hover:bg-blue-700`: Fondo más oscuro al hacer hover
- `focus:ring-blue-500`: Anillo azul al enfocar
- `active:bg-blue-800`: Fondo aún más oscuro al hacer clic

**Secondary (Líneas 51-57):** Estilo gris neutro
**Danger (Líneas 58-64):** Estilo rojo para acciones destructivas
**Warning (Líneas 65-71):** Estilo amarillo para advertencias
**Info (Líneas 72-78):** Estilo azul claro para información

### Clases de Tamaño (Líneas 81-85)

```typescript
const sizeClasses = {
  sm: ["px-3", "py-1.5", "text-sm", "gap-1.5"],
  md: ["px-4", "py-2", "text-base", "gap-2"],
  lg: ["px-6", "py-3", "text-lg", "gap-2.5"]
};
```

**Propósito:** Define padding, tamaño de texto y espaciado para cada tamaño:
- `px-*`: Padding horizontal
- `py-*`: Padding vertical
- `text-*`: Tamaño del texto
- `gap-*`: Espaciado entre elementos internos

### Clases de Ancho (Líneas 88-89)

```typescript
const widthClasses = fullWidth ? ["w-full"] : [];
```

**Propósito:** Aplica `w-full` (ancho completo) solo si `fullWidth` es `true`.

### Combinación de Clases (Líneas 92-98)

```typescript
const buttonClasses = [
  ...baseClasses,
  ...variantClasses[variant],
  ...sizeClasses[size],
  ...widthClasses,
  className
].join(" ");
```

**Propósito:** Combina todas las clases CSS en una sola cadena:
1. Clases base (siempre aplicadas)
2. Clases de la variante seleccionada
3. Clases del tamaño seleccionado
4. Clases de ancho (si aplica)
5. Clases personalizadas del prop `className`
6. `join(" ")` convierte el array en string separado por espacios

### Componente Loading Spinner (Líneas 101-119)

```typescript
const LoadingSpinner = () => (
  <svg
    className="animate-spin h-4 w-4"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    {/* SVG paths */}
  </svg>
);
```

**Propósito:** Componente interno que renderiza un spinner animado:
- `animate-spin`: Animación de rotación de Tailwind
- `h-4 w-4`: Tamaño fijo de 16x16px
- `aria-hidden="true"`: Oculta el elemento de lectores de pantalla
- SVG optimizado para indicar estado de carga

### Renderizado del Botón (Líneas 122-167)

```typescript
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
```

**Línea 123:** `ref={ref}` - Pasa la referencia al elemento DOM
**Línea 124:** `type={type}` - Tipo HTML del botón
**Línea 125:** `className={buttonClasses}` - Aplica todas las clases calculadas
**Línea 126:** `disabled={isDisabled || isLoading}` - Deshabilita si está disabled o loading
**Línea 127:** `data-testid={testId}` - Identificador para testing
**Línea 128:** `aria-disabled` - Atributo de accesibilidad para estado deshabilitado
**Línea 129:** `aria-busy` - Indica a lectores de pantalla que está ocupado
**Línea 130:** `{...rest}` - Pasa todas las props HTML nativas restantes

### Contenido del Botón (Líneas 132-167)

#### Icono Izquierdo o Spinner (Líneas 133-142)

```typescript
{isLoading ? (
  <LoadingSpinner />
) : (
  leftIcon && (
    <span className="flex-shrink-0" aria-hidden="true">
      {leftIcon}
    </span>
  )
)}
```

**Lógica:** Si está cargando, muestra el spinner; si no, muestra el icono izquierdo si existe.
- `flex-shrink-0`: Evita que el icono se reduzca
- `aria-hidden="true"`: Oculta iconos decorativos de lectores de pantalla

#### Contenido Principal (Líneas 145-149)

```typescript
{children && (
  <span className={isLoading ? "opacity-0" : ""}>
    {children}
  </span>
)}
```

**Lógica:** Muestra el contenido del botón (texto) con opacidad 0 durante la carga para mantener el tamaño.

#### Icono Derecho (Líneas 152-158)

```typescript
{!isLoading && rightIcon && (
  <span className="flex-shrink-0" aria-hidden="true">
    {rightIcon}
  </span>
)}
```

**Lógica:** Muestra el icono derecho solo si no está cargando y existe el icono.

### Display Name (Línea 171)

```typescript
Button.displayName = "Button";
```

**Propósito:** Establece el nombre del componente para herramientas de desarrollo y debugging.

## 🎯 Características Implementadas

### ✅ Accesibilidad
- **ARIA attributes** (`aria-disabled`, `aria-busy`, `aria-hidden`)
- **Navegación por teclado** (focus ring)
- **Screen reader** compatible
- **Estados semánticos** claros

### ✅ Performance
- **forwardRef** para acceso directo al DOM
- **Clases CSS** optimizadas y reutilizables
- **Conditional rendering** eficiente
- **No re-renders** innecesarios

### ✅ TypeScript
- **Tipado estricto** con interfaces
- **Props extendidas** de HTMLButtonElement
- **Valores por defecto** explícitos
- **IntelliSense** completo

### ✅ UX/UI
- **Estados visuales** claros (hover, focus, active, disabled, loading)
- **Transiciones suaves** (200ms)
- **Responsive design** con Tailwind
- **Iconos** con soporte izquierdo/derecho
- **Loading state** con spinner animado

### ✅ Mantenibilidad
- **Código autodocumentado** con comentarios
- **Separación de responsabilidades** clara
- **Patrones consistentes** en toda la implementación
- **Escalabilidad** para nuevas variantes

## 🧪 Testing

El componente está diseñado para ser fácilmente testeable con:
- `data-testid` para selección en tests
- Estados claramente definidos
- Props controlables
- Comportamiento predecible

## 📚 Uso del Componente

```typescript
// Ejemplo básico
<Button>Click me</Button>

// Con todas las props
<Button
  variant="primary"
  size="lg"
  isLoading={false}
  isDisabled={false}
  leftIcon={<PlusIcon />}
  rightIcon={<ArrowIcon />}
  fullWidth={true}
  onClick={handleClick}
  testId="submit-button"
>
  Submit Form
</Button>
```

Este componente Button representa un ejemplo perfecto de la filosofía Vibe Coding: código limpio, tipado estricto, accesible, performante y mantenible.