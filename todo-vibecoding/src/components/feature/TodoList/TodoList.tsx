/**
 * TodoList component for displaying a list of todos
 * Handles empty states and renders TodoItem components
 */

import type { Todo } from "../../../todos";
import { TodoItem } from "../TodoItem";

interface TodoListProps {
  todos: Todo[];
  formatDate: (date: Date) => string;
  emptyMessage?: string;
}

export const TodoList = ({
  todos,
  formatDate,
  emptyMessage = "No hay tareas para mostrar",
}: TodoListProps) => {
  if (todos.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📝</div>
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          {emptyMessage}
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} formatDate={formatDate} />
      ))}
    </div>
  );
};

export default TodoList;
