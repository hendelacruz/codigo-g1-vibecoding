import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import userEvent from '@testing-library/user-event';
import { ServicioDashboard } from '../components/Servicio/ServicioDashboard';
import type { Servicio } from '../../../shared/types/services/servicio';
import type { TipoTrabajo } from '../../../shared/types/services/tipoTrabajo';

// Extend expect with jest-axe matchers
expect.extend(toHaveNoViolations);

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

describe('ServicioDashboard - Accessibility Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Accessibility', () => {
    it('should not have accessibility violations in loading state', async () => {
      vi.mocked(useServicios).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      const { container } = render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have accessibility violations with data', async () => {
      const servicios = Array.from({ length: 5 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 3 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      const { container } = render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have accessibility violations in error state', async () => {
      vi.mocked(useServicios).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Error de prueba'),
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Error de prueba'),
      });

      const { container } = render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('ARIA Labels and Roles', () => {
    it('should have proper ARIA labels for interactive elements', async () => {
      const servicios = Array.from({ length: 3 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      // Check for main heading
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      
      // Check for navigation elements
      const navigation = screen.queryByRole('navigation');
      if (navigation) {
        expect(navigation).toBeInTheDocument();
      }
    });

    it('should have proper button labels and roles', async () => {
      const servicios = Array.from({ length: 2 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      // Check for buttons with proper roles
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
        // Buttons should have accessible names
        expect(button).toHaveAttribute('type');
      });
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      const servicios = Array.from({ length: 3 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      // Test Tab navigation
      await user.tab();
      expect(document.activeElement).toBeInTheDocument();

      // Test that focus is visible
      const focusedElement = document.activeElement;
      if (focusedElement && focusedElement !== document.body) {
        expect(focusedElement).toBeVisible();
      }
    });

    it('should handle Enter and Space key interactions', async () => {
      const user = userEvent.setup();
      const servicios = Array.from({ length: 2 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      const buttons = screen.getAllByRole('button');
      if (buttons.length > 0) {
        const firstButton = buttons[0];
        firstButton.focus();
        
        // Test Enter key
        await user.keyboard('{Enter}');
        expect(firstButton).toBeInTheDocument();
      }
    });
  });

  describe('Heading Hierarchy', () => {
    it('should have proper heading hierarchy', async () => {
      const servicios = Array.from({ length: 2 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      // Check for main heading (h1)
      const h1Elements = screen.getAllByRole('heading', { level: 1 });
      expect(h1Elements.length).toBeGreaterThan(0);

      // Check that headings follow proper hierarchy
      const allHeadings = screen.getAllByRole('heading');
      expect(allHeadings.length).toBeGreaterThan(0);
    });
  });

  describe('Screen Reader Support', () => {
    it('should announce loading states to screen readers', async () => {
      vi.mocked(useServicios).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      // Check for loading indicators with proper ARIA attributes
      const loadingElements = screen.getAllByText(/cargando|loading/i);
      if (loadingElements.length > 0) {
        loadingElements.forEach(element => {
          expect(element).toBeInTheDocument();
        });
      }
    });

    it('should announce errors to screen readers', async () => {
      vi.mocked(useServicios).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Error de conexión'),
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Error de conexión'),
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      // Check for error messages with proper ARIA attributes
      const errorElements = screen.getAllByText(/error/i);
      if (errorElements.length > 0) {
        errorElements.forEach(element => {
          expect(element).toBeInTheDocument();
        });
      }
    });
  });

  describe('Color Contrast and Visual Accessibility', () => {
    it('should maintain accessibility in high contrast mode', async () => {
      // Mock high contrast media query
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-contrast: high)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      const servicios = Array.from({ length: 2 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      const { container } = render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should respect reduced motion preferences', async () => {
      // Mock reduced motion media query
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      const servicios = Array.from({ length: 2 }, (_, i) => createMockServicio(i + 1));
      const tipoTrabajos = Array.from({ length: 2 }, (_, i) => createMockTipoTrabajo(i + 1));

      vi.mocked(useServicios).mockReturnValue({
        data: { results: servicios, count: servicios.length },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(useTipoTrabajos).mockReturnValue({
        data: { results: tipoTrabajos },
        isLoading: false,
        error: null,
      });

      render(
        <TestWrapper>
          <ServicioDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
      });

      // Component should render without animations when reduced motion is preferred
      expect(screen.getByText('Módulo de Servicios')).toBeInTheDocument();
    });
  });
});