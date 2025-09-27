import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { FiEdit2, FiTrash2, FiUserCheck, FiUserX, FiEye, FiPlus } from 'react-icons/fi'
import type { UnidadVehicular } from '../entitiesTypes'
import { TIPO_VEHICULO_OPTIONS } from '../entitiesTypes'
import { useUnidades } from '../useEntities'

interface UnidadesListProps {
  onEdit?: (unidad: UnidadVehicular) => void
  onAdd?: () => void
}

export const UnidadesList: React.FC<UnidadesListProps> = ({ onEdit, onAdd }) => {
  const { 
    unidades, 
    loadUnidades,
    removeUnidad,
    toggleActive
  } = useUnidades()

  // Load unidades when component mounts
  useEffect(() => {
    loadUnidades()
  }, [loadUnidades])

  const [searchTerm, setSearchTerm] = useState('')
  const [selectedUnidad, setSelectedUnidad] = useState<UnidadVehicular | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [filterActivo, setFilterActivo] = useState<boolean | null>(null)
  const [filterTipo, setFilterTipo] = useState<string>('')

  // Filter unidades based on search term, active status, and vehicle type
  const filteredUnidades = useMemo(() => {
    let filtered = unidades.items

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter((unidad: UnidadVehicular) => 
        unidad.placa.toLowerCase().includes(term) ||
        unidad.marca.toLowerCase().includes(term) ||
        unidad.modelo.toLowerCase().includes(term) ||
        unidad.id.toString().includes(term) ||
        unidad.serie.toLowerCase().includes(term) ||
        unidad.tipo.toLowerCase().includes(term) ||
        unidad.cliente_info?.nombre.toLowerCase().includes(term)
      )
    }

    if (filterActivo !== null) {
      filtered = filtered.filter((unidad: UnidadVehicular) => unidad.is_active === filterActivo)
    }

    if (filterTipo) {
      filtered = filtered.filter((unidad: UnidadVehicular) => unidad.tipo === filterTipo)
    }

    return filtered
  }, [unidades.items, searchTerm, filterActivo, filterTipo])

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta unidad?')) {
      try {
        await removeUnidad(id)
        toast.success('Unidad eliminada exitosamente')
        loadUnidades() // Reload the list
      } catch (error) {
        console.error('Error al eliminar unidad:', error)
        toast.error('Error al eliminar unidad')
      }
    }
  }

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      await toggleActive(id)
      toast.success(`Unidad ${currentStatus ? 'desactivada' : 'activada'} exitosamente`)
      loadUnidades() // Reload the list
    } catch (error) {
      console.error('Error al cambiar estado de la unidad:', error)
      toast.error('Error al cambiar estado de la unidad')
    }
  }

  const handleViewDetails = (unidad: UnidadVehicular) => {
    setSelectedUnidad(unidad)
    setShowDetails(true)
  }

  if (unidades.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (unidades.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{unidades.error}</p>
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
          <h1 className="text-2xl font-bold text-gray-900">Unidades Vehiculares</h1>
          <p className="text-gray-600">Gestiona las unidades vehiculares de tus clientes</p>
        </div>
        {onAdd && (
          <button
            onClick={onAdd}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
          >
            <FiPlus className="w-4 h-4" />
            Nueva Unidad
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Buscar
            </label>
            <input
              type="text"
              id="search"
              placeholder="Buscar por placa, marca, modelo, cliente..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Vehículo
            </label>
            <select
              id="tipo"
              value={filterTipo}
              onChange={(e) => setFilterTipo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los tipos</option>
              {TIPO_VEHICULO_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="estado" className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              id="estado"
              value={filterActivo === null ? '' : filterActivo.toString()}
              onChange={(e) => setFilterActivo(e.target.value === '' ? null : e.target.value === 'true')}
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">
            {unidades.items.length}
          </div>
          <div className="text-gray-600">Total Unidades</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">
            {unidades.items.filter(u => u.is_active).length}
          </div>
          <div className="text-gray-600">Activas</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">
            {unidades.items.filter(u => !u.is_active).length}
          </div>
          <div className="text-gray-600">Inactivas</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Placa
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vehículo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
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
              {filteredUnidades.map((unidad) => (
                <tr key={unidad.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{unidad.placa}</div>
                    <div className="text-sm text-gray-500">ID: {unidad.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{unidad.marca} {unidad.modelo}</div>
                    <div className="text-sm text-gray-500">{unidad.serie} • {unidad.tipo}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {unidad.cliente_info?.nombre || 'Sin cliente'}
                    </div>
                    <div className="text-sm text-gray-500">
                      ID: {unidad.cliente_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      unidad.is_active 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {unidad.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleViewDetails(unidad)}
                        className="text-blue-600 hover:text-blue-900 p-1 rounded"
                        title="Ver detalles"
                      >
                        <FiEye className="w-4 h-4" />
                      </button>
                      {onEdit && (
                        <button
                          onClick={() => onEdit(unidad)}
                          className="text-indigo-600 hover:text-indigo-900 p-1 rounded"
                          title="Editar"
                        >
                          <FiEdit2 className="w-4 h-4" />
                        </button>
                      )}
                      <button
                         onClick={() => handleToggleActive(unidad.id, unidad.is_active)}
                         className={`p-1 rounded ${
                           unidad.is_active 
                             ? 'text-orange-600 hover:text-orange-900' 
                             : 'text-green-600 hover:text-green-900'
                         }`}
                         title={unidad.is_active ? 'Desactivar' : 'Activar'}
                       >
                        {unidad.is_active ? (
                          <FiUserX className="w-4 h-4" />
                        ) : (
                          <FiUserCheck className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(unidad.id)}
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

        {filteredUnidades.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchTerm || filterActivo !== null ? 'No se encontraron unidades con los filtros aplicados' : 'No hay unidades vehiculares registradas'}
            </div>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {showDetails && selectedUnidad && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles de la Unidad
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
                  <label className="block text-sm font-medium text-gray-700">Placa</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.placa}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Marca</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.marca}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Modelo</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.modelo}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Serie</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.serie}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tipo</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.tipo}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <p className="text-sm text-gray-900">{selectedUnidad.is_active ? 'Activo' : 'Inactivo'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Cliente</label>
                  <p className="text-sm text-gray-900">
                    {selectedUnidad.cliente_info?.nombre || 'Sin cliente asignado'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha de Creación</label>
                  <p className="text-sm text-gray-900">
                    {new Date(selectedUnidad.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>



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
                      onEdit(selectedUnidad)
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