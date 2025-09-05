/**
 * @fileoverview Tests para el componente Header
 * 
 * Este archivo contiene tests unitarios que verifican:
 * - Renderizado correcto del título y subtítulo
 * - Aplicación de clases CSS y estilos responsivos
 * - Estructura semántica y accesibilidad
 * - Manejo de props personalizadas
 * - Comportamiento con diferentes tipos de contenido
 * 
 * @author Vibe Coding Team
 * @version 1.0.0
 */

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { Header } from "./Header";

/**
 * Suite de tests para el componente Header
 * 
 * Verifica el renderizado y funcionalidad del header principal
 * de la aplicación, incluyendo título, subtítulo y estilos.
 */
describe("Header Component", () => {
  /**
   * Props por defecto para los tests
   * 
   * @type {Object}
   * @property {string} title - Título principal del header
   * @property {string} subtitle - Subtítulo descriptivo
   */
  const defaultProps = {
    title: "Lista de Tareas",
    subtitle: "Gestiona tus tareas de manera eficiente",
  };

  /**
   * Test: Renderizado correcto del título
   * 
   * Verifica que el título se renderice como un heading h1
   * con el contenido de texto correcto.
   * 
   * @test {HTMLElement} title - Elemento h1 con el título
   * @test {string} textContent - Contenido "Lista de Tareas"
   */
  it("renders the title correctly", () => {
    render(<Header {...defaultProps} />);

    const title = screen.getByRole("heading", { level: 1 });
    expect(title).toBeInTheDocument();
    expect(title).toHaveTextContent("Lista de Tareas");
  });

  /**
   * Test: Renderizado correcto del subtítulo
   * 
   * Verifica que el subtítulo se renderice correctamente
   * con el texto descriptivo proporcionado.
   * 
   * @test {HTMLElement} subtitle - Elemento con el subtítulo
   */
  it("renders the subtitle correctly", () => {
    render(<Header {...defaultProps} />);

    const subtitle = screen.getByText(
      "Gestiona tus tareas de manera eficiente"
    );
    expect(subtitle).toBeInTheDocument();
  });

  /**
   * Test: Clases CSS del título
   * 
   * Verifica que el título tenga todas las clases CSS necesarias
   * para el diseño responsivo y el efecto de gradiente.
   * 
   * @test {string} text-4xl - Tamaño base del texto
   * @test {string} md:text-5xl - Tamaño responsivo para pantallas medianas
   * @test {string} font-bold - Peso de fuente en negrita
   * @test {string} bg-gradient-to-r - Gradiente horizontal
   * @test {string} from-blue-600 - Color inicial del gradiente
   * @test {string} to-purple-600 - Color final del gradiente
   * @test {string} bg-clip-text - Recorte del fondo al texto
   * @test {string} text-transparent - Texto transparente para mostrar gradiente
   */
  it("applies correct CSS classes for title styling", () => {
    render(<Header {...defaultProps} />);

    const title = screen.getByRole("heading", { level: 1 });
    expect(title).toHaveClass("text-4xl");
    expect(title).toHaveClass("md:text-5xl");
    expect(title).toHaveClass("font-bold");
    expect(title).toHaveClass("bg-gradient-to-r");
    expect(title).toHaveClass("from-blue-600");
    expect(title).toHaveClass("to-purple-600");
    expect(title).toHaveClass("bg-clip-text");
    expect(title).toHaveClass("text-transparent");
  });

  /**
   * Test: Clases CSS del subtítulo
   * 
   * Verifica que el subtítulo tenga las clases CSS correctas
   * para el color y tamaño, incluyendo soporte para modo oscuro.
   * 
   * @test {string} text-gray-600 - Color gris para modo claro
   * @test {string} dark:text-gray-300 - Color gris claro para modo oscuro
   * @test {string} text-lg - Tamaño de texto grande
   */
  it("applies correct CSS classes for subtitle styling", () => {
    render(<Header {...defaultProps} />);

    const subtitle = screen.getByText(
      "Gestiona tus tareas de manera eficiente"
    );
    expect(subtitle).toHaveClass("text-gray-600");
    expect(subtitle).toHaveClass("dark:text-gray-300");
    expect(subtitle).toHaveClass("text-lg");
  });

  /**
   * Test: Estructura semántica del header
   * 
   * Verifica que el componente use el elemento semántico header
   * con las clases de layout apropiadas.
   * 
   * @test {HTMLElement} header - Elemento con role="banner"
   * @test {string} text-center - Alineación centrada del texto
   * @test {string} mb-12 - Margen inferior para espaciado
   */
  it("has proper semantic structure with header element", () => {
    render(<Header {...defaultProps} />);

    const header = screen.getByRole("banner");
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass("text-center");
    expect(header).toHaveClass("mb-12");
  });

  /**
   * Test: Props personalizadas
   * 
   * Verifica que el componente acepte y renderice correctamente
   * props personalizadas para título y subtítulo.
   * 
   * @test {Object} customProps - Props con valores personalizados
   * @test {string} title - Título personalizado
   * @test {string} subtitle - Subtítulo personalizado
   */
  it("renders with custom title and subtitle", () => {
    const customProps = {
      title: "Mi Aplicación Custom",
      subtitle: "Descripción personalizada",
    };

    render(<Header {...customProps} />);

    const title = screen.getByRole("heading", { level: 1 });
    const subtitle = screen.getByText("Descripción personalizada");

    expect(title).toHaveTextContent("Mi Aplicación Custom");
    expect(subtitle).toBeInTheDocument();
  });

  /**
   * Test: Jerarquía de headings
   * 
   * Verifica que el componente mantenga la jerarquía semántica
   * correcta usando un elemento H1.
   * 
   * @test {HTMLElement} heading - Elemento heading de nivel 1
   * @test {string} tagName - Debe ser "H1"
   */
  it("maintains proper heading hierarchy", () => {
    render(<Header {...defaultProps} />);

    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading.tagName).toBe("H1");
  });

  /**
   * Test: Contenido de texto accesible
   * 
   * Verifica que el contenido de texto sea accesible y no esté vacío,
   * importante para lectores de pantalla y SEO.
   * 
   * @test {string} textContent - Contenido de texto no vacío
   * @test {boolean} toBeTruthy - Verificación de contenido existente
   */
  it("has accessible text content", () => {
    render(<Header {...defaultProps} />);

    const title = screen.getByRole("heading", { level: 1 });
    const subtitle = screen.getByText(
      "Gestiona tus tareas de manera eficiente"
    );

    // Check that text is accessible and not empty
    expect(title.textContent).toBeTruthy();
    expect(subtitle.textContent).toBeTruthy();
    expect(title.textContent?.trim()).not.toBe("");
    expect(subtitle.textContent?.trim()).not.toBe("");
  });

  /**
   * Test: Manejo de strings vacíos
   * 
   * Verifica que el componente maneje correctamente props vacías
   * sin romper la estructura o causar errores.
   * 
   * @test {Object} emptyProps - Props con strings vacíos
   * @test {HTMLElement} header - Header debe renderizarse
   * @test {HTMLElement} title - Título debe existir aunque esté vacío
   */
  it("renders correctly with empty strings", () => {
    const emptyProps = {
      title: "",
      subtitle: "",
    };

    render(<Header {...emptyProps} />);

    const header = screen.getByRole("banner");
    const title = screen.getByRole("heading", { level: 1 });

    expect(header).toBeInTheDocument();
    expect(title).toBeInTheDocument();
    expect(title).toHaveTextContent("");
  });

  /**
   * Test: Manejo de texto largo
   * 
   * Verifica que el componente maneje correctamente contenido de texto
   * largo sin romper el layout o la legibilidad.
   * 
   * @test {Object} longTextProps - Props con texto extenso
   * @test {HTMLElement} title - Título con texto largo
   * @test {HTMLElement} subtitle - Subtítulo con texto largo
   */
  it("handles long text content properly", () => {
    const longTextProps = {
      title:
        "Este es un título muy largo que debería manejarse correctamente en diferentes tamaños de pantalla",
      subtitle:
        "Esta es una descripción muy larga que también debería manejarse correctamente y mantener la legibilidad en diferentes dispositivos y tamaños de pantalla",
    };

    render(<Header {...longTextProps} />);

    const title = screen.getByRole("heading", { level: 1 });
    const subtitle = screen.getByText(longTextProps.subtitle);

    expect(title).toHaveTextContent(longTextProps.title);
    expect(subtitle).toBeInTheDocument();
  });

  /**
   * Test: Clases de diseño responsivo
   * 
   * Verifica que el componente mantenga las clases CSS responsivas
   * para diferentes tamaños de pantalla.
   * 
   * @test {string} text-4xl - Tamaño base para móviles
   * @test {string} md:text-5xl - Tamaño para pantallas medianas
   */
  it("maintains responsive design classes", () => {
    render(<Header {...defaultProps} />);

    const title = screen.getByRole("heading", { level: 1 });

    // Check responsive classes are present
    expect(title).toHaveClass("text-4xl"); // Base size
    expect(title).toHaveClass("md:text-5xl"); // Medium screen size
  });
});
