/**
 * FilterButtons component for todo filtering
 * Handles filter state and provides accessible filter controls
 */

import type { FilterType } from "../../../hooks/useTodo";

interface FilterButtonsProps {
  currentFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
}

interface FilterOption {
  key: FilterType;
  label: string;
  ariaLabel: string;
  activeColor: string;
  focusRing: string;
}

const filterOptions: FilterOption[] = [
  {
    key: "all",
    label: "Todas",
    ariaLabel: "Mostrar todas las tareas",
    activeColor: "bg-blue-600 text-white shadow-lg",
    focusRing: "focus:ring-blue-500",
  },
  {
    key: "pending",
    label: "Pendientes",
    ariaLabel: "Mostrar tareas pendientes",
    activeColor: "bg-orange-600 text-white shadow-lg",
    focusRing: "focus:ring-orange-500",
  },
  {
    key: "completed",
    label: "Completadas",
    ariaLabel: "Mostrar tareas completadas",
    activeColor: "bg-green-600 text-white shadow-lg",
    focusRing: "focus:ring-green-500",
  },
];

const inactiveClasses =
  "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700";

export const FilterButtons = ({
  currentFilter,
  onFilterChange,
}: FilterButtonsProps) => {
  return (
    <div className="flex flex-wrap justify-center gap-2 mb-8">
      {filterOptions.map((option) => (
        <button
          key={option.key}
          onClick={() => onFilterChange(option.key)}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 ${
            option.focusRing
          } focus:ring-offset-2 ${
            currentFilter === option.key ? option.activeColor : inactiveClasses
          }`}
          aria-label={option.ariaLabel}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default FilterButtons;
