import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { FiEdit2, FiTrash2, FiUserCheck, FiUserX, FiEye, FiPlus } from 'react-icons/fi'
import type { ProveedorEntity } from '../entitiesTypes'
import { useProveedores } from '../useEntities'

interface ProveedoresListProps {
  onEdit?: (proveedor: ProveedorEntity) => void
  onAdd?: () => void
}

export const ProveedoresList: React.FC<ProveedoresListProps> = ({ onEdit, onAdd }) => {
  const { 
    proveedores, 
    loadProveedores,
    removeProveedor,
    toggleActive
  } = useProveedores()

  // Load proveedores when component mounts
  useEffect(() => {
    loadProveedores()
  }, [loadProveedores])
  
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProveedor, setSelectedProveedor] = useState<ProveedorEntity | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [filterActive, setFilterActive] = useState<string>('')

  // Filter proveedores based on search term and active status
  const filteredProveedores = useMemo(() => {
    let filtered = proveedores.items

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter((proveedor: ProveedorEntity) => 
        proveedor.nombre.toLowerCase().includes(term) ||
        proveedor.ruc?.toLowerCase().includes(term) ||
        proveedor.correo?.toLowerCase().includes(term) ||
        proveedor.celular?.toLowerCase().includes(term) ||
        proveedor.id.toString().includes(term)
      )
    }

    if (filterActive) {
      filtered = filtered.filter((proveedor: ProveedorEntity) => 
        filterActive === 'active' ? proveedor.is_active : !proveedor.is_active
      )
    }

    return filtered
  }, [proveedores.items, searchTerm, filterActive])

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este proveedor?')) {
      try {
        await removeProveedor(id)
        toast.success('Proveedor eliminado exitosamente')
        loadProveedores() // Reload the list
      } catch (error) {
        console.error('Error al eliminar proveedor:', error)
        toast.error('Error al eliminar proveedor')
      }
    }
  }

  const handleToggleActive = async (id: number) => {
    const proveedor = proveedores.items.find(p => p.id === id)
    if (!proveedor) return

    const action = proveedor.is_active ? 'desactivar' : 'activar'
    const confirmMessage = `¿Está seguro de que desea ${action} el proveedor "${proveedor.nombre}"?`
    
    if (window.confirm(confirmMessage)) {
      try {
        const result = await toggleActive(id)
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success(`Proveedor "${proveedor.nombre}" ${action}do exitosamente`)
          // Recargar la lista para reflejar el cambio
          loadProveedores()
        } else if (result.meta.requestStatus === 'rejected') {
          toast.error(`Error al ${action} el proveedor. ${result.payload || 'Intente nuevamente.'}`)
        }
      } catch (error) {
        console.error(`Error al ${action} proveedor:`, error)
        toast.error(`Error al ${action} el proveedor. Por favor, intente nuevamente.`)
      }
    }
  }

  const handleViewDetails = (proveedor: ProveedorEntity) => {
    setSelectedProveedor(proveedor)
    setShowDetails(true)
  }

  if (proveedores.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (proveedores.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              {proveedores.error}
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
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
          >
            <FiPlus className="w-4 h-4" />
            Nuevo Proveedor
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Buscar
            </label>
            <input
              type="text"
              id="search"
              placeholder="Buscar por nombre, RUC, correo, teléfono..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="active" className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              id="active"
              value={filterActive}
              onChange={(e) => setFilterActive(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los estados</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">
            {proveedores.items.length}
          </div>
          <div className="text-gray-600">Total Proveedores</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">
            {proveedores.items.filter(p => p.is_active).length}
          </div>
          <div className="text-gray-600">Activos</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">
            {proveedores.items.filter(p => !p.is_active).length}
          </div>
          <div className="text-gray-600">Inactivos</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Proveedor
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
              {filteredProveedores.map((proveedor: ProveedorEntity) => (
                <tr key={proveedor.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{proveedor.nombre}</div>
                    <div className="text-sm text-gray-500">ID: {proveedor.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {proveedor.ruc || 'No especificado'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {proveedor.correo || 'Sin correo'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {proveedor.celular || 'Sin celular'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      proveedor.is_active 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {proveedor.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleViewDetails(proveedor)}
                        className="text-blue-600 hover:text-blue-900 p-1 rounded"
                        title="Ver detalles"
                      >
                        <FiEye className="w-4 h-4" />
                      </button>
                      {onEdit && (
                        <button
                          onClick={() => onEdit(proveedor)}
                          className="text-indigo-600 hover:text-indigo-900 p-1 rounded"
                          title="Editar"
                        >
                          <FiEdit2 className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleToggleActive(proveedor.id)}
                        className={`p-1 rounded ${
                          proveedor.is_active 
                            ? 'text-red-600 hover:text-red-900' 
                            : 'text-green-600 hover:text-green-900'
                        }`}
                        title={proveedor.is_active ? 'Desactivar' : 'Activar'}
                      >
                        {proveedor.is_active ? (
                          <FiUserX className="w-4 h-4" />
                        ) : (
                          <FiUserCheck className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(proveedor.id)}
                        className="text-red-600 hover:text-red-900 p-1 rounded"
                        title="Eliminar"
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

        {filteredProveedores.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchTerm || filterActive ? 'No se encontraron proveedores con los filtros aplicados' : 'No hay proveedores registrados'}
            </div>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {showDetails && selectedProveedor && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles del Proveedor
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
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nombre</label>
                  <p className="text-sm text-gray-900">{selectedProveedor.nombre}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">RUC</label>
                  <p className="text-sm text-gray-900">{selectedProveedor.ruc || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Teléfono</label>
                  <p className="text-sm text-gray-900">{selectedProveedor.celular || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Correo</label>
                  <p className="text-sm text-gray-900">{selectedProveedor.correo || 'No especificado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <p className="text-sm text-gray-900">
                    {selectedProveedor.is_active ? 'Activo' : 'Inactivo'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha de Creación</label>
                  <p className="text-sm text-gray-900">
                    {new Date(selectedProveedor.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {selectedProveedor.direccion && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700">Dirección</label>
                  <p className="text-sm text-gray-900 mt-1">{selectedProveedor.direccion}</p>
                </div>
              )}

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowDetails(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cerrar
                </button>
                {onEdit && (
                  <button
                    onClick={() => {
                      setShowDetails(false)
                      onEdit(selectedProveedor)
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Editar
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}