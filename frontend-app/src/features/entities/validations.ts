/**
 * Validaciones Zod para el módulo de entidades
 * Incluye esquemas para clientes, unidades vehiculares y proveedores
 * Siguiendo el patrón del módulo de inventario
 */

import { z } from 'zod'

// ===== VALIDACIONES COMUNES =====

const requiredString = (field: string) => 
  z.string().min(1, `${field} es requerido`)

const optionalString = z.string().optional()

const requiredEmail = z
  .string()
  .min(1, 'Email es requerido')
  .email('Email debe tener un formato válido')

const phoneRegex = /^(\+?51)?[9]\d{8}$/
const requiredPhone = z
  .string()
  .min(1, 'Teléfono es requerido')
  .regex(phoneRegex, 'Teléfono debe tener formato válido (+51 9XXXXXXXX)')

const optionalPhone = z
  .string()
  .optional()
  .refine((val) => !val || phoneRegex.test(val), {
    message: 'Teléfono debe tener formato válido (+51 9XXXXXXXX)'
  })

// RUC validation (11 digits)
const rucRegex = /^\d{11}$/
const requiredRuc = z
  .string()
  .min(1, 'RUC es requerido')
  .regex(rucRegex, 'RUC debe tener 11 dígitos')

// DNI validation (8 digits)
const dniRegex = /^\d{8}$/

// License plate validation (Peruvian format)
const placaRegex = /^[A-Z]{3}-\d{3}$|^[A-Z]{2}-\d{4}$/
const requiredPlaca = z
  .string()
  .min(1, 'Placa es requerida')
  .regex(placaRegex, 'Placa debe tener formato válido (ABC-123 o AB-1234)')

// ===== ESQUEMAS PARA CLIENTES =====

export const clienteCreateSchema = z.object({
  tipo_cliente: z.enum(['persona', 'empresa'], {
    message: 'Tipo de cliente es requerido'
  }),
  nombre: requiredString('Nombre'),
  apellido_paterno: z.string().optional(),
  apellido_materno: z.string().optional(),
  razon_social: z.string().optional(),
  documento_tipo: z.enum(['dni', 'ruc', 'pasaporte'], {
    message: 'Tipo de documento es requerido'
  }),
  documento_numero: requiredString('Número de documento'),
  email: requiredEmail,
  telefono: requiredPhone,
  telefono_secundario: optionalPhone,
  direccion: requiredString('Dirección'),
  distrito: requiredString('Distrito'),
  provincia: requiredString('Provincia'),
  departamento: requiredString('Departamento'),
  codigo_postal: optionalString,
  contacto_nombre: optionalString,
  contacto_telefono: optionalPhone,
  contacto_email: z.string().email('Email de contacto debe ser válido').optional().or(z.literal('')),
  observaciones: optionalString,
  activo: z.boolean().default(true)
}).refine((data) => {
  // Validation for persona type
  if (data.tipo_cliente === 'persona') {
    return data.apellido_paterno && data.apellido_paterno.length > 0
  }
  return true
}, {
  message: 'Apellido paterno es requerido para personas',
  path: ['apellido_paterno']
}).refine((data) => {
  // Validation for empresa type
  if (data.tipo_cliente === 'empresa') {
    return data.razon_social && data.razon_social.length > 0
  }
  return true
}, {
  message: 'Razón social es requerida para empresas',
  path: ['razon_social']
}).refine((data) => {
  // Document validation based on type
  if (data.documento_tipo === 'dni') {
    return dniRegex.test(data.documento_numero)
  }
  if (data.documento_tipo === 'ruc') {
    return rucRegex.test(data.documento_numero)
  }
  return true
}, {
  message: 'Formato de documento inválido',
  path: ['documento_numero']
})

export const clienteUpdateSchema = clienteCreateSchema.partial().extend({
  id: z.number().positive('ID debe ser un número positivo')
})

export const clienteFiltersSchema = z.object({
  search: optionalString,
  tipo_cliente: z.enum(['persona', 'empresa']).optional(),
  documento_tipo: z.enum(['dni', 'ruc', 'pasaporte']).optional(),
  activo: z.boolean().optional(),
  departamento: optionalString,
  provincia: optionalString,
  distrito: optionalString
}).partial()

// ===== ESQUEMAS PARA UNIDADES VEHICULARES =====

export const unidadCreateSchema = z.object({
  placa: requiredPlaca,
  marca: requiredString('Marca'),
  modelo: requiredString('Modelo'),
  año: z.number()
    .min(1900, 'Año debe ser mayor a 1900')
    .max(new Date().getFullYear() + 1, 'Año no puede ser futuro'),
  color: requiredString('Color'),
  numero_motor: requiredString('Número de motor'),
  numero_chasis: requiredString('Número de chasis'),
  tipo_vehiculo: z.enum(['auto', 'camioneta', 'camion', 'bus', 'moto', 'otro'], {
    message: 'Tipo de vehículo es requerido'
  }),
  tipo_combustible: z.enum(['gasolina', 'diesel', 'glp', 'gnv', 'electrico', 'hibrido'], {
    message: 'Tipo de combustible es requerido'
  }),
  numero_asientos: z.number()
    .min(1, 'Número de asientos debe ser mayor a 0')
    .max(100, 'Número de asientos no puede ser mayor a 100'),
  peso_bruto: z.number()
    .min(0, 'Peso bruto debe ser positivo')
    .optional(),
  carga_util: z.number()
    .min(0, 'Carga útil debe ser positiva')
    .optional(),
  propietario_nombre: requiredString('Nombre del propietario'),
  propietario_documento: requiredString('Documento del propietario'),
  propietario_telefono: requiredPhone,
  fecha_soat: z.string().min(1, 'Fecha de SOAT es requerida'),
  fecha_revision_tecnica: z.string().min(1, 'Fecha de revisión técnica es requerida'),
  observaciones: optionalString,
  activo: z.boolean().default(true)
})

export const unidadUpdateSchema = unidadCreateSchema.partial().extend({
  id: z.number().positive('ID debe ser un número positivo')
})

export const unidadFiltersSchema = z.object({
  search: optionalString,
  marca: optionalString,
  modelo: optionalString,
  tipo_vehiculo: z.enum(['auto', 'camioneta', 'camion', 'bus', 'moto', 'otro']).optional(),
  tipo_combustible: z.enum(['gasolina', 'diesel', 'glp', 'gnv', 'electrico', 'hibrido']).optional(),
  año_desde: z.number().optional(),
  año_hasta: z.number().optional(),
  activo: z.boolean().optional(),
  soat_vencido: z.boolean().optional(),
  revision_vencida: z.boolean().optional()
}).partial()

// ===== ESQUEMAS PARA PROVEEDORES =====

export const proveedorCreateSchema = z.object({
  tipo_proveedor: z.enum(['persona', 'empresa'], {
    message: 'Tipo de proveedor es requerido'
  }),
  nombre: requiredString('Nombre'),
  apellido_paterno: optionalString,
  apellido_materno: optionalString,
  razon_social: optionalString,
  nombre_comercial: optionalString,
  ruc: requiredRuc,
  email: requiredEmail,
  telefono: requiredPhone,
  telefono_secundario: optionalPhone,
  direccion: requiredString('Dirección'),
  distrito: requiredString('Distrito'),
  provincia: requiredString('Provincia'),
  departamento: requiredString('Departamento'),
  codigo_postal: optionalString,
  contacto_nombre: optionalString,
  contacto_cargo: optionalString,
  contacto_telefono: optionalPhone,
  contacto_email: z.string().email('Email de contacto debe ser válido').optional().or(z.literal('')),
  categoria: z.enum(['gps', 'sim', 'vehiculos', 'servicios', 'otros'], {
    message: 'Categoría es requerida'
  }),
  banco_nombre: optionalString,
  banco_cuenta: optionalString,
  banco_cci: optionalString,
  observaciones: optionalString,
  activo: z.boolean().default(true)
}).refine((data) => {
  // Validation for persona type
  if (data.tipo_proveedor === 'persona') {
    return data.apellido_paterno && data.apellido_paterno.length > 0
  }
  return true
}, {
  message: 'Apellido paterno es requerido para personas',
  path: ['apellido_paterno']
}).refine((data) => {
  // Validation for empresa type
  if (data.tipo_proveedor === 'empresa') {
    return data.razon_social && data.razon_social.length > 0
  }
  return true
}, {
  message: 'Razón social es requerida para empresas',
  path: ['razon_social']
})

export const proveedorUpdateSchema = proveedorCreateSchema.partial().extend({
  id: z.number().positive('ID debe ser un número positivo')
})

export const proveedorFiltersSchema = z.object({
  search: optionalString,
  tipo_proveedor: z.enum(['persona', 'empresa']).optional(),
  categoria: z.enum(['gps', 'sim', 'vehiculos', 'servicios', 'otros']).optional(),
  activo: z.boolean().optional(),
  departamento: optionalString,
  provincia: optionalString,
  distrito: optionalString
}).partial()

// ===== TIPOS INFERIDOS =====

export type ClienteCreateInput = z.infer<typeof clienteCreateSchema>
export type ClienteUpdateInput = z.infer<typeof clienteUpdateSchema>
export type ClienteFiltersInput = z.infer<typeof clienteFiltersSchema>

export type UnidadCreateInput = z.infer<typeof unidadCreateSchema>
export type UnidadUpdateInput = z.infer<typeof unidadUpdateSchema>
export type UnidadFiltersInput = z.infer<typeof unidadFiltersSchema>

export type ProveedorCreateInput = z.infer<typeof proveedorCreateSchema>
export type ProveedorUpdateInput = z.infer<typeof proveedorUpdateSchema>
export type ProveedorFiltersInput = z.infer<typeof proveedorFiltersSchema>

// ===== UTILIDADES DE VALIDACIÓN =====

export const validateCliente = (data: unknown) => {
  return clienteCreateSchema.safeParse(data)
}

export const validateUnidad = (data: unknown) => {
  return unidadCreateSchema.safeParse(data)
}

export const validateProveedor = (data: unknown) => {
  return proveedorCreateSchema.safeParse(data)
}

// ===== CONSTANTES PARA FORMULARIOS =====

export const TIPO_CLIENTE_OPTIONS = [
  { value: 'persona', label: 'Persona Natural' },
  { value: 'empresa', label: 'Empresa' }
] as const

export const DOCUMENTO_TIPO_OPTIONS = [
  { value: 'dni', label: 'DNI' },
  { value: 'ruc', label: 'RUC' },
  { value: 'pasaporte', label: 'Pasaporte' }
] as const

export const TIPO_VEHICULO_OPTIONS = [
  { value: 'auto', label: 'Automóvil' },
  { value: 'camioneta', label: 'Camioneta' },
  { value: 'camion', label: 'Camión' },
  { value: 'bus', label: 'Bus' },
  { value: 'moto', label: 'Motocicleta' },
  { value: 'otro', label: 'Otro' }
] as const

export const TIPO_COMBUSTIBLE_OPTIONS = [
  { value: 'gasolina', label: 'Gasolina' },
  { value: 'diesel', label: 'Diésel' },
  { value: 'glp', label: 'GLP' },
  { value: 'gnv', label: 'GNV' },
  { value: 'electrico', label: 'Eléctrico' },
  { value: 'hibrido', label: 'Híbrido' }
] as const

export const CATEGORIA_PROVEEDOR_OPTIONS = [
  { value: 'gps', label: 'Dispositivos GPS' },
  { value: 'sim', label: 'Tarjetas SIM' },
  { value: 'vehiculos', label: 'Vehículos' },
  { value: 'servicios', label: 'Servicios' },
  { value: 'otros', label: 'Otros' }
] as const