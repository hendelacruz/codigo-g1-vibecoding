/**
 * Custom hook for managing todo list logic
 * Encapsulates filtering, formatting, and state management
 */

import { useState, useMemo, useEffect } from "react";
import { todos as initialTodos } from "../todos";
import type { Todo } from "../todos";
import { formatDate } from "../utils";

export type FilterType = "all" | "pending" | "completed";

export interface UseTodoReturn {
  // State
  filter: FilterType;
  setFilter: (filter: FilterType) => void;
  todos: Todo[];

  // Computed values
  filteredTodos: Todo[];
  todosCount: {
    total: number;
    completed: number;
    pending: number;
  };

  // Actions
  addTodo: (todo: Omit<Todo, "id">) => void;
  updateTodo: (id: number, updates: Partial<Todo>) => void;
  deleteTodo: (id: number) => void;
  toggleTodo: (id: number) => void;

  // Utility functions
  formatDate: (date: Date) => string;
}

/**
 * Custom hook that manages todo list state and provides utility functions
 *
 * @returns {UseTodoReturn} Object containing state, computed values, and utility functions
 */
export const useTodo = (): UseTodoReturn => {
  const [filter, setFilter] = useState<FilterType>("all");
  const [todos, setTodos] = useState<Todo[]>(() => {
    // Try to load from localStorage, fallback to initial todos
    const savedTodos = localStorage.getItem("todos");
    if (savedTodos) {
      try {
        const parsed = JSON.parse(savedTodos);
        return parsed.map((todo: Todo) => ({
          ...todo,
          created_at: new Date(todo.created_at),
          updated_at: new Date(todo.updated_at),
        }));
      } catch {
        return initialTodos;
      }
    }
    return initialTodos;
  });

  // Save to localStorage whenever todos change
  useEffect(() => {
    localStorage.setItem("todos", JSON.stringify(todos));
  }, [todos]);

  // Memoized todos count to avoid recalculation on every render
  const todosCount = useMemo(() => {
    const total = todos.length;
    const completed = todos.filter((todo) => todo.is_finished).length;
    const pending = total - completed;
    return { total, completed, pending };
  }, [todos]);

  // Memoized filtered todos based on current filter
  const filteredTodos = useMemo(() => {
    return todos.filter((todo) => {
      if (filter === "completed") return todo.is_finished;
      if (filter === "pending") return !todo.is_finished;
      return true;
    });
  }, [todos, filter]);

  // Action functions
  const addTodo = (todoData: Omit<Todo, "id">) => {
    const newTodo: Todo = {
      ...todoData,
      id: Math.max(0, ...todos.map((t) => t.id)) + 1,
    };
    setTodos((prev) => [...prev, newTodo]);
  };

  const updateTodo = (id: number, updates: Partial<Todo>) => {
    setTodos((prev) =>
      prev.map((todo) =>
        todo.id === id ? { ...todo, ...updates, updated_at: new Date() } : todo
      )
    );
  };

  const deleteTodo = (id: number) => {
    setTodos((prev) => prev.filter((todo) => todo.id !== id));
  };

  const toggleTodo = (id: number) => {
    updateTodo(id, {
      is_finished: !todos.find((t) => t.id === id)?.is_finished,
    });
  };

  return {
    // State
    filter,
    setFilter,
    todos,

    // Computed values
    filteredTodos,
    todosCount,

    // Actions
    addTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,

    // Utility functions
    formatDate,
  };
};

export default useTodo;
