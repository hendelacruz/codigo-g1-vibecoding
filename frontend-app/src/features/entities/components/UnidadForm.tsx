import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import type { UnidadVehicular, CreateUnidadData, UpdateUnidadData } from '../entitiesTypes'
import { TIPO_VEHICULO_OPTIONS } from '../entitiesTypes'
import { useEntities } from '../useEntities'

interface UnidadFormProps {
  unidad?: UnidadVehicular
  onSave: () => void
  onCancel: () => void
}

export const UnidadForm: React.FC<UnidadFormProps> = ({ unidad, onSave, onCancel }) => {
  const { clientes, unidades, addUnidad, editUnidad, loadClientesActivos } = useEntities()
  
  const [formData, setFormData] = useState<CreateUnidadData>({
    placa: '',
    marca: '',
    modelo: '',
    tipo: 'bus',
    serie: '',
    cliente_id: 0,  // Consistent with backend API
    is_active: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoadingClientes, setIsLoadingClientes] = useState(false)

  // Load active clients when component mounts
  useEffect(() => {
    const loadData = async () => {
      if (clientes.items.length === 0) {
        setIsLoadingClientes(true)
        try {
          await loadClientesActivos()
        } catch (error) {
          console.error('❌ UnidadForm: Error loading active clients:', error)
          toast.error('Error al cargar la lista de clientes')
        } finally {
          setIsLoadingClientes(false)
        }
      }
    }
    
    loadData()
  }, [loadClientesActivos, clientes.items.length])

  // Update form data when editing
  useEffect(() => {
    if (unidad) {
      setFormData({
        placa: unidad.placa,
        marca: unidad.marca,
        modelo: unidad.modelo,
        tipo: unidad.tipo,
        serie: unidad.serie,
        cliente_id: unidad.cliente_id,  // Direct mapping - no conversion needed
        is_active: unidad.is_active
      })
    }
  }, [unidad])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Validate placa
    if (!formData.placa.trim()) {
      newErrors.placa = 'La placa es requerida'
    } else if (!/^[A-Z]{3}-\d{3,4}$/.test(formData.placa)) {
      newErrors.placa = 'Formato de placa inválido (ej: ABC-123 o ABC-1234)'
    }

    // Validate marca
    if (!formData.marca.trim()) {
      newErrors.marca = 'La marca es requerida'
    }

    // Validate modelo
    if (!formData.modelo.trim()) {
      newErrors.modelo = 'El modelo es requerido'
    }

    // Validate serie
    if (!formData.serie.trim()) {
      newErrors.serie = 'La serie es requerida'
    }

    // Validate cliente_id (cliente)
    if (!formData.cliente_id || formData.cliente_id === 0) {
      newErrors.cliente_id = 'Debe seleccionar un cliente'
    } else {
      // Verify that the selected client exists and is active
      const selectedCliente = clientes.items.find(c => c.id === formData.cliente_id && c.is_active)
      if (!selectedCliente) {
        newErrors.cliente_id = 'El cliente seleccionado no es válido o no está activo'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      if (unidad) {
        // Update existing unidad
        const updateData: UpdateUnidadData = { ...formData }
        await editUnidad(unidad.id, updateData)
        toast.success('Unidad actualizada exitosamente')
      } else {
        // Create new unidad
        await addUnidad(formData)
        toast.success('Unidad creada exitosamente')
      }
      
      onSave()
    } catch (error) {
      console.error('Error saving unidad:', error)
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
      toast.error(`Error al ${unidad ? 'actualizar' : 'crear'} la unidad: ${errorMessage}`)
    }
  }

  const handleInputChange = (field: keyof CreateUnidadData, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }



  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {unidad ? 'Editar Unidad Vehicular' : 'Nueva Unidad Vehicular'}
        </h2>
        <p className="text-gray-600">
          {unidad ? 'Modifica los datos de la unidad vehicular' : 'Completa los datos para registrar una nueva unidad vehicular'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Placa */}
        <div>
          <label htmlFor="placa" className="block text-sm font-medium text-gray-700 mb-1">
            Placa *
          </label>
          <input
            type="text"
            id="placa"
            value={formData.placa}
            onChange={(e) => handleInputChange('placa', e.target.value.toUpperCase())}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.placa ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Ej: ABC123"
            maxLength={10}
          />
          {errors.placa && <p className="mt-1 text-sm text-red-600">{errors.placa}</p>}
        </div>

        {/* Marca y Modelo */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="marca" className="block text-sm font-medium text-gray-700 mb-1">
              Marca *
            </label>
            <input
              type="text"
              id="marca"
              value={formData.marca}
              onChange={(e) => handleInputChange('marca', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.marca ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Ej: Toyota"
            />
            {errors.marca && <p className="mt-1 text-sm text-red-600">{errors.marca}</p>}
          </div>

          <div>
            {/* Modelo */}
            <div>
              <label htmlFor="modelo" className="block text-sm font-medium text-gray-700 mb-1">
                Modelo *
              </label>
              <input
                type="text"
                id="modelo"
                value={formData.modelo}
                onChange={(e) => handleInputChange('modelo', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.modelo ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ej: Corolla"
              />
              {errors.modelo && <p className="mt-1 text-sm text-red-600">{errors.modelo}</p>}
            </div>

            {/* Serie */}
            <div>
              <label htmlFor="serie" className="block text-sm font-medium text-gray-700 mb-1">
                Serie *
              </label>
              <input
                type="text"
                id="serie"
                value={formData.serie}
                onChange={(e) => handleInputChange('serie', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.serie ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ej: ABC123456789"
              />
              {errors.serie && <p className="mt-1 text-sm text-red-600">{errors.serie}</p>}
            </div>
          </div>
        </div>

        {/* Tipo de Vehículo */}
        <div>
          <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Vehículo *
          </label>
          <select
            id="tipo"
            value={formData.tipo}
            onChange={(e) => handleInputChange('tipo', e.target.value as UnidadVehicular['tipo'])}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.tipo ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            {TIPO_VEHICULO_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.tipo && <p className="mt-1 text-sm text-red-600">{errors.tipo}</p>}
        </div>

        {/* Cliente */}
        <div>
          <label htmlFor="cliente_id" className="block text-sm font-medium text-gray-700 mb-1">
            Cliente *
          </label>
          <select
            id="cliente_id"
            value={formData.cliente_id}
            onChange={(e) => handleInputChange('cliente_id', parseInt(e.target.value))}
            disabled={isLoadingClientes || clientes.isLoading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.cliente_id ? 'border-red-500' : 'border-gray-300'
            } ${(isLoadingClientes || clientes.isLoading) ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          >
            <option value={0}>
              {isLoadingClientes || clientes.isLoading ? 'Cargando clientes...' : 'Seleccionar cliente'}
            </option>
            {clientes.items.filter(c => c.is_active).map(cliente => (
              <option key={cliente.id} value={cliente.id}>
                {cliente.nombre} {cliente.ruc ? `(${cliente.ruc})` : ''}
              </option>
            ))}
          </select>
          {errors.cliente_id && <p className="mt-1 text-sm text-red-600">{errors.cliente_id}</p>}
          {clientes.items.filter(c => c.is_active).length === 0 && !isLoadingClientes && !clientes.isLoading && (
            <p className="mt-1 text-sm text-amber-600">
              No hay clientes activos disponibles. Debe crear un cliente primero.
            </p>
          )}
        </div>

        {/* Estado */}
        <div>
          <label htmlFor="is_active" className="block text-sm font-medium text-gray-700 mb-1">
            Estado *
          </label>
          <select
            id="is_active"
            value={formData.is_active?.toString() ?? 'true'}
            onChange={(e) => handleInputChange('is_active', e.target.value === 'true')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
          </select>
        </div>



        {/* Buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            disabled={unidades.isLoading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={unidades.isLoading}
          >
            {unidades.isLoading ? 'Guardando...' : unidad ? 'Actualizar' : 'Crear'}
          </button>
        </div>
      </form>
    </div>
  )
}