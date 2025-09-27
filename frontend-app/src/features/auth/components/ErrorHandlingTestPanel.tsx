import React from 'react'
import { useErrorHandlingTest } from '../hooks/useErrorHandlingTest'

/**
 * Panel de pruebas para el manejo de errores
 * Implementa las pruebas del punto 6 del phase1-manual-tests.md:
 * - Errores de red se muestran correctamente
 * - Errores de autenticación se manejan
 * - Loading states funcionan
 */
export const ErrorHandlingTestPanel: React.FC = () => {
  const {
    isLoading,
    error,
    isAuthenticated,
    testResults,
    isRunningTest,
    testNetworkError,
    testAuthError,
    testLoadingStates,
    testAPIErrorHandling,
    runAllTests,
    clearResults
  } = useErrorHandlingTest()

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          🧪 Pruebas de Manejo de Errores
        </h2>
        <p className="text-gray-600">
          Panel para probar el manejo de errores según el punto 6 de phase1-manual-tests.md
        </p>
      </div>

      {/* Estado actual del sistema */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-3">📊 Estado Actual del Sistema</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">Loading:</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              isLoading 
                ? 'bg-yellow-100 text-yellow-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {isLoading ? '⏳ Cargando' : '✅ Inactivo'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">Autenticado:</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              isAuthenticated 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {isAuthenticated ? '✅ Sí' : '❌ No'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">Error:</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              error 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {error ? '❌ Presente' : '✅ Ninguno'}
            </span>
          </div>
        </div>
        
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-sm text-red-700">
              <strong>Error actual:</strong> {error}
            </p>
          </div>
        )}
      </div>

      {/* Botones de prueba */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">🎯 Pruebas Individuales</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            onClick={testNetworkError}
            disabled={isRunningTest}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🌐 Test Error de Red
          </button>
          
          <button
            onClick={testAuthError}
            disabled={isRunningTest}
            className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🔐 Test Error Auth
          </button>
          
          <button
            onClick={testLoadingStates}
            disabled={isRunningTest}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ⏳ Test Loading
          </button>
          
          <button
            onClick={testAPIErrorHandling}
            disabled={isRunningTest}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            📡 Test API Errors
          </button>
        </div>
      </div>

      {/* Botones de control */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">🎮 Controles</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={runAllTests}
            disabled={isRunningTest}
            className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            🚀 Ejecutar Todas las Pruebas
          </button>
          
          <button
            onClick={clearResults}
            disabled={isRunningTest}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🗑️ Limpiar Resultados
          </button>
        </div>
      </div>

      {/* Resultados de las pruebas */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">📋 Resultados de las Pruebas</h3>
          {isRunningTest && (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-sm text-blue-600">Ejecutando prueba...</span>
            </div>
          )}
        </div>
        
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
          {testResults.length === 0 ? (
            <p className="text-gray-500">No hay resultados aún. Ejecuta una prueba para ver los resultados.</p>
          ) : (
            testResults.map((result, index) => (
              <div key={index} className="mb-1">
                {result}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Información sobre las pruebas */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-md font-semibold text-blue-800 mb-2">ℹ️ Información sobre las Pruebas</h4>
        <div className="text-sm text-blue-700 space-y-2">
          <p><strong>🌐 Test Error de Red:</strong> Simula problemas de conectividad cambiando temporalmente la URL base de la API.</p>
          <p><strong>🔐 Test Error Auth:</strong> Prueba el manejo de credenciales incorrectas y verifica que los errores se muestren correctamente.</p>
          <p><strong>⏳ Test Loading:</strong> Verifica que los estados de carga se activen y desactiven correctamente durante las operaciones.</p>
          <p><strong>📡 Test API Errors:</strong> Prueba el manejo de errores de endpoints inexistentes y otros errores de API.</p>
        </div>
      </div>
    </div>
  )
}