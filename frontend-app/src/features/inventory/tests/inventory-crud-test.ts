/**
 * Test file for Inventory CRUD operations
 * This file contains manual tests to verify the inventory module functionality
 * Run these tests directly in the browser console or create a test component
 */

import { store } from '../../../app/store'
import { 
  fetchGPSDevices, 
  createGPS, 
  updateGPS, 
  deleteGPS,
  fetchSIMCards,
  createSIMCard,
  updateSIMCard,
  deleteSIMCard,
  fetchOtrosProductos,
  createOtroProducto,
  updateOtroProducto,
  deleteOtroProducto,
  adjustStock,
  fetchProveedores
} from '../inventorySlice'
import type { CreateGPSData, CreateSIMCardData, CreateOtroProductoData } from '../inventoryTypes'

/**
 * Test GPS CRUD Operations
 */
export const testGPSOperations = async () => {
  
  try {
    // 1. Fetch GPS devices
    void await store.dispatch(fetchGPSDevices())
    
    // 2. Create new GPS device
    const newGPSData: CreateGPSData = {
      fecha_compra: '2024-01-15',
      imei: '123456789012345',
      marca: 'Garmin',
      modelo: 'Test Model',
      numero_factura: 'FAC-001',
      proveedor: 1,
      estado: 'no_asignado',
      proceso: 'en_transito',
      precio_compra: 150.00,
      observaciones: 'Test GPS device'
    }
    
    const createResult = await store.dispatch(createGPS(newGPSData))
    if (createGPS.fulfilled.match(createResult)) {
      
      // 3. Update GPS device
      void await store.dispatch(updateGPS({
        id: createResult.payload.id,
        data: { estado: 'asignado', observaciones: 'Updated test GPS' }
      }))
      
      // 4. Delete GPS device
      void await store.dispatch(deleteGPS(createResult.payload.id))
    }
    
  } catch (error) {
    console.error('❌ GPS operations failed:', error)
  }
}

/**
 * Test SIM Card CRUD Operations
 */
export const testSIMCardOperations = async () => {
  
  try {
    // 1. Fetch SIM cards
    void await store.dispatch(fetchSIMCards())
    
    // 2. Create new SIM card
    const newSIMData: CreateSIMCardData = {
      fecha_compra: '2024-01-15',
      numero_factura: 'FAC-SIM-001',
      numero_chip: '1234567890',
      icc: '89591234567890123456',
      proveedor: 1,
      cliente_id: 0,
      estado: 'no_asignado',
      proceso: 'en_almacen',
      plan: 'Plan Básico',
      precio_compra: 25.00,
      observaciones: 'Test SIM card',
      is_active: true
    }
    
    const createResult = await store.dispatch(createSIMCard(newSIMData))
    if (createSIMCard.fulfilled.match(createResult)) {
      
      // 3. Update SIM card
      void await store.dispatch(updateSIMCard({
        id: createResult.payload.id,
        data: { estado: 'asignado', plan: 'Plan Premium' }
      }))
      
      // 4. Delete SIM card
      void await store.dispatch(deleteSIMCard(createResult.payload.id))
    }
    
  } catch (error) {
    console.error('❌ SIM card operations failed:', error)
  }
}

/**
 * Test Other Products CRUD Operations
 */
export const testOtherProductsOperations = async () => {
  
  try {
    // 1. Fetch other products
    void await store.dispatch(fetchOtrosProductos())
    
    // 2. Create new product
    const newProductData: CreateOtroProductoData = {
      descripcion: 'Cable USB para pruebas',
      categoria: 'Cables',
      precio_unitario: 15.50,
      stock_actual: 100,
      stock_minimo: 10,
      proveedor: 1,
      fecha_compra: '2024-01-15',
      numero_factura: 'FAC-CABLE-001',
      cantidad: 100,
      precio_total: 1550.00,
      observaciones: 'Cable USB de prueba'
    }
    
    const createResult = await store.dispatch(createOtroProducto(newProductData))
    if (createOtroProducto.fulfilled.match(createResult)) {
      
      // 3. Update product
      void await store.dispatch(updateOtroProducto({
        id: createResult.payload.id,
        data: { precio_unitario: 18.00, descripcion: 'Cable USB actualizado' }
      }))
      
      // 4. Adjust stock
      void await store.dispatch(adjustStock({
        id: createResult.payload.id,
        data: { cantidad: -20, motivo: 'Venta de prueba' }
      }))
      
      // 5. Delete product
      void await store.dispatch(deleteOtroProducto(createResult.payload.id))
    }
    
  } catch (error) {
    console.error('❌ Other products operations failed:', error)
  }
}

/**
 * Test Providers fetch
 */
export const testProvidersOperations = async () => {
  
  try {
    void await store.dispatch(fetchProveedores())
    
  } catch (error) {
    console.error('❌ Providers operations failed:', error)
  }
}

/**
 * Run all inventory tests
 */
export const runAllInventoryTests = async () => {
  
  await testProvidersOperations()
  
  await testGPSOperations()
  
  await testSIMCardOperations()
  
  await testOtherProductsOperations()
  
}

/**
 * Test authentication and error handling
 */
export const testAuthenticationErrors = async () => {
  
  // Check current auth state
  const currentState = store.getState();
  console.log('🔐 Auth state:', {
    isAuthenticated: currentState.auth.isAuthenticated,
    hasToken: !!currentState.auth.token
  });
  
  if (!currentState.auth.isAuthenticated || !currentState.auth.token) {
    console.log('❌ User not authenticated');
    return;
  }
  
  try {
    // Try to fetch data with current authentication
    const result = await store.dispatch(fetchGPSDevices());
    if (fetchGPSDevices.fulfilled.match(result)) {
      console.log('✅ Authentication working correctly');
    } else {
      console.log('❌ Authentication failed');
    }
  } catch (error) {
    console.error('❌ Authentication error:', error);
  }
};

const inventoryTestsExport = {
  runAllInventoryTests,
  testGPSOperations,
  testSIMCardOperations,
  testOtherProductsOperations,
  testProvidersOperations,
  testAuthenticationErrors
}

// Export for browser console testing
if (typeof window !== 'undefined') {
  (window as Window & { inventoryTests?: typeof inventoryTestsExport }).inventoryTests = inventoryTestsExport
}