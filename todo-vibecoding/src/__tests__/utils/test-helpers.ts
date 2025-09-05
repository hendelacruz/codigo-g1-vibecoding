/**
 * @fileoverview Utilidades y helpers para testing
 *
 * Este archivo contiene funciones de utilidad, mocks y helpers
 * que pueden ser reutilizados a través de todos los tests:
 * - Factories para crear datos de prueba
 * - Mocks de localStorage y otras APIs
 * - Helpers para renderizado con providers
 * - Utilidades de aserción personalizadas
 */

import type { Todo } from "../../todos";

/**
 * Factory para crear objetos Todo de prueba
 *
 * @param overrides - Propiedades a sobrescribir en el TODO por defecto
 * @returns Un objeto Todo completo para usar en tests
 */
export const createMockTodo = (overrides: Partial<Todo> = {}): Todo => {
  const defaultTodo: Todo = {
    id: Number(Math.random().toString(36).substr(2, 9)),
    name: "Test todo",
    is_finished: false,
    created_at: new Date(),
    updated_at: new Date(),
  };

  return { ...defaultTodo, ...overrides };
};

/**
 * Factory para crear múltiples TODOs de prueba
 *
 * @param count - Número de TODOs a crear
 * @param baseOverrides - Propiedades base a aplicar a todos los TODOs
 * @returns Array de objetos Todo
 */
export const createMockTodos = (
  count: number,
  baseOverrides: Partial<Todo> = {}
): Todo[] => {
  return Array.from({ length: count }, (_, index) =>
    createMockTodo({
      ...baseOverrides,
      name: `Test todo ${index + 1}`,
      id: 1,
    })
  );
};

/**
 * Mock de localStorage para tests
 *
 * Proporciona una implementación completa de localStorage
 * que puede ser usada en tests sin efectos secundarios.
 */
export class MockLocalStorage {
  private store: Record<string, string> = {};

  getItem(key: string): string | null {
    return this.store[key] || null;
  }

  setItem(key: string, value: string): void {
    this.store[key] = value;
  }

  removeItem(key: string): void {
    delete this.store[key];
  }

  clear(): void {
    this.store = {};
  }

  get length(): number {
    return Object.keys(this.store).length;
  }

  key(index: number): string | null {
    const keys = Object.keys(this.store);
    return keys[index] || null;
  }
}

/**
 * Configura un mock de localStorage para tests
 *
 * @returns Instancia de MockLocalStorage configurada
 */
export const setupLocalStorageMock = (): MockLocalStorage => {
  const mockLocalStorage = new MockLocalStorage();

  Object.defineProperty(window, "localStorage", {
    value: mockLocalStorage,
    writable: true,
  });

  return mockLocalStorage;
};

/**
 * Limpia todos los mocks y restaura el estado original
 */
export const cleanupMocks = (): void => {
  jest.clearAllMocks();
  localStorage.clear();
};

/**
 * Espera a que un elemento aparezca en el DOM
 *
 * @param callback - Función que debe retornar true cuando la condición se cumpla
 * @param timeout - Tiempo máximo de espera en ms (default: 1000)
 * @returns Promise que se resuelve cuando la condición se cumple
 */
export const waitForCondition = async (
  callback: () => boolean,
  timeout = 1000
): Promise<void> => {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (callback()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 10));
  }

  throw new Error(`Condition not met within ${timeout}ms`);
};

/**
 * Simula un delay para tests asíncronos
 *
 * @param ms - Milisegundos a esperar
 * @returns Promise que se resuelve después del delay
 */
export const delay = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Matcher personalizado para verificar clases CSS de Tailwind
 *
 * @param element - Elemento a verificar
 * @param expectedClasses - Array de clases que deben estar presentes
 * @returns true si todas las clases están presentes
 */
export const hasAllClasses = (
  element: Element,
  expectedClasses: string[]
): boolean => {
  const classList = Array.from(element.classList);
  return expectedClasses.every((className) => classList.includes(className));
};

/**
 * Verifica que un elemento tenga los atributos de accesibilidad correctos
 *
 * @param element - Elemento a verificar
 * @returns Objeto con información sobre la accesibilidad del elemento
 */
export const checkAccessibility = (element: Element) => {
  return {
    hasAriaLabel: element.hasAttribute("aria-label"),
    hasRole: element.hasAttribute("role"),
    hasTabIndex: element.hasAttribute("tabindex"),
    isKeyboardAccessible: element.getAttribute("tabindex") !== "-1",
    ariaLabel: element.getAttribute("aria-label"),
    role: element.getAttribute("role"),
  };
};

/**
 * Simula eventos de teclado de forma más realista
 *
 * @param element - Elemento target del evento
 * @param key - Tecla a simular
 * @param options - Opciones adicionales del evento
 */
export const simulateKeyboardEvent = (
  element: Element,
  key: string,
  options: Partial<KeyboardEventInit> = {}
): void => {
  const event = new KeyboardEvent("keydown", {
    key,
    code: key,
    bubbles: true,
    cancelable: true,
    ...options,
  });

  element.dispatchEvent(event);
};

/**
 * Constantes útiles para tests
 */
export const TEST_CONSTANTS = {
  SAMPLE_TODOS: [
    "Completar el proyecto de React",
    "Revisar código con el equipo",
    "Escribir documentación",
    "Hacer testing de la aplicación",
    "Desplegar a producción",
  ],

  KEYBOARD_KEYS: {
    ENTER: "Enter",
    ESCAPE: "Escape",
    SPACE: " ",
    TAB: "Tab",
    ARROW_UP: "ArrowUp",
    ARROW_DOWN: "ArrowDown",
  },

  ARIA_LABELS: {
    ADD_TODO: "Agregar nueva tarea",
    EDIT_TODO: "Editar tarea",
    DELETE_TODO: "Eliminar tarea",
    COMPLETE_TODO: "Marcar como completada",
    FILTER_ALL: "Mostrar todas las tareas",
    FILTER_PENDING: "Mostrar tareas pendientes",
    FILTER_COMPLETED: "Mostrar tareas completadas",
  },

  CSS_CLASSES: {
    BUTTON_PRIMARY: ["bg-blue-600", "text-white", "hover:bg-blue-700"],
    BUTTON_SECONDARY: ["bg-gray-100", "text-gray-700", "hover:bg-gray-200"],
    INPUT_BASE: ["border", "rounded", "px-3", "py-2"],
    CARD_BASE: ["bg-white", "rounded-lg", "shadow", "p-4"],
  },
} as const;

/**
 * Tipos de utilidad para tests
 */
export type MockFunction<T extends (...args: any[]) => any> =
  jest.MockedFunction<T>;

export type TestTodo = Todo;

export type TestSetupOptions = {
  withLocalStorage?: boolean;
  initialTodos?: Todo[];
  mockTimers?: boolean;
};

/**
 * Setup completo para tests que necesitan configuración avanzada
 *
 * @param options - Opciones de configuración
 * @returns Objeto con utilidades configuradas
 */
export const setupAdvancedTest = (options: TestSetupOptions = {}) => {
  const {
    withLocalStorage = true,
    initialTodos = [],
    mockTimers = false,
  } = options;

  let mockLocalStorage: MockLocalStorage | undefined;

  if (withLocalStorage) {
    mockLocalStorage = setupLocalStorageMock();
    if (initialTodos.length > 0) {
      mockLocalStorage.setItem("todos", JSON.stringify(initialTodos));
    }
  }

  if (mockTimers) {
    jest.useFakeTimers();
  }

  const cleanup = () => {
    cleanupMocks();
    if (mockTimers) {
      jest.useRealTimers();
    }
  };

  return {
    mockLocalStorage,
    cleanup,
    createTodo: createMockTodo,
    createTodos: createMockTodos,
  };
};
