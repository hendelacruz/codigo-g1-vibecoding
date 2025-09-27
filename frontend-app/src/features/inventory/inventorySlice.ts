import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { inventoryAPI } from './inventoryAPI'
import type { 
  InventoryState, 
  CreateGPSData, 
  CreateSIMCardData, 
  CreateOtroProductoData,
  AdjustStockData
} from './inventoryTypes'

const initialState: InventoryState = {
  gps: {
    items: [],
    isLoading: false,
    error: null,
  },
  simCards: {
    items: [],
    isLoading: false,
    error: null,
  },
  otrosProductos: {
    items: [],
    isLoading: false,
    error: null,
  },
  proveedores: {
    items: [],
    isLoading: false,
    error: null,
  },
}

// GPS Async Thunks
export const fetchGPSDevices = createAsyncThunk(
  'inventory/fetchGPSDevices',
  async (_, { rejectWithValue }) => {
    try {
      const result = await inventoryAPI.getGPSDevices()
      return result
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Error desconocido al obtener dispositivos GPS')
    }
  }
)

export const createGPS = createAsyncThunk(
  'inventory/createGPS',
  async (data: CreateGPSData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createGPS(data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to create GPS device')
    }
  }
)

export const updateGPS = createAsyncThunk(
  'inventory/updateGPS',
  async ({ id, data }: { id: number; data: Partial<CreateGPSData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateGPS(id, data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to update GPS device')
    }
  }
)

export const deleteGPS = createAsyncThunk(
  'inventory/deleteGPS',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteGPS(id)
      return id
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to delete GPS device')
    }
  }
)

export const toggleGPSState = createAsyncThunk(
  'inventory/toggleGPSState',
  async (id: number, { rejectWithValue }) => {
    try {
      const updatedGPS = await inventoryAPI.toggleGPSState(id)
      return updatedGPS
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to toggle GPS state')
    }
  }
)

// SIM Cards Async Thunks
export const fetchSIMCards = createAsyncThunk(
  'inventory/fetchSIMCards',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getSIMCards()
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to fetch SIM cards')
    }
  }
)

export const createSIMCard = createAsyncThunk(
  'inventory/createSIMCard',
  async (data: CreateSIMCardData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createSIMCard(data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to create SIM card')
    }
  }
)

export const updateSIMCard = createAsyncThunk(
  'inventory/updateSIMCard',
  async ({ id, data }: { id: number; data: Partial<CreateSIMCardData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateSIMCard(id, data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to update SIM card')
    }
  }
)

export const deleteSIMCard = createAsyncThunk(
  'inventory/deleteSIMCard',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteSIMCard(id)
      return id
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to delete SIM card')
    }
  }
)

// Otros Productos Async Thunks
export const fetchOtrosProductos = createAsyncThunk(
  'inventory/fetchOtrosProductos',
  async (_, { rejectWithValue }) => {
    try {
      const result = await inventoryAPI.getOtrosProductos()
      return result
    } catch (_error: unknown) {
      console.error('❌ fetchOtrosProductos: Error en consulta', _error)
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Error desconocido al obtener otros productos')
    }
  }
)

export const createOtroProducto = createAsyncThunk(
  'inventory/createOtroProducto',
  async (data: CreateOtroProductoData, { rejectWithValue }) => {
    try {
      return await inventoryAPI.createOtroProducto(data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to create producto')
    }
  }
)

export const updateOtroProducto = createAsyncThunk(
  'inventory/updateOtroProducto',
  async ({ id, data }: { id: number; data: Partial<CreateOtroProductoData> }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.updateOtroProducto(id, data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to update producto')
    }
  }
)

export const deleteOtroProducto = createAsyncThunk(
  'inventory/deleteOtroProducto',
  async (id: number, { rejectWithValue }) => {
    try {
      await inventoryAPI.deleteOtroProducto(id)
      return id
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to delete producto')
    }
  }
)

export const adjustStock = createAsyncThunk(
  'inventory/adjustStock',
  async ({ id, data }: { id: number; data: AdjustStockData }, { rejectWithValue }) => {
    try {
      return await inventoryAPI.adjustStock(id, data)
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to adjust stock')
    }
  }
)

// Proveedores Async Thunk
export const fetchProveedores = createAsyncThunk(
  'inventory/fetchProveedores',
  async (_, { rejectWithValue }) => {
    try {
      return await inventoryAPI.getProveedores()
    } catch (_error: unknown) {
      if (_error instanceof Error) {
        return rejectWithValue(_error.message)
      }
      return rejectWithValue('Failed to fetch proveedores')
    }
  }
)

const inventorySlice = createSlice({
  name: 'inventory',
  initialState,
  reducers: {
    clearInventoryErrors: (state) => {
      state.gps.error = null
      state.simCards.error = null
      state.otrosProductos.error = null
      state.proveedores.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // GPS reducers
      .addCase(fetchGPSDevices.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(fetchGPSDevices.fulfilled, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = null
        
        // Verificar si la respuesta es un array o necesita ser convertida
        if (Array.isArray(action.payload)) {
          state.gps.items = action.payload
        } else if (action.payload && typeof action.payload === 'object') {
          // Si la API devuelve un objeto con una propiedad que contiene el array
          const response = action.payload as { results?: unknown; data?: unknown };
          if ('results' in action.payload && Array.isArray(response.results)) {
            state.gps.items = response.results
          } else if ('data' in action.payload && Array.isArray(response.data)) {
            state.gps.items = response.data
          } else {
            // Si es un objeto pero no tiene las propiedades esperadas, convertir a array vacío
            console.warn('⚠️ API response is not an array and doesn\'t have expected properties')
            state.gps.items = []
          }
        } else {
          state.gps.items = []
        }
      })
      .addCase(fetchGPSDevices.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      .addCase(createGPS.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(createGPS.fulfilled, (state, action) => {
        state.gps.isLoading = false
        state.gps.items.push(action.payload)
      })
      .addCase(createGPS.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      .addCase(updateGPS.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(updateGPS.fulfilled, (state, action) => {
        state.gps.isLoading = false
        const index = state.gps.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.gps.items[index] = action.payload
        }
      })
      .addCase(updateGPS.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      .addCase(deleteGPS.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(deleteGPS.fulfilled, (state, action) => {
        state.gps.isLoading = false
        state.gps.items = state.gps.items.filter(item => item.id !== action.payload)
      })
      .addCase(deleteGPS.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      .addCase(toggleGPSState.pending, (state) => {
        state.gps.isLoading = true
        state.gps.error = null
      })
      .addCase(toggleGPSState.fulfilled, (state, action) => {
        state.gps.isLoading = false
        const index = state.gps.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.gps.items[index] = action.payload
        }
      })
      .addCase(toggleGPSState.rejected, (state, action) => {
        state.gps.isLoading = false
        state.gps.error = action.payload as string
      })
      // SIM Cards reducers
      .addCase(fetchSIMCards.pending, (state) => {
        state.simCards.isLoading = true
        state.simCards.error = null
      })
      .addCase(fetchSIMCards.fulfilled, (state, action) => {
        state.simCards.isLoading = false
        
        // Verificar si la respuesta es un array o necesita ser convertida
        if (Array.isArray(action.payload)) {
          state.simCards.items = action.payload
        } else if (action.payload && typeof action.payload === 'object') {
          // Si la API devuelve un objeto con una propiedad que contiene el array
          const response = action.payload as { results?: unknown; data?: unknown };
          if ('results' in action.payload && Array.isArray(response.results)) {
            state.simCards.items = response.results
          } else if ('data' in action.payload && Array.isArray(response.data)) {
            state.simCards.items = response.data
          } else {
            // Si es un objeto pero no tiene las propiedades esperadas, convertir a array vacío
            console.warn('⚠️ SIM Cards API response is not an array and doesn\'t have expected properties')
            state.simCards.items = []
          }
        } else {
          state.simCards.items = []
        }
      })
      .addCase(fetchSIMCards.rejected, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.error = action.payload as string
      })
      .addCase(createSIMCard.pending, (state) => {
        state.simCards.isLoading = true
        state.simCards.error = null
      })
      .addCase(createSIMCard.fulfilled, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.items.push(action.payload)
      })
      .addCase(createSIMCard.rejected, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.error = action.payload as string
      })
      .addCase(updateSIMCard.pending, (state) => {
        state.simCards.isLoading = true
        state.simCards.error = null
      })
      .addCase(updateSIMCard.fulfilled, (state, action) => {
        state.simCards.isLoading = false
        const index = state.simCards.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.simCards.items[index] = action.payload
        }
      })
      .addCase(updateSIMCard.rejected, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.error = action.payload as string
      })
      .addCase(deleteSIMCard.pending, (state) => {
        state.simCards.isLoading = true
        state.simCards.error = null
      })
      .addCase(deleteSIMCard.fulfilled, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.items = state.simCards.items.filter(item => item.id !== action.payload)
      })
      .addCase(deleteSIMCard.rejected, (state, action) => {
        state.simCards.isLoading = false
        state.simCards.error = action.payload as string
      })
      // Otros Productos reducers
      .addCase(fetchOtrosProductos.pending, (state) => {
        state.otrosProductos.isLoading = true
        state.otrosProductos.error = null
      })
      .addCase(fetchOtrosProductos.fulfilled, (state, action) => {
        state.otrosProductos.isLoading = false
        
        // Verificar si la respuesta es un array o necesita ser convertida
        if (Array.isArray(action.payload)) {
          state.otrosProductos.items = action.payload
        } else if (action.payload && typeof action.payload === 'object') {
          // Si la API devuelve un objeto con una propiedad que contiene el array
          const response = action.payload as { results?: unknown; data?: unknown };
          if ('results' in action.payload && Array.isArray(response.results)) {
            state.otrosProductos.items = response.results
          } else if ('data' in action.payload && Array.isArray(response.data)) {
            state.otrosProductos.items = response.data
          } else {
            // Si es un objeto pero no tiene las propiedades esperadas, convertir a array vacío
            console.warn('⚠️ Otros Productos API response is not an array and doesn\'t have expected properties')
            state.otrosProductos.items = []
          }
        } else {
          state.otrosProductos.items = []
        }
      })
      .addCase(fetchOtrosProductos.rejected, (state, action) => {
        state.otrosProductos.isLoading = false
        state.otrosProductos.error = action.payload as string
      })
      .addCase(createOtroProducto.fulfilled, (state, action) => {
        state.otrosProductos.items.push(action.payload)
      })
      .addCase(updateOtroProducto.fulfilled, (state, action) => {
        const index = state.otrosProductos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.otrosProductos.items[index] = action.payload
        }
      })
      .addCase(deleteOtroProducto.fulfilled, (state, action) => {
        state.otrosProductos.items = state.otrosProductos.items.filter(item => item.id !== action.payload)
      })
      .addCase(adjustStock.fulfilled, (state, action) => {
        const index = state.otrosProductos.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.otrosProductos.items[index] = action.payload
        }
      })
      // Proveedores reducers
      .addCase(fetchProveedores.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(fetchProveedores.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        
        // Verificar si la respuesta es un array o necesita ser convertida
        if (Array.isArray(action.payload)) {
          state.proveedores.items = action.payload
        } else if (action.payload && typeof action.payload === 'object') {
          // Si la API devuelve un objeto con una propiedad que contiene el array
          const response = action.payload as { results?: unknown; data?: unknown };
          if ('results' in action.payload && Array.isArray(response.results)) {
            state.proveedores.items = response.results
          } else if ('data' in action.payload && Array.isArray(response.data)) {
            state.proveedores.items = response.data
          } else {
            // Si es un objeto pero no tiene las propiedades esperadas, convertir a array vacío
            console.warn('⚠️ Proveedores API response is not an array and doesn\'t have expected properties')
            state.proveedores.items = []
          }
        } else {
          state.proveedores.items = []
        }
      })
      .addCase(fetchProveedores.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })
  },
})

export const { clearInventoryErrors } = inventorySlice.actions
export default inventorySlice.reducer