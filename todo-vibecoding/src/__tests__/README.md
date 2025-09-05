# Testing Structure - Todo VibeCoding

Este proyecto implementa una **arquitectura de testing distribuido** siguiendo las mejores prácticas de testing moderno en React. Los tests están organizados de manera que cada componente tenga sus tests co-localizados, facilitando el mantenimiento y la escalabilidad.

## 📁 Estructura de Directorios

```
src/
├── components/
│   ├── ui/
│   │   ├── Header/
│   │   │   ├── Header.tsx
│   │   │   ├── Header.test.tsx      # ✅ Test unitario co-localizado
│   │   │   └── index.ts
│   │   ├── Footer/
│   │   │   ├── Footer.tsx
│   │   │   ├── Footer.test.tsx      # ✅ Test unitario co-localizado
│   │   │   └── index.ts
│   │   └── StatsCard/
│   │       ├── StatsCard.tsx
│   │       ├── StatsCard.test.tsx   # ✅ Test unitario co-localizado
│   │       └── index.ts
│   └── feature/
│       ├── FilterButtons/
│       │   ├── FilterButtons.tsx
│       │   ├── FilterButtons.test.tsx  # ✅ Test unitario co-localizado
│       │   └── index.ts
│       ├── TodoItem/
│       │   ├── TodoItem.tsx
│       │   ├── TodoItem.test.tsx       # ✅ Test unitario co-localizado
│       │   └── index.ts
│       ├── TodoList/
│       │   ├── TodoList.tsx
│       │   ├── TodoList.test.tsx       # ✅ Test unitario co-localizado
│       │   └── index.ts
│       └── StatsSection/
│           ├── StatsSection.tsx
│           ├── StatsSection.test.tsx   # ✅ Test unitario co-localizado
│           └── index.ts
└── __tests__/
    ├── integration/
    │   ├── App.test.tsx                # ✅ Test de integración principal
    │   └── TodoSystem.test.tsx         # ✅ Test de integración del sistema
    ├── e2e/                            # 📁 Para tests end-to-end futuros
    └── utils/
        ├── setup.ts                    # ✅ Configuración global de tests
        ├── test-helpers.ts             # ✅ Utilidades y helpers
        └── README.md                   # 📖 Esta documentación
```

## 🎯 Tipos de Tests

### 1. **Tests Unitarios** (Co-localizados)
- **Ubicación**: Junto a cada componente
- **Propósito**: Probar componentes de forma aislada
- **Cobertura**: Props, eventos, renderizado, accesibilidad
- **Ejemplo**: `Header.test.tsx`, `TodoItem.test.tsx`

### 2. **Tests de Integración**
- **Ubicación**: `src/__tests__/integration/`
- **Propósito**: Probar interacción entre múltiples componentes
- **Cobertura**: Flujos de usuario, estado compartido, comunicación entre componentes
- **Ejemplo**: `App.test.tsx`, `TodoSystem.test.tsx`

### 3. **Tests End-to-End** (Preparado para el futuro)
- **Ubicación**: `src/__tests__/e2e/`
- **Propósito**: Probar la aplicación completa desde la perspectiva del usuario
- **Herramientas sugeridas**: Playwright, Cypress

### 4. **Utilidades de Testing**
- **Ubicación**: `src/__tests__/utils/`
- **Propósito**: Helpers, mocks, configuración compartida
- **Archivos**: `setup.ts`, `test-helpers.ts`

## 🛠️ Herramientas y Configuración

### Stack de Testing
- **Jest**: Framework de testing principal
- **React Testing Library**: Utilidades para testing de React
- **@testing-library/jest-dom**: Matchers adicionales para Jest
- **@testing-library/user-event**: Simulación realista de eventos de usuario

### Configuración Jest
El archivo `jest.config.cjs` está configurado para:
- ✅ Detectar tests co-localizados en `src/components/`
- ✅ Ejecutar tests de integración en `src/__tests__/`
- ✅ Usar setup personalizado desde `src/__tests__/utils/setup.ts`
- ✅ Generar reportes de cobertura completos
- ✅ Soporte para TypeScript y JSX

## 📋 Convenciones de Naming

### Archivos de Test
```
✅ ComponentName.test.tsx    # Preferido
✅ ComponentName.spec.tsx    # Alternativo
❌ ComponentName.test.js     # Evitar JS en favor de TS
```

### Estructura de Tests
```typescript
describe("ComponentName", () => {
  // Setup común
  beforeEach(() => {
    // Configuración antes de cada test
  });

  describe("Rendering", () => {
    it("should render correctly", () => {
      // Test de renderizado básico
    });
  });

  describe("User Interactions", () => {
    it("should handle click events", () => {
      // Test de interacciones
    });
  });

  describe("Accessibility", () => {
    it("should be keyboard accessible", () => {
      // Test de accesibilidad
    });
  });
});
```

## 🎨 Mejores Prácticas

### 1. **Co-localización de Tests**
```
✅ BIEN: src/components/ui/Button/Button.test.tsx
❌ MAL:  src/__tests__/Button.test.tsx
```

### 2. **Imports Relativos**
```typescript
// En tests co-localizados
import { Button } from "./Button";           // ✅ BIEN
import { Button } from "../../../Button";    // ❌ MAL
```

### 3. **Uso de Test Helpers**
```typescript
import { createMockTodo, setupLocalStorageMock } from "../../__tests__/utils/test-helpers";

// Usar helpers para datos de prueba consistentes
const mockTodo = createMockTodo({ text: "Test todo" });
```

### 4. **Testing de Accesibilidad**
```typescript
// Siempre incluir tests de accesibilidad
it("should be accessible", () => {
  render(<Component />);
  
  const button = screen.getByRole("button");
  expect(button).toHaveAttribute("aria-label");
  expect(button).not.toHaveAttribute("tabindex", "-1");
});
```

### 5. **Testing de Estados**
```typescript
// Probar todos los estados del componente
it("should handle loading state", () => {
  render(<Component loading={true} />);
  expect(screen.getByText("Loading...")).toBeInTheDocument();
});

it("should handle error state", () => {
  render(<Component error="Something went wrong" />);
  expect(screen.getByText("Something went wrong")).toBeInTheDocument();
});
```

## 🚀 Comandos de Testing

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests en modo watch
npm run test:watch

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar solo tests unitarios (co-localizados)
npm test -- --testPathPattern="src/components"

# Ejecutar solo tests de integración
npm test -- --testPathPattern="src/__tests__/integration"

# Ejecutar tests de un componente específico
npm test -- --testNamePattern="TodoItem"
```

## 📊 Métricas de Cobertura

El proyecto mantiene los siguientes objetivos de cobertura:
- **Statements**: > 90%
- **Branches**: > 85%
- **Functions**: > 90%
- **Lines**: > 90%

## 🔄 Flujo de Desarrollo con Tests

1. **Crear Componente**: `ComponentName.tsx`
2. **Crear Test**: `ComponentName.test.tsx` (mismo directorio)
3. **Implementar Tests**: Renderizado, props, eventos, accesibilidad
4. **Verificar Cobertura**: `npm run test:coverage`
5. **Refactorizar**: Mantener tests verdes durante refactoring

## 🤝 Contribución

Al agregar nuevos componentes:
1. ✅ Crear el test junto al componente
2. ✅ Seguir las convenciones de naming
3. ✅ Incluir tests de accesibilidad
4. ✅ Usar helpers cuando sea apropiado
5. ✅ Mantener cobertura > 90%

## 📚 Recursos Adicionales

- [React Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Accessibility Testing](https://web.dev/accessibility-testing/)

---

**Nota**: Esta estructura de testing distribuido facilita el mantenimiento, mejora la discoverabilidad de tests y promueve la responsabilidad de cada desarrollador sobre la calidad de sus componentes.