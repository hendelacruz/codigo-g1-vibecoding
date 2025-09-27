import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UserManagement } from '../UserManagement'
import * as userService from '../../../services/userService'

// Mock del servicio de usuario
vi.mock('../../../services/userService')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('UserFormValidation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock successful responses
    vi.mocked(userService.getUsers).mockResolvedValue({
      data: [],
      total: 0,
      page: 1,
      limit: 10,
      totalPages: 0
    })
    vi.mocked(userService.getAvailableRoles).mockResolvedValue([
      { id: 1, name: 'ADMIN' },
      { id: 2, name: 'USER' }
    ])
    vi.mocked(userService.createUser).mockResolvedValue({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      dni: '12345678',
      celular: '987 654 321',
      rol_nombre: 'ADMIN',
      is_active: true,
      is_staff: false,
      is_superuser: false,
      date_joined: '2025-01-25T00:00:00Z',
      created_at: '2025-01-25T00:00:00Z',
      updated_at: '2025-01-25T00:00:00Z'
    })
  })

  it('should validate celular field with national format (9 digits starting with 9)', async () => {
    const Wrapper = createWrapper()
    render(<UserManagement />, { wrapper: Wrapper })

    // Esperar a que se cargue el componente
    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument()
    })

    // Abrir modal de creación
    const createButton = screen.getByText('Crear Usuario')
    fireEvent.click(createButton)

    // Llenar el formulario con celular nacional válido
    const celularInput = screen.getByLabelText(/celular/i)
    fireEvent.change(celularInput, { target: { value: '987654321' } })

    // Verificar que no hay errores de validación
    await waitFor(() => {
      const errorMessage = screen.queryByText(/El número de celular debe tener el formato peruano/i)
      expect(errorMessage).not.toBeInTheDocument()
    })
  })

  it('should validate celular field with international format (+51)', async () => {
    const Wrapper = createWrapper()
    render(<UserManagement />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument()
    })

    const createButton = screen.getByText('Crear Usuario')
    fireEvent.click(createButton)

    const celularInput = screen.getByLabelText(/celular/i)
    fireEvent.change(celularInput, { target: { value: '+51987654321' } })

    // Verificar que no hay errores de validación
    await waitFor(() => {
      const errorMessage = screen.queryByText(/El número de celular debe tener el formato peruano/i)
      expect(errorMessage).not.toBeInTheDocument()
    })
  })

  it('should reject invalid celular formats', async () => {
    const Wrapper = createWrapper()
    render(<UserManagement />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument()
    })

    const createButton = screen.getByText('Crear Usuario')
    fireEvent.click(createButton)

    const celularInput = screen.getByLabelText(/celular/i)
    
    // Probar formato inválido (no empieza con 9)
    fireEvent.change(celularInput, { target: { value: '812345678' } })
    fireEvent.blur(celularInput)

    await waitFor(() => {
      const errorMessage = screen.getByText(/El número de celular debe tener el formato peruano/i)
      expect(errorMessage).toBeInTheDocument()
    })
  })

  it('should send correct data format to backend including password_confirm and rol', async () => {
    const Wrapper = createWrapper()
    render(<UserManagement />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument()
    })

    const createButton = screen.getByText('Crear Usuario')
    fireEvent.click(createButton)

    // Llenar todos los campos requeridos
    fireEvent.change(screen.getByLabelText(/nombre de usuario/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/nombres/i), { target: { value: 'Test' } })
    fireEvent.change(screen.getByLabelText(/apellidos/i), { target: { value: 'User' } })
    fireEvent.change(screen.getByLabelText(/dni/i), { target: { value: '12345678' } })
    fireEvent.change(screen.getByLabelText(/celular/i), { target: { value: '987654321' } })
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: 'TestPassword123!' } })
    fireEvent.change(screen.getByLabelText(/confirmar contraseña/i), { target: { value: 'TestPassword123!' } })
    fireEvent.change(screen.getByLabelText(/licencia/i), { target: { value: 'A12345678' } })
    
    // Seleccionar rol
    const rolSelect = screen.getByLabelText(/rol/i)
    fireEvent.change(rolSelect, { target: { value: '1' } })

    // Enviar formulario
    const submitButton = screen.getByText('Crear')
    fireEvent.click(submitButton)

    // Verificar que se llamó al servicio con los datos correctos
    await waitFor(() => {
      expect(userService.createUser).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        dni: '12345678',
        celular: '987 654 321',
        password: 'TestPassword123!',
        password_confirm: 'TestPassword123!',
        rol: 1,
        licencia: 'A12345678',
        is_active: true
      })
    })
  })

  it('should validate licencia format (1 letter + 8 digits)', async () => {
    const Wrapper = createWrapper()
    render(<UserManagement />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument()
    })

    const createButton = screen.getByText('Crear Usuario')
    fireEvent.click(createButton)

    const licenciaInput = screen.getByLabelText(/licencia/i)
    
    // Probar formato válido
    fireEvent.change(licenciaInput, { target: { value: 'A12345678' } })
    fireEvent.blur(licenciaInput)

    await waitFor(() => {
      const errorMessage = screen.queryByText(/La licencia debe tener el formato/i)
      expect(errorMessage).not.toBeInTheDocument()
    })

    // Probar formato inválido
    fireEvent.change(licenciaInput, { target: { value: 'ABC123' } })
    fireEvent.blur(licenciaInput)

    await waitFor(() => {
      const errorMessage = screen.getByText(/La licencia debe tener el formato/i)
      expect(errorMessage).toBeInTheDocument()
    })
  })
})