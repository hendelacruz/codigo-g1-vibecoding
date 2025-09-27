import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import type { GPS } from '../inventoryTypes'
import { GPS_ESTADOS, GPS_PROCESOS } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'
import { useClientes, useProveedores } from '../../entities/useEntities'
import type { Cliente, ProveedorEntity } from '../../entities/entitiesTypes'

// Mapeo para mostrar valores amigables al usuario
const ESTADO_DISPLAY_MAP = {
  'asignado': 'Asignado',
  'no_asignado': 'No Asignado'
} as const

interface GPSFormProps {
  gps?: GPS
  onSave: () => void
  onCancel: () => void
}

interface FormData {
  imei: string
  modelo: string
  marca: string
  numero_factura: string
  estado: GPS['estado']
  proceso: GPS['proceso']
  proveedor: number
  cliente: number
  precio_compra: number
  fecha_compra: string
  observaciones: string
}

// Payload type for API calls - cliente is optional
type GPSPayload = Omit<FormData, 'cliente'> & {
  cliente?: number
}

export const GPSForm: React.FC<GPSFormProps> = ({ gps, onSave, onCancel }) => {
  
  const { addGPS, editGPS, gps: gpsState } = useInventory()
  const { items: clientes, isLoading: clientesLoading, loadClientes } = useClientes()
  const { items: proveedores, isLoading: proveedoresLoading, loadProveedores } = useProveedores()
  const isEditing = !!gps
  const isLoading = proveedoresLoading || clientesLoading
  
  const [formData, setFormData] = useState<FormData>({
    imei: '',
    modelo: '',
    marca: '',
    numero_factura: '',
    estado: 'no_asignado',
    proceso: 'en_produccion',
    proveedor: 0,
    cliente: 0,
    precio_compra: 0,
    fecha_compra: new Date().toISOString().split('T')[0] as string,
    observaciones: ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Cargar proveedores y clientes al montar el componente
  useEffect(() => {
    loadProveedores()
    loadClientes()
  }, [loadProveedores, loadClientes])

  useEffect(() => {
    if (gps) {
      setFormData({
        imei: gps.imei,
        modelo: gps.modelo,
        marca: gps.marca,
        numero_factura: gps.numero_factura || '',
        estado: gps.estado,
        proceso: gps.proceso,
        proveedor: gps.proveedor,
        cliente: gps.cliente || 0,
        precio_compra: gps.precio_compra || 0,
        fecha_compra: gps.fecha_compra.split('T')[0] as string,
        observaciones: gps.observaciones || ''
      })
    }
  }, [gps])

  const handleInputChange = (field: keyof FormData, value: string | number) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value }
      
      // Auto-manage estado based on cliente assignment (business rule enforcement)
      if (field === 'cliente') {
        if (value !== 0 && newData.estado !== 'asignado') {
          // Client assigned: change estado to 'asignado'
          newData.estado = 'asignado'
          toast('Estado cambiado automáticamente a "asignado" porque se seleccionó un cliente', {
            icon: 'ℹ️',
          })
        } else if (value === 0 && newData.estado === 'asignado') {
          // Client removed: change estado to 'no_asignado'
          newData.estado = 'no_asignado'
          toast('Estado cambiado automáticamente a "no asignado" porque se quitó el cliente', {
            icon: 'ℹ️',
          })
        }
      }
      
      return newData
    })
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
    
    // Clear estado error if it was automatically fixed
    if (field === 'cliente' && errors.estado) {
      setErrors(prev => ({ ...prev, estado: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Required field validation
    if (!formData.imei.trim()) {
      newErrors.imei = 'El IMEI es requerido'
    } else if (formData.imei.length < 15) {
      newErrors.imei = 'El IMEI debe tener al menos 15 caracteres'
    }

    if (!formData.modelo.trim()) {
      newErrors.modelo = 'El modelo es requerido'
    }

    if (!formData.marca.trim()) {
      newErrors.marca = 'La marca es requerida'
    }

    if (formData.proveedor === 0) {
      newErrors.proveedor = 'Debe seleccionar un proveedor'
    }

    if (formData.precio_compra <= 0) {
      newErrors.precio_compra = 'El precio de compra debe ser mayor a 0'
    }

    if (!formData.fecha_compra) {
      newErrors.fecha_compra = 'La fecha de compra es requerida'
    }

    // Business rule validation for estado and cliente consistency
    if (formData.cliente !== 0 && formData.estado !== 'asignado') {
      newErrors.estado = 'Un GPS con cliente asociado debe tener estado "asignado"'
    } else if (formData.cliente === 0 && formData.estado === 'asignado') {
      newErrors.estado = 'Un GPS sin cliente no puede tener estado "asignado"'
    } else if (formData.cliente === 0 && formData.estado !== 'no_asignado') {
      newErrors.estado = 'Un GPS sin cliente debe tener estado "no asignado"'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setErrors(prev => ({ ...prev, submit: '' })) // Clear previous submit errors
    
    try {
      // Prepare payload - exclude cliente when no client is assigned
      const payload: GPSPayload = {
        imei: formData.imei,
        modelo: formData.modelo,
        marca: formData.marca,
        numero_factura: formData.numero_factura,
        estado: formData.estado,
        proceso: formData.proceso,
        proveedor: formData.proveedor,
        precio_compra: formData.precio_compra,
        fecha_compra: formData.fecha_compra,
        observaciones: formData.observaciones,
        ...(formData.cliente !== 0 && { cliente: formData.cliente })
      }

      if (isEditing && gps) {
        const result = await editGPS(gps.id, payload)
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success('GPS actualizado exitosamente')
          onSave()
        } else {
          // Handle specific backend errors
          const errorMessage = result.payload as string || gpsState.error || 'Error al actualizar GPS'
          console.error('Error al actualizar GPS:', errorMessage)
          setErrors(prev => ({ ...prev, submit: errorMessage }))
          toast.error(errorMessage)
        }
      } else {
        const result = await addGPS(payload)
        if (result.meta.requestStatus === 'fulfilled') {
          toast.success('GPS creado exitosamente')
          onSave()
        } else {
          // Handle specific backend errors
          const errorMessage = result.payload as string || gpsState.error || 'Error al crear GPS'
          console.error('Error al crear GPS:', errorMessage)
          setErrors(prev => ({ ...prev, submit: errorMessage }))
          toast.error(errorMessage)
        }
      }
    } catch (error) {
      console.error('Error en handleSubmit:', error)
      const errorMessage = error instanceof Error ? error.message : 'Error inesperado'
      setErrors(prev => ({ ...prev, submit: errorMessage }))
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {isEditing ? 'Editar Dispositivo GPS' : 'Nuevo Dispositivo GPS'}
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          {isEditing ? 'Modifica la información del dispositivo GPS' : 'Completa los datos del nuevo dispositivo GPS'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Error general */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-800 text-sm">{errors.submit}</div>
          </div>
        )}

        {/* Información del dispositivo */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información del Dispositivo</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="imei" className="block text-sm font-medium text-gray-700 mb-1">
                IMEI *
              </label>
              <input
                type="text"
                id="imei"
                value={formData.imei}
                onChange={(e) => handleInputChange('imei', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.imei ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ingrese el IMEI del dispositivo"
              />
              {errors.imei && (
                <p className="mt-1 text-sm text-red-600">{errors.imei}</p>
              )}
            </div>

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
                  errors.modelo ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ingrese el modelo"
              />
              {errors.modelo && (
                <p className="mt-1 text-sm text-red-600">{errors.modelo}</p>
              )}
            </div>

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
                  errors.marca ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ingrese la marca"
              />
              {errors.marca && (
                <p className="mt-1 text-sm text-red-600">{errors.marca}</p>
              )}
            </div>

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
                {GPS_ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {ESTADO_DISPLAY_MAP[estado]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="proceso" className="block text-sm font-medium text-gray-700 mb-1">
                Proceso *
              </label>
              <select
                id="proceso"
                value={formData.proceso}
                onChange={(e) => handleInputChange('proceso', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {GPS_PROCESOS.map((proceso) => (
                  <option key={proceso} value={proceso}>
                    {proceso.charAt(0).toUpperCase() + proceso.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Información de compra */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información de Compra</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <label htmlFor="cliente" className="block text-sm font-medium text-gray-700 mb-1">
                Cliente Asignado
              </label>
              <select
                id="cliente"
                value={formData.cliente}
                onChange={(e) => handleInputChange('cliente', Number(e.target.value))}
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
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="precio_compra" className="block text-sm font-medium text-gray-700 mb-1">
                Precio de Compra *
              </label>
              <input
                type="number"
                id="precio_compra"
                value={formData.precio_compra === 0 ? '' : formData.precio_compra}
                onChange={(e) => handleInputChange('precio_compra', parseFloat(e.target.value) || 0)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.precio_compra ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="0.00"
                min="0"
                step="0.01"
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

            <div>
              <label htmlFor="numero_factura" className="block text-sm font-medium text-gray-700 mb-1">
                Número de Factura
              </label>
              <input
                type="text"
                id="numero_factura"
                value={formData.numero_factura}
                onChange={(e) => handleInputChange('numero_factura', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ingrese el número de factura"
              />
            </div>
          </div>
        </div>

        {/* Observaciones */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Observaciones</h3>
          
          <div>
            <label htmlFor="observaciones" className="block text-sm font-medium text-gray-700 mb-1">
              Observaciones adicionales
            </label>
            <textarea
              id="observaciones"
              value={formData.observaciones}
              onChange={(e) => handleInputChange('observaciones', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ingrese observaciones adicionales sobre el dispositivo"
            />
          </div>
        </div>

        {/* Botones */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || isSubmitting}
          >
            {isLoading || isSubmitting ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>
    </div>
  )
}