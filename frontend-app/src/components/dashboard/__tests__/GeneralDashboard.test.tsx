import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { GeneralDashboard } from '../GeneralDashboard'

// Mock de la función onModuleSelect
const mockOnModuleSelect = jest.fn()

describe('GeneralDashboard', () => {
  beforeEach(() => {
    mockOnModuleSelect.mockClear()
  })

  it('renders the dashboard title correctly', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    expect(screen.getByText('Sistema de Gestión Vehicular')).toBeInTheDocument()
    expect(screen.getByText('Plataforma integral para el control y monitoreo de flotas')).toBeInTheDocument()
  })

  it('renders all vehicle images', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    // Verificar que las imágenes de vehículos estén presentes
    const vehicleImages = screen.getAllByRole('img')
    expect(vehicleImages).toHaveLength(3) // Bus, Camión, Auto
  })

  it('renders all module cards with correct titles', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    const expectedModules = [
      'Autenticación',
      'Compras/Inventario',
      'Clientes',
      'Proveedores',
      'Unidades',
      'Servicios',
      'Ventas',
      'Reportes'
    ]

    expectedModules.forEach(moduleName => {
      expect(screen.getByText(moduleName)).toBeInTheDocument()
    })
  })

  it('calls onModuleSelect when a module is clicked', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    // Click en el módulo de Autenticación
    const authModule = screen.getByText('Autenticación').closest('div')
    fireEvent.click(authModule!)
    
    expect(mockOnModuleSelect).toHaveBeenCalledWith('auth')
  })

  it('calls onModuleSelect with correct module IDs for all modules', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    const moduleTests = [
      { text: 'Autenticación', expectedId: 'auth' },
      { text: 'Compras/Inventario', expectedId: 'inventory' },
      { text: 'Clientes', expectedId: 'clientes' },
      { text: 'Proveedores', expectedId: 'proveedores' },
      { text: 'Unidades', expectedId: 'unidades' },
      { text: 'Servicios', expectedId: 'services' },
      { text: 'Ventas', expectedId: 'sales' },
      { text: 'Reportes', expectedId: 'reports' }
    ]

    moduleTests.forEach(({ text, expectedId }) => {
      const moduleElement = screen.getByText(text).closest('div')
      fireEvent.click(moduleElement!)
      expect(mockOnModuleSelect).toHaveBeenCalledWith(expectedId)
    })
  })

  it('applies hover effects to module cards', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    const authModule = screen.getByText('Autenticación').closest('div')
    expect(authModule).toHaveClass('hover:scale-105')
    expect(authModule).toHaveClass('transition-all')
  })

  it('has proper accessibility attributes', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    // Verificar que los módulos sean clickeables
    const moduleCards = screen.getAllByRole('button')
    expect(moduleCards.length).toBeGreaterThan(0)
  })

  it('renders with proper responsive classes', () => {
    render(<GeneralDashboard onModuleSelect={mockOnModuleSelect} />)
    
    // Verificar que el contenedor principal tenga clases responsive
    const mainContainer = screen.getByText('Sistema de Gestión Vehicular').closest('div')
    expect(mainContainer).toHaveClass('min-h-screen')
  })
})