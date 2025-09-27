import { z } from 'zod'

export const gpsSchema = z.object({
  fecha_compra: z.string().min(1, 'Fecha de compra es requerida'),
  imei: z.string().min(15, 'IMEI debe tener al menos 15 caracteres').max(17, 'IMEI no puede tener más de 17 caracteres'),
  marca: z.string().min(1, 'Marca es requerida'),
  modelo: z.string().min(1, 'Modelo es requerido'),
  numero_factura: z.string().min(1, 'Número de factura es requerido'),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja']),
  precio_compra: z.number().min(0, 'Precio debe ser mayor a 0').optional(),
  observaciones: z.string().optional(),
})

export const simCardSchema = z.object({
  fecha_compra: z.string()
    .min(1, 'Fecha de compra es requerida')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato de fecha inválido (YYYY-MM-DD)'),
  numero_factura: z.string()
    .min(1, 'Número de factura es requerido')
    .max(50, 'Número de factura no puede exceder 50 caracteres')
    .trim(),
  numero_chip: z.string()
    .min(1, 'Número de chip es requerido')
    .min(9, 'Número de chip debe tener al menos 9 caracteres')
    .max(20, 'Número de chip no puede exceder 20 caracteres')
    .regex(/^[0-9]+$/, 'Número de chip debe contener solo números')
    .trim(),
  icc: z.string()
    .min(1, 'ICC es requerido')
    .min(19, 'ICC debe tener al menos 19 caracteres')
    .max(22, 'ICC no puede exceder 22 caracteres')
    .regex(/^[0-9]+$/, 'ICC debe contener solo números')
    .trim(),
  proveedor_id: z.number()
    .int('ID de proveedor debe ser un número entero')
    .min(1, 'Proveedor es requerido'),
  estado: z.enum(['disponible', 'activo', 'asignado', 'suspendido', 'en_mantenimiento', 'dañado', 'perdido', 'dado_de_baja'], {
    message: 'Estado inválido'
  }),
  cliente_id: z.number()
    .int('ID de cliente debe ser un número entero')
    .min(1, 'Cliente debe ser válido')
    .optional()
    .nullable(),
  plan: z.string()
    .max(100, 'Plan no puede exceder 100 caracteres')
    .trim()
    .optional()
    .or(z.literal('')),
  precio_compra: z.number()
    .min(0, 'Precio debe ser mayor o igual a 0')
    .max(99999.99, 'Precio no puede exceder 99,999.99')
    .optional()
    .nullable(),
  observaciones: z.string()
    .max(500, 'Observaciones no pueden exceder 500 caracteres')
    .trim()
    .optional()
    .or(z.literal(''))
}).refine((data) => {
  // Custom validation: fecha_compra should not be in the future
  const purchaseDate = new Date(data.fecha_compra)
  const today = new Date()
  today.setHours(23, 59, 59, 999) // Set to end of today
  return purchaseDate <= today
}, {
  message: 'La fecha de compra no puede ser en el futuro',
  path: ['fecha_compra']
})

export const otroProductoSchema = z.object({
  nombre: z.string().min(1, 'Nombre es requerido'),
  descripcion: z.string().optional(),
  categoria: z.string().min(1, 'Categoría es requerida'),
  precio_unitario: z.number().min(0, 'Precio debe ser mayor a 0'),
  stock_actual: z.number().min(0, 'Stock actual debe ser mayor o igual a 0'),
  stock_minimo: z.number().min(0, 'Stock mínimo debe ser mayor o igual a 0'),
  proveedor: z.number().min(1, 'Proveedor es requerido'),
})

export const adjustStockSchema = z.object({
  cantidad: z.number().int('Cantidad debe ser un número entero'),
  motivo: z.string().optional(),
})

export type GPSFormData = z.infer<typeof gpsSchema>
export type SIMCardFormData = z.infer<typeof simCardSchema>
export type OtroProductoFormData = z.infer<typeof otroProductoSchema>
export type AdjustStockFormData = z.infer<typeof adjustStockSchema>