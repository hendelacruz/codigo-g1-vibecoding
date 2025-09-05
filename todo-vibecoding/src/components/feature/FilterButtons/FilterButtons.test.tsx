/**
 * @fileoverview Tests para el componente FilterButtons
 * 
 * Este archivo contiene tests unitarios que verifican:
 * - Renderizado correcto de los botones de filtro
 * - Funcionalidad de cambio de filtro
 * - Estados activos e inactivos
 * - Accesibilidad y navegación por teclado
 * - Estilos y clases CSS aplicadas
 */

import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { FilterButtons } from "./FilterButtons";
import type { FilterType } from "../../../hooks/useTodo";

/**
 * Suite de tests para el componente FilterButtons
 * 
 * Verifica el renderizado y funcionalidad de los botones de filtrado,
 * incluyendo estados activos, eventos de click y accesibilidad.
 */
describe("FilterButtons Component", () => {
  const mockOnFilterChange = jest.fn();
  
  const defaultProps = {
    currentFilter: "all" as FilterType,
    onFilterChange: mockOnFilterChange,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * @test Renderizado básico
   * Verifica que el componente se renderiza correctamente
   * con todos los botones de filtro esperados.
   */
  it("should render all filter buttons correctly", () => {
    render(<FilterButtons {...defaultProps} />);
    
    expect(screen.getByText("Todas")).toBeInTheDocument();
    expect(screen.getByText("Pendientes")).toBeInTheDocument();
    expect(screen.getByText("Completadas")).toBeInTheDocument();
  });

  /**
   * @test Estado activo
   * Verifica que el botón correspondiente al filtro actual
   * tenga las clases CSS correctas para el estado activo.
   */
  it("should highlight the active filter button", () => {
    render(<FilterButtons {...defaultProps} currentFilter="pending" />);
    
    const pendingButton = screen.getByText("Pendientes");
    const allButton = screen.getByText("Todas");
    
    expect(pendingButton).toHaveClass("bg-orange-600", "text-white");
    expect(allButton).toHaveClass("bg-white", "text-gray-700");
  });

  /**
   * @test Funcionalidad de click
   * Verifica que al hacer click en un botón se llame
   * la función onFilterChange con el filtro correcto.
   */
  it("should call onFilterChange when a button is clicked", () => {
    render(<FilterButtons {...defaultProps} />);
    
    const completedButton = screen.getByText("Completadas");
    fireEvent.click(completedButton);
    
    expect(mockOnFilterChange).toHaveBeenCalledWith("completed");
    expect(mockOnFilterChange).toHaveBeenCalledTimes(1);
  });

  /**
   * @test Accesibilidad - ARIA labels
   * Verifica que todos los botones tengan los atributos
   * de accesibilidad correctos.
   */
  it("should have proper accessibility attributes", () => {
    render(<FilterButtons {...defaultProps} />);
    
    const buttons = screen.getAllByRole("button");
    
    buttons.forEach((button) => {
      expect(button).toHaveAttribute("aria-label");
    });
    
    // Verificar ARIA labels específicos
    expect(screen.getByLabelText("Mostrar todas las tareas")).toBeInTheDocument();
    expect(screen.getByLabelText("Mostrar tareas pendientes")).toBeInTheDocument();
    expect(screen.getByLabelText("Mostrar tareas completadas")).toBeInTheDocument();
  });

  /**
   * @test Navegación por teclado
   * Verifica que los botones sean accesibles mediante
   * navegación por teclado y focus.
   */
  it("should handle keyboard navigation", () => {
    render(<FilterButtons {...defaultProps} />);
    
    const buttons = screen.getAllByRole("button");
    
    // Verificar que los botones son focusables
    buttons.forEach((button) => {
      expect(button).not.toHaveAttribute("tabindex", "-1");
    });
    
    // Test focus y click
    const pendingButton = screen.getByText("Pendientes");
    pendingButton.focus();
    expect(pendingButton).toHaveFocus();
    
    fireEvent.click(pendingButton);
    expect(mockOnFilterChange).toHaveBeenCalledWith("pending");
  });

  /**
   * @test Estilos responsivos
   * Verifica que el contenedor tenga las clases CSS
   * correctas para el diseño responsivo.
   */
  it("should have responsive design classes", () => {
    const { container } = render(<FilterButtons {...defaultProps} />);
    
    const buttonContainer = container.firstChild;
    expect(buttonContainer).toHaveClass(
      "flex",
      "flex-wrap",
      "gap-2",
      "justify-center",
      "mb-8"
    );
  });

  /**
   * @test Todos los filtros disponibles
   * Verifica que se puedan seleccionar todos los tipos
   * de filtro disponibles (all, pending, completed).
   */
  it("should handle all filter types", () => {
    const { rerender } = render(<FilterButtons {...defaultProps} />);
    
    // Test "all" filter
    rerender(<FilterButtons {...defaultProps} currentFilter="all" />);
    expect(screen.getByText("Todas")).toHaveClass("bg-blue-600");
    
    // Test "pending" filter
    rerender(<FilterButtons {...defaultProps} currentFilter="pending" />);
    expect(screen.getByText("Pendientes")).toHaveClass("bg-orange-600");
    
    // Test "completed" filter
    rerender(<FilterButtons {...defaultProps} currentFilter="completed" />);
    expect(screen.getByText("Completadas")).toHaveClass("bg-green-600");
  });

  /**
   * @test Estructura semántica
   * Verifica que el componente tenga una estructura
   * HTML semánticamente correcta.
   */
  it("should have proper semantic structure", () => {
    const { container } = render(<FilterButtons {...defaultProps} />);
    
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);
    
    // Verify container structure
    expect(container.firstChild).toBeInTheDocument();
    expect(container.firstChild?.nodeName).toBe("DIV");
  });
});