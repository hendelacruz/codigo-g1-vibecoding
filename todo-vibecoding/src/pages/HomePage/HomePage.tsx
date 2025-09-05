/**
 * HomePage component - Main landing page with todo list
 * Main view for displaying and managing todos
 */

import { Link } from 'react-router-dom'
import { useTodo } from '../../hooks/useTodo'
import {
  Header,
  Footer,
  StatsSection,
  FilterButtons,
  TodoList,
} from '../../components'

export const HomePage = () => {
  const { filter, setFilter, filteredTodos, todosCount, formatDate } =
    useTodo()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Header
          title="Lista de Tareas"
          subtitle="Gestiona tus tareas de manera eficiente"
        />

        {/* Navigation Links */}
        <nav className="mb-6 flex gap-4 justify-center">
          <Link
            to="/"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Inicio
          </Link>
          <Link
            to="/crear-todo"
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            Crear Todo
          </Link>
        </nav>

        <StatsSection todosCount={todosCount} />

        <FilterButtons currentFilter={filter} onFilterChange={setFilter} />

        <TodoList
          todos={filteredTodos}
          formatDate={formatDate}
          emptyMessage="No hay tareas para mostrar"
        />

        <Footer />
      </div>
    </div>
  )
}

export default HomePage