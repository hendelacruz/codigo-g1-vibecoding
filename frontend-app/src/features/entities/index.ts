// Components
export { ClientesList } from './components/ClientesList'
export { ClienteForm } from './components/ClienteForm'
export { UnidadesList } from './components/UnidadesList'
export { UnidadForm } from './components/UnidadForm'
export { ProveedoresList } from './components/ProveedoresList'
export { ProveedorForm } from './components/ProveedorForm'
export { EntitiesPage } from './components/EntitiesPage'
export { EntitiesDashboard } from './components/EntitiesDashboard'

// Hooks
export { useEntities } from './useEntities'

// Types
export type {
  Cliente,
  UnidadVehicular,
  ProveedorEntity,
  CreateClienteData,
  UpdateClienteData,
  CreateUnidadData,
  UpdateUnidadData,
  CreateProveedorData,
  UpdateProveedorData,
  ClienteFilters,
  UnidadFilters,
  ProveedorFilters,
  EntitiesState,
  PaginatedResponse,
  EntitiesStats,
  TipoVehiculo
} from './entitiesTypes'

// Redux slice
export { default as entitiesReducer } from './entitiesSlice'
export {
  fetchClientes,
  fetchCliente,
  createCliente,
  updateCliente,
  deleteCliente,
  toggleClienteActive,
  fetchClienteUnidades,
  fetchUnidades,
  fetchUnidad,
  createUnidad,
  updateUnidad,
  deleteUnidad,
  toggleUnidadActive,
  fetchProveedoresEntity,
  fetchProveedor,
  createProveedorEntity,
  updateProveedorEntity,
  deleteProveedor,
  toggleProveedorActive,
  fetchClientesActivos,
  fetchProveedoresActivos,
  clearEntitiesErrors,
  clearClientesError,
  clearUnidadesError,
  clearProveedoresError
} from './entitiesSlice'

// API
export { entitiesAPI } from './entitiesAPI'