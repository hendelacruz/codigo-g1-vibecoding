# Instalación de React Router v7

## Descripción
Este documento describe el proceso de instalación de React Router v7 en el proyecto todo-vibecoding, siguiendo las mejores prácticas de Vibe Coding.

## Prerrequisitos
- Node.js instalado
- Proyecto React con Vite configurado
- npm como gestor de paquetes

## Pasos de Instalación

### 1. Instalación de Dependencias

Ejecutar el siguiente comando en la terminal desde la raíz del proyecto:

```bash
npm install react-router@7 react-router-dom@7
```

### 2. Verificación de la Instalación

Después de la instalación, verificar que las dependencias se agregaron correctamente al `package.json`:

```json
{
  "dependencies": {
    "react-router": "^7.8.0",
    "react-router-dom": "^7.8.0"
  }
}
```

### 3. Configuración Básica

Para implementar React Router v7 en tu aplicación, sigue estos pasos:

#### 3.1 Configurar el Router Principal

Modifica tu archivo `main.tsx` para incluir el BrowserRouter:

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

#### 3.2 Configurar Rutas en App.tsx

```tsx
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import AboutPage from './pages/AboutPage'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </div>
  )
}

export default App
```

## Características de React Router v7

### Nuevas Funcionalidades
- **Mejor rendimiento**: Optimizaciones en el bundle size
- **TypeScript mejorado**: Mejor tipado y autocompletado
- **Lazy loading**: Soporte nativo para carga diferida de componentes
- **Nested routing**: Rutas anidadas más intuitivas

### Hooks Principales
- `useNavigate()`: Para navegación programática
- `useLocation()`: Para acceder a la ubicación actual
- `useParams()`: Para obtener parámetros de la URL
- `useSearchParams()`: Para manejar query parameters

## Ejemplo de Uso Básico

```tsx
import { useNavigate, useParams } from 'react-router-dom'

function UserProfile() {
  const navigate = useNavigate()
  const { userId } = useParams()

  const handleGoBack = () => {
    navigate(-1) // Navegar hacia atrás
  }

  return (
    <div>
      <h1>Perfil del Usuario {userId}</h1>
      <button onClick={handleGoBack}>Volver</button>
    </div>
  )
}
```

## Consideraciones de Testing

Para testing con React Router v7, usar `MemoryRouter` en los tests:

```tsx
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

test('renders app with routing', () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>
  )
})
```

## Próximos Pasos

1. Crear estructura de páginas en `src/pages/`
2. Implementar navegación en componentes
3. Configurar rutas protegidas si es necesario
4. Agregar tests para componentes con routing

## Recursos Adicionales

- [Documentación oficial de React Router v7](https://reactrouter.com/)
- [Guía de migración desde v6](https://reactrouter.com/upgrading/v6)
- [Ejemplos de implementación](https://github.com/remix-run/react-router/tree/main/examples)

---

**Fecha de instalación**: $(date)
**Versión instalada**: 7.8.0
**Proyecto**: todo-vibecoding
**Metodología**: Vibe Coding