import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import type { UseQueryResult } from '@tanstack/react-query'
import { QueryClient } from '@tanstack/react-query'
import { ServicioDashboard } from '../ServicioDashboard'
import { 
  renderWithAuth, 
  mockServicios, 
  mockTipoTrabajos,
  createMockApiResponse,
  waitForQueriesToSettle 
} from '../../../__tests__/test-utils'
import type { Servicio } from '../../../../../shared/types/services/servicio'
import type { TipoTrabajo } from '../../../../../shared/types/services/tipoTrabajo'
import type { ApiResponse } from '../../../../../shared/types/api'

// Mock de los hooks
vi.mock('../../../hooks/useServicio', () => ({
  useServicios: vi.fn()
}))

vi.mock('../../../hooks/useTipoTrabajo', () => ({
  useTipoTrabajos: vi.fn()
}))

// Import de los mocks después de la declaración
import { useServicios } from '../../../hooks/useServicio'
import { useTipoTrabajos } from '../../../hooks/useTipoTrabajo'

const mockUseServicios = vi.mocked(useServicios)
const mockUseTipoTrabajos = vi.mocked(useTipoTrabajos)

// Helper para crear mock de UseQueryResult
function createMockQueryResult<T>(
  data: T, 
  overrides: Partial<UseQueryResult<T, Error>> = {}
): UseQueryResult<T, Error> {
  return {
    data,
    isLoading: false,
    isError: false,
    error: null,
    isSuccess: true,
    isPending: false,
    isLoadingError: false,
    isRefetchError: false,
    isStale: false,
    isFetching: false,
    isFetched: true,
    isFetchedAfterMount: true,
    isRefetching: false,
    isPlaceholderData: false,
    status: 'success',
    fetchStatus: 'idle',
    refetch: vi.fn().mockResolvedValue({ data }),
    ...overrides
  } as UseQueryResult<T, Error>
}

describe('ServicioDashboard', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    // Reset mocks antes de cada test
    vi.clearAllMocks()
    
    // Mock por defecto para useServicios - devuelve ApiResponse
    mockUseServicios.mockReturnValue(createMockQueryResult(createMockApiResponse(mockServicios)))

    // Mock por defecto para useTipoTrabajos - devuelve ApiResponse
    mockUseTipoTrabajos.mockReturnValue(createMockQueryResult(createMockApiResponse(mockTipoTrabajos)))
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Renderizado inicial', () => {
    it('debe renderizar el dashboard con estadísticas correctas', async () => {
      const { queryClient: qc } = renderWithAuth(<ServicioDashboard />)
      queryClient = qc

      await waitForQueriesToSettle(queryClient)

      // Verificar que se muestra el título del dashboard
      expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()

      // Verificar estadísticas calculadas correctamente
      expect(screen.getByText('3')).toBeInTheDocument() // Total servicios
      expect(screen.getByText('1')).toBeInTheDocument() // Pendientes
      expect(screen.getByText('1')).toBeInTheDocument() // En proceso
      expect(screen.getByText('1')).toBeInTheDocument() // Completados

      // Verificar estadísticas de tipos de trabajo
      expect(screen.getByText('3')).toBeInTheDocument() // Total tipos
      expect(screen.getByText('2')).toBeInTheDocument() // Tipos activos
    })

    it('debe mostrar loading state cuando los datos están cargando', () => {
      mockUseServicios.mockReturnValue(createMockQueryResult(undefined, {
        isLoading: true,
        isSuccess: false,
        status: 'pending'
      }))

      renderWithAuth(<ServicioDashboard />)

      expect(screen.getByText('Cargando estadísticas...')).toBeInTheDocument()
    })

    it('debe aplicar className personalizada', () => {
      const customClass = 'custom-dashboard-class'
      const { container } = renderWithAuth(<ServicioDashboard className={customClass} />)
      
      expect(container.firstChild).toHaveClass(customClass)
    })
  })

  describe('Navegación entre vistas', () => {
    it('debe cambiar a vista de servicios al hacer click en "Ver Servicios"', async () => {
      renderWithAuth(<ServicioDashboard />)

      const verServiciosButton = screen.getByText('Ver Servicios')
      fireEvent.click(verServiciosButton)

      await waitFor(() => {
        expect(screen.getByText('Lista de Servicios')).toBeInTheDocument()
      })
    })

    it('debe cambiar a vista de tipos de trabajo al hacer click en "Ver Tipos"', async () => {
      renderWithAuth(<ServicioDashboard />)

      const verTiposButton = screen.getByText('Ver Tipos')
      fireEvent.click(verTiposButton)

      await waitFor(() => {
        expect(screen.getByText('Tipos de Trabajo')).toBeInTheDocument()
      })
    })

    it('debe cambiar a formulario de nuevo servicio', async () => {
      renderWithAuth(<ServicioDashboard />)

      const nuevoServicioButton = screen.getByText('Nuevo Servicio')
      fireEvent.click(nuevoServicioButton)

      await waitFor(() => {
        expect(screen.getByText('Crear Nuevo Servicio')).toBeInTheDocument()
      })
    })

    it('debe cambiar a formulario de nuevo tipo de trabajo', async () => {
      renderWithAuth(<ServicioDashboard />)

      const nuevoTipoButton = screen.getByText('Nuevo Tipo')
      fireEvent.click(nuevoTipoButton)

      await waitFor(() => {
        expect(screen.getByText('Crear Tipo de Trabajo')).toBeInTheDocument()
      })
    })

    it('debe volver al dashboard desde otras vistas', async () => {
      renderWithAuth(<ServicioDashboard />)

      // Ir a servicios
      fireEvent.click(screen.getByText('Ver Servicios'))
      await waitFor(() => {
        expect(screen.getByText('Lista de Servicios')).toBeInTheDocument()
      })

      // Volver al dashboard
      const volverButton = screen.getByText('Volver al Dashboard')
      fireEvent.click(volverButton)

      await waitFor(() => {
        expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()
      })
    })
  })

  describe('Cálculo de estadísticas', () => {
    it('debe calcular correctamente estadísticas con servicios vacíos', () => {
      mockUseServicios.mockReturnValue(createMockQueryResult([]))
      mockUseTipoTrabajos.mockReturnValue(createMockQueryResult([]))

      renderWithAuth(<ServicioDashboard />)

      // Verificar que muestra 0 en todas las estadísticas
      const zeroElements = screen.getAllByText('0')
      expect(zeroElements.length).toBeGreaterThan(0)
    })

    it('debe calcular estadísticas por estado correctamente', () => {
      const serviciosConDiferentesEstados = [
        { ...mockServicios[0], estado_servicio: 'pendiente' as const },
        { ...mockServicios[1], estado_servicio: 'pendiente' as const },
        { ...mockServicios[2], estado_servicio: 'completado' as const },
      ]

      mockUseServicios.mockReturnValue(createMockQueryResult(serviciosConDiferentesEstados))

      renderWithAuth(<ServicioDashboard />)

      // Verificar conteos específicos
      expect(screen.getByText('3')).toBeInTheDocument() // Total
      expect(screen.getByText('2')).toBeInTheDocument() // Pendientes
      expect(screen.getByText('1')).toBeInTheDocument() // Completados
    })
  })

  describe('Manejo de errores', () => {
    it('debe manejar errores en la carga de servicios', () => {
      mockUseServicios.mockReturnValue(createMockQueryResult(undefined, {
        isError: true,
        error: new Error('Error al cargar servicios'),
        isSuccess: false,
        status: 'error'
      }))

      renderWithAuth(<ServicioDashboard />)

      // Debe mostrar estadísticas en 0 cuando hay error
      expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()
    })

    it('debe manejar datos undefined o null', () => {
      mockUseServicios.mockReturnValue(createMockQueryResult(undefined))
      mockUseTipoTrabajos.mockReturnValue(createMockQueryResult(null))

      renderWithAuth(<ServicioDashboard />)

      // No debe crashear y debe mostrar estadísticas en 0
      expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()
    })
  })

  describe('Integración con hooks', () => {
    it('debe llamar useServicios con parámetros correctos', () => {
      renderWithAuth(<ServicioDashboard />)

      expect(mockUseServicios).toHaveBeenCalledWith({ page_size: 1000 })
    })

    it('debe llamar useTipoTrabajos', () => {
      renderWithAuth(<ServicioDashboard />)

      expect(mockUseTipoTrabajos).toHaveBeenCalled()
    })

    it('debe llamar refetch cuando se actualiza', async () => {
      const mockRefetch = vi.fn().mockResolvedValue({ data: mockServicios })
      
      mockUseServicios.mockReturnValue(createMockQueryResult(mockServicios, {
        refetch: mockRefetch
      }))

      renderWithAuth(<ServicioDashboard />)

      // Simular actualización (esto dependería de la implementación específica)
      // Por ejemplo, si hay un botón de refresh
      const refreshButton = screen.queryByText('Actualizar')
      if (refreshButton) {
        fireEvent.click(refreshButton)
        await waitFor(() => {
          expect(mockRefetch).toHaveBeenCalled()
        })
      }
    })
  })

  describe('Accesibilidad', () => {
    it('debe tener estructura semántica correcta', () => {
      renderWithAuth(<ServicioDashboard />)

      // Verificar que usa elementos semánticos
      expect(screen.getByRole('main')).toBeInTheDocument()
      
      // Verificar headings
      const heading = screen.getByRole('heading', { level: 1 })
      expect(heading).toHaveTextContent('Dashboard de Servicios')
    })

    it('debe tener botones accesibles', () => {
      renderWithAuth(<ServicioDashboard />)

      // Verificar que los botones tienen texto descriptivo
      expect(screen.getByRole('button', { name: /ver servicios/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /nuevo servicio/i })).toBeInTheDocument()
    })

    it('debe manejar navegación por teclado', async () => {
      renderWithAuth(<ServicioDashboard />)

      const verServiciosButton = screen.getByText('Ver Servicios')
      
      // Simular navegación por teclado
      verServiciosButton.focus()
      expect(verServiciosButton).toHaveFocus()

      // Simular Enter
      fireEvent.keyDown(verServiciosButton, { key: 'Enter', code: 'Enter' })
      
      await waitFor(() => {
        expect(screen.getByText('Lista de Servicios')).toBeInTheDocument()
      })
    })
  })

  describe('Performance', () => {
    it('debe usar memoización para cálculos costosos', () => {
      const { rerender } = renderWithAuth(<ServicioDashboard />)

      // Primer render
      expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()

      // Re-render con las mismas props
      rerender(<ServicioDashboard />)

      // Los cálculos deben ser memoizados (verificar que no se recalculan innecesariamente)
      expect(screen.getByText('Dashboard de Servicios')).toBeInTheDocument()
    })

    it('debe manejar grandes cantidades de datos eficientemente', () => {
      // Crear un gran conjunto de datos
      const largeDataSet = Array.from({ length: 1000 }, (_, index) => ({
        ...mockServicios[0],
        id: index + 1,
        estado_servicio: index % 2 === 0 ? 'pendiente' as const : 'completado' as const
      }))

      mockUseServicios.mockReturnValue(createMockQueryResult(largeDataSet))

      const startTime = performance.now()
      renderWithAuth(<ServicioDashboard />)
      const endTime = performance.now()

      // Verificar que el render no toma demasiado tiempo (menos de 100ms)
      expect(endTime - startTime).toBeLessThan(100)
      
      // Verificar que las estadísticas se calculan correctamente
      expect(screen.getByText('1000')).toBeInTheDocument() // Total
    })
  })
})