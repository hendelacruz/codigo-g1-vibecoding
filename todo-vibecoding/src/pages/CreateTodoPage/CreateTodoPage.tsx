/**
 * CreateTodoPage component - Form to create new todos
 * Simple form with input and button for adding new tasks
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Header, Footer } from '../../components'
import { useTodo } from '../../hooks/useTodo'

export const CreateTodoPage = () => {
  const [todoText, setTodoText] = useState('')
  const navigate = useNavigate()
  const { addTodo } = useTodo()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (todoText.trim()) {
      // Create new todo using the hook
      addTodo({
        name: todoText.trim(),
        is_finished: false,
        created_at: new Date(),
        updated_at: new Date()
      })
      
      // Reset form and navigate back
      setTodoText('')
      navigate('/')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Header
          title="Crear Nueva Tarea"
          subtitle="Agrega una nueva tarea a tu lista"
        />

        {/* Navigation */}
        <nav className="mb-8 flex gap-4 justify-center">
          <Link
            to="/"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            ← Volver al Inicio
          </Link>
        </nav>

        {/* Form */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="todo-input"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Descripción de la tarea
              </label>
              <input
                id="todo-input"
                type="text"
                value={todoText}
                onChange={(e) => setTodoText(e.target.value)}
                placeholder="Escribe tu nueva tarea aquí..."
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white transition-colors"
                required
                autoFocus
                aria-describedby="todo-help"
              />
              <p id="todo-help" className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Describe brevemente la tarea que quieres agregar
              </p>
            </div>

            <button
              type="submit"
              disabled={!todoText.trim()}
              className="w-full px-6 py-3 bg-green-500 text-white font-medium rounded-lg hover:bg-green-600 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              ✅ Crear Tarea
            </button>
          </form>
        </div>

        <Footer />
      </div>
    </div>
  )
}

export default CreateTodoPage