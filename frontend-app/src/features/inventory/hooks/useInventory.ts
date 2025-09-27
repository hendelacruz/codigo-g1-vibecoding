import { useSelector, useDispatch } from 'react-redux'
import { useCallback, useMemo } from 'react'
import type { RootState, AppDispatch } from '../../../app/store'
import {
  fetchGPSDevices,
  createGPS,
  updateGPS,
  deleteGPS,
  toggleGPSState,
  fetchSIMCards,
  createSIMCard,
  updateSIMCard,
  deleteSIMCard,
  fetchOtrosProductos,
  createOtroProducto,
  updateOtroProducto,
  deleteOtroProducto,
  adjustStock,
  fetchProveedores,
  clearInventoryErrors,
} from '../inventorySlice'
import type { 
  CreateGPSData, 
  CreateSIMCardData, 
  CreateOtroProductoData,
  AdjustStockData
} from '../inventoryTypes'

export const useInventory = () => {
  const dispatch = useDispatch<AppDispatch>()
  const inventory = useSelector((state: RootState) => state.inventory)

  // GPS operations
  const loadGPSDevices = useCallback(async () => {
    const result = await dispatch(fetchGPSDevices())
    return result
  }, [dispatch])

  const addGPS = useCallback(async (data: CreateGPSData) => {
    const result = await dispatch(createGPS(data))
    return result
  }, [dispatch])

  const editGPS = useCallback(async (id: number, data: Partial<CreateGPSData>) => {
    const result = await dispatch(updateGPS({ id, data }))
    return result
  }, [dispatch])

  const removeGPS = useCallback(async (id: number) => {
    const result = await dispatch(deleteGPS(id))
    return result
  }, [dispatch])

  const toggleGPSActive = useCallback(async (id: number) => {
    const result = await dispatch(toggleGPSState(id))
    return result
  }, [dispatch])

  // SIM Cards operations
  const loadSIMCards = useCallback(async () => {
    await dispatch(fetchSIMCards())
  }, [dispatch])

  const addSIMCard = useCallback(async (data: CreateSIMCardData) => {
    const result = await dispatch(createSIMCard(data))
    return result
  }, [dispatch])

  const editSIMCard = useCallback(async (id: number, data: Partial<CreateSIMCardData>) => {
    const result = await dispatch(updateSIMCard({ id, data }))
    return result
  }, [dispatch])

  const removeSIMCard = useCallback(async (id: number) => {
    const result = await dispatch(deleteSIMCard(id))
    return result
  }, [dispatch])

  // Otros Productos operations
  const loadOtrosProductos = useCallback(async () => {
    return dispatch(fetchOtrosProductos())
  }, [dispatch])

  const addOtroProducto = useCallback(async (data: CreateOtroProductoData) => {
    const result = await dispatch(createOtroProducto(data))
    return result
  }, [dispatch])

  const editOtroProducto = useCallback(async (id: number, data: Partial<CreateOtroProductoData>) => {
    const result = await dispatch(updateOtroProducto({ id, data }))
    return result
  }, [dispatch])

  const removeOtroProducto = useCallback(async (id: number) => {
    const result = await dispatch(deleteOtroProducto(id))
    return result
  }, [dispatch])

  const adjustProductStock = useCallback(async (id: number, data: AdjustStockData) => {
    const result = await dispatch(adjustStock({ id, data }))
    return result
  }, [dispatch])

  // Proveedores operations
  const loadProveedores = useCallback(async () => {
    await dispatch(fetchProveedores())
  }, [dispatch])

  const clearErrors = useCallback(() => {
    dispatch(clearInventoryErrors())
  }, [dispatch])

  return useMemo(() => ({
    ...inventory,
    // GPS
    loadGPSDevices,
    addGPS,
    editGPS,
    removeGPS,
    toggleGPSActive,
    // SIM Cards
    loadSIMCards,
    addSIMCard,
    editSIMCard,
    removeSIMCard,
    // Otros Productos
    loadOtrosProductos,
    addOtroProducto,
    editOtroProducto,
    removeOtroProducto,
    adjustProductStock,
    // Proveedores
    loadProveedores,
    // Utils
    clearErrors,
  }), [
    inventory,
    loadGPSDevices,
    addGPS,
    editGPS,
    removeGPS,
    toggleGPSActive,
    loadSIMCards,
    addSIMCard,
    editSIMCard,
    removeSIMCard,
    loadOtrosProductos,
    addOtroProducto,
    editOtroProducto,
    removeOtroProducto,
    adjustProductStock,
    loadProveedores,
    clearErrors,
  ])
}