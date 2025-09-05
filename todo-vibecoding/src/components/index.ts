/**
 * Components barrel file
 * Centralizes all component exports from UI and Feature modules
 */

// Export all UI components
export * from './ui';

// Export all Feature components
export * from './feature';

// Re-export specific components for convenience
export { default as Header } from './ui/Header';
export { default as Footer } from './ui/Footer';
export { default as StatsCard } from './ui/StatsCard';

export { default as FilterButtons } from './feature/FilterButtons';
export { default as StatsSection } from './feature/StatsSection';
export { default as TodoItem } from './feature/TodoItem';
export { default as TodoList } from './feature/TodoList';