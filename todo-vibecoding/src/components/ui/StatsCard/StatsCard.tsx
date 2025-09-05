/**
 * @fileoverview Componente StatsCard para mostrar estadísticas de todos
 *
 * Este componente renderiza una tarjeta de estadísticas reutilizable
 * que muestra un valor numérico y una etiqueta descriptiva.
 * Incluye variantes de color y soporte para modo oscuro.
 *
 * @author Vibe Coding Team
 * @version 1.0.0
 * @since 1.0.0
 */

/**
 * Propiedades del componente StatsCard
 *
 * @interface StatsCardProps
 * @property {number} value - Valor numérico a mostrar en la tarjeta
 * @property {string} label - Etiqueta descriptiva del valor
 * @property {"blue" | "green" | "orange"} color - Variante de color para el valor
 */
interface StatsCardProps {
  /** Valor numérico a mostrar (ej: cantidad de todos) */
  value: number;
  /** Etiqueta descriptiva del valor (ej: "Total", "Completadas") */
  label: string;
  /** Variante de color: azul para total, verde para completadas, naranja para pendientes */
  color: "blue" | "green" | "orange";
}

/**
 * Mapeo de colores para las variantes del componente
 *
 * Define las clases CSS de Tailwind para cada variante de color,
 * incluyendo soporte para modo oscuro.
 *
 * @constant {Object} colorClasses
 * @property {string} blue - Clases para variante azul (total)
 * @property {string} green - Clases para variante verde (completadas)
 * @property {string} orange - Clases para variante naranja (pendientes)
 */
const colorClasses = {
  /** Azul para estadísticas totales */
  blue: "text-blue-600 dark:text-blue-400",
  /** Verde para tareas completadas */
  green: "text-green-600 dark:text-green-400",
  /** Naranja para tareas pendientes */
  orange: "text-orange-600 dark:text-orange-400",
};

/**
 * Componente StatsCard - Tarjeta de estadísticas
 *
 * Renderiza una tarjeta elegante que muestra un valor numérico prominente
 * y una etiqueta descriptiva. El componente es completamente reutilizable
 * y soporta diferentes variantes de color según el tipo de estadística.
 *
 * @component
 * @param {StatsCardProps} props - Propiedades del componente
 * @param {number} props.value - Valor numérico a mostrar
 * @param {string} props.label - Etiqueta descriptiva
 * @param {"blue" | "green" | "orange"} props.color - Variante de color
 * @returns {JSX.Element} Elemento JSX de la tarjeta de estadísticas
 *
 * @example
 * ```tsx
 * // Tarjeta para total de todos
 * <StatsCard value={10} label="Total" color="blue" />
 *
 * // Tarjeta para todos completados
 * <StatsCard value={7} label="Completadas" color="green" />
 *
 * // Tarjeta para todos pendientes
 * <StatsCard value={3} label="Pendientes" color="orange" />
 * ```
 *
 * @accessibility
 * - Estructura semántica con divs apropiados
 * - Contraste de colores adecuado en modo claro y oscuro
 * - Tamaños de fuente legibles
 * - Espaciado apropiado para facilitar la lectura
 *
 * @design
 * - Fondo blanco/slate-800 según el tema
 * - Bordes redondeados (rounded-xl)
 * - Sombra sutil (shadow-lg)
 * - Padding interno de 6 unidades
 * - Texto centrado
 * - Valor en texto grande y bold
 * - Etiqueta en texto pequeño y color secundario
 */
export const StatsCard = ({ value, label, color }: StatsCardProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-slate-700">
      <div className="text-center">
        <div className={`text-3xl font-bold ${colorClasses[color]}`}>
          {value}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
          {label}
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
