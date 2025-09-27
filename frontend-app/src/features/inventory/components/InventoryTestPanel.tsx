/**
 * Inventory Test Panel Component
 * This component provides a UI for testing inventory CRUD operations
 * Use this component to manually test the inventory functionality
 */

import React, { useState } from 'react'
import { useAppDispatch, useAppSelector } from '../../../app/hooks'
import { 
  fetchGPSDevices, 
  createGPS, 
  updateGPS, 
  deleteGPS,
  fetchSIMCards,
  createSIMCard,
  deleteSIMCard,
  fetchOtrosProductos,
  createOtroProducto,
  deleteOtroProducto,
  adjustStock,
  fetchProveedores,
  clearInventoryErrors
} from '../inventorySlice'
import type { CreateGPSData, CreateSIMCardData, CreateOtroProductoData } from '../inventoryTypes'

interface TestResult {
  operation: string
  status: 'success' | 'error' | 'pending'
  message: string
  timestamp: string
}

export const InventoryTestPanel: React.FC = () => {
  const dispatch = useAppDispatch()
  const inventory = useAppSelector((state) => state.inventory)
  const auth = useAppSelector((state) => state.auth)
  
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [isRunningTests, setIsRunningTests] = useState(false)

  const addTestResult = (operation: string, status: 'success' | 'error' | 'pending', message: string) => {
    const result: TestResult = {
      operation,
      status,
      message,
      timestamp: new Date().toLocaleTimeString()
    }
    setTestResults(prev => [result, ...prev])
  }

  const clearResults = () => {
    setTestResults([])
    dispatch(clearInventoryErrors())
  }

  // Test GPS Operations
  const testGPSOperations = async () => {
    try {
      addTestResult('GPS Fetch', 'pending', 'Fetching GPS devices...')
      const fetchResult = await dispatch(fetchGPSDevices())
      
      if (fetchGPSDevices.fulfilled.match(fetchResult)) {
        addTestResult('GPS Fetch', 'success', `Fetched ${fetchResult.payload.length} GPS devices`)
        
        // Test create GPS
        const newGPS: CreateGPSData = {
          fecha_compra: '2024-01-15',
          imei: `TEST${Date.now()}`,
          marca: 'Test Brand',
          modelo: 'Test Model',
          numero_factura: `TEST-${Date.now()}`,
          proveedor: 1,
          estado: 'no_asignado',
          proceso: 'en_produccion',
          precio_compra: 100.00,
          observaciones: 'Test GPS device'
        }
        
        addTestResult('GPS Create', 'pending', 'Creating test GPS...')
        const createResult = await dispatch(createGPS(newGPS))
        
        if (createGPS.fulfilled.match(createResult)) {
          addTestResult('GPS Create', 'success', `Created GPS with ID: ${createResult.payload.id}`)
          
          // Test update GPS
          addTestResult('GPS Update', 'pending', 'Updating GPS...')
          const updateResult = await dispatch(updateGPS({
            id: createResult.payload.id,
            data: { estado: 'asignado', observaciones: 'Updated test GPS' }
          }))
          
          if (updateGPS.fulfilled.match(updateResult)) {
            addTestResult('GPS Update', 'success', 'GPS updated successfully')
          } else {
            addTestResult('GPS Update', 'error', updateResult.payload as string)
          }
          
          // Test delete GPS
          addTestResult('GPS Delete', 'pending', 'Deleting GPS...')
          const deleteResult = await dispatch(deleteGPS(createResult.payload.id))
          
          if (deleteGPS.fulfilled.match(deleteResult)) {
            addTestResult('GPS Delete', 'success', 'GPS deleted successfully')
          } else {
            addTestResult('GPS Delete', 'error', deleteResult.payload as string)
          }
        } else {
          addTestResult('GPS Create', 'error', createResult.payload as string)
        }
      } else {
        addTestResult('GPS Fetch', 'error', fetchResult.payload as string)
      }
    } catch (error) {
      addTestResult('GPS Operations', 'error', `Unexpected error: ${error}`)
    }
  }

  // Test SIM Card Operations
  const testSIMCardOperations = async () => {
    try {
      addTestResult('SIM Fetch', 'pending', 'Fetching SIM cards...')
      const fetchResult = await dispatch(fetchSIMCards())
      
      if (fetchSIMCards.fulfilled.match(fetchResult)) {
        addTestResult('SIM Fetch', 'success', `Fetched ${fetchResult.payload.length} SIM cards`)
        
        // Test create SIM
        const newSIM: CreateSIMCardData = {
          fecha_compra: '2024-01-15',
          numero_factura: `SIM-TEST-${Date.now()}`,
          numero_chip: `${Date.now()}`,
          icc: `89591234567890${Date.now()}`,
          proveedor: 1,
          estado: 'no_asignado',
          proceso: 'en_almacen',
          plan: 'Test Plan',
          precio_compra: 25.00,
          observaciones: 'Test SIM card'
        }
        
        addTestResult('SIM Create', 'pending', 'Creating test SIM...')
        const createResult = await dispatch(createSIMCard(newSIM))
        
        if (createSIMCard.fulfilled.match(createResult)) {
          addTestResult('SIM Create', 'success', `Created SIM with ID: ${createResult.payload.id}`)
          
          // Test delete SIM
          addTestResult('SIM Delete', 'pending', 'Deleting SIM...')
          const deleteResult = await dispatch(deleteSIMCard(createResult.payload.id))
          
          if (deleteSIMCard.fulfilled.match(deleteResult)) {
            addTestResult('SIM Delete', 'success', 'SIM deleted successfully')
          } else {
            addTestResult('SIM Delete', 'error', deleteResult.payload as string)
          }
        } else {
          addTestResult('SIM Create', 'error', createResult.payload as string)
        }
      } else {
        addTestResult('SIM Fetch', 'error', fetchResult.payload as string)
      }
    } catch (error) {
      addTestResult('SIM Operations', 'error', `Unexpected error: ${error}`)
    }
  }

  // Test Other Products Operations
  const testOtherProductsOperations = async () => {
    try {
      addTestResult('Products Fetch', 'pending', 'Fetching other products...')
      const fetchResult = await dispatch(fetchOtrosProductos())
      
      if (fetchOtrosProductos.fulfilled.match(fetchResult)) {
        addTestResult('Products Fetch', 'success', `Fetched ${fetchResult.payload.length} products`)
        
        // Test create product
        const newProduct: CreateOtroProductoData = {
          fecha_compra: '2024-01-15',
          numero_factura: `FAC-TEST-${Date.now()}`,
          cantidad: 100,
          descripcion: 'Test product description',
          categoria: 'Test Category',
          precio_unitario: 15.50,
          precio_total: 1550.00,
          stock_actual: 100,
          stock_minimo: 10,
          proveedor: 1,
          observaciones: 'Test product'
        }
        
        addTestResult('Product Create', 'pending', 'Creating test product...')
        const createResult = await dispatch(createOtroProducto(newProduct))
        
        if (createOtroProducto.fulfilled.match(createResult)) {
          addTestResult('Product Create', 'success', `Created product with ID: ${createResult.payload.id}`)
          
          // Test stock adjustment
          addTestResult('Stock Adjust', 'pending', 'Adjusting stock...')
          const adjustResult = await dispatch(adjustStock({
            id: createResult.payload.id,
            data: { cantidad: -10, motivo: 'Test adjustment' }
          }))
          
          if (adjustStock.fulfilled.match(adjustResult)) {
            addTestResult('Stock Adjust', 'success', 'Stock adjusted successfully')
          } else {
            addTestResult('Stock Adjust', 'error', adjustResult.payload as string)
          }
          
          // Test delete product
          addTestResult('Product Delete', 'pending', 'Deleting product...')
          const deleteResult = await dispatch(deleteOtroProducto(createResult.payload.id))
          
          if (deleteOtroProducto.fulfilled.match(deleteResult)) {
            addTestResult('Product Delete', 'success', 'Product deleted successfully')
          } else {
            addTestResult('Product Delete', 'error', deleteResult.payload as string)
          }
        } else {
          addTestResult('Product Create', 'error', createResult.payload as string)
        }
      } else {
        addTestResult('Products Fetch', 'error', fetchResult.payload as string)
      }
    } catch (error) {
      addTestResult('Product Operations', 'error', `Unexpected error: ${error}`)
    }
  }

  // Test Providers
  const testProviders = async () => {
    try {
      addTestResult('Providers Fetch', 'pending', 'Fetching providers...')
      const fetchResult = await dispatch(fetchProveedores())
      
      if (fetchProveedores.fulfilled.match(fetchResult)) {
        addTestResult('Providers Fetch', 'success', `Fetched ${fetchResult.payload.length} providers`)
      } else {
        addTestResult('Providers Fetch', 'error', fetchResult.payload as string)
      }
    } catch (error) {
      addTestResult('Providers Operations', 'error', `Unexpected error: ${error}`)
    }
  }

  // Run all tests
  const runAllTests = async () => {
    setIsRunningTests(true)
    clearResults()
    
    addTestResult('Test Suite', 'pending', 'Starting inventory tests...')
    
    await testProviders()
    await testGPSOperations()
    await testSIMCardOperations()
    await testOtherProductsOperations()
    
    addTestResult('Test Suite', 'success', 'All tests completed!')
    setIsRunningTests(false)
  }

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return 'text-green-600'
      case 'error': return 'text-red-600'
      case 'pending': return 'text-yellow-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return '✅'
      case 'error': return '❌'
      case 'pending': return '⏳'
      default: return '❓'
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          🧪 Inventory CRUD Test Panel
        </h2>
        
        {/* Authentication Status */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Authentication Status</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Authenticated:</span> 
              <span className={auth.isAuthenticated ? 'text-green-600' : 'text-red-600'}>
                {auth.isAuthenticated ? ' ✅ Yes' : ' ❌ No'}
              </span>
            </div>
            <div>
              <span className="font-medium">Has Token:</span> 
              <span className={auth.token ? 'text-green-600' : 'text-red-600'}>
                {auth.token ? ' ✅ Yes' : ' ❌ No'}
              </span>
            </div>
          </div>
        </div>

        {/* Test Controls */}
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={runAllTests}
            disabled={isRunningTests || !auth.isAuthenticated}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isRunningTests ? '🔄 Running Tests...' : '🚀 Run All Tests'}
          </button>
          
          <button
            onClick={testProviders}
            disabled={isRunningTests || !auth.isAuthenticated}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
          >
            🏢 Test Providers
          </button>
          
          <button
            onClick={testGPSOperations}
            disabled={isRunningTests || !auth.isAuthenticated}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
          >
            📡 Test GPS
          </button>
          
          <button
            onClick={testSIMCardOperations}
            disabled={isRunningTests || !auth.isAuthenticated}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400"
          >
            📱 Test SIM Cards
          </button>
          
          <button
            onClick={testOtherProductsOperations}
            disabled={isRunningTests || !auth.isAuthenticated}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
          >
            📦 Test Products
          </button>
          
          <button
            onClick={clearResults}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🗑️ Clear Results
          </button>
        </div>

        {/* Current State */}
        <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="font-medium text-blue-800">GPS Devices</div>
            <div className="text-blue-600">
              {Array.isArray(inventory.gps.items) ? inventory.gps.items.length : 0} items
              {inventory.gps.isLoading && ' (Loading...)'}
            </div>
          </div>
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="font-medium text-green-800">SIM Cards</div>
            <div className="text-green-600">
              {Array.isArray(inventory.simCards.items) ? inventory.simCards.items.length : 0} items
              {inventory.simCards.isLoading && ' (Loading...)'}
            </div>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg">
            <div className="font-medium text-purple-800">Other Products</div>
            <div className="text-purple-600">
              {Array.isArray(inventory.otrosProductos.items) ? inventory.otrosProductos.items.length : 0} items
              {inventory.otrosProductos.isLoading && ' (Loading...)'}
            </div>
          </div>
          <div className="p-3 bg-orange-50 rounded-lg">
            <div className="font-medium text-orange-800">Providers</div>
            <div className="text-orange-600">
              {Array.isArray(inventory.proveedores.items) ? inventory.proveedores.items.length : 0} items
              {inventory.proveedores.isLoading && ' (Loading...)'}
            </div>
          </div>
        </div>

        {/* Test Results */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Test Results</h3>
          
          {testResults.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No test results yet. Run some tests to see results here.
            </p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-white rounded-lg border"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getStatusIcon(result.status)}</span>
                    <div>
                      <div className="font-medium">{result.operation}</div>
                      <div className={`text-sm ${getStatusColor(result.status)}`}>
                        {result.message}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.timestamp}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {!auth.isAuthenticated && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">
              ⚠️ You need to be authenticated to run inventory tests. Please login first.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default InventoryTestPanel