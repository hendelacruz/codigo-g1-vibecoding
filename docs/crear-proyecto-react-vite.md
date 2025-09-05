# Guía Completa: Crear un Proyecto React con Vite

Esta guía te llevará paso a paso para crear un proyecto React moderno usando Vite, siguiendo las mejores prácticas de la filosofía **Vibe Coding**.

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Node.js** >= 18.0.0 ([Descargar aquí](https://nodejs.org/))
- **npm** >= 9.0.0 (incluido con Node.js)
- **Git** para control de versiones
- Un editor de código (recomendado: Trae)

### Verificar instalación

```bash
node --version
npm --version
git --version
```

## 🚀 Paso 1: Crear el Proyecto Base

### Opción A: Usando create-vite (Recomendado)

```bash
# Crear proyecto con template React + TypeScript
npm create vite@latest mi-proyecto-react -- --template react-ts

# Navegar al directorio del proyecto
cd mi-proyecto-react

# Instalar dependencias
npm install
```

### Opción B: Usando Vite directamente

```bash
# Crear proyecto interactivo
npm create vite@latest
# Seleccionar: React → TypeScript
```

## 🛠️ Paso 2: Configurar el Entorno de Desarrollo (Opcional)

```
Solo usar estos comandos, si el `package.json` esta vacio
```

### Instalar dependencias adicionales para desarrollo profesional

```bash
# Dependencias de desarrollo esenciales
npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D @vitejs/plugin-react

# Para testing (siguiendo filosofía Vibe Coding)
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event jest-environment-jsdom
npm install -D @types/jest ts-jest babel-jest

# Para styling moderno (Tailwind CSS v4)
npm install tailwindcss @tailwindcss/vite
```

## ⚙️ Paso 3: Configuración de Archivos

### 3.1 Configurar Vite (`vite.config.ts`) (Opcional)

- Recordemos que podemos trabajar con la configuración por defecto

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
```

### 3.2 Configurar TypeScript (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 3.3 Configurar ESLint (`eslint.config.js`)

```javascript
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  }
);
```

### 3.4 Configurar Jest (`jest.config.cjs`)

```javascript
/** @type {import('jest').Config} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/__tests__/setup.ts"],
  moduleNameMapping: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|svg)$": "jest-transform-stub",
  },
  transform: {
    "^.+\\.(ts|tsx)$": [
      "ts-jest",
      {
        tsconfig: {
          jsx: "react-jsx",
        },
      },
    ],
  },
  collectCoverageFrom: ["src/**/*.(ts|tsx)", "!src/**/*.d.ts", "!src/main.tsx"],
};
```

## 📁 Paso 4: Estructura de Carpetas (Arquitectura Vibe Coding)

Crea la siguiente estructura de carpetas:

```
src/
├── components/          # Componentes reutilizables
│   ├── ui/             # Componentes base (Button, Input, etc.)
│   └── feature/        # Componentes específicos de funcionalidad
├── hooks/              # Custom hooks
├── stores/             # State management (Zustand/Context)
├── services/           # API calls y lógica de negocio
├── types/              # TypeScript types
├── utils/              # Funciones utilitarias
├── constants/          # Constantes de la aplicación
├── assets/             # Recursos estáticos
└── __tests__/          # Configuración de testing
```

### Crear estructura automáticamente:

```bash
mkdir -p src/{components/{ui,feature},hooks,stores,services,types,utils,constants,assets,__tests__}
```

## 📦 Paso 5: Configurar Scripts en package.json

Añade estos scripts a tu `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "preview": "vite preview",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

## 🎨 Paso 6: Configurar Tailwind CSS v4

<mcreference link="https://tailwindcss.com/blog/tailwindcss-v4" index="2">2</mcreference> <mcreference link="https://tailwindcss.com/docs" index="5">5</mcreference> <mcreference link="https://medium.com/@npguapo/installation-of-tailwind-vite-react-javascript-or-typescript-ec1abdfa56b2" index="4">4</mcreference>

### Instalar Tailwind CSS v4

```bash
# Instalar Tailwind CSS v4 con el plugin de Vite
npm install tailwindcss @tailwindcss/vite
```

### Configurar el plugin de Vite (`vite.config.ts`)

Añade el plugin de Tailwind a tu configuración de Vite:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    open: true,
  },
});
```

### Importar Tailwind en `src/index.css`

Reemplaza todo el contenido de `src/index.css` con:

```css
@import "tailwindcss";

@layer base {
  html {
    font-family: "Inter", system-ui, sans-serif;
  }
}
```

### Ventajas de Tailwind CSS v4

- **Rendimiento mejorado**: Hasta 5x más rápido en builds completos y 100x más rápido en builds incrementales
- **Plugin nativo de Vite**: Integración optimizada sin necesidad de PostCSS
- **Instalación simplificada**: Solo una línea de CSS para importar
- **Detección automática de contenido**: No necesita configuración manual de rutas
- **CSS moderno**: Aprovecha cascade layers, custom properties y color-mix()
- **Sin archivo de configuración**: La configuración se hace directamente en CSS

## 🧪 Paso 7: Configurar Testing

### Crear archivo de setup para tests (`src/__tests__/setup.ts`)

```typescript
import "@testing-library/jest-dom";

// Mock para módulos que Jest no puede manejar
jest.mock("../assets/react.svg", () => "react-logo");
```

### Crear primer test (`src/__tests__/App.test.tsx`)

```typescript
import { render, screen } from "@testing-library/react";
import App from "../App";

describe("App Component", () => {
  test("renders without crashing", () => {
    render(<App />);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
```

## 🚀 Paso 8: Ejecutar el Proyecto

```bash
# Iniciar servidor de desarrollo
npm run dev

# Ejecutar tests
npm test

# Verificar linting
npm run lint

# Construir para producción
npm run build
```

## ✅ Verificación Final

Tu proyecto debería tener:

- ✅ React 18+ con TypeScript
- ✅ Vite como build tool
- ✅ ESLint configurado
- ✅ Jest y Testing Library
- ✅ Tailwind CSS
- ✅ Estructura de carpetas organizada
- ✅ Scripts de desarrollo y producción

## 🎯 Próximos Pasos

1. **Configurar Git**: `git init && git add . && git commit -m "Initial commit"`
2. **Añadir más dependencias** según necesidades del proyecto
3. **Configurar CI/CD** con GitHub Actions
4. **Implementar State Management** (Zustand, Context API)
5. **Añadir librerías específicas** (React Hook Form, Framer Motion, etc.)

## 📚 Recursos Adicionales

- [Documentación oficial de Vite](https://vitejs.dev/)
- [Documentación de React](https://react.dev/)
- [Guía de TypeScript](https://www.typescriptlang.org/docs/)
- [Testing Library](https://testing-library.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**¡Felicidades! 🎉 Has creado un proyecto React moderno siguiendo las mejores prácticas de Vibe Coding.**
