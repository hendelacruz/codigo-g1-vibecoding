import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { 
  FiEdit2, 
  FiTrash2, 
  FiEye, 
  FiPlus,
  FiPower,
  FiSquare,
  FiLoader
} from 'react-icons/fi'
import type { GPS } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'


interface GPSListProps {
  onEdit?: (gps: GPS) => void
  onAdd?: () => void
}

export const GPSList: React.FC<GPSListProps> = ({ onEdit, onAdd }) => {
  const { 
    gps, 
    removeGPS, 
    loadGPSDevices,
    toggleGPSActive
  } = useInventory()

  // Load GPS devices when component mounts
  useEffect(() => {
    loadGPSDevices()
  }, [loadGPSDevices])

  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedGPS, setSelectedGPS] = useState<GPS | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [togglingDevices, setTogglingDevices] = useState<Set<number>>(new Set())

  // Filter GPS devices based on search term and status
  const filteredGPS = useMemo(() => {
    const items = Array.isArray(gps?.items) ? gps.items : []
    let filtered = [...items]
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(device => 
        device.imei.toLowerCase().includes(term) ||
        device.modelo.toLowerCase().includes(term) ||
        device.marca.toLowerCase().includes(term) ||
        device.id.toString().includes(term)
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(device => device.estado === statusFilter)
    }

    return filtered
  }, [gps?.items, searchTerm, statusFilter])

  const handleDelete = async (id: number) => {
    const device = gps?.items?.find(d => d.id === id)
    if (!device) return

    const confirmMessage = `¿Está seguro de que desea eliminar el dispositivo GPS "${device.imei}"?`
    
    if (window.confirm(confirmMessage)) {
      try {
        await removeGPS(id)
        toast.success(`Dispositivo GPS "${device.imei}" eliminado exitosamente`)
        // Recargar la lista después de eliminar
        loadGPSDevices()
      } catch (error) {
        console.error('Error al eliminar dispositivo GPS:', error)
        toast.error('Error al eliminar el dispositivo GPS. Por favor, intente nuevamente.')
      }
    }
  }

  const handleToggleActive = async (id: number) => {
    const device = gps?.items?.find(d => d.id === id)
    if (!device) {
      toast.error('Dispositivo GPS no encontrado')
      return
    }

    // Prevent multiple simultaneous toggles on the same device
    if (togglingDevices.has(id)) {
      toast.error('Operación en progreso, por favor espere...')
      return
    }

    const isActive = device.estado === 'no_asignado'
    const action = isActive ? 'desactivar' : 'activar'
    const confirmMessage = `¿Está seguro de que desea ${action} el dispositivo GPS "${device.imei}"?`
    
    if (window.confirm(confirmMessage)) {
      // Add device to toggling set
      setTogglingDevices(prev => new Set(prev).add(id))
      
      try {
        const result = await toggleGPSActive(id)
        
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success(`Dispositivo GPS "${device.imei}" ${action}do exitosamente`)
          // Recargar la lista para reflejar el cambio
          await loadGPSDevices()
        } else if (result.meta.requestStatus === 'rejected') {
          const errorMessage = typeof result.payload === 'string' 
            ? result.payload 
            : 'Error desconocido'
          toast.error(`Error al ${action} el dispositivo GPS: ${errorMessage}`)
        }
      } catch (error) {
        console.error(`Error al ${action} dispositivo GPS:`, error)
        const errorMessage = error instanceof Error 
          ? error.message 
          : 'Error desconocido'
        toast.error(`Error al ${action} el dispositivo GPS: ${errorMessage}`)
      } finally {
        // Remove device from toggling set
        setTogglingDevices(prev => {
          const newSet = new Set(prev)
          newSet.delete(id)
          return newSet
        })
      }
    }
  }

  const handleViewDetails = (device: GPS) => {
    setSelectedGPS(device)
    setShowDetails(true)
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'disponible': return 'bg-green-100 text-green-800'
      case 'asignado': return 'bg-blue-100 text-blue-800'
      case 'en_mantenimiento': return 'bg-yellow-100 text-yellow-800'
      case 'dañado': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (gps.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (gps.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error al cargar dispositivos GPS</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{gps.error}</p>
            </div>
            <div className="mt-4">
              <button
                type="button"
                className="bg-red-100 px-2 py-1 text-sm font-medium text-red-800 rounded-md hover:bg-red-200"
                onClick={() => loadGPSDevices()}
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dispositivos GPS</h1>
          <p className="text-gray-600 mt-1">
            Gestiona los dispositivos GPS del inventario
          </p>
        </div>
        {onAdd && (
          <button
            onClick={onAdd}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center gap-2"
            title="Agregar nuevo dispositivo GPS"
          >
            <FiPlus className="w-4 h-4" />
            Agregar GPS
          </button>
        )}
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Buscar por IMEI, modelo o marca..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="sm:w-48">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todos los estados</option>
            <option value="disponible">Disponible</option>
            <option value="asignado">Asignado</option>
            <option value="mantenimiento">Mantenimiento</option>
            <option value="dañado">Dañado</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{gps?.items?.length || 0}</div>
          <div className="text-gray-600">Total GPS</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">
            {Array.isArray(gps?.items) ? gps.items.filter(d => d.estado === 'no_asignado').length : 0}
          </div>
          <div className="text-gray-600">Disponibles</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">
            {Array.isArray(gps?.items) ? gps.items.filter(d => d.estado === 'asignado').length : 0}
          </div>
          <div className="text-gray-600">Asignados</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-yellow-600">
            {Array.isArray(gps?.items) ? gps.items.filter(d => d.proceso === 'en_mantenimiento').length : 0}
          </div>
          <div className="text-gray-600">Mantenimiento</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IMEI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Modelo/Marca
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha Compra
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredGPS.map((device) => (
                <tr key={device.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{device.imei}</div>
                    <div className="text-sm text-gray-500">ID: {device.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{device.modelo}</div>
                    <div className="text-sm text-gray-500">{device.marca}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeColor(device.estado)}`}>
                      {device.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      S/ {(device.precio_compra || 0).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {new Date(device.fecha_compra).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleViewDetails(device)}
                        className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 p-2 rounded-full transition-colors"
                        title="Ver detalles del dispositivo GPS"
                      >
                        <FiEye className="w-4 h-4" />
                      </button>
                      {onEdit && (
                        <button
                          onClick={() => onEdit(device)}
                          className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 p-2 rounded-full transition-colors"
                          title="Editar dispositivo GPS"
                        >
                          <FiEdit2 className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleToggleActive(device.id)}
                        disabled={togglingDevices.has(device.id)}
                        className={`p-2 rounded-full transition-colors ${
                          togglingDevices.has(device.id)
                            ? 'text-gray-400 cursor-not-allowed'
                            : device.estado === 'no_asignado'
                            ? 'text-orange-600 hover:text-orange-900 hover:bg-orange-50' 
                            : 'text-green-600 hover:text-green-900 hover:bg-green-50'
                        }`}
                        title={
                          togglingDevices.has(device.id)
                            ? 'Procesando...'
                            : device.estado === 'no_asignado' 
                            ? 'Desactivar dispositivo GPS' 
                            : 'Activar dispositivo GPS'
                        }
                      >
                        {togglingDevices.has(device.id) ? (
                          <FiLoader className="w-4 h-4 animate-spin" />
                        ) : device.estado === 'no_asignado' ? (
                          <FiSquare className="w-4 h-4" />
                        ) : (
                          <FiPower className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(device.id)}
                        className="text-red-600 hover:text-red-900 hover:bg-red-50 p-2 rounded-full transition-colors"
                        title="Eliminar dispositivo GPS"
                      >
                        <FiTrash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredGPS.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchTerm || statusFilter !== 'all' 
                ? 'No se encontraron dispositivos GPS que coincidan con los filtros' 
                : 'No hay dispositivos GPS registrados'}
            </div>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {showDetails && selectedGPS && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles del Dispositivo GPS
                </h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Cerrar</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">IMEI</label>
                  <p className="text-sm text-gray-900">{selectedGPS.imei}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ID</label>
                  <p className="text-sm text-gray-900">{selectedGPS.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Modelo</label>
                  <p className="text-sm text-gray-900">{selectedGPS.modelo}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Marca</label>
                  <p className="text-sm text-gray-900">{selectedGPS.marca}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <p className="text-sm text-gray-900">{selectedGPS.estado}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Precio de Compra</label>
                  <p className="text-sm text-gray-900">${(selectedGPS.precio_compra || 0).toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha de Compra</label>
                  <p className="text-sm text-gray-900">{new Date(selectedGPS.fecha_compra).toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Número de Factura</label>
                  <p className="text-sm text-gray-900">{selectedGPS.numero_factura || 'No especificado'}</p>
                </div>
                {selectedGPS.observaciones && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Observaciones</label>
                    <p className="text-sm text-gray-900">{selectedGPS.observaciones}</p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowDetails(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}