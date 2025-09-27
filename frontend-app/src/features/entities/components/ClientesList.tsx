import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { 
  FiEdit2, 
  FiTrash2, 
  FiEye, 
  FiUserCheck, 
  FiUserX,
  FiPlus 
} from 'react-icons/fi'
import type { Cliente } from '../entitiesTypes'
import { useClientes } from '../useEntities'

interface ClientesListProps {
  onEdit?: (cliente: Cliente) => void
  onAdd?: () => void
}

export const ClientesList: React.FC<ClientesListProps> = ({ onEdit, onAdd }) => {
  const { 
    items: clientes, 
    isLoading: loading, 
    error, 
    deleteCliente, 
    toggleActive,
    loadClientes 
  } = useClientes()

  // Load clientes when component mounts
  useEffect(() => {
    loadClientes()
  }, [loadClientes])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCliente, setSelectedCliente] = useState<Cliente | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  // Filter clientes based on search term
  const filteredClientes = useMemo(() => {
    if (!searchTerm) return clientes
    
    const term = searchTerm.toLowerCase()
    return clientes.filter(cliente => 
      cliente.nombre.toLowerCase().includes(term) ||
      cliente.ruc?.toLowerCase().includes(term) ||
      cliente.id.toString().includes(term) ||
      cliente.celular?.toLowerCase().includes(term) ||
      cliente.contacto?.toLowerCase().includes(term) ||
      cliente.correo?.toLowerCase().includes(term)
    )
  }, [clientes, searchTerm])

  const handleDelete = async (id: number) => {
    const cliente = clientes.find(c => c.id === id)
    if (!cliente) return

    const confirmMessage = `¿Está seguro de que desea eliminar el cliente "${cliente.nombre}"?`
    
    if (window.confirm(confirmMessage)) {
      try {
        const result = await deleteCliente(id)
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success(`Cliente "${cliente.nombre}" eliminado exitosamente`)
          // Recargar la lista después de eliminar
          loadClientes()
        }
      } catch (error) {
        console.error('Error al eliminar cliente:', error)
        toast.error('Error al eliminar el cliente. Por favor, intente nuevamente.')
      }
    }
  }

  const handleToggleActive = async (id: number) => {
    const cliente = clientes.find(c => c.id === id)
    if (!cliente) return

    const action = cliente.is_active ? 'desactivar' : 'activar'
    const confirmMessage = `¿Está seguro de que desea ${action} el cliente "${cliente.nombre}"?`
    
    if (window.confirm(confirmMessage)) {
      try {
        const result = await toggleActive(id)
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success(`Cliente "${cliente.nombre}" ${action}do exitosamente`)
          // Recargar la lista para reflejar el cambio
          loadClientes()
        } else if (result.meta.requestStatus === 'rejected') {
          toast.error(`Error al ${action} el cliente. ${result.payload || 'Intente nuevamente.'}`)
        }
      } catch (error) {
        console.error(`Error al ${action} cliente:`, error)
        toast.error(`Error al ${action} el cliente. Por favor, intente nuevamente.`)
      }
    }
  }

  const handleViewDetails = (cliente: Cliente) => {
    setSelectedCliente(cliente)
    setShowDetails(true)
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error al cargar clientes</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
            <div className="mt-4">
              <button
                type="button"
                className="bg-red-100 px-2 py-1 text-sm font-medium text-red-800 rounded-md hover:bg-red-200"
                onClick={() => window.location.reload()}
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
        {onAdd && (
          <button
            onClick={onAdd}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center gap-2"
            title="Agregar nuevo cliente"
          >
            <FiPlus className="w-4 h-4" />
            Agregar Cliente
          </button>
        )}
      </div>

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Buscar por nombre, RUC, teléfono o correo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{clientes.length}</div>
          <div className="text-gray-600">Total Clientes</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">
            {clientes.filter(c => c.is_active).length}
          </div>
          <div className="text-gray-600">Activos</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">
            {clientes.filter(c => !c.is_active).length}
          </div>
          <div className="text-gray-600">Inactivos</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  RUC
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contacto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredClientes.map((cliente) => (
                <tr key={cliente.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.nombre}</div>
                    <div className="text-sm text-gray-500">ID: {cliente.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.ruc || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{cliente.contacto || 'N/A'}</div>
                    <div className="text-sm text-gray-500">{cliente.celular || 'N/A'}</div>
                    <div className="text-sm text-gray-500">{cliente.correo || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      cliente.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {cliente.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleViewDetails(cliente)}
                        className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 p-2 rounded-full transition-colors"
                        title="Ver detalles del cliente"
                      >
                        <FiEye className="w-4 h-4" />
                      </button>
                      {onEdit && (
                        <button
                          onClick={() => onEdit(cliente)}
                          className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 p-2 rounded-full transition-colors"
                          title="Editar cliente"
                        >
                          <FiEdit2 className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleToggleActive(cliente.id)}
                        className={`p-2 rounded-full transition-colors ${
                          cliente.is_active 
                            ? 'text-orange-600 hover:text-orange-900 hover:bg-orange-50' 
                            : 'text-green-600 hover:text-green-900 hover:bg-green-50'
                        }`}
                        title={cliente.is_active ? 'Desactivar cliente' : 'Activar cliente'}
                      >
                        {cliente.is_active ? <FiUserX className="w-4 h-4" /> : <FiUserCheck className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleDelete(cliente.id)}
                        className="text-red-600 hover:text-red-900 hover:bg-red-50 p-2 rounded-full transition-colors"
                        title="Eliminar cliente"
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

        {filteredClientes.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchTerm ? 'No se encontraron clientes que coincidan con la búsqueda' : 'No hay clientes registrados'}
            </div>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {showDetails && selectedCliente && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles del Cliente
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
                  <label className="block text-sm font-medium text-gray-700">Nombre</label>
                  <p className="text-sm text-gray-900">{selectedCliente.nombre}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ID</label>
                  <p className="text-sm text-gray-900">{selectedCliente.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">RUC</label>
                  <p className="text-sm text-gray-900">{selectedCliente.ruc || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Contacto</label>
                  <p className="text-sm text-gray-900">{selectedCliente.contacto || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Celular</label>
                  <p className="text-sm text-gray-900">{selectedCliente.celular || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Correo</label>
                  <p className="text-sm text-gray-900">{selectedCliente.correo || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Dirección</label>
                  <p className="text-sm text-gray-900">{selectedCliente.direccion || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <p className="text-sm text-gray-900">{selectedCliente.is_active ? 'Activo' : 'Inactivo'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha de Creación</label>
                  <p className="text-sm text-gray-900">{new Date(selectedCliente.created_at).toLocaleDateString()}</p>
                </div>
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