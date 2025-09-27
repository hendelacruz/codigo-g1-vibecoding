import { useState, useCallback, memo } from 'react'
import { ServiceTypeSelect } from '../shared/ServiceTypeSelect'
import { ESTADO_SERVICIO_CHOICES, type EstadoChoice } from '../../../shared/utils/services/serviceConstants'
import type { ServicioFilters as ServicioFiltersType } from '../../../shared/types/services/servicio'

interface ServicioFiltersProps {
  filters: ServicioFiltersType
  onFiltersChange: (filters: ServicioFiltersType) => void
  className?: string
}

export const ServicioFilters = memo<ServicioFiltersProps>(({
  filters,
  onFiltersChange,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // Handle filter changes with proper type safety
  const handleFilterChange = useCallback((
    field: keyof ServicioFiltersType,
    value: string | undefined
  ) => {
    onFiltersChange({
      ...filters,
      [field]: value || undefined
    })
  }, [filters, onFiltersChange])

  // Clear all filters
  const handleClearFilters = useCallback(() => {
    onFiltersChange({})
  }, [onFiltersChange])

  // Check if any filters are active
  const hasActiveFilters = Object.values(filters).some(value => 
    value !== undefined && value !== ''
  )

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}>
      {/* Main search bar */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Buscar servicios..."
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`flex items-center gap-2 px-4 py-2 border rounded-md transition-colors ${
            isExpanded 
              ? 'bg-blue-50 border-blue-300 text-blue-700' 
              : 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100'
          }`}
          aria-expanded={isExpanded}
          aria-label="Toggle advanced filters"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filtros
        </button>

        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
            aria-label="Clear all filters"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Limpiar
          </button>
        )}
      </div>

      {/* Expandable filters */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
          {/* Service Status Filter */}
          <div className="space-y-2">
            <label htmlFor="estado-filter" className="block text-sm font-medium text-gray-700">
              Estado
            </label>
            <select
              id="estado-filter"
              value={filters.estado_servicio || ''}
              onChange={(e) => handleFilterChange('estado_servicio', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              {ESTADO_SERVICIO_CHOICES.map((estado: EstadoChoice) => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
          </div>

          {/* Service Type Filter */}
          <div className="space-y-2">
            <label htmlFor="tipo-trabajo-filter" className="block text-sm font-medium text-gray-700">
              Tipo de Trabajo
            </label>
            <ServiceTypeSelect
              value={filters.tipo_trabajo?.toString() || ''}
              onChange={(value) => handleFilterChange('tipo_trabajo', value)}
              placeholder="Todos los tipos"
              className="w-full"
            />
          </div>

          {/* Date From Filter */}
          <div className="space-y-2">
            <label htmlFor="fecha-desde-filter" className="block text-sm font-medium text-gray-700">
              Fecha Desde
            </label>
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <input
                id="fecha-desde-filter"
                type="date"
                value={filters.fecha_desde || ''}
                onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Date To Filter */}
          <div className="space-y-2">
            <label htmlFor="fecha-hasta-filter" className="block text-sm font-medium text-gray-700">
              Fecha Hasta
            </label>
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <input
                id="fecha-hasta-filter"
                type="date"
                value={filters.fecha_hasta || ''}
                onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
})

ServicioFilters.displayName = 'ServicioFilters'