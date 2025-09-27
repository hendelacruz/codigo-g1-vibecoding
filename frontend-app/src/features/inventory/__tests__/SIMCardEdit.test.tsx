import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { SIMCardForm } from '../components/SIMCardForm'
import inventoryReducer from '../inventorySlice'
import type { SIMCard, Proveedor } from '../inventoryTypes'

// Mock the API
vi.mock('../inventoryAPI', () => ({
  inventoryAPI: {
    updateSIMCard: vi.fn(),
    getProveedores: vi.fn()
  }
}))

// Mock toast notifications
vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

const mockStore = configureStore({
  reducer: {
    inventory: inventoryReducer
  },
  preloadedState: {
    inventory: {
      gps: {
        items: [],
        isLoading: false,
        error: null
      },
      simCards: {
        items: [],
        isLoading: false,
        error: null
      },
      otrosProductos: {
        items: [],
        isLoading: false,
        error: null
      },
      proveedores: {
        items: [
          { id: 1, nombre: 'Proveedor Test', telefono: '123456789', is_active: true }
        ] as Proveedor[],
        isLoading: false,
        error: null
      }
    }
  }
})

const mockSIMCard: SIMCard = {
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
}

describe('SIMCard Edit Functionality', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should load SIM card data for editing', async () => {
    render(
      <Provider store={mockStore}>
        <SIMCardForm 
          simCard={mockSIMCard}
          onSave={vi.fn()}
          onCancel={vi.fn()}
        />
      </Provider>
    )

    // Verify form is populated with SIM card data
    expect(screen.getByDisplayValue('123456789')).toBeInTheDocument()
    expect(screen.getByDisplayValue('100.5')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Test SIM card')).toBeInTheDocument()
  })

  it('should submit edit form with PUT method', async () => {
    const mockOnSave = vi.fn()
    const { inventoryAPI } = await import('../inventoryAPI')
    
    // Mock successful API response
    vi.mocked(inventoryAPI.updateSIMCard).mockResolvedValue({
      ...mockSIMCard,
      numero_chip: '987654321'
    })

    render(
      <Provider store={mockStore}>
        <SIMCardForm 
          simCard={mockSIMCard}
          onSave={mockOnSave}
          onCancel={vi.fn()}
        />
      </Provider>
    )

    // Change the number field
    const numeroInput = screen.getByDisplayValue('123456789')
    fireEvent.change(numeroInput, { target: { value: '987654321' } })

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /actualizar/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      // Verify the API was called with correct parameters
      expect(inventoryAPI.updateSIMCard).toHaveBeenCalledWith(1, {
        numero: '987654321',
        proveedor: 1,
        precio_compra: 100.5,
        estado: 'disponible',
        observaciones: 'Test SIM card',
        fecha_compra: '2024-01-01'
      })
    })
  })

  it('should handle edit form validation errors', async () => {
    render(
      <Provider store={mockStore}>
        <SIMCardForm 
          simCard={mockSIMCard}
          onSave={vi.fn()}
          onCancel={vi.fn()}
        />
      </Provider>
    )

    // Clear required field
    const numeroInput = screen.getByDisplayValue('123456789')
    fireEvent.change(numeroInput, { target: { value: '' } })

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /actualizar/i })
    fireEvent.click(submitButton)

    // Verify validation error is shown
    await waitFor(() => {
      expect(screen.getByText(/número es requerido/i)).toBeInTheDocument()
    })
  })

  it('should handle API errors during edit', async () => {
    const { inventoryAPI } = await import('../inventoryAPI')
    const { toast } = await import('react-hot-toast')
    
    // Mock API error
    vi.mocked(inventoryAPI.updateSIMCard).mockRejectedValue(
      new Error('Error al actualizar tarjeta SIM')
    )

    render(
      <Provider store={mockStore}>
        <SIMCardForm 
          simCard={mockSIMCard}
          onSave={vi.fn()}
          onCancel={vi.fn()}
        />
      </Provider>
    )

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /actualizar/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      // Verify error toast is shown
      expect(toast.error).toHaveBeenCalledWith('Error al actualizar tarjeta SIM')
    })
  })
})