import React, { useState, useEffect } from 'react'
import type { ProveedorEntity, CreateProveedorData, UpdateProveedorData } from '../entitiesTypes'
import { useEntities } from '../useEntities'
import { updateProveedorSchema, type UpdateProveedorFormData } from '../../../shared/lib/validations'
import { ZodError } from 'zod'

interface ProveedorFormProps {
  proveedor?: ProveedorEntity
  onSave: () => void
  onCancel: () => void
}

export const ProveedorForm: React.FC<ProveedorFormProps> = ({ 
  proveedor, 
  onSave, 
  onCancel 
}) => {
  const { addProveedor, editProveedor, proveedores } = useEntities()
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    nombre: '',
    ruc: '',
    celular: '',
    correo: '',
    direccion: '',
    is_active: true
  })

  // Update form data when editing
  useEffect(() => {
    if (proveedor) {
      setFormData({
        nombre: proveedor.nombre,
        ruc: proveedor.ruc || '',
        celular: proveedor.celular || '',
        correo: proveedor.correo || '',
        direccion: proveedor.direccion || '',
        is_active: proveedor.is_active
      })
    }
  }, [proveedor])

  const validateForm = (): boolean => {
    try {
      // Prepare data for validation (only include non-empty fields)
      const dataToValidate: Partial<UpdateProveedorFormData> = {}
      
      if (formData.nombre.trim()) dataToValidate.nombre = formData.nombre.trim()
      if (formData.ruc.trim()) dataToValidate.ruc = formData.ruc.trim()
      if (formData.celular.trim()) dataToValidate.celular = formData.celular.trim()
      if (formData.correo.trim()) dataToValidate.correo = formData.correo.trim()
      if (formData.direccion.trim()) dataToValidate.direccion = formData.direccion.trim()
      
      // Validate using Zod schema
      updateProveedorSchema.parse(dataToValidate)
      
      // Additional required field validation
      const newErrors: Record<string, string> = {}
      if (!formData.nombre.trim()) {
        newErrors.nombre = 'El nombre es requerido'
      }
      
      setErrors(newErrors)
      return Object.keys(newErrors).length === 0
    } catch (error) {
       if (error instanceof ZodError) {
         const newErrors: Record<string, string> = {}
         error.issues.forEach((issue) => {
           if (issue.path.length > 0) {
             newErrors[issue.path[0] as string] = issue.message
           }
         })
         setErrors(newErrors)
         return false
       }
       
       // Fallback for unexpected errors
       setErrors({ submit: 'Error de validación inesperado' })
       return false
     }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      if (proveedor) {
        // Update existing proveedor
        const updateData: UpdateProveedorData = {
          nombre: formData.nombre,
          is_active: formData.is_active,
          ...(formData.ruc && { ruc: formData.ruc }),
          ...(formData.celular && { celular: formData.celular }),
          ...(formData.correo && { correo: formData.correo }),
          ...(formData.direccion && { direccion: formData.direccion })
        }
        await editProveedor(proveedor.id, updateData)
      } else {
        // Create new proveedor
        const createData: CreateProveedorData = {
          nombre: formData.nombre,
          is_active: formData.is_active,
          ...(formData.ruc && { ruc: formData.ruc }),
          ...(formData.celular && { celular: formData.celular }),
          ...(formData.correo && { correo: formData.correo }),
          ...(formData.direccion && { direccion: formData.direccion })
        }
        await addProveedor(createData)
      }
      onSave()
    } catch (error: unknown) {
      console.error('Error al guardar proveedor:', error)
      
      // Handle specific validation errors from backend
      const errorMessage = error && typeof error === 'object' && 'message' in error && 
                          typeof error.message === 'string' ? error.message : null
      
      if (errorMessage && errorMessage.includes('Errores de validación:')) {
        const validationErrors: Record<string, string> = {}
        const errorLines = errorMessage.split('\n').slice(1) // Skip the "Errores de validación:" line
        
        errorLines.forEach((line: string) => {
          const [field, message] = line.split(': ', 2)
          if (field && message) {
            validationErrors[field] = message
          }
        })
        
        if (Object.keys(validationErrors).length > 0) {
          setErrors(validationErrors)
          return
        }
      }
      
      // Handle other specific error messages
      if (errorMessage) {
        if (errorMessage.includes('RUC')) {
          setErrors({ ruc: errorMessage })
        } else if (errorMessage.includes('celular')) {
          setErrors({ celular: errorMessage })
        } else if (errorMessage.includes('correo') || errorMessage.includes('email')) {
          setErrors({ correo: errorMessage })
        } else {
          setErrors({ submit: errorMessage })
        }
      } else {
        setErrors({ submit: 'Error al guardar el proveedor. Inténtelo nuevamente.' })
      }
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow border">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          {proveedor ? 'Editar Proveedor' : 'Nuevo Proveedor'}
        </h2>
        <p className="text-gray-600">
          {proveedor ? 'Modifica los datos del proveedor' : 'Completa los datos del nuevo proveedor'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nombre */}
        <div>
          <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-1">
            Nombre *
          </label>
          <input
            type="text"
            id="nombre"
            value={formData.nombre}
            onChange={(e) => handleInputChange('nombre', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.nombre ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Ingrese el nombre del proveedor"
          />
          {errors.nombre && (
            <p className="mt-1 text-sm text-red-600">{errors.nombre}</p>
          )}
        </div>

        {/* RUC */}
        <div>
          <label htmlFor="ruc" className="block text-sm font-medium text-gray-700 mb-1">
            RUC
          </label>
          <input
            type="text"
            id="ruc"
            value={formData.ruc}
            onChange={(e) => handleInputChange('ruc', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.ruc ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Ingrese el RUC (11 dígitos)"
            maxLength={11}
          />
          {errors.ruc && (
            <p className="mt-1 text-sm text-red-600">{errors.ruc}</p>
          )}
        </div>

        {/* Celular */}
        <div>
          <label htmlFor="celular" className="block text-sm font-medium text-gray-700 mb-1">
            Celular
          </label>
          <input
            type="tel"
            id="celular"
            value={formData.celular}
            onChange={(e) => handleInputChange('celular', e.target.value)}
            placeholder="Ingrese el celular"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.celular ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.celular && (
            <p className="mt-1 text-sm text-red-600">{errors.celular}</p>
          )}
        </div>

        {/* Correo */}
        <div>
          <label htmlFor="correo" className="block text-sm font-medium text-gray-700 mb-1">
            Correo Electrónico
          </label>
          <input
            type="email"
            id="correo"
            value={formData.correo}
            onChange={(e) => handleInputChange('correo', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.correo ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Ingrese el correo electrónico"
          />
          {errors.correo && (
            <p className="mt-1 text-sm text-red-600">{errors.correo}</p>
          )}
        </div>

        {/* Dirección */}
        <div>
          <label htmlFor="direccion" className="block text-sm font-medium text-gray-700 mb-1">
            Dirección
          </label>
          <textarea
            id="direccion"
            value={formData.direccion}
            onChange={(e) => handleInputChange('direccion', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ingrese la dirección del proveedor"
          />
        </div>

        {/* Estado */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => handleInputChange('is_active', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">Proveedor activo</span>
          </label>
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={proveedores.isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {proveedores.isLoading ? 'Guardando...' : (proveedor ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>
    </div>
  )
}