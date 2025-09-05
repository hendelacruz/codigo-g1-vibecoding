# Todo VibeCoding

Una aplicación de gestión de tareas (Todo App) desarrollada siguiendo la filosofía **Vibe Coding**, enfocada en escribir código eficiente, mantenible y con estándares profesionales usando las mejores prácticas de desarrollo moderno.

## 🚀 Stack Tecnológico

### Frontend Framework
- **React 19.1.0** - Biblioteca principal para la interfaz de usuario
- **TypeScript 5.8.3** - Tipado estático para mayor robustez del código
- **Vite 7.0.4** - Build tool y dev server ultrarrápido

### Styling
- **Tailwind CSS 4.1.11** - Framework de CSS utility-first para diseño moderno
- **@tailwindcss/vite** - Plugin de Vite para integración optimizada

### Testing
- **Jest 30.0.5** - Framework de testing principal
- **@testing-library/react 16.3.0** - Utilidades para testing de componentes React
- **@testing-library/jest-dom 6.6.3** - Matchers adicionales para Jest
- **@testing-library/user-event 14.6.1** - Simulación de eventos de usuario
- **ts-jest 29.4.0** - Preset de Jest para TypeScript
- **jsdom** - Entorno DOM para testing

### Desarrollo y Calidad de Código
- **ESLint 9.30.1** - Linter para mantener calidad del código
- **TypeScript ESLint** - Reglas específicas para TypeScript
- **Babel** - Transpilador para compatibilidad

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura modular y escalable basada en los principios de **Clean Architecture** y **SOLID**:

```
src/
├── components/              # Componentes reutilizables
│   ├── ui/                  # Componentes base del sistema de diseño
│   │   ├── FilterButtons.tsx
│   │   ├── Footer.tsx
│   │   ├── Header.tsx
│   │   ├── StatsCard.tsx
│   │   ├── StatsSection.tsx
│   │   ├── TodoItem.tsx
│   │   ├── TodoList.tsx
│   │   └── index.ts         # Barrel exports
│   └── feature/             # Componentes específicos de funcionalidad
├── hooks/                   # Custom hooks para lógica reutilizable
│   └── useTodo.ts          # Hook principal para gestión de todos
├── stores/                  # State management (Zustand/Context)
├── services/                # API calls y lógica de negocio
├── types/                   # Definiciones de tipos TypeScript
│   └── svg.d.ts            # Tipos para archivos SVG
├── utils/                   # Funciones utilitarias
│   ├── dateUtils.ts        # Utilidades para manejo de fechas
│   └── index.ts            # Barrel exports
├── constants/               # Constantes de la aplicación
├── assets/                  # Recursos estáticos
├── __tests__/               # Configuración y tests
│   ├── setup.ts            # Configuración global de testing
│   └── *.test.tsx          # Archivos de test
└── main.tsx                 # Punto de entrada de la aplicación
```

### Patrones de Diseño Implementados

- **Container/Presentational Pattern**: Separación entre lógica y presentación
- **Custom Hooks Pattern**: Encapsulación de lógica reutilizable
- **Barrel Exports**: Organización limpia de imports/exports
- **Composition over Inheritance**: Uso de composición para reutilización

## 🛠️ Instalación y Configuración

### Prerrequisitos

- **Node.js** >= 18.0.0
- **npm** >= 9.0.0 (o yarn/pnpm como alternativa)
- **Git** para clonar el repositorio

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd todo-vibecoding
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Ejecutar en modo desarrollo**
   ```bash
   npm run dev
   ```
   La aplicación estará disponible en `http://localhost:3000`

## 📜 Scripts Disponibles

### Desarrollo
```bash
npm run dev          # Inicia el servidor de desarrollo
npm run build        # Construye la aplicación para producción
npm run preview      # Previsualiza la build de producción
npm run lint         # Ejecuta el linter para verificar calidad del código
```

### Testing
```bash
npm run test         # Ejecuta todos los tests
npm run test:watch   # Ejecuta tests en modo watch
npm run test:coverage # Ejecuta tests con reporte de cobertura
npm run test:ci      # Ejecuta tests para CI/CD
```

## 🧪 Testing

El proyecto incluye una configuración completa de testing con:

- **Unit Tests**: Para componentes individuales
- **Integration Tests**: Para verificar la interacción entre componentes
- **Coverage Reports**: Reportes de cobertura en HTML y LCOV

### Ejecutar Tests

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar tests en modo watch para desarrollo
npm run test:watch
```

## 🎯 Características Principales

- ✅ **TypeScript** con tipado estricto
- ✅ **Testing** completo con Jest y Testing Library
- ✅ **Linting** con ESLint para calidad de código
- ✅ **Arquitectura escalable** siguiendo principios SOLID
- ✅ **Componentes reutilizables** con sistema de diseño
- ✅ **Custom Hooks** para lógica compartida
- ✅ **Accesibilidad** con soporte para lectores de pantalla
- ✅ **Responsive Design** con Tailwind CSS

## 🚀 Despliegue

Para construir la aplicación para producción:

```bash
npm run build
```

Los archivos optimizados se generarán en la carpeta `dist/` y estarán listos para ser desplegados en cualquier servidor web estático.

## 🤝 Contribución

Este proyecto sigue la filosofía **Vibe Coding**. Al contribuir, asegúrate de:

1. Mantener el tipado estricto de TypeScript
2. Escribir tests para nuevas funcionalidades
3. Seguir los patrones de arquitectura establecidos
4. Mantener la accesibilidad en todos los componentes
5. Usar ESLint para mantener la calidad del código

---

**Desarrollado con ❤️ siguiendo la filosofía Vibe Coding**