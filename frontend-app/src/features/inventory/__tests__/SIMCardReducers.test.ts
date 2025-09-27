import { describe, it, expect, vi } from 'vitest'
import { configureStore } from '@reduxjs/toolkit'
import inventoryReducer, { updateSIMCard } from '../inventorySlice'
import type { SIMCard, CreateSIMCardData } from '../inventoryTypes'

// Mock the API
vi.mock('../inventoryAPI', () => ({
  inventoryAPI: {
    updateSIMCard: vi.fn()
  }
}))

const initialState = {
  gps: {
    items: [],
    isLoading: false,
    error: null
  },
  simCards: {
    items: [
      {
        id: 1,
        numero_chip: '123456789',
        numero_factura: 'FAC-001',
        icc: 'ICC123456789',
        plan: 'Plan Test',
        proveedor_id: 1,
        precio_compra: 100.50,
        estado: 'no_asignado',
        proceso: 'en_almacen',
        observaciones: 'Test SIM card',
        fecha_compra: '2024-01-01',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        is_active: true,
        estado_display: 'No Asignado'
      } as SIMCard
    ],
    isLoading: false,
    error: null
  },
  otrosProductos: {
    items: [],
    isLoading: false,
    error: null
  },
  proveedores: {
    items: [],
    isLoading: false,
    error: null
  }
}

describe('SIMCard Reducers', () => {
  it('should handle updateSIMCard.pending', () => {
    const action = { type: updateSIMCard.pending.type }
    const state = inventoryReducer(initialState, action)
    
    expect(state.simCards.isLoading).toBe(true)
    expect(state.simCards.error).toBe(null)
  })

  it('should handle updateSIMCard.fulfilled', () => {
    const updatedSIMCard: SIMCard = {
      id: 1,
      numero_chip: '987654321',
      numero_factura: 'FAC-001',
      icc: 'ICC123456789',
      plan: 'Plan Test Updated',
      proveedor_id: 1,
      precio_compra: 150.75,
      estado: 'asignado',
      proceso: 'en_produccion',
      observaciones: 'Updated SIM card',
      fecha_compra: '2024-01-01',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
      is_active: true,
      estado_display: 'Asignado'
    }

    const action = {
      type: updateSIMCard.fulfilled.type,
      payload: updatedSIMCard
    }
    
    const state = inventoryReducer(initialState, action)
    
    expect(state.simCards.isLoading).toBe(false)
    expect(state.simCards.error).toBe(null)
    expect(state.simCards.items[0]).toEqual(updatedSIMCard)
    expect(state.simCards.items[0]?.numero_chip).toBe('987654321')
    expect(state.simCards.items[0]?.precio_compra).toBe(150.75)
  })

  it('should handle updateSIMCard.rejected', () => {
    const errorMessage = 'Error al actualizar tarjeta SIM'
    const action = {
      type: updateSIMCard.rejected.type,
      payload: errorMessage
    }
    
    const state = inventoryReducer(initialState, action)
    
    expect(state.simCards.isLoading).toBe(false)
    expect(state.simCards.error).toBe(errorMessage)
    expect(state.simCards.items).toEqual(initialState.simCards.items)
  })

  it('should dispatch updateSIMCard async thunk correctly', async () => {
    const { inventoryAPI } = await import('../inventoryAPI')
    
    const mockUpdatedSIMCard: SIMCard = {
      id: 1,
      numero_chip: '987654321',
      numero_factura: 'FAC-001',
      icc: 'ICC123456789',
      plan: 'Plan Test Updated',
      proveedor_id: 1,
      precio_compra: 150.75,
      estado: 'asignado',
      proceso: 'en_produccion',
      observaciones: 'Updated SIM card',
      fecha_compra: '2024-01-01',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
      is_active: true,
      estado_display: 'Asignado'
    }

    vi.mocked(inventoryAPI.updateSIMCard).mockResolvedValue(mockUpdatedSIMCard)

    const store = configureStore({
      reducer: {
        inventory: inventoryReducer
      },
      preloadedState: {
        inventory: initialState
      }
    })

    const updateData: Partial<CreateSIMCardData> = {
      numero_chip: '987654321',
      plan: 'Plan Test Updated',
      precio_compra: 150.75,
      estado: 'asignado',
      proceso: 'en_produccion',
      observaciones: 'Updated SIM card'
    }

    const result = await store.dispatch(updateSIMCard({ id: 1, data: updateData }))
    
    expect(result.type).toBe('inventory/updateSIMCard/fulfilled')
    expect(result.payload).toEqual(mockUpdatedSIMCard)
    expect(inventoryAPI.updateSIMCard).toHaveBeenCalledWith(1, updateData)
    
    const state = store.getState()
    expect(state.inventory.simCards.items[0]).toEqual(mockUpdatedSIMCard)
  })

  it('should handle API errors in updateSIMCard async thunk', async () => {
    const { inventoryAPI } = await import('../inventoryAPI')
    
    const errorMessage = 'Error al actualizar tarjeta SIM'
    vi.mocked(inventoryAPI.updateSIMCard).mockRejectedValue(new Error(errorMessage))

    const store = configureStore({
      reducer: {
        inventory: inventoryReducer
      },
      preloadedState: {
        inventory: initialState
      }
    })

    const updateData: Partial<CreateSIMCardData> = {
      numero_chip: '987654321'
    }

    const result = await store.dispatch(updateSIMCard({ id: 1, data: updateData }))
    
    expect(result.type).toBe('inventory/updateSIMCard/rejected')
    expect(result.payload).toBe(errorMessage)
    
    const state = store.getState()
    expect(state.inventory.simCards.error).toBe(errorMessage)
    expect(state.inventory.simCards.isLoading).toBe(false)
  })
})