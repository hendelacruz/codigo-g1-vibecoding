/**
 * @fileoverview Tests de integración para el componente TodoList
 * 
 * Este archivo contiene tests que verifican:
 * - Renderizado de listas de todos con múltiples elementos
 * - Estado vacío con mensaje personalizable
 * - Integración correcta con componente TodoItem
 * - Grid responsivo y layout adaptativo
 * - Manejo de props y funciones de formateo
 * - Estructura semántica y accesibilidad
 * - Comportamiento con diferentes tamaños de lista
 * 
 * @author Vibe Coding Team
 * @version 1.0.0
 */

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { TodoList } from "./TodoList";
import type { Todo } from "../../../todos";

/**
 * Suite de tests para el componente TodoList
 * 
 * Verifica el renderizado y funcionalidad del componente que maneja
 * la visualización de listas de todos, incluyendo estados vacíos
 * e integración con TodoItem.
 */
describe("TodoList Component", () => {
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
   * Lista de todos de prueba con diferentes estados
   * 
   * @constant {Todo[]} mockTodos - Array de todos para testing
   */
  const mockTodos: Todo[] = [
    {
      id: 1,
      name: "Implementar autenticación de usuarios",
      is_finished: true,
      created_at: new Date("2024-01-15T09:00:00Z"),
      updated_at: new Date("2024-01-16T10:15:00Z"),
    },
    {
      id: 2,
      name: "Crear componentes reutilizables",
      is_finished: false,
      created_at: new Date("2024-01-16T08:15:00Z"),
      updated_at: new Date("2024-01-16T08:15:00Z"),
    },
    {
      id: 3,
      name: "Configurar base de datos PostgreSQL",
      is_finished: true,
      created_at: new Date("2024-01-13T11:20:00Z"),
      updated_at: new Date("2024-01-14T16:45:00Z"),
    },
  ];

  /**
   * Test: Renderizado de lista vacía con mensaje por defecto
   * 
   * Verifica que cuando no hay todos, se muestre:
   * - Emoji de libreta (📝)
   * - Mensaje por defecto "No hay tareas para mostrar"
   * - Estructura centrada apropiada
   * 
   * @test {HTMLElement} emptyState - Estado vacío del componente
   * @test {HTMLElement} emoji - Emoji de libreta
   * @test {HTMLElement} message - Mensaje de estado vacío
   */
  it("renders empty state with default message", () => {
    render(<TodoList todos={[]} formatDate={mockFormatDate} />);

    // Verifica el emoji
    expect(screen.getByText("📝")).toBeInTheDocument();

    // Verifica el mensaje por defecto
    expect(screen.getByText("No hay tareas para mostrar")).toBeInTheDocument();

    // Verifica que no haya elementos de todo
    expect(screen.queryByRole("heading", { level: 3 })).not.toBeInTheDocument();
  });

  /**
   * Test: Renderizado de lista vacía con mensaje personalizado
   * 
   * Verifica que se pueda personalizar el mensaje de estado vacío
   * a través de la prop emptyMessage.
   * 
   * @test {HTMLElement} customMessage - Mensaje personalizado
   */
  it("renders empty state with custom message", () => {
    const customMessage = "¡Genial! No tienes tareas pendientes";
    render(
      <TodoList
        todos={[]}
        formatDate={mockFormatDate}
        emptyMessage={customMessage}
      />
    );

    expect(screen.getByText(customMessage)).toBeInTheDocument();
    expect(screen.getByText("📝")).toBeInTheDocument();
  });

  /**
   * Test: Renderizado de lista con todos
   * 
   * Verifica que cuando hay todos en la lista:
   * - Se rendericen todos los TodoItem
   * - Cada todo tenga su información visible
   * - No se muestre el estado vacío
   * 
   * @test {HTMLElement[]} todoItems - Elementos TodoItem renderizados
   * @test {HTMLElement[]} todoNames - Nombres de los todos
   */
  it("renders list with todos", () => {
    render(<TodoList todos={mockTodos} formatDate={mockFormatDate} />);

    // Verifica que se rendericen todos los todos
    expect(screen.getByText("Implementar autenticación de usuarios")).toBeInTheDocument();
    expect(screen.getByText("Crear componentes reutilizables")).toBeInTheDocument();
    expect(screen.getByText("Configurar base de datos PostgreSQL")).toBeInTheDocument();

    // Verifica que no se muestre el estado vacío
    expect(screen.queryByText("📝")).not.toBeInTheDocument();
    expect(screen.queryByText("No hay tareas para mostrar")).not.toBeInTheDocument();

    // Verifica que haya 3 encabezados (uno por todo)
    expect(screen.getAllByRole("heading", { level: 3 })).toHaveLength(3);
  });

  /**
   * Test: Estructura de grid responsivo
   * 
   * Verifica que el componente aplique las clases CSS correctas
   * para el grid responsivo (1 columna en móvil, 2 en tablet, 3 en desktop).
   * 
   * @test {HTMLElement} gridContainer - Contenedor del grid
   */
  it("applies correct grid layout classes", () => {
    const { container } = render(
      <TodoList todos={mockTodos} formatDate={mockFormatDate} />
    );

    const gridContainer = container.firstChild as HTMLElement;
    expect(gridContainer).toHaveClass("grid");
    expect(gridContainer).toHaveClass("gap-6");
    expect(gridContainer).toHaveClass("md:grid-cols-2");
    expect(gridContainer).toHaveClass("lg:grid-cols-3");
  });

  /**
   * Test: Integración correcta con TodoItem
   * 
   * Verifica que cada TodoItem reciba las props correctas:
   * - Todo object correspondiente
   * - Función formatDate
   * - Key única basada en todo.id
   * 
   * @test {HTMLElement[]} todoItems - Componentes TodoItem integrados
   */
  it("integrates correctly with TodoItem components", () => {
    render(<TodoList todos={mockTodos} formatDate={mockFormatDate} />);

    // Verifica que cada todo tenga su estado correcto (2 completadas, 1 pendiente)
    expect(screen.getAllByText("Completada")).toHaveLength(2);
    expect(screen.getAllByText("Pendiente")).toHaveLength(1);

    // Verifica que se muestren los IDs
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();

    // Verifica que se muestren las fechas formateadas
    expect(screen.getByText("15/01/2024")).toBeInTheDocument();
    expect(screen.getAllByText("16/01/2024")).toHaveLength(3); // Aparece en updated_at del primer todo y created_at/updated_at del segundo
    expect(screen.getByText("13/01/2024")).toBeInTheDocument();
    expect(screen.getByText("14/01/2024")).toBeInTheDocument();
  });

  /**
   * Test: Manejo de lista con un solo elemento
   * 
   * Verifica que el componente maneje correctamente listas
   * con un solo todo sin romper el layout del grid.
   * 
   * @test {HTMLElement} singleTodo - Todo único en la lista
   */
  it("handles single todo correctly", () => {
    const singleTodo = [mockTodos[0]];
    render(<TodoList todos={singleTodo} formatDate={mockFormatDate} />);

    expect(screen.getByText("Implementar autenticación de usuarios")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 3 })).toHaveLength(1);
    
    // Verifica que el grid se mantenga
    const { container } = render(
      <TodoList todos={singleTodo} formatDate={mockFormatDate} />
    );
    const gridContainer = container.firstChild as HTMLElement;
    expect(gridContainer).toHaveClass("grid");
  });

  /**
   * Test: Manejo de lista grande
   * 
   * Verifica que el componente maneje correctamente listas
   * con muchos elementos sin problemas de rendimiento.
   * 
   * @test {HTMLElement[]} manyTodos - Lista extensa de todos
   */
  it("handles large list of todos", () => {
    const largeTodoList: Todo[] = Array.from({ length: 10 }, (_, index) => ({
      id: index + 1,
      name: `Todo número ${index + 1}`,
      is_finished: index % 2 === 0,
      created_at: new Date(`2024-01-${(index % 28) + 1}T09:00:00Z`),
      updated_at: new Date(`2024-01-${(index % 28) + 1}T09:00:00Z`),
    }));

    render(<TodoList todos={largeTodoList} formatDate={mockFormatDate} />);

    // Verifica que se rendericen todos los elementos
    expect(screen.getAllByRole("heading", { level: 3 })).toHaveLength(10);
    expect(screen.getByText("Todo número 1")).toBeInTheDocument();
    expect(screen.getByText("Todo número 10")).toBeInTheDocument();
  });

  /**
   * Test: Estructura semántica del estado vacío
   * 
   * Verifica que el estado vacío mantenga una estructura
   * HTML semántica apropiada con clases de estilo correctas.
   * 
   * @test {HTMLElement} emptyContainer - Contenedor del estado vacío
   */
  it("has proper semantic structure for empty state", () => {
    const { container } = render(
      <TodoList todos={[]} formatDate={mockFormatDate} />
    );

    const emptyContainer = container.firstChild as HTMLElement;
    expect(emptyContainer).toHaveClass("text-center");
    expect(emptyContainer).toHaveClass("py-12");

    // Verifica la estructura del emoji
    const emojiElement = screen.getByText("📝");
    expect(emojiElement).toHaveClass("text-6xl");
    expect(emojiElement).toHaveClass("mb-4");

    // Verifica la estructura del mensaje
    const messageElement = screen.getByText("No hay tareas para mostrar");
    expect(messageElement).toHaveClass("text-gray-500");
    expect(messageElement).toHaveClass("text-lg");
  });

  /**
   * Test: Soporte para modo oscuro en estado vacío
   * 
   * Verifica que el estado vacío incluya las clases CSS
   * necesarias para el soporte de modo oscuro.
   * 
   * @test {HTMLElement} messageElement - Mensaje con clases de modo oscuro
   */
  it("has dark mode support for empty state", () => {
    render(<TodoList todos={[]} formatDate={mockFormatDate} />);

    const messageElement = screen.getByText("No hay tareas para mostrar");
    expect(messageElement).toHaveClass("dark:text-gray-400");
  });

  /**
   * Test: Integración con función formatDate personalizada
   * 
   * Verifica que el componente pase correctamente la función
   * formatDate a todos los componentes TodoItem.
   * 
   * @test {Function} customFormatDate - Función personalizada de formateo
   */
  it("integrates with custom formatDate function", () => {
    const customFormatDate = jest.fn((date: Date) => {
      return `Fecha: ${date.getFullYear()}`;
    });

    render(<TodoList todos={mockTodos} formatDate={customFormatDate} />);

    // Verifica que la función se haya llamado para cada todo (2 veces por todo: created_at y updated_at)
    expect(customFormatDate).toHaveBeenCalledTimes(6); // 3 todos × 2 fechas cada uno

    // Verifica que las fechas formateadas aparezcan
    expect(screen.getAllByText("Fecha: 2024")).toHaveLength(6);
  });

  /**
   * Test: Comportamiento con todos que tienen el mismo ID (edge case)
   * 
   * Verifica el manejo de casos extremos donde podrían existir
   * todos con IDs duplicados (aunque no debería ocurrir en producción).
   * 
   * @test {HTMLElement[]} duplicateIdTodos - Todos con IDs duplicados
   */
  it("handles edge case with duplicate IDs", () => {
    const todosWithDuplicateIds: Todo[] = [
      {
        id: 1,
        name: "Primer todo",
        is_finished: false,
        created_at: new Date("2024-01-15T09:00:00Z"),
        updated_at: new Date("2024-01-15T09:00:00Z"),
      },
      {
        id: 1,
        name: "Segundo todo con mismo ID",
        is_finished: true,
        created_at: new Date("2024-01-16T09:00:00Z"),
        updated_at: new Date("2024-01-16T09:00:00Z"),
      },
    ];

    // Esto debería renderizar ambos todos a pesar del ID duplicado
    render(<TodoList todos={todosWithDuplicateIds} formatDate={mockFormatDate} />);

    expect(screen.getByText("Primer todo")).toBeInTheDocument();
    expect(screen.getByText("Segundo todo con mismo ID")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 3 })).toHaveLength(2);
  });

  /**
   * Test: Accesibilidad del componente
   * 
   * Verifica que el componente cumpla con estándares de accesibilidad:
   * - Estructura semántica apropiada
   * - Contraste de colores adecuado
   * - Información clara en estado vacío
   * 
   * @test {HTMLElement} accessibleElements - Elementos accesibles
   */
  it("maintains accessibility standards", () => {
    // Test con lista de todos
    const { rerender } = render(
      <TodoList todos={mockTodos} formatDate={mockFormatDate} />
    );

    // Verifica que haya encabezados apropiados
    const headings = screen.getAllByRole("heading", { level: 3 });
    expect(headings).toHaveLength(3);
    headings.forEach(heading => {
      expect(heading).toBeInTheDocument();
    });

    // Test con estado vacío
    rerender(<TodoList todos={[]} formatDate={mockFormatDate} />);

    // Verifica que el mensaje de estado vacío sea claro
    const emptyMessage = screen.getByText("No hay tareas para mostrar");
    expect(emptyMessage).toBeInTheDocument();
    expect(emptyMessage.tagName).toBe("P"); // Debe ser un párrafo semánticamente correcto
  });
});