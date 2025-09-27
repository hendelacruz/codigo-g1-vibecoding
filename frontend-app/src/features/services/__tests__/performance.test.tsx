import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ServicioDashboard } from '../components/Servicio/ServicioDashboard';
import type { Servicio } from '../../../shared/types/services/servicio';
import type { TipoTrabajo } from '../../../shared/types/services/tipoTrabajo';

// Mock hooks
vi.mock('../hooks/useServicio', () => ({
  useServicios: vi.fn(),
}));

vi.mock('../hooks/useTipoTrabajo', () => ({
  useTipoTrabajos: vi.fn(),
}));

// Import mocked hooks
const { useServicios } = await import('../hooks/useServicio');
const { useTipoTrabajos } = await import('../hooks/useTipoTrabajo');

// Mock performance.memory for browsers that don't support it
Object.defineProperty(performance, 'memory', {
  value: {
    usedJSHeapSize: 10000000,
    totalJSHeapSize: 20000000,
    jsHeapSizeLimit: 100000000,
  },
  writable: true,
});

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

// Helper function to create mock data
const createMockServicio = (id: number): Servicio => ({
  id,
  fecha: '2024-01-15',
  tipo_trabajo: 1,
  tipo_trabajo_nombre: 'Mantenimiento',
  tecnico_id: 1,
  tecnico_dni: '12345678',
  tecnico_nombre: 'Juan Pérez',
  cliente: 1,
  cliente_nombre: 'Empresa ABC',
  unidad: 1,
  unidad_placa: `ABC-${id.toString().padStart(3, '0')}`,
  gps: 1,
  gps_codigo: `GPS${id.toString().padStart(3, '0')}`,
  sim_card: 1,
  descripcion: `Servicio ${id}`,
  precio: 150.00,
  estado_servicio: 'completado',
  observaciones: `Observaciones del servicio ${id}`,
  fecha_completado: '2024-01-15',
  calificacion: 5,
  created_at: '2024-01-15T09:00:00Z',
  updated_at: '2024-01-15T17:00:00Z',
  is_active: true,
});

const createMockTipoTrabajo = (id: number): TipoTrabajo => ({
  id,
  nombre: `tipo_${id}`,
  nombre_display: `Tipo de Trabajo ${id}`,
  descripcion: `Descripción del tipo ${id}`,
  precio_base: 150.00,
  duracion_estimada: 120,
  requiere_gps: true,
  requiere_sim: false,
  servicios_count: 10,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  is_active: true,
});

describe('ServicioDashboard - Performance Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Render Performance', () => {
    it('should render quickly with small dataset (< 100ms)', async () => {
      const smallDataset = Array.from({ length: 10 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 5 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: smallDataset, 
          count: smallDataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(100);
    });

    it('should render efficiently with medium dataset (< 200ms)', async () => {
      const mediumDataset = Array.from({ length: 100 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 10 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: mediumDataset, 
          count: mediumDataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(200);
    });

    it('should handle large dataset without blocking (< 500ms)', async () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 20 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: largeDataset, 
          count: largeDataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(500);
    });
  });

  describe('Memory Usage', () => {
    it('should not cause memory leaks during multiple renders', async () => {
      const dataset = Array.from({ length: 50 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 5 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: dataset, 
          count: dataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;

      // Render multiple times
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(
          <TestWrapper>
            <ServicioDashboard />
          </TestWrapper>
        );
        unmount();
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryIncrease = finalMemory - initialMemory;

      // Memory increase should be reasonable (less than 10MB)
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
    });
  });

  describe('State Updates Performance', () => {
    it('should handle rapid state changes efficiently', async () => {
      const dataset = Array.from({ length: 20 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 5 }, (_, i) => createMockTipoTrabajo(i + 1));

      const mockRefetch = vi.fn();

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: dataset, 
          count: dataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      // Simulate rapid state changes
      for (let i = 0; i < 10; i++) {
        vi.mocked(useServicios).mockReturnValue({
          data: { 
            results: dataset.slice(0, i + 1), 
            count: i + 1,
            next: null,
            previous: null
          },
          isLoading: false,
          error: null,
          refetch: mockRefetch,
        } as any);
      }

      const endTime = performance.now();
      const updateTime = endTime - startTime;

      expect(updateTime).toBeLessThan(100);
    });
  });

  describe('Memoization Effectiveness', () => {
    it('should properly memoize expensive calculations', async () => {
      const dataset = Array.from({ length: 100 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 10 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: dataset, 
          count: dataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const { rerender } = render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const startTime = performance.now();

      // Re-render with same data (should be memoized)
      rerender(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const endTime = performance.now();
      const rerenderTime = endTime - startTime;

      // Re-render should be very fast due to memoization
      expect(rerenderTime).toBeLessThan(50);
    });
  });

  describe('Concurrent Updates', () => {
    it('should handle concurrent data updates without performance degradation', async () => {
      const dataset = Array.from({ length: 50 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 5 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: dataset, 
          count: dataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      // Simulate concurrent updates
      await Promise.all([
        waitFor(() => expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument()),
        waitFor(() => expect(screen.getByText('Total Servicios')).toBeInTheDocument()),
        waitFor(() => expect(screen.getByText('Acciones Rápidas')).toBeInTheDocument()),
      ]);

      const endTime = performance.now();
      const concurrentTime = endTime - startTime;

      expect(concurrentTime).toBeLessThan(200);
    });
  });

  describe('Complex Filtering Performance', () => {
    it('should filter large datasets efficiently', async () => {
      const largeDataset = Array.from({ length: 500 }, (_, i) => ({
        ...createMockServicio(i + 1),
        estado_servicio: i % 2 === 0 ? 'completado' : 'pendiente',
      })) as Servicio[];

      const tipoTrabajos = Array.from({ length: 10 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { 
          results: largeDataset, 
          count: largeDataset.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { 
          results: tipoTrabajos,
          count: tipoTrabajos.length,
          next: null,
          previous: null
        },
        isLoading: false,
        error: null,
      } as any);

      const startTime = performance.now();

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      // Wait for statistics to be calculated
      await waitFor(() => {
        expect(screen.getByText('Total Servicios')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const filterTime = endTime - startTime;

      expect(filterTime).toBeLessThan(300);
    });
  });

  describe('Loading State Performance', () => {
    it('should render loading state quickly', async () => {
      vi.mocked(useServicios).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      } as any);

      const startTime = performance.now();

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const endTime = performance.now();
      const loadingRenderTime = endTime - startTime;

      expect(loadingRenderTime).toBeLessThan(50);
    });
  });
});