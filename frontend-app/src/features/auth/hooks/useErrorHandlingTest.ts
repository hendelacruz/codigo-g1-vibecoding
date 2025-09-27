import { useCallback, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '../../../app/store'
import { loginUser } from '../authSlice'
import { api } from '../../../shared/lib/api'

// Hook tipado para Redux
const useAppDispatch = () => useDispatch<AppDispatch>()
const useAppSelector = <T>(selector: (state: RootState) => T) => useSelector(selector)

/**
 * Hook personalizado para probar el manejo de errores
 * Implementa las pruebas del punto 6 del phase1-manual-tests.md:
 * - Errores de red se muestran correctamente
 * - Errores de autenticación se manejan
 * - Loading states funcionan
 */
export const useErrorHandlingTest = () => {
  const dispatch = useAppDispatch()
  const { isLoading, error, isAuthenticated } = useAppSelector((state: RootState) => state.auth)
  
  const [testResults, setTestResults] = useState<string[]>([])
  const [isRunningTest, setIsRunningTest] = useState(false)

  // Función para agregar resultados de prueba
  const addResult = useCallback((message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }, [])

  // Función para limpiar resultados
  const clearResults = useCallback(() => {
    setTestResults([])
  }, [])

  // Test 1: Simular error de red
  const testNetworkError = useCallback(async () => {
    addResult('🔍 Iniciando Test 1: Error de red')
    setIsRunningTest(true)
    
    try {
      // Simular error de red usando un endpoint inexistente
      addResult('📡 Simulando error de red...')
      
      // Intentar hacer login con endpoint incorrecto para simular error de red
      const originalBaseURL = api.defaults.baseURL
      api.defaults.baseURL = 'http://localhost:9999' // Puerto que no existe
      
      const result = await dispatch(loginUser({
        username: 'test',
        password: 'test'
      }))
      
      // Restaurar URL original
      if (originalBaseURL) {
        api.defaults.baseURL = originalBaseURL
      }
      
      if (loginUser.rejected.match(result)) {
        addResult('✅ Error de red detectado correctamente')
        addResult(`📝 Mensaje de error: ${result.error.message || 'Error desconocido'}`)
        
        // Verificar que el error se muestra en el estado
        if (error) {
          addResult('✅ Error se guardó en el estado de Redux')
        } else {
          addResult('❌ Error no se guardó en el estado')
        }
      } else {
        addResult('❌ Error de red no se detectó correctamente')
      }
      
    } catch (testError) {
      addResult(`❌ Error en la prueba: ${testError}`)
    } finally {
      setIsRunningTest(false)
    }
  }, [dispatch, addResult, error])

  // Test 2: Simular error de autenticación
  const testAuthError = useCallback(async () => {
    addResult('🔍 Iniciando Test 2: Error de autenticación')
    setIsRunningTest(true)
    
    try {
      addResult('🔐 Probando credenciales incorrectas...')
      
      const result = await dispatch(loginUser({
        username: 'usuario_inexistente',
        password: 'password_incorrecto'
      }))
      
      if (loginUser.rejected.match(result)) {
        addResult('✅ Error de autenticación detectado correctamente')
        addResult(`📝 Mensaje de error: ${result.error.message}`)
        
        // Verificar que no se autenticó
        if (!isAuthenticated) {
          addResult('✅ Usuario no se autenticó (correcto)')
        } else {
          addResult('❌ Usuario se autenticó incorrectamente')
        }
        
        // Verificar que el error se muestra
        if (error) {
          addResult('✅ Error de autenticación se muestra en UI')
        } else {
          addResult('❌ Error de autenticación no se muestra')
        }
      } else {
        addResult('❌ Error de autenticación no se manejó correctamente')
      }
      
    } catch (testError) {
      addResult(`❌ Error en la prueba: ${testError}`)
    } finally {
      setIsRunningTest(false)
    }
  }, [dispatch, addResult, isAuthenticated, error])

  // Test 3: Verificar loading states
  const testLoadingStates = useCallback(async () => {
    addResult('🔍 Iniciando Test 3: Loading states')
    setIsRunningTest(true)
    
    try {
      addResult('⏳ Verificando estado de loading inicial...')
      
      // Verificar estado inicial
      if (!isLoading) {
        addResult('✅ Estado inicial: no loading')
      } else {
        addResult('❌ Estado inicial: loading activo incorrectamente')
      }
      
      addResult('🔄 Iniciando operación que activa loading...')
      
      // Hacer una operación que active loading
      const loginPromise = dispatch(loginUser({
        username: 'test_loading',
        password: 'test_loading'
      }))
      
      // Verificar que loading se activó
      setTimeout(() => {
        if (isLoading) {
          addResult('✅ Loading state se activó correctamente')
        } else {
          addResult('⚠️ Loading state no se detectó (puede ser muy rápido)')
        }
      }, 100)
      
      // Esperar a que termine
      await loginPromise
      
      // Verificar que loading se desactivó
      setTimeout(() => {
        if (!isLoading) {
          addResult('✅ Loading state se desactivó correctamente')
        } else {
          addResult('❌ Loading state no se desactivó')
        }
      }, 100)
      
      addResult('📊 Test de loading states completado')
      
    } catch (testError) {
      addResult(`❌ Error en la prueba: ${testError}`)
    } finally {
      setIsRunningTest(false)
    }
  }, [dispatch, addResult, isLoading])

  // Test 4: Verificar manejo de errores de API
  const testAPIErrorHandling = useCallback(async () => {
    addResult('🔍 Iniciando Test 4: Manejo de errores de API')
    setIsRunningTest(true)
    
    try {
      addResult('📡 Probando request a endpoint inexistente...')
      
      // Hacer request a endpoint que no existe
      try {
        await api.get('/api/endpoint/inexistente/')
        addResult('❌ Request a endpoint inexistente no falló')
      } catch (apiError: unknown) {
        addResult('✅ Request a endpoint inexistente falló correctamente')
        const errorMessage = apiError instanceof Error ? apiError.message : 'Error desconocido'
        addResult(`📝 Error capturado: ${errorMessage}`)
        
        // Verificar tipo de error
        if (apiError && typeof apiError === 'object' && 'response' in apiError && 
            apiError.response && typeof apiError.response === 'object' && 'status' in apiError.response &&
            apiError.response.status === 404) {
          addResult('✅ Error 404 manejado correctamente')
        } else if (apiError && typeof apiError === 'object' && 'code' in apiError && apiError.code === 'ECONNREFUSED') {
          addResult('✅ Error de conexión manejado correctamente')
        } else {
          const errorCode = apiError && typeof apiError === 'object' && 'code' in apiError ? 
            String(apiError.code) : 'Desconocido'
          addResult(`📝 Tipo de error: ${errorCode}`)
        }
      }
      
      addResult('📊 Test de manejo de errores de API completado')
      
    } catch (testError) {
      addResult(`❌ Error en la prueba: ${testError}`)
    } finally {
      setIsRunningTest(false)
    }
  }, [addResult])

  // Ejecutar todas las pruebas
  const runAllTests = useCallback(async () => {
    addResult('🚀 Iniciando todas las pruebas de manejo de errores')
    clearResults()
    
    await testNetworkError()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await testAuthError()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await testLoadingStates()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await testAPIErrorHandling()
    
    addResult('🎉 Todas las pruebas completadas')
  }, [testNetworkError, testAuthError, testLoadingStates, testAPIErrorHandling, addResult, clearResults])

  return {
    // Estado actual
    isLoading,
    error,
    isAuthenticated,
    testResults,
    isRunningTest,
    
    // Funciones de prueba
    testNetworkError,
    testAuthError,
    testLoadingStates,
    testAPIErrorHandling,
    runAllTests,
    clearResults
  }
}