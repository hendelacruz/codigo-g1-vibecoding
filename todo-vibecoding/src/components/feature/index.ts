/**
 * Barrel file for Feature components
 * Centralizes exports for todo-specific functionality components
 */

export { default as FilterButtons } from "./FilterButtons";
export { default as StatsSection } from "./StatsSection";
export { default as TodoItem } from "./TodoItem";
export { default as TodoList } from "./TodoList";

export * from "./FilterButtons";
export * from "./StatsSection";
export * from "./TodoItem";
export * from "./TodoList";

// Re-export FilterType from hooks
export type { FilterType } from "../../hooks/useTodo";
