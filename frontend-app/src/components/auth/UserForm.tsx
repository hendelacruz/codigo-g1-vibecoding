import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../../shared/components/ui/Button'
import type { User } from '../../features/auth/authTypes'
import { dniSchema, celularSchema } from '../../shared/lib/validations'

// Validation schema for license format (A12345678)
const licenciaSchema = z.string()
  .regex(/^[A-Z]\d{8}$/, 'La licencia debe tener el formato A12345678 (una letra seguida de 8 dígitos)')
  .optional()
  .or(z.literal(''))

// Validation schema with Zod
const userFormSchema = z.object({
  username: z
    .string()
    .min(3, 'El nombre de usuario debe tener al menos 3 caracteres')
    .max(150, 'El nombre de usuario no puede exceder 150 caracteres')
    .regex(/^[a-zA-Z0-9._-]+$/, 'Solo se permiten letras, números, puntos, guiones y guiones bajos'),
  email: z
    .string()
    .email('Debe ser un email válido')
    .min(1, 'El email es requerido'),
  first_name: z
    .string()
    .min(1, 'El nombre es requerido')
    .max(30, 'El nombre no puede exceder 30 caracteres'),
  last_name: z
    .string()
    .min(1, 'El apellido es requerido')
    .max(30, 'El apellido no puede exceder 30 caracteres'),
  dni: dniSchema,
  celular: celularSchema,
  password: z
    .string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .optional()
    .or(z.literal('')),
  confirm_password: z
    .string()
    .optional()
    .or(z.literal('')),
  rol_nombre: z
    .string()
    .min(1, 'Debe seleccionar un rol'),
  licencia: licenciaSchema,
  is_active: z.boolean()
}).refine((data) => {
  // Only validate password confirmation if password is provided
  if (data.password && data.password.length > 0) {
    return data.password === data.confirm_password
  }
  return true
}, {
  message: 'Las contraseñas no coinciden',
  path: ['confirm_password']
})

export type UserFormData = z.infer<typeof userFormSchema>

interface UserFormProps {
  user?: User | null
  onSubmit: (data: UserFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode: 'create' | 'edit'
}

const AVAILABLE_ROLES = [
  { value: 'ADMIN', label: 'Administrador' },
  { value: 'administrador', label: 'Administrador' },
  { value: 'supervisor', label: 'Supervisor' },
  { value: 'tecnico', label: 'Técnico' },
  { value: 'operador', label: 'Operador' }
]

export const UserForm: React.FC<UserFormProps> = ({
  user,
  onSubmit,
  onCancel,
  isLoading = false,
  mode
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue
  } = useForm<UserFormData>({
    resolver: zodResolver(userFormSchema),
    defaultValues: {
      username: user?.username || '',
      email: user?.email || '',
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      dni: user?.dni || '',
      celular: user?.celular || '',
      password: '',
      confirm_password: '',
      rol_nombre: user?.rol_nombre || '',
      licencia: user?.licencia || '',
      is_active: user?.is_active ?? true
    }
  })

  // Watch the is_active value
  const isActiveValue = watch('is_active')

  const handleFormSubmit = async (data: UserFormData) => {
    try {
      await onSubmit(data)
      if (mode === 'create') {
        reset()
      }
    } catch (error) {
      console.error('Error submitting form:', error)
    }
  }

  const isFormLoading = isLoading || isSubmitting

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {mode === 'create' ? 'Crear Nuevo Usuario' : 'Editar Usuario'}
            </h3>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              disabled={isFormLoading}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            {/* Personal Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  {...register('first_name')}
                  type="text"
                  id="first_name"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.first_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Apellido *
                </label>
                <input
                  {...register('last_name')}
                  type="text"
                  id="last_name"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.last_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            {/* Account Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de Usuario *
                </label>
                <input
                  {...register('username')}
                  type="text"
                  id="username"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.username ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.email ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>
            </div>

            {/* DNI and Celular */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="dni" className="block text-sm font-medium text-gray-700 mb-1">
                  DNI *
                </label>
                <input
                  {...register('dni')}
                  type="text"
                  id="dni"
                  placeholder="12345678"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.dni ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.dni && (
                  <p className="mt-1 text-sm text-red-600">{errors.dni.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="celular" className="block text-sm font-medium text-gray-700 mb-1">
                  Celular *
                </label>
                <input
                  {...register('celular')}
                  type="text"
                  id="celular"
                  placeholder="987654321"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.celular ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.celular && (
                  <p className="mt-1 text-sm text-red-600">{errors.celular.message}</p>
                )}
              </div>
            </div>

            {/* Role and License */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="rol_nombre" className="block text-sm font-medium text-gray-700 mb-1">
                  Rol *
                </label>
                <select
                  {...register('rol_nombre')}
                  id="rol_nombre"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.rol_nombre ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                >
                  <option value="">Seleccionar rol</option>
                  {AVAILABLE_ROLES.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
                {errors.rol_nombre && (
                  <p className="mt-1 text-sm text-red-600">{errors.rol_nombre.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="licencia" className="block text-sm font-medium text-gray-700 mb-1">
                  Licencia (opcional)
                </label>
                <input
                  {...register('licencia')}
                  type="text"
                  id="licencia"
                  placeholder="A12345678"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.licencia ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.licencia && (
                  <p className="mt-1 text-sm text-red-600">{errors.licencia.message}</p>
                )}
              </div>
            </div>

            {/* Password Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  {mode === 'create' ? 'Contraseña *' : 'Nueva Contraseña (opcional)'}
                </label>
                <input
                  {...register('password')}
                  type="password"
                  id="password"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.password ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                  Confirmar Contraseña
                </label>
                <input
                  {...register('confirm_password')}
                  type="password"
                  id="confirm_password"
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.confirm_password ? 'border-red-300' : 'border-gray-300'
                  }`}
                  disabled={isFormLoading}
                />
                {errors.confirm_password && (
                  <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
                )}
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={isActiveValue}
                onChange={(e) => setValue('is_active', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                disabled={isFormLoading}
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                Usuario activo
              </label>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isFormLoading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                disabled={isFormLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {isFormLoading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {mode === 'create' ? 'Creando...' : 'Guardando...'}
                  </div>
                ) : (
                  mode === 'create' ? 'Crear Usuario' : 'Guardar Cambios'
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}