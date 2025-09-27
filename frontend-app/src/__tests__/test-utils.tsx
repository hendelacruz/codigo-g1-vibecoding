import React, { type ReactElement } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { store } from '@/app/store'

// Wrapper personalizado que incluye providers necesarios
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </Provider>
  )
}

// Función de render personalizada que incluye providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-exportar todo de testing-library
export * from '@testing-library/react'

// Sobrescribir el método render
export { customRender as render }

// Utilidades adicionales para tests
export const createMockUser = () => ({
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user' as const,
})

export const createMockGPSDevice = () => ({
  id: '1',
  imei: '123456789012345',
  modelo: 'Test Model',
  estado: 'activo' as const,
  fechaInstalacion: '2024-01-01',
  ubicacion: 'Test Location',
})

export const createMockSimCard = () => ({
  id: '1',
  numero: '1234567890',
  operadora: 'Test Operator',
  estado: 'activa' as const,
  fechaActivacion: '2024-01-01',
})

export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))