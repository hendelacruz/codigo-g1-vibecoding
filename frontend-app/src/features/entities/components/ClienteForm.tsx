import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import type { Cliente, CreateClienteData, UpdateClienteData } from '../entitiesTypes'
import { useEntities } from '../useEntities'

interface ClienteFormProps {
  cliente?: Cliente
  onSave: () => void
  onCancel: () => void
}

interface FormData {
  nombre: string
  ruc: string
  direccion: string
  contacto: string
  celular: string
  correo: string
  is_active: boolean
}

export const ClienteForm: React.FC<ClienteFormProps> = ({ cliente, onSave, onCancel }) => {
  const { addCliente, editCliente, clientes } = useEntities()
  const isEditing = !!cliente
  
  const [formData, setFormData] = useState<FormData>({
    nombre: '',
    ruc: '',
    direccion: '',
    contacto: '',
    celular: '',
    correo: '',
    is_active: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (cliente) {
      setFormData({
        nombre: cliente.nombre,
        ruc: cliente.ruc || '',
        direccion: cliente.direccion || '',
        contacto: cliente.contacto || '',
        celular: cliente.celular || '',
        correo: cliente.correo || '',
        is_active: cliente.is_active
      })
    }
  }, [cliente])

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Required field validation
    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido'
    }

    // Email validation
    if (formData.correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
      newErrors.correo = 'El formato del correo no es válido'
    }

    // RUC validation (basic)
    if (formData.ruc && formData.ruc.length !== 11) {
      newErrors.ruc = 'El RUC debe tener 11 dígitos'
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
      if (isEditing && cliente) {
        const updateData: UpdateClienteData = {
          nombre: formData.nombre,
          is_active: formData.is_active
        }
        
        if (formData.ruc.trim()) updateData.ruc = formData.ruc
        if (formData.direccion.trim()) updateData.direccion = formData.direccion
        if (formData.contacto.trim()) updateData.contacto = formData.contacto
        if (formData.celular.trim()) updateData.celular = formData.celular
        if (formData.correo.trim()) updateData.correo = formData.correo
        await editCliente(cliente.id, updateData)
        toast.success(`Cliente "${formData.nombre}" actualizado exitosamente`)
      } else {
        const createData: CreateClienteData = {
          nombre: formData.nombre
        }
        
        if (formData.ruc.trim()) createData.ruc = formData.ruc
        if (formData.direccion.trim()) createData.direccion = formData.direccion
        if (formData.contacto.trim()) createData.contacto = formData.contacto
        if (formData.celular.trim()) createData.celular = formData.celular
        if (formData.correo.trim()) createData.correo = formData.correo
        await addCliente(createData)
        toast.success(`Cliente "${formData.nombre}" creado exitosamente`)
      }
      
      onSave()
    } catch (error) {
      console.error('Error al guardar cliente:', error)
      toast.error('Error al guardar el cliente. Inténtelo de nuevo.')
      setErrors({ submit: 'Error al guardar el cliente. Inténtelo de nuevo.' })
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          {isEditing ? 'Modifica la información del cliente' : 'Completa los datos del nuevo cliente'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Error general */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-800 text-sm">{errors.submit}</div>
          </div>
        )}

        {/* Información básica */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información Básica</h3>
          
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
                errors.nombre ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Ingrese el nombre del cliente"
            />
            {errors.nombre && (
              <p className="mt-1 text-sm text-red-600">{errors.nombre}</p>
            )}
          </div>

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
                errors.ruc ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Ingrese el RUC (11 dígitos)"
              maxLength={11}
            />
            {errors.ruc && (
              <p className="mt-1 text-sm text-red-600">{errors.ruc}</p>
            )}
          </div>
        </div>

        {/* Información de contacto */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Información de Contacto</h3>
          
          <div>
            <label htmlFor="contacto" className="block text-sm font-medium text-gray-700 mb-1">
              Contacto
            </label>
            <input
              type="text"
              id="contacto"
              value={formData.contacto}
              onChange={(e) => handleInputChange('contacto', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nombre de la persona de contacto"
            />
          </div>

          <div>
            <label htmlFor="celular" className="block text-sm font-medium text-gray-700 mb-1">
              Celular
            </label>
            <input
              type="tel"
              id="celular"
              value={formData.celular}
              onChange={(e) => handleInputChange('celular', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ingrese el número de celular"
            />
          </div>

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
                errors.correo ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="correo@ejemplo.com"
            />
            {errors.correo && (
              <p className="mt-1 text-sm text-red-600">{errors.correo}</p>
            )}
          </div>

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
              placeholder="Ingrese la dirección completa"
            />
          </div>
        </div>

        {/* Estado (solo para edición) */}
        {isEditing && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Estado</h3>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                Cliente activo
              </label>
            </div>
          </div>
        )}

        {/* Botones */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={clientes?.isLoading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={clientes?.isLoading}
          >
            {clientes?.isLoading ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>
    </div>
  )
}