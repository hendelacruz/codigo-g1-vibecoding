import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { 
  FiEdit2, 
  FiTrash2, 
  FiEye, 
  FiPlus,
  FiSquare,
  FiLoader
} from 'react-icons/fi'
import type { SIMCard } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'

interface SIMCardListProps {
  onEdit?: (simCard: SIMCard) => void
  onAdd?: () => void
}

export const SIMCardList: React.FC<SIMCardListProps> = ({ onEdit, onAdd }) => {
  const { 
    simCards, 
    removeSIMCard, 
    loadSIMCards
  } = useInventory()

  // Load SIM cards when component mounts
  useEffect(() => {
    loadSIMCards()
  }, [loadSIMCards])

  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [procesoFilter, setProcesoFilter] = useState('all')
  const [selectedSIMCard, setSelectedSIMCard] = useState<SIMCard | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [deletingCards, setDeletingCards] = useState<Set<number>>(new Set())

  // Filter SIM cards based on search term, status, and proceso
  const filteredSIMCards = useMemo(() => {
    const items = Array.isArray(simCards?.items) ? simCards.items : []
    let filtered = [...items]
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(card => 
        card.numero_chip.toLowerCase().includes(term) ||
        card.icc.toLowerCase().includes(term) ||
        (card.plan || '').toLowerCase().includes(term) ||
        card.id.toString().includes(term)
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(card => card.estado === statusFilter)
    }

    if (procesoFilter !== 'all') {
      filtered = filtered.filter(card => card.proceso === procesoFilter)
    }

    return filtered
  }, [simCards?.items, searchTerm, statusFilter, procesoFilter])

  // Get unique procesos for filter
  const procesos = useMemo(() => {
    const items = Array.isArray(simCards?.items) ? simCards.items : []
    const uniqueProcesos = [...new Set(items.map(card => card.proceso).filter(Boolean))]
    return uniqueProcesos.sort()
  }, [simCards?.items])

  // Get statistics
  const stats = useMemo(() => {
    const items = Array.isArray(simCards?.items) ? simCards.items : []
    return {
      total: items.length,
      no_asignado: items.filter(card => card.estado === 'no_asignado').length,
      asignado: items.filter(card => card.estado === 'asignado').length,
      en_almacen: items.filter(card => card.proceso === 'en_almacen').length,
      en_produccion: items.filter(card => card.proceso === 'en_produccion').length,
      activas: items.filter(card => card.is_active === true).length
    }
  }, [simCards?.items])

  const handleDelete = async (card: SIMCard) => {
    if (!window.confirm(`¿Estás seguro de que deseas eliminar la tarjeta SIM ${card.numero_chip}?`)) {
      return
    }

    setDeletingCards(prev => new Set(prev).add(card.id))
    
    try {
      const result = await removeSIMCard(card.id)
      
      if (result.meta.requestStatus === 'fulfilled') {
        toast.success('Tarjeta SIM eliminada exitosamente')
        await loadSIMCards() // Recargar la lista
      } else {
        toast.error('Error al eliminar la tarjeta SIM')
      }
    } catch (error) {
      console.error('Error al eliminar tarjeta SIM:', error)
      toast.error('Error inesperado al eliminar la tarjeta SIM')
    } finally {
      setDeletingCards(prev => {
        const newSet = new Set(prev)
        newSet.delete(card.id)
        return newSet
      })
    }
  }

  const handleViewDetails = (card: SIMCard) => {
    setSelectedSIMCard(card)
    setShowDetails(true)
  }

  const getStatusBadgeColor = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'activo':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'asignado':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'suspendido':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'en_mantenimiento':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'dañado':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'perdido':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      case 'dado_de_baja':
        return 'bg-black text-white border-black'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-PE')
  }

  if (simCards?.isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <FiLoader className="animate-spin h-8 w-8 text-blue-600 mx-auto" />
          <p className="mt-2 text-gray-600">Cargando tarjetas SIM...</p>
        </div>
      </div>
    )
  }

  if (simCards?.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">
          Error al cargar las tarjetas SIM: {simCards.error}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tarjetas SIM</h2>
          <p className="text-gray-600">Gestiona el inventario de tarjetas SIM</p>
        </div>
        {onAdd && (
          <button
            onClick={onAdd}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center gap-2"
            title="Agregar nueva tarjeta SIM"
          >
            <FiPlus className="w-4 h-4" />
            Agregar Tarjeta SIM
          </button>
        )}
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Buscar por número de chip, ICC, cliente o plan..."
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
            <option value="no_asignado">No Asignado</option>
            <option value="asignado">Asignado</option>
          </select>
        </div>
        <div className="sm:w-48">
          <select
            value={procesoFilter}
            onChange={(e) => setProcesoFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todos los procesos</option>
            {procesos.map((proceso) => (
              <option key={proceso} value={proceso}>
                {proceso}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">{stats.no_asignado}</div>
          <div className="text-sm text-gray-600">No Asignadas</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{stats.asignado}</div>
          <div className="text-sm text-gray-600">Asignadas</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-yellow-600">{stats.en_produccion}</div>
          <div className="text-sm text-gray-600">En Producción</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-purple-600">{stats.activas}</div>
          <div className="text-sm text-gray-600">Activas</div>
        </div>
      </div>

      {/* SIM Cards Table */}
      <div className="bg-white rounded-lg shadow border">
        {filteredSIMCards.length === 0 ? (
          <div className="p-8 text-center">
            <FiSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm || statusFilter !== 'all' || procesoFilter !== 'all'
                ? 'No se encontraron tarjetas SIM con los filtros aplicados'
                : 'No hay tarjetas SIM registradas'
              }
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Número de Chip
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ICC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente/Plan
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
                {filteredSIMCards.map((card) => (
                  <tr key={card.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{card.numero_chip}</div>
                      <div className="text-sm text-gray-500">ID: {card.id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{card.icc}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{card.cliente_id ? `Cliente ID: ${card.cliente_id}` : 'Sin asignar'}</div>
                      <div className="text-sm text-gray-500">{card.plan || 'Sin plan'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusBadgeColor(card.estado)}`}>
                        {card.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {card.precio_compra ? formatCurrency(card.precio_compra) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(card.fecha_compra)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleViewDetails(card)}
                          className="text-blue-600 hover:text-blue-900 p-1 rounded"
                          title="Ver detalles"
                        >
                          <FiEye className="w-4 h-4" />
                        </button>
                        {onEdit && (
                          <button
                            onClick={() => onEdit(card)}
                            className="text-indigo-600 hover:text-indigo-900 p-1 rounded"
                            title="Editar tarjeta SIM"
                          >
                            <FiEdit2 className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(card)}
                          disabled={deletingCards.has(card.id)}
                          className="text-red-600 hover:text-red-900 p-1 rounded disabled:opacity-50"
                          title="Eliminar tarjeta SIM"
                        >
                          {deletingCards.has(card.id) ? (
                            <FiLoader className="w-4 h-4 animate-spin" />
                          ) : (
                            <FiTrash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {showDetails && selectedSIMCard && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles de Tarjeta SIM
                </h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Número de Chip</label>
                  <p className="text-sm text-gray-900">{selectedSIMCard.numero_chip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ICC</label>
                  <p className="text-sm text-gray-900">{selectedSIMCard.icc}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Cliente</label>
                  <p className="text-sm text-gray-900">{selectedSIMCard.cliente_id ? `Cliente ID: ${selectedSIMCard.cliente_id}` : 'Sin asignar'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Plan</label>
                  <p className="text-sm text-gray-900">{selectedSIMCard.plan || 'N/A'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Estado</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusBadgeColor(selectedSIMCard.estado)}`}>
                    {selectedSIMCard.estado}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Precio de Compra</label>
                  <p className="text-sm text-gray-900">
                    {selectedSIMCard.precio_compra ? formatCurrency(selectedSIMCard.precio_compra) : 'N/A'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha de Compra</label>
                  <p className="text-sm text-gray-900">{formatDate(selectedSIMCard.fecha_compra)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Proveedor</label>
                  <p className="text-sm text-gray-900">{selectedSIMCard.proveedor_info?.nombre || 'N/A'}</p>
                </div>
                {selectedSIMCard.observaciones && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Observaciones</label>
                    <p className="text-sm text-gray-900">{selectedSIMCard.observaciones}</p>
                  </div>
                )}
              </div>
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowDetails(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
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