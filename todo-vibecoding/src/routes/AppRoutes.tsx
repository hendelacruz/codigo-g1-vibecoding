/**
 * AppRoutes component - Main routing configuration
 * Centralized route management for the application
 */

import { Routes, Route } from 'react-router-dom'
import { HomePage, CreateTodoPage } from '../pages'

/**
 * Main routing component that defines all application routes
 * 
 * Routes:
 * - "/" - HomePage: Main todo list view
 * - "/crear-todo" - CreateTodoPage: Form to create new todos
 * - "*" - Fallback: Redirects to HomePage for unknown routes
 */
export const AppRoutes = () => {
  return (
    <Routes>
      {/* Main todo list page */}
      <Route path="/" element={<HomePage />} />
      
      {/* Create new todo page */}
      <Route path="/crear-todo" element={<CreateTodoPage />} />
      
      {/* Fallback route for 404 - redirects to home */}
      <Route path="*" element={<HomePage />} />
    </Routes>
  )
}

export default AppRoutes