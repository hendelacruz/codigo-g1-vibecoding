import React, { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import toast from 'react-hot-toast'
import type { SIMCard } from '../inventoryTypes'
import { SIMCARD_ESTADOS, SIMCARD_PROCESOS } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'
import { useClientes, useProveedores } from '../../entities/useEntities'
import type { Cliente, ProveedorEntity } from '../../entities/entitiesTypes'
import AuthGuard from './AuthGuard'
import type { RootState } from '../../../app/store'

// Mapeo de estados para mostrar en el formulario
const ESTADO_DISPLAY_MAP = {
  'asignado': 'Asignado',
  'no_asignado': 'No Asignado'
} as const

// Mapeo de procesos para mostrar en el formulario
const PROCESO_DISPLAY_MAP = {
  'en_produccion': 'En Producción',
  'dado_de_baja': 'Dado de Baja',
  'en_almacen': 'En Almacén'
} as const

interface SIMCardFormProps {
  simCard?: SIMCard
  onSave: () => void
  onCancel: () => void
}

interface FormData {
  numero_factura: string
  numero_chip: string
  icc: string
  plan: string
  estado: SIMCard['estado']
  proceso: SIMCard['proceso']
  proveedor: number  // Cambiado de proveedor_id a proveedor
  cliente_id: number
  precio_compra: string
  fecha_compra: string
  observaciones: string
  is_active: boolean
}



export const SIMCardForm: React.FC<SIMCardFormProps> = ({ simCard, onSave, onCancel }) => {
  const { isAuthenticated, token } = useSelector((state: RootState) => state.auth)
  const { addSIMCard, editSIMCard, simCards: simCardsState } = useInventory()
  const { items: clientes, isLoading: clientesLoading, loadClientes } = useClientes()
  const { items: proveedores, isLoading: proveedoresLoading, loadProveedores } = useProveedores()
  const isEditing = !!simCard
  const isLoading = proveedoresLoading || clientesLoading
  
  const getDefaultFormData = (): FormData => ({
    numero_factura: '',
    numero_chip: '',
    icc: '',
    plan: '',
    estado: 'no_asignado',
    proceso: 'en_almacen',
    proveedor: 0,  // Cambiado de proveedor_id a proveedor
    cliente_id: 0,
    precio_compra: '',
    fecha_compra: new Date().toISOString().split('T')[0] as string,
    observaciones: '',
    is_active: true
  })

  const [formData, setFormData] = useState<FormData>(getDefaultFormData())

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Cargar proveedores y clientes al montar el componente
  useEffect(() => {
    loadProveedores()
    loadClientes()
  }, [loadProveedores, loadClientes])

  useEffect(() => {
    if (simCard) {
      setFormData({
        numero_factura: simCard.numero_factura,
        numero_chip: simCard.numero_chip,
        icc: simCard.icc,
        plan: simCard.plan || '',
        estado: simCard.estado,
        proceso: simCard.proceso,
        proveedor: simCard.proveedor_id,  // Mapear proveedor_id del SIMCard a proveedor del formulario
        cliente_id: simCard.cliente_id || 0,
        precio_compra: simCard.precio_compra ? simCard.precio_compra.toString() : '',
        fecha_compra: (simCard.fecha_compra || new Date().toISOString()).split('T')[0] as string,
        observaciones: simCard.observaciones || '',
        is_active: simCard.is_active
      })
    }
  }, [simCard])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Validaciones requeridas
    if (!formData.numero_factura.trim()) {
      newErrors.numero_factura = 'El número de factura es requerido'
    }

    if (!formData.numero_chip.trim()) {
      newErrors.numero_chip = 'El número de chip es requerido'
    } else if (formData.numero_chip.length < 9) {
      newErrors.numero_chip = 'El número de chip debe tener al menos 9 dígitos'
    }

    if (!formData.icc.trim()) {
      newErrors.icc = 'El ICC es requerido'
    } else if (formData.icc.length < 15) {
      newErrors.icc = 'El ICC debe tener al menos 15 dígitos'
    }

    if (!formData.proveedor || formData.proveedor === 0) {
      newErrors.proveedor = 'Debe seleccionar un proveedor'
    }

    if (!formData.fecha_compra) {
      newErrors.fecha_compra = 'La fecha de compra es requerida'
    }

    // Validar que la fecha no sea futura
    const fechaCompra = new Date(formData.fecha_compra)
    const hoy = new Date()
    hoy.setHours(23, 59, 59, 999) // Permitir hasta el final del día actual
    
    if (fechaCompra > hoy) {
      newErrors.fecha_compra = 'La fecha de compra no puede ser futura'
    }

    // Validar precio si se proporciona
    if (formData.precio_compra && parseFloat(formData.precio_compra) < 0) {
      newErrors.precio_compra = 'El precio no puede ser negativo'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (field: keyof FormData, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: field === 'precio_compra' && typeof value === 'number' ? value.toString() : value
    }))

    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Verificar autenticación antes de proceder
    if (!isAuthenticated || !token) {
      toast.error('Debes iniciar sesión para realizar esta acción')
      return
    }
    
    if (!validateForm()) {
      toast.error('Por favor, corrige los errores en el formulario')
      return
    }

    try {
      // Convertir precio_compra a número y preparar payload
      const payload = {
        ...formData,
        precio_compra: Number(formData.precio_compra)
      }

      let result
      if (isEditing && simCard) {
        result = await editSIMCard(simCard.id, payload)
      } else {
        result = await addSIMCard(payload)
      }

      if (result.meta.requestStatus === 'fulfilled') {
        toast.success(
          isEditing 
            ? 'Tarjeta SIM actualizada exitosamente' 
            : 'Tarjeta SIM creada exitosamente'
        )
        onSave()
      } else {
        // Manejar errores específicos del servidor
        const errorPayload = result.payload as { message?: string } | undefined;
        const errorMessage = errorPayload?.message || 'Error al procesar la solicitud'
        setErrors({ submit: errorMessage })
        toast.error(errorMessage)
      }
    } catch (error) {
      console.error('Error al guardar tarjeta SIM:', error)
      const errorMessage = 'Error inesperado al guardar la tarjeta SIM'
      setErrors({ submit: errorMessage })
      toast.error(errorMessage)
    }
  }

  const handleCancel = () => {
    setFormData(getDefaultFormData())
    setErrors({})
    onCancel()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Cargando datos...</p>
        </div>
      </div>
    )
  }

  return (
    <AuthGuard>
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {isEditing ? 'Editar Tarjeta SIM' : 'Nueva Tarjeta SIM'}
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          {isEditing ? 'Modifica la información de la tarjeta SIM' : 'Completa los datos de la nueva tarjeta SIM'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Error general */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-800 text-sm">{errors.submit}</div>
          </div>
        )}

        {/* Información de la tarjeta SIM */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información de la Tarjeta SIM</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="numero_chip" className="block text-sm font-medium text-gray-700 mb-1">
                Número de Chip *
              </label>
              <input
                type="text"
                id="numero_chip"
                value={formData.numero_chip}
                onChange={(e) => handleInputChange('numero_chip', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.numero_chip ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: 1234567890"
              />
              {errors.numero_chip && (
                <p className="mt-1 text-sm text-red-600">{errors.numero_chip}</p>
              )}
            </div>

            <div>
              <label htmlFor="icc" className="block text-sm font-medium text-gray-700 mb-1">
                ICC *
              </label>
              <input
                type="text"
                id="icc"
                value={formData.icc}
                onChange={(e) => handleInputChange('icc', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.icc ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: 123456789012345678"
              />
              {errors.icc && (
                <p className="mt-1 text-sm text-red-600">{errors.icc}</p>
              )}
            </div>



            <div>
              <label htmlFor="plan" className="block text-sm font-medium text-gray-700 mb-1">
                Plan
              </label>
              <input
                type="text"
                id="plan"
                value={formData.plan}
                onChange={(e) => handleInputChange('plan', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Plan Básico, Plan Premium"
              />
            </div>
          </div>
        </div>

        {/* Estado y Proceso */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Estado</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="estado" className="block text-sm font-medium text-gray-700 mb-1">
                Estado *
              </label>
              <select
                id="estado"
                value={formData.estado}
                onChange={(e) => handleInputChange('estado', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {SIMCARD_ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {ESTADO_DISPLAY_MAP[estado]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="proceso" className="block text-sm font-medium text-gray-700 mb-1">
                Proceso
              </label>
              <select
                id="proceso"
                value={formData.proceso}
                onChange={(e) => handleInputChange('proceso', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {SIMCARD_PROCESOS.map((proceso) => (
                  <option key={proceso} value={proceso}>
                    {PROCESO_DISPLAY_MAP[proceso]}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Información Comercial */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información Comercial</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="numero_factura" className="block text-sm font-medium text-gray-700 mb-1">
                Número de Factura *
              </label>
              <input
                type="text"
                id="numero_factura"
                value={formData.numero_factura}
                onChange={(e) => handleInputChange('numero_factura', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.numero_factura ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: FAC-001"
              />
              {errors.numero_factura && (
                <p className="mt-1 text-sm text-red-600">{errors.numero_factura}</p>
              )}
            </div>

            <div>
              <label htmlFor="proveedor" className="block text-sm font-medium text-gray-700 mb-1">
                Proveedor *
              </label>
              <select
                id="proveedor"
                value={formData.proveedor}
                onChange={(e) => handleInputChange('proveedor', Number(e.target.value))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.proveedor ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value={0}>Seleccione un proveedor</option>
                {Array.isArray(proveedores) ? proveedores.map((proveedor: ProveedorEntity) => (
                  <option key={proveedor.id} value={proveedor.id}>
                    {proveedor.nombre}
                  </option>
                )) : null}
              </select>
              {errors.proveedor && (
                <p className="mt-1 text-sm text-red-600">{errors.proveedor}</p>
              )}
            </div>

            <div>
              <label htmlFor="cliente_id" className="block text-sm font-medium text-gray-700 mb-1">
                Cliente
              </label>
              <select
                id="cliente_id"
                value={formData.cliente_id}
                onChange={(e) => handleInputChange('cliente_id', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0}>Sin asignar</option>
                {Array.isArray(clientes) ? clientes.map((cliente: Cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.nombre}
                  </option>
                )) : null}
              </select>
            </div>

            <div>
              <label htmlFor="precio_compra" className="block text-sm font-medium text-gray-700 mb-1">
                Precio de Compra *
              </label>
              <input
                type="number"
                id="precio_compra"
                step="0.01"
                min="0"
                value={formData.precio_compra}
                  onChange={(e) => handleInputChange('precio_compra', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.precio_compra ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="0.00"
              />
              {errors.precio_compra && (
                <p className="mt-1 text-sm text-red-600">{errors.precio_compra}</p>
              )}
            </div>

            <div>
              <label htmlFor="fecha_compra" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Compra *
              </label>
              <input
                type="date"
                id="fecha_compra"
                value={formData.fecha_compra}
                onChange={(e) => handleInputChange('fecha_compra', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.fecha_compra ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.fecha_compra && (
                <p className="mt-1 text-sm text-red-600">{errors.fecha_compra}</p>
              )}
            </div>
          </div>
        </div>

        {/* Estado Activo */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Estado</h3>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Tarjeta SIM activa</span>
            </label>
          </div>
        </div>

        {/* Observaciones */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Observaciones</h3>
          
          <div>
            <label htmlFor="observaciones" className="block text-sm font-medium text-gray-700 mb-1">
              Observaciones Adicionales
            </label>
            <textarea
              id="observaciones"
              rows={4}
              value={formData.observaciones}
              onChange={(e) => handleInputChange('observaciones', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Información adicional sobre la tarjeta SIM..."
            />
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={simCardsState?.isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {simCardsState?.isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
              </span>
            ) : (
              isEditing ? 'Actualizar Tarjeta SIM' : 'Crear Tarjeta SIM'
            )}
          </button>
        </div>
      </form>
    </div>
    </AuthGuard>
  )
}