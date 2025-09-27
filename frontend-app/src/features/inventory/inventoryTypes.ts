/**
 * Types para el módulo de inventario
 * Incluye interfaces para GPS, SIM Cards, Otros Productos y Proveedores
 */

export interface GPS {
  id: number
  fecha_compra: string
  imei: string
  marca: string
  modelo: string
  numero_factura: string
  proveedor: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  cliente?: number
  cliente_info?: {
    id: number
    nombre: string
  }
  estado: 'asignado' | 'no_asignado'
  estado_display: string
  proceso: 'en_produccion' | 'dañado' | 'garantia' | 'en_mantenimiento' | 'dado_de_baja' | 'en_transito'
  precio_compra?: number
  observaciones?: string
  created_at: string
  updated_at: string
}

export interface SIMCard {
  id: number
  fecha_compra: string
  numero_factura: string
  numero_chip: string
  icc: string
  plan?: string
  precio_compra?: number
  observaciones?: string
  created_at: string
  updated_at: string
  proveedor_id: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  cliente_id?: number
  cliente_info?: {
    id: number
    nombre: string
  }
  is_active: boolean
  proceso: 'en_produccion' | 'dado_de_baja' | 'en_almacen'
  estado: 'asignado' | 'no_asignado'
  estado_display: string
}

export interface OtroProducto {
  id: number
  nombre: string
  descripcion?: string
  categoria: string
  precio_unitario: number
  stock_actual: number
  stock_minimo: number
  proveedor: number
  proveedor_info?: {
    id: number
    nombre: string
  }
  estado_stock: 'disponible' | 'agotado' | 'bajo_stock'
  created_at: string
  updated_at: string
}

export interface Proveedor {
  id: number
  nombre: string
  ruc?: string
  telefono?: string
  correo?: string
  direccion?: string
  is_active: boolean
}

export interface InventoryState {
  gps: {
    items: GPS[]
    isLoading: boolean
    error: string | null
  }
  simCards: {
    items: SIMCard[]
    isLoading: boolean
    error: string | null
  }
  otrosProductos: {
    items: OtroProducto[]
    isLoading: boolean
    error: string | null
  }
  proveedores: {
    items: Proveedor[]
    isLoading: boolean
    error: string | null
  }
}

export interface CreateGPSData {
  fecha_compra: string
  imei: string
  marca: string
  modelo: string
  numero_factura: string
  proveedor: number
  cliente?: number
  estado: GPS['estado']
  proceso: GPS['proceso']
  precio_compra?: number
  observaciones?: string
}

export interface CreateSIMCardData {
  fecha_compra: string
  numero_factura: string
  numero_chip: string
  icc: string
  plan?: string
  precio_compra?: number
  observaciones?: string
  proveedor: number  // Cambiado de proveedor_id a proveedor para coincidir con la API
  estado: SIMCard['estado']
  proceso: SIMCard['proceso']
  // Campos opcionales que pueden no ser requeridos por el servidor
  cliente_id?: number
  is_active?: boolean
}

export interface CreateOtroProductoData {
  fecha_compra: string
  numero_factura: string
  cantidad: number  // Cantidad inicial comprada
  descripcion: string
  proveedor: number
  categoria: string
  precio_unitario: number
  precio_total: number
  stock_actual: number
  stock_minimo: number
  observaciones?: string
}

export interface AdjustStockData {
  cantidad: number
  motivo?: string
}

// Types para formularios y validaciones
// Update data types - extend partial create data for flexible updates
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateGPSData extends Partial<CreateGPSData> {}
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateSIMCardData extends Partial<CreateSIMCardData> {}
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateOtroProductoData extends Partial<CreateOtroProductoData> {}

// Types para filtros y búsquedas
export interface GPSFilters {
  estado?: GPS['estado']
  marca?: string
  proveedor?: number
  cliente?: number
  fecha_desde?: string
  fecha_hasta?: string
}

export interface SIMCardFilters {
  estado?: SIMCard['estado']
  cliente_id?: number
  proveedor?: number
  fecha_desde?: string
  fecha_hasta?: string
}

export interface OtroProductoFilters {
  categoria?: string
  estado_stock?: OtroProducto['estado_stock']
  proveedor?: number
  bajo_stock?: boolean
}

// Types para filtros generales de inventario
export interface InventoryFilters {
  search?: string
  status?: string
  proveedor?: number
  fecha_desde?: string
  fecha_hasta?: string
}

// Types para respuestas paginadas de API
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Types para respuestas de API
export interface InventoryAPIResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Types para errores de API
export interface APIError {
  message: string
  field?: string
  code?: string
}

// Types para errores específicos del inventario
export interface InventoryError {
  field?: string
  message: string
  code?: string
}

// Types para estadísticas del inventario
export interface InventoryStats {
  total_gps: number
  gps_por_estado: Record<GPS['estado'], number>
  total_simcards: number
  simcards_por_estado: Record<SIMCard['estado'], number>
  total_otros_productos: number
  productos_bajo_stock: number
  valor_total_inventario: number
}

// Enums para mejor type safety
export const GPS_ESTADOS = [
  'asignado',
  'no_asignado'
] as const

export const GPS_PROCESOS = [
  'en_produccion',
  'dañado',
  'garantia',
  'en_mantenimiento',
  'dado_de_baja',
  'en_transito'
] as const

export const SIMCARD_ESTADOS = [
  'asignado',
  'no_asignado'
] as const

export const SIMCARD_PROCESOS = [
  'en_produccion',
  'dado_de_baja',
  'en_almacen'
] as const

export const STOCK_ESTADOS = [
  'disponible',
  'agotado',
  'bajo_stock'
] as const

export type GPSEstado = typeof GPS_ESTADOS[number]
export type GPSProceso = typeof GPS_PROCESOS[number]
export type SIMCardEstado = typeof SIMCARD_ESTADOS[number]
export type SIMCardProceso = typeof SIMCARD_PROCESOS[number]
export type StockEstado = typeof STOCK_ESTADOS[number]