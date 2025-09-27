import React, { useState } from 'react'
import { api } from '../shared/lib/api'

interface APIResponse {
  status: number
  statusText: string
  data: unknown
  dataType: string
  isArray: boolean
  dataKeys: string[]
  dataLength: number | string
}

export const APITestComponent: React.FC = () => {
  const [response, setResponse] = useState<APIResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testGPSAPI = async () => {
    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      
      // Llamada directa a la API
      const result = await api.get('/api/inventory/gps/')
      
      
      setResponse({
        status: result.status,
        statusText: result.statusText,
        data: result.data,
        dataType: typeof result.data,
        isArray: Array.isArray(result.data),
        dataKeys: Object.keys(result.data || {}),
        dataLength: result.data?.length || 'N/A'
      })
      
    } catch (err: unknown) {
      console.error('🧪 APITestComponent: Error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <h3 className="text-lg font-semibold text-yellow-800 mb-3">🧪 API Test Component</h3>
      
      <button
        onClick={testGPSAPI}
        disabled={loading}
        className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 disabled:opacity-50 mb-4"
      >
        {loading ? 'Testing...' : 'Test Direct GPS API Call'}
      </button>

      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {response && (
        <div className="bg-white border rounded p-4">
          <h4 className="font-semibold mb-2">API Response Details:</h4>
          <div className="space-y-2 text-sm">
            <p><strong>Status:</strong> {response.status} {response.statusText}</p>
            <p><strong>Data Type:</strong> {response.dataType}</p>
            <p><strong>Is Array:</strong> {response.isArray ? 'Yes' : 'No'}</p>
            <p><strong>Data Length:</strong> {response.dataLength}</p>
            <p><strong>Data Keys:</strong> {response.dataKeys.join(', ')}</p>
            
            <div className="mt-4">
              <strong>Raw Data:</strong>
              <pre className="bg-gray-100 p-2 rounded mt-2 text-xs overflow-auto max-h-40">
                {JSON.stringify(response.data, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}