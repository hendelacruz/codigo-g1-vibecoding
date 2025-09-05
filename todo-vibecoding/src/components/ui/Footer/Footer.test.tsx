/**
 * @fileoverview Tests para el componente Footer
 *
 * Este archivo contiene tests unitarios que verifican:
 * - Renderizado correcto del footer y badge de Tailwind
 * - Aplicación de clases CSS y estilos de tema
 * - Estructura semántica y accesibilidad
 * - Espaciado y layout responsivo
 * - Contraste de colores y legibilidad
 *
 * @author Vibe Coding Team
 * @version 1.0.0
 */

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { Footer } from "./Footer";

/**
 * Suite de tests para el componente Footer
 *
 * Verifica el renderizado y funcionalidad del footer de la aplicación,
 * incluyendo el badge de Tailwind CSS y estilos de tema.
 */
describe("Footer Component", () => {
  /**
   * Test: Renderizado correcto del elemento footer
   *
   * Verifica que el footer se renderice correctamente como un
   * elemento semántico con role="contentinfo".
   *
   * @test {HTMLElement} footer - Elemento footer con role contentinfo
   */
  it("renders the footer element correctly", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    expect(footer).toBeInTheDocument();
  });

  /**
   * Test: Texto del badge de Tailwind CSS
   *
   * Verifica que el badge muestre correctamente el texto
   * "Powered by Tailwind CSS v4".
   *
   * @test {HTMLElement} badgeText - Elemento con el texto del badge
   */
  it("displays the Tailwind CSS badge text", () => {
    render(<Footer />);

    const badgeText = screen.getByText("Powered by Tailwind CSS v4");
    expect(badgeText).toBeInTheDocument();
  });

  /**
   * Test: Clases CSS del elemento footer
   *
   * Verifica que el footer tenga todas las clases CSS necesarias
   * para el layout, espaciado y bordes.
   *
   * @test {string} text-center - Alineación centrada del contenido
   * @test {string} mt-12 - Margen superior
   * @test {string} pt-8 - Padding superior
   * @test {string} border-t - Borde superior
   * @test {string} border-gray-200 - Color del borde en modo claro
   * @test {string} dark:border-slate-700 - Color del borde en modo oscuro
   */
  it("applies correct CSS classes to footer element", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    expect(footer).toHaveClass("text-center");
    expect(footer).toHaveClass("mt-12");
    expect(footer).toHaveClass("pt-8");
    expect(footer).toHaveClass("border-t");
    expect(footer).toHaveClass("border-gray-200");
    expect(footer).toHaveClass("dark:border-slate-700");
  });

  /**
   * Test: Clases CSS del contenedor del badge
   *
   * Verifica que el contenedor del badge tenga todas las clases
   * necesarias para el diseño, colores y espaciado.
   *
   * @test {string} inline-flex - Display flex inline
   * @test {string} items-center - Alineación vertical centrada
   * @test {string} gap-2 - Espacio entre elementos
   * @test {string} bg-blue-50 - Fondo azul claro
   * @test {string} dark:bg-blue-900/20 - Fondo azul oscuro con opacidad
   * @test {string} text-blue-700 - Color de texto azul
   * @test {string} dark:text-blue-300 - Color de texto azul claro en modo oscuro
   * @test {string} px-4 - Padding horizontal
   * @test {string} py-2 - Padding vertical
   * @test {string} rounded-full - Bordes completamente redondeados
   * @test {string} text-sm - Tamaño de texto pequeño
   * @test {string} font-medium - Peso de fuente medio
   */
  it("applies correct CSS classes to badge container", () => {
    render(<Footer />);

    const badgeContainer = screen
      .getByText("Powered by Tailwind CSS v4")
      .closest("div");
    expect(badgeContainer).toHaveClass("inline-flex");
    expect(badgeContainer).toHaveClass("items-center");
    expect(badgeContainer).toHaveClass("gap-2");
    expect(badgeContainer).toHaveClass("bg-blue-50");
    expect(badgeContainer).toHaveClass("dark:bg-blue-900/20");
    expect(badgeContainer).toHaveClass("text-blue-700");
    expect(badgeContainer).toHaveClass("dark:text-blue-300");
    expect(badgeContainer).toHaveClass("px-4");
    expect(badgeContainer).toHaveClass("py-2");
    expect(badgeContainer).toHaveClass("rounded-full");
    expect(badgeContainer).toHaveClass("text-sm");
    expect(badgeContainer).toHaveClass("font-medium");
  });

  /**
   * Test: Estructura semántica correcta
   *
   * Verifica que el componente use el elemento semántico FOOTER
   * apropiado para la estructura HTML.
   *
   * @test {HTMLElement} footer - Elemento footer semántico
   * @test {string} tagName - Debe ser "FOOTER"
   */
  it("has proper semantic structure", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    expect(footer.tagName).toBe("FOOTER");
  });

  /**
   * Test: Consistencia de estilos entre temas
   *
   * Verifica que el componente tenga las clases CSS necesarias
   * para mantener consistencia visual en modo claro y oscuro.
   *
   * @test {string} dark:border-slate-700 - Borde en modo oscuro
   * @test {string} dark:bg-blue-900/20 - Fondo del badge en modo oscuro
   * @test {string} dark:text-blue-300 - Color de texto en modo oscuro
   */
  it("maintains consistent styling across themes", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    const badgeContainer = screen
      .getByText("Powered by Tailwind CSS v4")
      .closest("div");

    // Check dark mode classes are present
    expect(footer).toHaveClass("dark:border-slate-700");
    expect(badgeContainer).toHaveClass("dark:bg-blue-900/20");
    expect(badgeContainer).toHaveClass("dark:text-blue-300");
  });

  /**
   * Test: Contraste de colores accesible
   *
   * Verifica que el badge tenga colores con contraste suficiente
   * para cumplir con estándares de accesibilidad.
   *
   * @test {string} text-blue-700 - Color de texto con buen contraste
   * @test {string} bg-blue-50 - Color de fondo que contrasta con el texto
   */
  it("has accessible color contrast", () => {
    render(<Footer />);

    const badgeContainer = screen
      .getByText("Powered by Tailwind CSS v4")
      .closest("div");

    // Check that appropriate color classes are applied for contrast
    expect(badgeContainer).toHaveClass("text-blue-700");
    expect(badgeContainer).toHaveClass("bg-blue-50");
  });

  /**
   * Test: Componente sin estado (stateless)
   *
   * Verifica que el componente se renderice correctamente sin
   * necesidad de props, siendo completamente autónomo.
   *
   * @test {HTMLElement} footer - Footer se renderiza sin props
   * @test {HTMLElement} badgeText - Badge se renderiza sin props
   */
  it("renders without any props (stateless component)", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    const badgeText = screen.getByText("Powered by Tailwind CSS v4");

    expect(footer).toBeInTheDocument();
    expect(badgeText).toBeInTheDocument();
  });

  /**
   * Test: Clases de espaciado y layout
   *
   * Verifica que el footer y el badge tengan el espaciado
   * correcto para una buena presentación visual.
   *
   * @test {string} mt-12 - Margen superior del footer
   * @test {string} pt-8 - Padding superior del footer
   * @test {string} px-4 - Padding horizontal del badge
   * @test {string} py-2 - Padding vertical del badge
   * @test {string} gap-2 - Espacio entre elementos del badge
   */
  it("has proper spacing and layout classes", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    const badgeContainer = screen
      .getByText("Powered by Tailwind CSS v4")
      .closest("div");

    // Check spacing classes
    expect(footer).toHaveClass("mt-12"); // Margin top
    expect(footer).toHaveClass("pt-8"); // Padding top
    expect(badgeContainer).toHaveClass("px-4"); // Horizontal padding
    expect(badgeContainer).toHaveClass("py-2"); // Vertical padding
    expect(badgeContainer).toHaveClass("gap-2"); // Gap between items
  });

  /**
   * Test: Jerarquía de texto apropiada
   *
   * Verifica que el texto del badge tenga el tamaño y peso
   * de fuente apropiados para su función secundaria.
   *
   * @test {string} text-sm - Tamaño de texto pequeño
   * @test {string} font-medium - Peso de fuente medio
   */
  it("maintains proper text hierarchy", () => {
    render(<Footer />);

    const badgeText = screen.getByText("Powered by Tailwind CSS v4");
    expect(badgeText).toHaveClass("text-sm");
    expect(badgeText).toHaveClass("font-medium");
  });

  /**
   * Test: Estilo de bordes apropiado
   *
   * Verifica que el footer tenga el borde superior correcto
   * para separarlo visualmente del contenido principal.
   *
   * @test {string} border-t - Borde superior
   * @test {string} border-gray-200 - Color del borde en modo claro
   * @test {string} dark:border-slate-700 - Color del borde en modo oscuro
   */
  it("has proper border styling", () => {
    render(<Footer />);

    const footer = screen.getByRole("contentinfo");
    expect(footer).toHaveClass("border-t");
    expect(footer).toHaveClass("border-gray-200");
    expect(footer).toHaveClass("dark:border-slate-700");
  });
});
