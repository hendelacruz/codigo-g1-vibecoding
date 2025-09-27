/**
 * Inventory Module - Punto de entrada principal
 * 
 * Este archivo exporta todos los types, interfaces y utilidades
 * del módulo de inventario para facilitar las importaciones.
 */

// Exportar todos los types e interfaces
export type {
  GPS,
  SIMCard,
  OtroProducto,
  Proveedor,
  InventoryState,
  CreateGPSData,
  CreateSIMCardData,
  CreateOtroProductoData,
  AdjustStockData,
  UpdateGPSData,
  UpdateSIMCardData,
  UpdateOtroProductoData,
  GPSFilters,
  SIMCardFilters,
  OtroProductoFilters,
  InventoryFilters,
  PaginatedResponse,
  InventoryAPIResponse,
  APIError,
  InventoryError,
  InventoryStats,
  GPSEstado,
  SIMCardEstado,
  StockEstado
} from './inventoryTypes'

// Exportar constantes
export {
  GPS_ESTADOS,
  SIMCARD_ESTADOS,
  STOCK_ESTADOS
} from './inventoryTypes'

// Exportar API functions
export { inventoryAPI, handleInventoryAPIError } from './inventoryAPI'

// Inventory Slice exports
export { default as inventoryReducer } from './inventorySlice'
export {
  // GPS async thunks
  fetchGPSDevices,
  createGPS,
  updateGPS,
  deleteGPS,
  // SIM Cards async thunks
  fetchSIMCards,
  createSIMCard,
  updateSIMCard,
  deleteSIMCard,
  // Otros Productos async thunks
  fetchOtrosProductos,
  createOtroProducto,
  updateOtroProducto,
  deleteOtroProducto,
  adjustStock,
  // Proveedores async thunks
  fetchProveedores,
  // Actions
  clearInventoryErrors,
} from './inventorySlice'

// Hooks exports
export { useInventory } from './hooks/useInventory'

// Validations exports
export {
  gpsSchema,
  simCardSchema,
  otroProductoSchema,
  adjustStockSchema,
  type GPSFormData,
  type SIMCardFormData,
  type OtroProductoFormData,
  type AdjustStockFormData
} from './validations'

// Components exports
export { GPSDevicesPage } from './components/GPSDevicesPage'
export { GPSManager } from './components/GPSManager'
export { GPSList } from './components/GPSList'
export { GPSForm } from './components/GPSForm'
export { SIMCardsPage } from './components/SIMCardsPage'
export { SIMCardsManager } from './components/SIMCardsManager'
export { SIMCardList } from './components/SIMCardList'
export { SIMCardForm } from './components/SIMCardForm'
export { InventoryDashboard } from './components/InventoryDashboard'
export { OtrosProductosManager } from './components/OtrosProductosManager'