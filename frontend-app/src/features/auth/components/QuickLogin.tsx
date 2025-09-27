import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '../../../app/store'
import { loginUser } from '../authSlice'
import toast from 'react-hot-toast'

export const QuickLogin: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { isLoading, isAuthenticated, user, error } = useSelector((state: RootState) => state.auth)
  
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!credentials.username || !credentials.password) {
      toast.error('Por favor ingresa usuario y contraseña')
      return
    }

    try {
      const result = await dispatch(loginUser(credentials))
      if (loginUser.fulfilled.match(result)) {
        toast.success('Login exitoso')
      } else {
        toast.error(result.payload as string || 'Error en login')
      }
    } catch (_) {
      toast.error('Error en login')
    }
  }

  if (isAuthenticated) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-green-800 mb-2">✅ Autenticado</h3>
        <p className="text-green-700">Usuario: <strong>{user?.username}</strong></p>
        <p className="text-green-700">Email: <strong>{user?.email}</strong></p>
      </div>
    )
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-blue-800 mb-4">🔐 Login Requerido</h3>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Usuario
          </label>
          <input
            type="text"
            value={credentials.username}
            onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ingresa tu usuario"
            disabled={isLoading}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contraseña
          </label>
          <input
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ingresa tu contraseña"
            disabled={isLoading}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
        </button>
      </form>
      
      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Credenciales de prueba:</strong></p>
        <p>Usuario: admin</p>
        <p>Contraseña: admin123</p>
      </div>
    </div>
  )
}