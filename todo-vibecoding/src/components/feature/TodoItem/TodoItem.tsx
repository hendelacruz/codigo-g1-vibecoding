/**
 * TodoItem component for displaying individual todo items
 * Reusable component with status indicator and formatted dates
 */

import type { Todo } from "../../../todos";

interface TodoItemProps {
  todo: Todo;
  formatDate: (date: Date) => string;
}

export const TodoItem = ({ todo, formatDate }: TodoItemProps) => {
  const statusClasses = todo.is_finished
    ? "bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300"
    : "bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300";

  const statusText = todo.is_finished ? "Completada" : "Pendiente";
  const statusIcon = todo.is_finished ? "✓" : "○";

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-slate-700 hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1 mr-4">
          {todo.name}
        </h3>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${statusClasses}`}
        >
          <span className="text-xs">{statusIcon}</span>
          {statusText}
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
        <div className="flex items-center gap-2">
          <span className="font-medium">ID:</span>
          <span className="bg-gray-100 dark:bg-slate-700 px-2 py-1 rounded text-xs font-mono">
            {todo.id}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-medium">Creada:</span>
          <span>{formatDate(todo.created_at)}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-medium">Actualizada:</span>
          <span>{formatDate(todo.updated_at)}</span>
        </div>
      </div>
    </div>
  );
};

export default TodoItem;