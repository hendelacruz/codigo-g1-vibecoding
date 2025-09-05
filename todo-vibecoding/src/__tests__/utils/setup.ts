/**
 * @fileoverview Configuración global para tests de Jest
 * 
 * Este archivo contiene la configuración necesaria para ejecutar tests
 * en el entorno de Jest, incluyendo:
 * - Extensiones de Jest DOM para matchers adicionales
 * - Mocks de APIs del navegador no disponibles en Node.js
 * - Configuración de objetos globales para testing
 * 
 * @author Vibe Coding Team
 * @version 1.0.0
 */

// Importa matchers adicionales de Jest DOM para testing
import "@testing-library/jest-dom";

/**
 * Mock de IntersectionObserver API
 * 
 * IntersectionObserver no está disponible en el entorno de Node.js,
 * por lo que creamos un mock para evitar errores en los tests.
 * 
 * @class IntersectionObserver
 * @description Mock que simula la API IntersectionObserver del navegador
 */
Object.defineProperty(globalThis, "IntersectionObserver", {
  writable: true,
  value: class IntersectionObserver {
    /**
     * Constructor del mock de IntersectionObserver
     * @constructor
     */
    constructor() {}
    
    /**
     * Mock del método disconnect
     * @method disconnect
     */
    disconnect() {}
    
    /**
     * Mock del método observe
     * @method observe
     */
    observe() {}
    
    /**
     * Mock del método unobserve
     * @method unobserve
     */
    unobserve() {}
  },
});

/**
 * Mock de ResizeObserver API
 * 
 * ResizeObserver no está disponible en el entorno de Node.js,
 * por lo que creamos un mock para evitar errores en los tests.
 * 
 * @class ResizeObserver
 * @description Mock que simula la API ResizeObserver del navegador
 */
Object.defineProperty(globalThis, "ResizeObserver", {
  writable: true,
  value: class ResizeObserver {
    /**
     * Constructor del mock de ResizeObserver
     * @constructor
     */
    constructor() {}
    
    /**
     * Mock del método disconnect
     * @method disconnect
     */
    disconnect() {}
    
    /**
     * Mock del método observe
     * @method observe
     */
    observe() {}
    
    /**
     * Mock del método unobserve
     * @method unobserve
     */
    unobserve() {}
  },
});

/**
 * Mock de window.matchMedia API
 * 
 * matchMedia no está disponible en el entorno de Node.js,
 * por lo que creamos un mock para testing de media queries.
 * 
 * @function matchMedia
 * @param {string} query - Media query string
 * @returns {Object} Mock object con propiedades de MediaQueryList
 * @description Mock que simula la API matchMedia del navegador
 */
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: jest.fn().mockImplementation((query: string) => ({
    matches: false,                    // Siempre retorna false en tests
    media: query,                      // Retorna la query original
    onchange: null,                    // Handler de cambio
    addListener: jest.fn(),            // Método deprecated
    removeListener: jest.fn(),         // Método deprecated
    addEventListener: jest.fn(),       // Método moderno para eventos
    removeEventListener: jest.fn(),    // Método moderno para remover eventos
    dispatchEvent: jest.fn(),          // Método para disparar eventos
  })),
});

/**
 * Mock de CSS API
 * 
 * Proporciona un mock de la API CSS para testing,
 * especialmente útil para CSS.supports().
 * 
 * @namespace CSS
 * @property {Function} supports - Mock de CSS.supports() que siempre retorna false
 * @description Mock que simula la API CSS del navegador
 */
Object.defineProperty(window, "CSS", {
  value: {
    /**
     * Mock del método CSS.supports()
     * @function supports
     * @returns {boolean} Siempre retorna false en el entorno de testing
     */
    supports: jest.fn().mockReturnValue(false),
  },
});