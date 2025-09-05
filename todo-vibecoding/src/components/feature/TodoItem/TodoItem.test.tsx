/**
 * @fileoverview Tests de integración para el componente TodoItem
 * 
 * Este archivo contiene tests que verifican:
 * - Renderizado correcto de todos completados y pendientes
 * - Visualización de información del todo (ID, nombre, fechas)
 * - Aplicación correcta de estilos según el estado
 * - Integración con función formatDate
 * - Estructura semántica y accesibilidad
 * - Comportamiento de hover y transiciones
 * - Manejo de diferentes tipos de datos
 * 
 * @author Vibe Coding Team
 * @version 1.0.0
 */

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { TodoItem } from "./TodoItem";
import type { Todo } from "../../../todos";

/**
 * Suite de tests para el componente TodoItem
 * 
 * Verifica el renderizado y funcionalidad del componente que muestra
 * información individual de cada todo, incluyendo estado, fechas y metadatos.
 */
describe("TodoItem Component", () => {
  /**
   * Función mock para formatear fechas en los tests
   * 
   * @function mockFormatDate
   * @param {Date} date - Fecha a formatear
   * @returns {string} Fecha formateada como string
   */
  const mockFormatDate = (date: Date): string => {
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  };

  /**
   * Todo de prueba en estado completado
   * 
   * @constant {Todo} completedTodo - Todo marcado como finalizado
   */
  const completedTodo: Todo = {
    id: 1,
    name: "Implementar autenticación de usuarios",
    is_finished: true,
    created_at: new Date("2024-01-15T09:00:00Z"),
    updated_at: new Date("2024-01-16T10:15:00Z"),
  };

  /**
   * Todo de prueba en estado pendiente
   * 
   * @constant {Todo} pendingTodo - Todo marcado como no finalizado
   */
  const pendingTodo: Todo = {
    id: 2,
    name: "Crear componentes reutilizables",
    is_finished: false,
    created_at: new Date("2024-01-16T08:15:00Z"),
    updated_at: new Date("2024-01-16T08:15:00Z"),
  };

  /**
   * Test: Renderizado correcto de todo completado
   * 
   * Verifica que un todo completado se renderice con:
   * - Nombre del todo visible
   * - Estado "Completada" con ícono de check
   * - ID formateado correctamente
   * - Fechas de creación y actualización
   * 
   * @test {HTMLElement} todoName - Título del todo
   * @test {HTMLElement} statusBadge - Badge de estado completado
   * @test {HTMLElement} todoId - ID del todo
   * @test {HTMLElement} dates - Fechas de creación y actualización
   */
  it("renders completed todo correctly", () => {
    render(<TodoItem todo={completedTodo} formatDate={mockFormatDate} />);

    // Verifica el nombre del todo
    expect(screen.getByText("Implementar autenticación de usuarios")).toBeInTheDocument();

    // Verifica el estado completado
    expect(screen.getByText("Completada")).toBeInTheDocument();
    expect(screen.getByText("✓")).toBeInTheDocument();

    // Verifica el ID
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("ID:")).toBeInTheDocument();

    // Verifica las fechas
    expect(screen.getByText("Creada:")).toBeInTheDocument();
    expect(screen.getByText("Actualizada:")).toBeInTheDocument();
    expect(screen.getByText("15/01/2024")).toBeInTheDocument();
    expect(screen.getByText("16/01/2024")).toBeInTheDocument();
  });

  /**
   * Test: Renderizado correcto de todo pendiente
   * 
   * Verifica que un todo pendiente se renderice con:
   * - Nombre del todo visible
   * - Estado "Pendiente" con ícono de círculo
   * - ID formateado correctamente
   * - Fechas de creación y actualización
   * 
   * @test {HTMLElement} todoName - Título del todo
   * @test {HTMLElement} statusBadge - Badge de estado pendiente
   * @test {HTMLElement} todoId - ID del todo
   * @test {HTMLElement} dates - Fechas de creación y actualización
   */
  it("renders pending todo correctly", () => {
    render(<TodoItem todo={pendingTodo} formatDate={mockFormatDate} />);

    // Verifica el nombre del todo
    expect(screen.getByText("Crear componentes reutilizables")).toBeInTheDocument();

    // Verifica el estado pendiente
    expect(screen.getByText("Pendiente")).toBeInTheDocument();
    expect(screen.getByText("○")).toBeInTheDocument();

    // Verifica el ID
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("ID:")).toBeInTheDocument();

    // Verifica las fechas (misma fecha para creación y actualización)
    expect(screen.getByText("Creada:")).toBeInTheDocument();
    expect(screen.getByText("Actualizada:")).toBeInTheDocument();
    expect(screen.getAllByText("16/01/2024")).toHaveLength(2);
  });

  /**
   * Test: Aplicación correcta de clases CSS para todo completado
   * 
   * Verifica que los estilos de estado completado se apliquen correctamente:
   * - Badge con colores verdes
   * - Estructura de layout apropiada
   * 
   * @test {HTMLElement} statusBadge - Badge con clases de estado completado
   */
  it("applies correct CSS classes for completed todo", () => {
    render(<TodoItem todo={completedTodo} formatDate={mockFormatDate} />);

    const statusBadge = screen.getByText("Completada").closest("span");
    expect(statusBadge).toHaveClass("bg-green-100");
    expect(statusBadge).toHaveClass("text-green-800");
  });

  /**
   * Test: Aplicación correcta de clases CSS para todo pendiente
   * 
   * Verifica que los estilos de estado pendiente se apliquen correctamente:
   * - Badge con colores naranjas
   * - Estructura de layout apropiada
   * 
   * @test {HTMLElement} statusBadge - Badge con clases de estado pendiente
   */
  it("applies correct CSS classes for pending todo", () => {
    render(<TodoItem todo={pendingTodo} formatDate={mockFormatDate} />);

    const statusBadge = screen.getByText("Pendiente").closest("span");
    expect(statusBadge).toHaveClass("bg-orange-100");
    expect(statusBadge).toHaveClass("text-orange-800");
  });

  /**
   * Test: Estructura semántica correcta
   * 
   * Verifica que el componente mantenga una estructura HTML semántica:
   * - Contenedor principal con clases apropiadas
   * - Jerarquía de encabezados correcta
   * - Elementos de información bien estructurados
   * 
   * @test {HTMLElement} container - Contenedor principal del componente
   * @test {HTMLElement} title - Título del todo como h3
   */
  it("has proper semantic structure", () => {
    const { container } = render(
      <TodoItem todo={completedTodo} formatDate={mockFormatDate} />
    );

    // Verifica el contenedor principal
    const mainContainer = container.firstChild as HTMLElement;
    expect(mainContainer).toHaveClass("bg-white");
    expect(mainContainer).toHaveClass("rounded-xl");
    expect(mainContainer).toHaveClass("shadow-lg");

    // Verifica el título como h3
    const title = screen.getByRole("heading", { level: 3 });
    expect(title).toBeInTheDocument();
    expect(title).toHaveTextContent("Implementar autenticación de usuarios");
  });

  /**
   * Test: Integración correcta con función formatDate
   * 
   * Verifica que el componente utilice correctamente la función
   * formatDate proporcionada como prop para mostrar las fechas.
   * 
   * @test {Function} formatDate - Función de formateo de fechas
   */
  it("integrates correctly with formatDate function", () => {
    const customFormatDate = jest.fn((date: Date) => {
      return `Custom: ${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    });

    render(<TodoItem todo={completedTodo} formatDate={customFormatDate} />);

    // Verifica que la función se haya llamado para ambas fechas
    expect(customFormatDate).toHaveBeenCalledTimes(2);
    expect(customFormatDate).toHaveBeenCalledWith(completedTodo.created_at);
    expect(customFormatDate).toHaveBeenCalledWith(completedTodo.updated_at);

    // Verifica que las fechas formateadas aparezcan en el DOM
    expect(screen.getByText("Custom: 2024-1-15")).toBeInTheDocument();
    expect(screen.getByText("Custom: 2024-1-16")).toBeInTheDocument();
  });

  /**
   * Test: Clases de hover y transición
   * 
   * Verifica que el componente tenga las clases CSS necesarias
   * para efectos de hover y transiciones suaves.
   * 
   * @test {HTMLElement} container - Contenedor con clases de hover
   */
  it("has hover and transition classes", () => {
    const { container } = render(
      <TodoItem todo={completedTodo} formatDate={mockFormatDate} />
    );

    const mainContainer = container.firstChild as HTMLElement;
    expect(mainContainer).toHaveClass("hover:shadow-xl");
    expect(mainContainer).toHaveClass("transition-shadow");
    expect(mainContainer).toHaveClass("duration-200");
  });

  /**
   * Test: Manejo de IDs grandes
   * 
   * Verifica que el componente maneje correctamente IDs de gran tamaño
   * y los muestre en el formato apropiado.
   * 
   * @test {HTMLElement} idElement - Elemento que muestra el ID
   */
  it("handles large ID numbers correctly", () => {
    const todoWithLargeId: Todo = {
      ...completedTodo,
      id: 999999,
    };

    render(<TodoItem todo={todoWithLargeId} formatDate={mockFormatDate} />);

    expect(screen.getByText("999999")).toBeInTheDocument();
    
    // Verifica que el ID tenga las clases de formato apropiadas
    const idElement = screen.getByText("999999");
    expect(idElement).toHaveClass("bg-gray-100");
    expect(idElement).toHaveClass("font-mono");
  });

  /**
   * Test: Manejo de nombres largos
   * 
   * Verifica que el componente maneje correctamente nombres de todos
   * muy largos sin romper el layout.
   * 
   * @test {HTMLElement} titleElement - Título del todo
   */
  it("handles long todo names correctly", () => {
    const todoWithLongName: Todo = {
      ...completedTodo,
      name: "Este es un nombre de todo extremadamente largo que debería manejarse correctamente sin romper el diseño del componente y manteniendo la legibilidad",
    };

    render(<TodoItem todo={todoWithLongName} formatDate={mockFormatDate} />);

    const titleElement = screen.getByRole("heading", { level: 3 });
    expect(titleElement).toBeInTheDocument();
    expect(titleElement).toHaveClass("flex-1");
    expect(titleElement).toHaveClass("mr-4");
  });

  /**
   * Test: Soporte para modo oscuro
   * 
   * Verifica que el componente incluya las clases CSS necesarias
   * para el soporte de modo oscuro (dark mode).
   * 
   * @test {HTMLElement} container - Contenedor con clases de modo oscuro
   * @test {HTMLElement} statusBadge - Badge con clases de modo oscuro
   */
  it("has dark mode support classes", () => {
    const { container } = render(
      <TodoItem todo={completedTodo} formatDate={mockFormatDate} />
    );

    const mainContainer = container.firstChild as HTMLElement;
    expect(mainContainer).toHaveClass("dark:bg-slate-800");
    expect(mainContainer).toHaveClass("dark:border-slate-700");

    const statusBadge = screen.getByText("Completada").closest("span");
    expect(statusBadge).toHaveClass("dark:bg-green-900/20");
    expect(statusBadge).toHaveClass("dark:text-green-300");
  });

  /**
   * Test: Accesibilidad del componente
   * 
   * Verifica que el componente cumpla con estándares de accesibilidad:
   * - Estructura de encabezados apropiada
   * - Contraste de colores adecuado
   * - Información clara y legible
   * 
   * @test {HTMLElement} heading - Encabezado accesible
   * @test {HTMLElement} statusInfo - Información de estado accesible
   */
  it("maintains accessibility standards", () => {
    render(<TodoItem todo={completedTodo} formatDate={mockFormatDate} />);

    // Verifica que haya un encabezado de nivel 3
    const heading = screen.getByRole("heading", { level: 3 });
    expect(heading).toBeInTheDocument();

    // Verifica que la información esté claramente etiquetada
    expect(screen.getByText("ID:")).toBeInTheDocument();
    expect(screen.getByText("Creada:")).toBeInTheDocument();
    expect(screen.getByText("Actualizada:")).toBeInTheDocument();

    // Verifica que el estado sea claramente visible
    expect(screen.getByText("Completada")).toBeInTheDocument();
  });
});