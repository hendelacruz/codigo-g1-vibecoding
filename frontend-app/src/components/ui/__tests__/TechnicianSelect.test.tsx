import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { TechnicianSelect } from '../TechnicianSelect';
import * as useTechniciansHook from '../../../hooks/useTechnicians';

// Mock the useTechnicians hook
const mockUseTechnicians = vi.fn();
vi.mock('../../../hooks/useTechnicians', () => ({
  useTechnicians: () => mockUseTechnicians(),
}));

// Mock data
const mockTechnicians = [
  {
    id: 1,
    nombre: 'Juan',
    apellido: 'Pérez',
    dni: '12345678',
    email: 'juan@example.com',
    rol_nombre: 'tecnico',
    activo: true,
  },
  {
    id: 2,
    nombre: 'María',
    apellido: 'García',
    dni: '87654321',
    email: 'maria@example.com',
    rol_nombre: 'tecnico',
    activo: true,
  },
];

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('TechnicianSelect', () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTechnicians.mockReturnValue({
      technicians: mockTechnicians,
      isLoading: false,
      error: null,
      total: 2,
    });
  });

  it('renders with placeholder text', () => {
    render(
      <TechnicianSelect
        onChange={mockOnChange}
        placeholder="Select a technician"
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Select a technician')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    mockUseTechnicians.mockReturnValue({
      technicians: [],
      isLoading: true,
      error: null,
      total: 0,
    });

    render(
      <TechnicianSelect onChange={mockOnChange} />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Cargando técnicos...')).toBeInTheDocument();
  });

  it('displays error state', () => {
    mockUseTechnicians.mockReturnValue({
      technicians: [],
      isLoading: false,
      error: new Error('Failed to fetch'),
      total: 0,
    });

    render(
      <TechnicianSelect onChange={mockOnChange} />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Error al cargar técnicos')).toBeInTheDocument();
  });

  it('displays technicians list when opened', async () => {
    render(
      <TechnicianSelect onChange={mockOnChange} />,
      { wrapper: createWrapper() }
    );

    // Click to open dropdown
    const selectButton = screen.getByRole('button');
    fireEvent.click(selectButton);

    await waitFor(() => {
      expect(screen.getByText('Juan Pérez - DNI: 12345678')).toBeInTheDocument();
      expect(screen.getByText('María García - DNI: 87654321')).toBeInTheDocument();
    });
  });

  it('calls onChange when technician is selected', async () => {
    render(
      <TechnicianSelect onChange={mockOnChange} />,
      { wrapper: createWrapper() }
    );

    // Click to open dropdown
    const selectButton = screen.getByRole('button');
    fireEvent.click(selectButton);

    // Select first technician
    await waitFor(() => {
      const option = screen.getByText('Juan Pérez - DNI: 12345678');
      fireEvent.click(option);
    });

    expect(mockOnChange).toHaveBeenCalledWith(1);
  });

  it('displays selected technician name', () => {
    render(
      <TechnicianSelect
        value={1}
        onChange={mockOnChange}
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
  });

  it('shows error message when provided', () => {
    render(
      <TechnicianSelect
        onChange={mockOnChange}
        error="This field is required"
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <TechnicianSelect
        onChange={mockOnChange}
        disabled={true}
      />,
      { wrapper: createWrapper() }
    );

    const selectButton = screen.getByRole('button');
    expect(selectButton).toBeDisabled();
  });

  it('displays no technicians message when list is empty', async () => {
    mockUseTechnicians.mockReturnValue({
      technicians: [],
      isLoading: false,
      error: null,
      total: 0,
    });

    render(
      <TechnicianSelect onChange={mockOnChange} />,
      { wrapper: createWrapper() }
    );

    // Click to open dropdown
    const selectButton = screen.getByRole('button');
    fireEvent.click(selectButton);

    await waitFor(() => {
      expect(screen.getByText('No hay técnicos disponibles')).toBeInTheDocument();
    });
  });
});