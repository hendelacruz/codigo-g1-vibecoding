/**
 * @fileoverview Componente Header para la aplicación Todo Vibe Coding
 *
 * Este componente renderiza el encabezado principal de la aplicación,
 * incluyendo el título con gradiente y el subtítulo descriptivo.
 * Implementa diseño responsivo y soporte para modo oscuro.
 *
 * @author Vibe Coding Team
 * @version 1.0.0
 * @since 1.0.0
 */

/**
 * Propiedades del componente Header
 *
 * @interface HeaderProps
 * @property {string} title - Título principal que se mostrará en el encabezado
 * @property {string} subtitle - Subtítulo descriptivo que aparece debajo del título
 */
interface HeaderProps {
  /** Título principal de la aplicación */
  title: string;
  /** Subtítulo descriptivo de la aplicación */
  subtitle: string;
}

/**
 * Componente Header - Encabezado principal de la aplicación
 *
 * Renderiza un encabezado centrado con título y subtítulo.
 * El título incluye un gradiente de colores (azul a púrpura) y es responsivo.
 * El subtítulo adapta su color según el tema (claro/oscuro).
 *
 * @component
 * @param {HeaderProps} props - Propiedades del componente
 * @param {string} props.title - Título principal a mostrar
 * @param {string} props.subtitle - Subtítulo descriptivo a mostrar
 * @returns {JSX.Element} Elemento JSX del encabezado
 *
 * @example
 * ```tsx
 * <Header
 *   title="Todo Vibe Coding"
 *   subtitle="Gestiona tus tareas de manera eficiente"
 * />
 * ```
 *
 * @accessibility
 * - Utiliza elementos semánticos (header, h1, p)
 * - El título principal usa h1 para jerarquía correcta
 * - Colores con contraste adecuado para legibilidad
 * - Soporte para modo oscuro
 *
 * @responsive
 * - Título: text-4xl en móvil, text-5xl en desktop (md:)
 * - Diseño centrado en todas las resoluciones
 * - Espaciado adaptativo con Tailwind CSS
 */
export const Header = ({ title, subtitle }: HeaderProps) => {
  return (
    <header className="text-center mb-12">
      <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
        {title}
      </h1>
      <p className="text-gray-600 dark:text-gray-300 text-lg">{subtitle}</p>
    </header>
  );
};

export default Header;
