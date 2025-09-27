import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import type { OtroProducto, CreateOtroProductoData } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'
import { useProveedores } from '../../entities/useEntities'

import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'
import { Select } from '../../../shared/components/ui/Select'
import { Textarea } from '../../../shared/components/ui/Textarea'

interface OtroProductoFormProps {
  producto?: OtroProducto
  onSave: () => void
  onCancel: () => void
}

interface FormData {
  fecha_compra: string
  numero_factura: string
  cantidad: string
  descripcion: string
  proveedor: number
  categoria: string
  precio_unitario: string
  precio_total: string
  stock_actual: string
  stock_minimo: string
  observaciones: string
}

// Common categories for other products
const CATEGORIAS_COMUNES = [
  'Accesorios',
  'Cables',
  'Conectores',
  'Herramientas',
  'Repuestos',
  'Consumibles',
  'Equipos',
  'Software',
  'Otros'
] as const

export const OtroProductoForm: React.FC<OtroProductoFormProps> = ({ 
  producto, 
  onSave, 
  onCancel 
}) => {
  const { addOtroProducto, editOtroProducto } = useInventory()
  const { items: proveedores, isLoading: proveedoresLoading, loadProveedores } = useProveedores()
  const isEditing = !!producto
  const isLoading = proveedoresLoading
  
  const [formData, setFormData] = useState<FormData>({
    fecha_compra: new Date().toISOString().split('T')[0] as string,
    numero_factura: '',
    cantidad: '',
    descripcion: '',
    proveedor: 0,
    categoria: '',
    precio_unitario: '',
    precio_total: '',
    stock_actual: '',
    stock_minimo: '',
    observaciones: ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Load providers on component mount
  useEffect(() => {
    loadProveedores()
  }, [loadProveedores])

  // Populate form when editing
  useEffect(() => {
    if (producto) {
      setFormData({
        fecha_compra: (producto.created_at ? producto.created_at.split('T')[0] : new Date().toISOString().split('T')[0]) as string,
        numero_factura: '', // Este campo no existe en el modelo actual, se deja vacío para edición
        cantidad: producto.stock_actual.toString(), // Usar stock_actual como cantidad inicial
        descripcion: producto.descripcion || '',
        proveedor: producto.proveedor,
        categoria: producto.categoria,
        precio_unitario: producto.precio_unitario.toString(),
        precio_total: (producto.precio_unitario * producto.stock_actual).toString(),
        stock_actual: producto.stock_actual.toString(),
        stock_minimo: producto.stock_minimo.toString(),
        observaciones: '' // Este campo no existe en el modelo actual, se deja vacío para edición
      })
    }
  }, [producto])

  const handleInputChange = (field: keyof FormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    try {
      // Convert string values to numbers for validation
      const validationData: CreateOtroProductoData = {
        fecha_compra: formData.fecha_compra,
        numero_factura: formData.numero_factura.trim(),
        cantidad: parseInt(formData.cantidad) || 0,
        descripcion: formData.descripcion.trim(),
        proveedor: formData.proveedor,
        categoria: formData.categoria,
        precio_unitario: parseFloat(formData.precio_unitario) || 0,
        precio_total: parseFloat(formData.precio_total) || 0,
        stock_actual: parseInt(formData.stock_actual) || 0,
        stock_minimo: parseInt(formData.stock_minimo) || 0,
        observaciones: formData.observaciones.trim()
      }

      // Additional business validations
      const newErrors: Record<string, string> = {}

      if (validationData.cantidad <= 0) {
        newErrors.cantidad = 'La cantidad debe ser mayor a 0'
      }

      if (validationData.stock_actual < 0) {
        newErrors.stock_actual = 'El stock actual no puede ser negativo'
      }

      if (validationData.stock_minimo < 0) {
        newErrors.stock_minimo = 'El stock mínimo no puede ser negativo'
      }

      if (validationData.precio_unitario <= 0) {
        newErrors.precio_unitario = 'El precio unitario debe ser mayor a 0'
      }

      if (validationData.precio_total <= 0) {
        newErrors.precio_total = 'El precio total debe ser mayor a 0'
      }

      if (!validationData.fecha_compra) {
        newErrors.fecha_compra = 'La fecha de compra es requerida'
      }

      if (!validationData.numero_factura.trim()) {
        newErrors.numero_factura = 'El número de factura es requerido'
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors)
        return false
      }

      setErrors({})
      return true
    } catch (error: unknown) {
      const newErrors: Record<string, string> = {}
      
      if (error && typeof error === 'object' && 'errors' in error) {
        const errorObj = error as { errors: Array<{ path: string[]; message: string }> }
        errorObj.errors.forEach((err) => {
          const field = err.path[0]
          if (field) {
            newErrors[field] = err.message
          }
        })
      }
      
      setErrors(newErrors)
      return false
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      toast.error('Por favor corrige los errores en el formulario')
      return
    }

    setIsSubmitting(true)

    try {
      // Prepare payload with proper types
      const payload: CreateOtroProductoData = {
        fecha_compra: formData.fecha_compra,
        numero_factura: formData.numero_factura.trim(),
        cantidad: parseInt(formData.cantidad),
        descripcion: formData.descripcion.trim(),
        proveedor: formData.proveedor,
        categoria: formData.categoria,
        precio_unitario: parseFloat(formData.precio_unitario),
        precio_total: parseFloat(formData.precio_total),
        stock_actual: parseInt(formData.stock_actual),
        stock_minimo: parseInt(formData.stock_minimo),
        observaciones: formData.observaciones.trim()
      }

      if (isEditing && producto) {
        await editOtroProducto(producto.id, payload)
        toast.success('Producto actualizado exitosamente')
      } else {
        await addOtroProducto(payload)
        toast.success('Producto creado exitosamente')
      }

      onSave()
    } catch (error: unknown) {
      console.error('Error saving product:', error)
      const errorMessage = error instanceof Error ? error.message : 'Error al guardar el producto'
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    // Reset form
    setFormData({
      fecha_compra: new Date().toISOString().split('T')[0] as string,
      numero_factura: '',
      cantidad: '',
      descripcion: '',
      proveedor: 0,
      categoria: '',
      precio_unitario: '',
      precio_total: '',
      stock_actual: '',
      stock_minimo: '',
      observaciones: ''
    })
    setErrors({})
    onCancel()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-600">Cargando...</div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-sm">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {isEditing ? 'Editar Producto' : 'Nuevo Producto'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Fecha de Compra */}
        <div>
          <label htmlFor="fecha_compra" className="block text-sm font-medium text-gray-700 mb-2">
            Fecha de Compra *
          </label>
          <Input
            id="fecha_compra"
            type="date"
            value={formData.fecha_compra}
            onChange={(e) => handleInputChange('fecha_compra', e.target.value)}
            error={errors.fecha_compra ?? ''}
            required
          />
        </div>

        {/* Número de Factura */}
        <div>
          <label htmlFor="numero_factura" className="block text-sm font-medium text-gray-700 mb-2">
            Número de Factura *
          </label>
          <Input
            id="numero_factura"
            type="text"
            value={formData.numero_factura}
            onChange={(e) => handleInputChange('numero_factura', e.target.value)}
            placeholder="Ej: F001-2024-002"
            error={errors.numero_factura ?? ''}
            required
          />
        </div>

        {/* Cantidad */}
        <div>
          <label htmlFor="cantidad" className="block text-sm font-medium text-gray-700 mb-2">
            Cantidad *
          </label>
          <Input
            id="cantidad"
            type="number"
            min="1"
            value={formData.cantidad}
            onChange={(e) => handleInputChange('cantidad', e.target.value)}
            placeholder="Ej: 50"
            error={errors.cantidad ?? ''}
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-2">
            Descripción *
          </label>
          <Textarea
            id="descripcion"
            value={formData.descripcion}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('descripcion', e.target.value)}
            placeholder="Descripción detallada del producto..."
            rows={3}
            error={errors.descripcion ?? ''}
            required
          />
        </div>

        {/* Category */}
        <div>
          <label htmlFor="categoria" className="block text-sm font-medium text-gray-700 mb-2">
            Categoría *
          </label>
          <Select
            id="categoria"
            value={formData.categoria}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleInputChange('categoria', e.target.value)}
            error={errors.categoria ?? ''}
            required
          >
            <option value="">Seleccionar categoría</option>
            {CATEGORIAS_COMUNES.map((categoria) => (
              <option key={categoria} value={categoria}>
                {categoria}
              </option>
            ))}
          </Select>
        </div>

        {/* Provider */}
        <div>
          <label htmlFor="proveedor" className="block text-sm font-medium text-gray-700 mb-2">
            Proveedor *
          </label>
          <Select
            id="proveedor"
            value={formData.proveedor}
            onChange={(e) => handleInputChange('proveedor', parseInt(e.target.value))}
            error={errors.proveedor ?? ''}
            required
          >
            <option value={0}>Seleccionar proveedor</option>
            {proveedores?.map((proveedor) => (
              <option key={proveedor.id} value={proveedor.id}>
                {proveedor.nombre}
              </option>
            ))}
          </Select>
        </div>

        {/* Price and Stock Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Unit Price */}
          <div>
            <label htmlFor="precio_unitario" className="block text-sm font-medium text-gray-700 mb-2">
              Precio Unitario *
            </label>
            <Input
              id="precio_unitario"
              type="number"
              step="0.01"
              min="0"
              value={formData.precio_unitario}
              onChange={(e) => handleInputChange('precio_unitario', e.target.value)}
              placeholder="0.00"
              error={errors.precio_unitario ?? ''}
              required
            />
          </div>

          {/* Total Price */}
          <div>
            <label htmlFor="precio_total" className="block text-sm font-medium text-gray-700 mb-2">
              Precio Total *
            </label>
            <Input
              id="precio_total"
              type="number"
              step="0.01"
              min="0"
              value={formData.precio_total}
              onChange={(e) => handleInputChange('precio_total', e.target.value)}
              placeholder="0.00"
              error={errors.precio_total ?? ''}
              required
            />
          </div>
        </div>

        {/* Stock Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Current Stock */}
          <div>
            <label htmlFor="stock_actual" className="block text-sm font-medium text-gray-700 mb-2">
              Stock Actual *
            </label>
            <Input
              id="stock_actual"
              type="number"
              min="0"
              value={formData.stock_actual}
              onChange={(e) => handleInputChange('stock_actual', e.target.value)}
              placeholder="0"
              error={errors.stock_actual ?? ''}
              required
            />
          </div>

          {/* Minimum Stock */}
          <div>
            <label htmlFor="stock_minimo" className="block text-sm font-medium text-gray-700 mb-2">
              Stock Mínimo *
            </label>
            <Input
              id="stock_minimo"
              type="number"
              min="0"
              value={formData.stock_minimo}
              onChange={(e) => handleInputChange('stock_minimo', e.target.value)}
              placeholder="0"
              error={errors.stock_minimo ?? ''}
              required
            />
          </div>
        </div>

        {/* Observaciones */}
        <div>
          <label htmlFor="observaciones" className="block text-sm font-medium text-gray-700 mb-2">
            Observaciones
          </label>
          <Textarea
            id="observaciones"
            value={formData.observaciones}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('observaciones', e.target.value)}
            placeholder="Observaciones adicionales sobre el producto..."
            rows={3}
            error={errors.observaciones ?? ''}
          />
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
          <Button
            type="button"
            variant="secondary"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="default"
            disabled={isSubmitting}
            isLoading={isSubmitting}
          >
            {isEditing ? 'Actualizar' : 'Crear'} Producto
          </Button>
        </div>
      </form>
    </div>
  )
}