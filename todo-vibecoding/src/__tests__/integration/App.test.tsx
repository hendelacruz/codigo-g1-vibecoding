/**
 * @fileoverview Tests para el componente principal App
 *
 * Este archivo contiene tests de integración que verifican:
 * - Renderizado correcto de elementos principales
 * - Funcionalidad de filtros de tareas
 * - Estructura semántica y accesibilidad
 * - Estadísticas de tareas
 * - Navegación e interacciones del usuario
 *
 * @author Vibe Coding Team
 * @version 1.0.0
 */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import App from "../../App";

/**
 * Helper function to render App with Router context
 */
const renderWithRouter = (component: React.ReactElement = <App />) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

/**
 * Suite de tests para el componente App principal
 *
 * Verifica la funcionalidad completa de la aplicación de tareas,
 * incluyendo renderizado, interacciones y accesibilidad.
 */
describe("App Component", () => {
  /**
   * Test: Renderizado del título principal
   *
   * Verifica que el título principal "Lista de Tareas" se renderice correctamente
   * como un heading de nivel 1 (h1) para mantener la jerarquía semántica.
   *
   * @test {string} title - Debe mostrar "Lista de Tareas"
   * @test {HTMLElement} heading - Debe ser un elemento h1
   */
  it("renders the main title correctly", () => {
    renderWithRouter();

    const title = screen.getByRole("heading", { level: 1 });
    expect(title).toBeInTheDocument();
    expect(title).toHaveTextContent("Lista de Tareas");
  });

  /**
   * Test: Renderizado del subtítulo
   *
   * Verifica que el subtítulo descriptivo se muestre correctamente
   * para proporcionar contexto sobre la funcionalidad de la app.
   *
   * @test {HTMLElement} subtitle - Debe contener el texto descriptivo
   */
  it("renders the subtitle correctly", () => {
    renderWithRouter();

    const subtitle = screen.getByText(
      "Gestiona tus tareas de manera eficiente"
    );
    expect(subtitle).toBeInTheDocument();
  });

  /**
   * Test: Sección de estadísticas
   *
   * Verifica que las tarjetas de estadísticas se rendericen correctamente
   * mostrando los contadores de Total, Completadas y Pendientes.
   *
   * @test {HTMLElement[]} totalLabels - Elementos que muestran "Total"
   * @test {HTMLElement[]} completedLabels - Elementos que muestran "Completadas"
   * @test {HTMLElement[]} pendingLabels - Elementos que muestran "Pendientes"
   */
  it("displays statistics section with correct values", () => {
    renderWithRouter();

    // Check for stats cards - there should be multiple elements with these texts
    const totalLabels = screen.getAllByText("Total");
    const completedLabels = screen.getAllByText("Completadas");
    const pendingLabels = screen.getAllByText("Pendientes");

    expect(totalLabels.length).toBeGreaterThan(0);
    expect(completedLabels.length).toBeGreaterThan(0);
    expect(pendingLabels.length).toBeGreaterThan(0);
  });

  /**
   * Test: Botones de filtro
   *
   * Verifica que los botones de filtro se rendericen con las etiquetas
   * correctas y tengan los atributos de accesibilidad apropiados.
   *
   * @test {HTMLElement} allButton - Botón "Todas" con aria-label
   * @test {HTMLElement} pendingButton - Botón "Pendientes" con aria-label
   * @test {HTMLElement} completedButton - Botón "Completadas" con aria-label
   */
  it("renders filter buttons with correct labels", () => {
    renderWithRouter();

    const allButton = screen.getByLabelText("Mostrar todas las tareas");
    const pendingButton = screen.getByLabelText("Mostrar tareas pendientes");
    const completedButton = screen.getByLabelText("Mostrar tareas completadas");

    expect(allButton).toBeInTheDocument();
    expect(pendingButton).toBeInTheDocument();
    expect(completedButton).toBeInTheDocument();

    expect(allButton).toHaveTextContent("Todas");
    expect(pendingButton).toHaveTextContent("Pendientes");
    expect(completedButton).toHaveTextContent("Completadas");
  });

  /**
   * Test: Funcionalidad de filtros interactivos
   *
   * Verifica que los filtros cambien correctamente cuando se hace clic
   * en los botones, aplicando las clases CSS correspondientes para
   * indicar el estado activo.
   *
   * @test {Function} user.click - Simula clics del usuario
   * @test {string} bg-orange-600 - Clase CSS para filtro pendientes activo
   * @test {string} bg-green-600 - Clase CSS para filtro completadas activo
   * @test {string} bg-blue-600 - Clase CSS para filtro todas activo
   */
  it("changes filter when filter buttons are clicked", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    const pendingButton = screen.getByLabelText("Mostrar tareas pendientes");
    const completedButton = screen.getByLabelText("Mostrar tareas completadas");
    const allButton = screen.getByLabelText("Mostrar todas las tareas");

    // Click pending filter
    await user.click(pendingButton);
    expect(pendingButton).toHaveClass("bg-orange-600");

    // Click completed filter
    await user.click(completedButton);
    expect(completedButton).toHaveClass("bg-green-600");

    // Click all filter
    await user.click(allButton);
    expect(allButton).toHaveClass("bg-blue-600");
  });

  /**
   * Test: Badge de Tailwind CSS en footer
   *
   * Verifica que el footer contenga el badge de Tailwind CSS
   * para mostrar la tecnología utilizada en el proyecto.
   *
   * @test {HTMLElement} badge - Elemento con texto "Powered by Tailwind CSS v4"
   */
  it("displays Tailwind CSS badge in footer", () => {
    renderWithRouter();

    const badge = screen.getByText("Powered by Tailwind CSS v4");
    expect(badge).toBeInTheDocument();
  });

  /**
   * Test: Estructura semántica HTML
   *
   * Verifica que la aplicación tenga una estructura semántica correcta
   * con elementos header, main y footer apropiados para accesibilidad.
   *
   * @test {HTMLElement} header - Elemento con role="banner"
   * @test {HTMLElement} heading - Elemento h1 para jerarquía
   * @test {HTMLElement} footer - Elemento con role="contentinfo"
   */
  it("has proper semantic structure", () => {
    renderWithRouter();

    // Check for header
    const header = screen.getByRole("banner");
    expect(header).toBeInTheDocument();

    // Check for heading hierarchy
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();

    // Check for footer
    const footer = screen.getByRole("contentinfo");
    expect(footer).toBeInTheDocument();
  });

  /**
   * Test: Clases CSS de fondo degradado
   *
   * Verifica que el contenedor principal tenga las clases CSS
   * correctas para el fondo degradado y altura mínima de pantalla.
   *
   * @test {HTMLElement} rootDiv - Elemento raíz del componente
   * @test {string} min-h-screen - Clase para altura mínima
   * @test {string} bg-gradient-to-br - Clase para degradado
   */
  it("applies correct gradient background classes", () => {
    const { container } = renderWithRouter();

    // Check the root div has the gradient classes
    const rootDiv = container.firstChild as HTMLElement;
    expect(rootDiv).toHaveClass("min-h-screen");
    expect(rootDiv).toHaveClass("bg-gradient-to-br");
  });

  /**
   * Test: Lista de tareas con datos existentes
   *
   * Verifica que la lista de tareas se renderice correctamente
   * mostrando las tareas existentes del dataset de prueba.
   *
   * @test {HTMLElement} todoItem - Elemento de tarea específica
   */
  it("renders todo list with existing todos", () => {
    renderWithRouter();

    // Since we have todos in the data, we should see todo items
    // Look for todo names from our test data
    const todoItem = screen.getByText("Implementar autenticación de usuarios");
    expect(todoItem).toBeInTheDocument();
  });

  /**
   * Test: Atributos de accesibilidad en botones
   *
   * Verifica que todos los botones de filtro tengan los atributos
   * aria-label necesarios para lectores de pantalla.
   *
   * @test {HTMLElement[]} filterButtons - Todos los botones de la interfaz
   * @test {string} aria-label - Atributo de accesibilidad requerido
   */
  it("has proper accessibility attributes on filter buttons", () => {
    renderWithRouter();

    const filterButtons = screen.getAllByRole("button");

    filterButtons.forEach((button) => {
      expect(button).toHaveAttribute("aria-label");
    });
  });
});
