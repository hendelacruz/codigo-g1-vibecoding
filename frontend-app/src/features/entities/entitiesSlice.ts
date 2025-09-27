import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { entitiesAPI } from './entitiesAPI'
import type { 
  EntitiesState, 
  CreateClienteData, 
  CreateUnidadData, 
  CreateProveedorData,
  UpdateClienteData,
  UpdateUnidadData,
  UpdateProveedorData,
  ClienteFilters,
  UnidadFilters,
  ProveedorFilters
} from './entitiesTypes'

const initialState: EntitiesState = {
  clientes: {
    items: [],
    isLoading: false,
    error: null,
  },
  unidades: {
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

// ==================== CLIENTES ASYNC THUNKS ====================

export const fetchClientes = createAsyncThunk(
  'entities/fetchClientes',
  async (filters: ClienteFilters | undefined, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.getClientes(filters)
      return result
    } catch (error: unknown) {
      console.error('❌ fetchClientes: Error en consulta', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error desconocido al obtener clientes')
    }
  }
)

export const fetchCliente = createAsyncThunk(
  'entities/fetchCliente',
  async (id: number, { rejectWithValue }) => {
    try {
      return await entitiesAPI.getCliente(id)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener cliente')
    }
  }
)

export const createCliente = createAsyncThunk(
  'entities/createCliente',
  async (data: CreateClienteData, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.createCliente(data)
      return result
    } catch (error: unknown) {
      console.error('❌ createCliente: Error al crear cliente', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al crear cliente')
    }
  }
)

export const updateCliente = createAsyncThunk(
  'entities/updateCliente',
  async ({ id, data }: { id: number; data: UpdateClienteData }, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.updateCliente(id, data)
      return result
    } catch (error: unknown) {
      console.error('❌ updateCliente: Error al actualizar cliente', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al actualizar cliente')
    }
  }
)

export const deleteCliente = createAsyncThunk(
  'entities/deleteCliente',
  async (id: number, { rejectWithValue }) => {
    try {
      await entitiesAPI.deleteCliente(id)
      return id
    } catch (error: unknown) {
      console.error('❌ deleteCliente: Error al eliminar cliente', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al eliminar cliente')
    }
  }
)

export const toggleClienteActive = createAsyncThunk(
  'entities/toggleClienteActive',
  async (id: number, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.toggleClienteActive(id)
      return result
    } catch (error: unknown) {
      console.error('❌ toggleClienteActive: Error al cambiar estado del cliente', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al cambiar estado del cliente')
    }
  }
)

export const fetchClienteUnidades = createAsyncThunk(
  'entities/fetchClienteUnidades',
  async (id: number, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.getClienteUnidades(id)
      return { clienteId: id, unidades: result }
    } catch (error: unknown) {
      console.error('❌ fetchClienteUnidades: Error al obtener unidades del cliente', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener unidades del cliente')
    }
  }
)

// ==================== UNIDADES ASYNC THUNKS ====================

export const fetchUnidades = createAsyncThunk(
  'entities/fetchUnidades',
  async (filters: UnidadFilters | undefined, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.getUnidades(filters)
      return result
    } catch (error: unknown) {
      console.error('❌ fetchUnidades: Error en consulta', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error desconocido al obtener unidades')
    }
  }
)

export const fetchUnidad = createAsyncThunk(
  'entities/fetchUnidad',
  async (id: number, { rejectWithValue }) => {
    try {
      return await entitiesAPI.getUnidad(id)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener unidad')
    }
  }
)

export const createUnidad = createAsyncThunk(
  'entities/createUnidad',
  async (data: CreateUnidadData, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.createUnidad(data)
      return result
    } catch (error: unknown) {
      console.error('❌ createUnidad: Error al crear unidad', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al crear unidad')
    }
  }
)

export const updateUnidad = createAsyncThunk(
  'entities/updateUnidad',
  async ({ id, data }: { id: number; data: UpdateUnidadData }, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.updateUnidad(id, data)
      return result
    } catch (error: unknown) {
      console.error('❌ updateUnidad: Error al actualizar unidad', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al actualizar unidad')
    }
  }
)

export const deleteUnidad = createAsyncThunk(
  'entities/deleteUnidad',
  async (id: number, { rejectWithValue }) => {
    try {
      await entitiesAPI.deleteUnidad(id)
      return id
    } catch (error: unknown) {
      console.error('❌ deleteUnidad: Error al eliminar unidad', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al eliminar unidad')
    }
  }
)

export const toggleUnidadActive = createAsyncThunk(
  'entities/toggleUnidadActive',
  async (id: number, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.toggleUnidadActive(id)
      return result
    } catch (error: unknown) {
      console.error('❌ toggleUnidadActive: Error al cambiar estado de unidad', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al cambiar estado de unidad')
    }
  }
)

// ==================== PROVEEDORES ASYNC THUNKS ====================

export const fetchProveedoresEntity = createAsyncThunk(
  'entities/fetchProveedoresEntity',
  async (filters: ProveedorFilters | undefined, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.getProveedores(filters)
      return result
    } catch (error: unknown) {
      console.error('❌ fetchProveedoresEntity: Error en consulta', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error desconocido al obtener proveedores')
    }
  }
)

export const createProveedorEntity = createAsyncThunk(
  'entities/createProveedorEntity',
  async (data: CreateProveedorData, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.createProveedor(data)
      return result
    } catch (error: unknown) {
      console.error('❌ createProveedorEntity: Error al crear proveedor', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al crear proveedor')
    }
  }
)

export const updateProveedorEntity = createAsyncThunk(
  'entities/updateProveedorEntity',
  async ({ id, data }: { id: number; data: UpdateProveedorData }, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.updateProveedor(id, data)
      return result
    } catch (error: unknown) {
      console.error('❌ updateProveedorEntity: Error al actualizar proveedor', error)
      
      // Propagar el mensaje de error específico desde la API
      if (error instanceof Error) {
        console.error('❌ updateProveedorEntity: Mensaje de error:', error.message)
        return rejectWithValue(error.message)
      }
      
      // Fallback para errores no tipados
      const errorMessage = typeof error === 'string' ? error : 'Error desconocido al actualizar proveedor'
      console.error('❌ updateProveedorEntity: Error no tipado:', errorMessage)
      return rejectWithValue(errorMessage)
    }
  }
)

export const fetchProveedor = createAsyncThunk(
  'entities/fetchProveedor',
  async (id: number, { rejectWithValue }) => {
    try {
      return await entitiesAPI.getProveedor(id)
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener proveedor')
    }
  }
)

export const deleteProveedor = createAsyncThunk(
  'entities/deleteProveedor',
  async (id: number, { rejectWithValue }) => {
    try {
      await entitiesAPI.deleteProveedor(id)
      return id
    } catch (error: unknown) {
      console.error('❌ deleteProveedor: Error al eliminar proveedor', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al eliminar proveedor')
    }
  }
)

export const toggleProveedorActive = createAsyncThunk(
  'entities/toggleProveedorActive',
  async (id: number, { rejectWithValue }) => {
    try {
      const result = await entitiesAPI.toggleProveedorActive(id)
      return result
    } catch (error: unknown) {
      console.error('❌ toggleProveedorActive: Error al cambiar estado de proveedor', error)
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al cambiar estado de proveedor')
    }
  }
)

// ==================== UTILITY THUNKS ====================

export const fetchClientesActivos = createAsyncThunk(
  'entities/fetchClientesActivos',
  async (_, { rejectWithValue }) => {
    try {
      return await entitiesAPI.getClientesActivos()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener clientes activos')
    }
  }
)

export const fetchProveedoresActivos = createAsyncThunk(
  'entities/fetchProveedoresActivos',
  async (_, { rejectWithValue }) => {
    try {
      return await entitiesAPI.getProveedoresActivos()
    } catch (error: unknown) {
      if (error instanceof Error) {
        return rejectWithValue(error.message)
      }
      return rejectWithValue('Error al obtener proveedores activos')
    }
  }
)

// ==================== SLICE DEFINITION ====================

const entitiesSlice = createSlice({
  name: 'entities',
  initialState,
  reducers: {
    clearEntitiesErrors: (state) => {
      state.clientes.error = null
      state.unidades.error = null
      state.proveedores.error = null
    },
    clearClientesError: (state) => {
      state.clientes.error = null
    },
    clearUnidadesError: (state) => {
      state.unidades.error = null
    },
    clearProveedoresError: (state) => {
      state.proveedores.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // ==================== CLIENTES REDUCERS ====================
      .addCase(fetchClientes.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(fetchClientes.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.items = action.payload
      })
      .addCase(fetchClientes.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(fetchCliente.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(fetchCliente.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        // Update existing item or add if not exists
        const index = state.clientes.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.clientes.items[index] = action.payload
        } else {
          state.clientes.items.push(action.payload)
        }
      })
      .addCase(fetchCliente.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(createCliente.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(createCliente.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.items.push(action.payload)
      })
      .addCase(createCliente.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(updateCliente.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(updateCliente.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        const index = state.clientes.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.clientes.items[index] = action.payload
        }
      })
      .addCase(updateCliente.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(deleteCliente.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(deleteCliente.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.items = state.clientes.items.filter(item => item.id !== action.payload)
      })
      .addCase(deleteCliente.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(toggleClienteActive.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(toggleClienteActive.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        const index = state.clientes.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.clientes.items[index] = action.payload
        }
      })
      .addCase(toggleClienteActive.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(fetchClienteUnidades.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(fetchClienteUnidades.fulfilled, (state) => {
        state.clientes.isLoading = false
        // Las unidades del cliente se pueden almacenar en un estado separado si es necesario
        // Por ahora solo actualizamos el estado de loading
      })
      .addCase(fetchClienteUnidades.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      .addCase(fetchClientesActivos.pending, (state) => {
        state.clientes.isLoading = true
        state.clientes.error = null
      })
      .addCase(fetchClientesActivos.fulfilled, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.items = action.payload
      })
      .addCase(fetchClientesActivos.rejected, (state, action) => {
        state.clientes.isLoading = false
        state.clientes.error = action.payload as string
      })

      // ==================== UNIDADES REDUCERS ====================
      .addCase(fetchUnidades.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(fetchUnidades.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.items = action.payload
      })
      .addCase(fetchUnidades.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      .addCase(fetchUnidad.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(fetchUnidad.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        const index = state.unidades.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.unidades.items[index] = action.payload
        } else {
          state.unidades.items.push(action.payload)
        }
      })
      .addCase(fetchUnidad.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      .addCase(createUnidad.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(createUnidad.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.items.push(action.payload)
      })
      .addCase(createUnidad.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      .addCase(updateUnidad.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(updateUnidad.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        const index = state.unidades.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.unidades.items[index] = action.payload
        }
      })
      .addCase(updateUnidad.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      .addCase(deleteUnidad.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(deleteUnidad.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.items = state.unidades.items.filter(item => item.id !== action.payload)
      })
      .addCase(deleteUnidad.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      .addCase(toggleUnidadActive.pending, (state) => {
        state.unidades.isLoading = true
        state.unidades.error = null
      })
      .addCase(toggleUnidadActive.fulfilled, (state, action) => {
        state.unidades.isLoading = false
        const index = state.unidades.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.unidades.items[index] = action.payload
        }
      })
      .addCase(toggleUnidadActive.rejected, (state, action) => {
        state.unidades.isLoading = false
        state.unidades.error = action.payload as string
      })

      // ==================== PROVEEDORES REDUCERS ====================
      .addCase(fetchProveedoresEntity.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(fetchProveedoresEntity.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.items = action.payload
      })
      .addCase(fetchProveedoresEntity.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })

      .addCase(createProveedorEntity.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(createProveedorEntity.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.items.push(action.payload)
      })
      .addCase(createProveedorEntity.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })

      .addCase(updateProveedorEntity.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(updateProveedorEntity.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        const index = state.proveedores.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.proveedores.items[index] = action.payload
        }
      })
      .addCase(updateProveedorEntity.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })

      .addCase(fetchProveedor.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(fetchProveedor.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        const index = state.proveedores.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.proveedores.items[index] = action.payload
        } else {
          state.proveedores.items.push(action.payload)
        }
      })
      .addCase(fetchProveedor.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })

      .addCase(deleteProveedor.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(deleteProveedor.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.items = state.proveedores.items.filter(item => item.id !== action.payload)
      })
      .addCase(deleteProveedor.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })

      .addCase(toggleProveedorActive.pending, (state) => {
        state.proveedores.isLoading = true
        state.proveedores.error = null
      })
      .addCase(toggleProveedorActive.fulfilled, (state, action) => {
        state.proveedores.isLoading = false
        const index = state.proveedores.items.findIndex(item => item.id === action.payload.id)
        if (index !== -1) {
          state.proveedores.items[index] = action.payload
        }
      })
      .addCase(toggleProveedorActive.rejected, (state, action) => {
        state.proveedores.isLoading = false
        state.proveedores.error = action.payload as string
      })
  },
})

// Export actions
export const { 
  clearEntitiesErrors, 
  clearClientesError, 
  clearUnidadesError, 
  clearProveedoresError 
} = entitiesSlice.actions

// Export reducer
export default entitiesSlice.reducer