/**
 * Types para el módulo de entidades
 * Incluye interfaces para Clientes, Unidades Vehiculares y Proveedores
 */

// ==================== CLIENTE INTERFACES ====================

export interface Cliente {
  id: number
  nombre: string
  ruc?: string
  direccion?: string
  contacto?: string
  celular?: string
  correo?: string
  is_active: boolean
  unidades_count?: number
  created_at: string
  updated_at: string
}

export interface CreateClienteData {
  nombre: string
  ruc?: string
  direccion?: string
  contacto?: string
  celular?: string
  correo?: string
  is_active?: boolean
}

// Update data type - extends partial create data for flexible updates
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateClienteData extends Partial<CreateClienteData> {}

// ==================== UNIDAD VEHICULAR INTERFACES ====================

export interface UnidadVehicular {
  id: number
  tipo: 'bus' | 'camion' | 'otro'
  placa: string
  marca: string
  modelo: string
  serie: string
  is_active: boolean
  created_at: string
  updated_at: string
  cliente_id: number
  cliente_info?: {
    id: number
    nombre: string
  }
}

export interface CreateUnidadData {
  tipo: UnidadVehicular['tipo']
  placa: string
  marca: string
  modelo: string
  serie: string
  cliente_id: number  // Consistent with UnidadVehicular interface
  is_active?: boolean
}

// Update data type - extends partial create data for flexible updates
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateUnidadData extends Partial<CreateUnidadData> {}

// ==================== PROVEEDOR INTERFACES ====================

export interface ProveedorEntity {
  id: number
  nombre: string
  ruc?: string
  direccion?: string
  contacto?: string
  celular?: string
  correo?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateProveedorData {
  nombre: string
  ruc?: string
  direccion?: string
  contacto?: string
  celular?: string
  correo?: string
  is_active?: boolean
}

// Update data type - extends partial create data for flexible updates
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface UpdateProveedorData extends Partial<CreateProveedorData> {}

// ==================== STATE INTERFACES ====================

export interface EntitiesState {
  clientes: {
    items: Cliente[]
    isLoading: boolean
    error: string | null
  }
  unidades: {
    items: UnidadVehicular[]
    isLoading: boolean
    error: string | null
  }
  proveedores: {
    items: ProveedorEntity[]
    isLoading: boolean
    error: string | null
  }
}

// ==================== FILTER INTERFACES ====================

export interface ClienteFilters {
  search?: string
  is_active?: boolean
  ruc?: string
}

export interface UnidadFilters {
  search?: string
  cliente_id?: number
  tipo?: UnidadVehicular['tipo']
  placa?: string
  is_active?: boolean
  marca?: string
}

export interface ProveedorFilters {
  search?: string
  is_active?: boolean
  ruc?: string
}

export interface EntitiesFilters {
  clientes?: ClienteFilters
  unidades?: UnidadFilters
  proveedores?: ProveedorFilters
}

// ==================== API RESPONSE INTERFACES ====================

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface EntitiesAPIResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface APIError {
  message: string
  status?: number
  details?: Record<string, string[]>
}

export interface EntitiesError {
  type: 'network' | 'validation' | 'server' | 'unknown'
  message: string
  details?: Record<string, string[]>
}

// ==================== STATS INTERFACES ====================

export interface EntitiesStats {
  totalClientes: number
  totalUnidades: number
  totalProveedores: number
  clientesActivos: number
  unidadesActivas: number
  proveedoresActivos: number
}

// ==================== CONSTANTS ====================

export const TIPO_VEHICULO_OPTIONS = [
  { value: 'bus', label: 'Bus' },
  { value: 'camion', label: 'Camión' },
  { value: 'otro', label: 'Otro' },
] as const

// ==================== TYPE GUARDS ====================

export const isCliente = (entity: unknown): entity is Cliente => {
  return (
    typeof entity === 'object' &&
    entity !== null &&
    'id' in entity &&
    'nombre' in entity &&
    'is_active' in entity
  )
}

export const isUnidadVehicular = (entity: unknown): entity is UnidadVehicular => {
  return (
    typeof entity === 'object' &&
    entity !== null &&
    'id' in entity &&
    'placa' in entity &&
    'cliente_id' in entity
  )
}

export const isProveedorEntity = (entity: unknown): entity is ProveedorEntity => {
  return (
    typeof entity === 'object' &&
    entity !== null &&
    'id' in entity &&
    'nombre' in entity &&
    'is_active' in entity
  )
}

// ==================== UTILITY TYPES ====================

export type TipoVehiculo = UnidadVehicular['tipo']
export type EntityType = 'clientes' | 'unidades' | 'proveedores'