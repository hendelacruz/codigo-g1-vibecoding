import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { UserForm, type UserFormData } from '../UserForm'
import type { User } from '../../../features/auth/authTypes'

// Mock user data
const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  dni: '12345678',
  celular: '987654321',
  licencia: 'A12345678',
  rol_nombre: 'admin',
  is_active: true,
  is_staff: false,
  is_superuser: false,
  date_joined: '2024-01-01T00:00:00Z',
  last_login: null
}

describe('UserForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Create Mode', () => {
    it('should render all required fields for user creation', () => {
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      // Check all required fields are present
      expect(screen.getByLabelText(/nombre \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/apellido \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/username \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/dni \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/celular \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/rol \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirmar password \*/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/licencia \(opcional\)/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/activo/i)).toBeInTheDocument()
    })

    it('should show validation errors for required fields', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      // Try to submit empty form
      const submitButton = screen.getByRole('button', { name: /crear/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/nombre es requerido/i)).toBeInTheDocument()
        expect(screen.getByText(/apellido es requerido/i)).toBeInTheDocument()
        expect(screen.getByText(/username es requerido/i)).toBeInTheDocument()
        expect(screen.getByText(/email inválido/i)).toBeInTheDocument()
        expect(screen.getByText(/el dni debe tener 8 dígitos/i)).toBeInTheDocument()
        expect(screen.getByText(/el celular debe ser un número peruano válido/i)).toBeInTheDocument()
        expect(screen.getByText(/password debe tener al menos 8 caracteres/i)).toBeInTheDocument()
      })
    })

    it('should validate DNI format (8 digits)', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      const dniInput = screen.getByLabelText(/dni \*/i)
      
      // Test invalid DNI
      await user.type(dniInput, '123')
      await user.tab()

      await waitFor(() => {
        expect(screen.getByText(/el dni debe tener 8 dígitos/i)).toBeInTheDocument()
      })

      // Test valid DNI
      await user.clear(dniInput)
      await user.type(dniInput, '12345678')
      await user.tab()

      await waitFor(() => {
        expect(screen.queryByText(/el dni debe tener 8 dígitos/i)).not.toBeInTheDocument()
      })
    })

    it('should validate Peruvian mobile number format', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      const celularInput = screen.getByLabelText(/celular \*/i)
      
      // Test invalid celular (not starting with 9)
      await user.type(celularInput, '812345678')
      await user.tab()

      await waitFor(() => {
        expect(screen.getByText(/el celular debe ser un número peruano válido/i)).toBeInTheDocument()
      })

      // Test valid celular
      await user.clear(celularInput)
      await user.type(celularInput, '987654321')
      await user.tab()

      await waitFor(() => {
        expect(screen.queryByText(/el celular debe ser un número peruano válido/i)).not.toBeInTheDocument()
      })
    })

    it('should validate license format (A12345678)', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      const licenciaInput = screen.getByLabelText(/licencia \(opcional\)/i)
      
      // Test invalid license format
      await user.type(licenciaInput, '123456789')
      await user.tab()

      await waitFor(() => {
        expect(screen.getByText(/la licencia debe tener el formato a12345678/i)).toBeInTheDocument()
      })

      // Test valid license format
      await user.clear(licenciaInput)
      await user.type(licenciaInput, 'A12345678')
      await user.tab()

      await waitFor(() => {
        expect(screen.queryByText(/la licencia debe tener el formato a12345678/i)).not.toBeInTheDocument()
      })
    })

    it('should validate password confirmation match', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      const passwordInput = screen.getByLabelText(/^password \*/i)
      const confirmPasswordInput = screen.getByLabelText(/confirmar password \*/i)
      
      // Enter different passwords
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password456')
      await user.tab()

      await waitFor(() => {
        expect(screen.getByText(/las contraseñas no coinciden/i)).toBeInTheDocument()
      })

      // Enter matching passwords
      await user.clear(confirmPasswordInput)
      await user.type(confirmPasswordInput, 'password123')
      await user.tab()

      await waitFor(() => {
        expect(screen.queryByText(/las contraseñas no coinciden/i)).not.toBeInTheDocument()
      })
    })

    it('should submit form with valid data', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      // Fill all required fields
      await user.type(screen.getByLabelText(/nombre \*/i), 'John')
      await user.type(screen.getByLabelText(/apellido \*/i), 'Doe')
      await user.type(screen.getByLabelText(/username \*/i), 'johndoe')
      await user.type(screen.getByLabelText(/email \*/i), 'john@example.com')
      await user.type(screen.getByLabelText(/dni \*/i), '12345678')
      await user.type(screen.getByLabelText(/celular \*/i), '987654321')
      await user.selectOptions(screen.getByLabelText(/rol \*/i), 'admin')
      await user.type(screen.getByLabelText(/^password \*/i), 'password123')
      await user.type(screen.getByLabelText(/confirmar password \*/i), 'password123')
      await user.type(screen.getByLabelText(/licencia \(opcional\)/i), 'A12345678')

      // Submit form
      const submitButton = screen.getByRole('button', { name: /crear/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe',
          username: 'johndoe',
          email: 'john@example.com',
          dni: '12345678',
          celular: '987654321',
          password: 'password123',
          confirm_password: 'password123',
          rol_nombre: 'admin',
          licencia: 'A12345678',
          is_active: true
        })
      })
    })
  })

  describe('Edit Mode', () => {
    it('should populate form with existing user data', () => {
      render(
        <UserForm
          user={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="edit"
        />
      )

      expect(screen.getByDisplayValue('Test')).toBeInTheDocument()
      expect(screen.getByDisplayValue('User')).toBeInTheDocument()
      expect(screen.getByDisplayValue('testuser')).toBeInTheDocument()
      expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument()
      expect(screen.getByDisplayValue('12345678')).toBeInTheDocument()
      expect(screen.getByDisplayValue('987654321')).toBeInTheDocument()
      expect(screen.getByDisplayValue('A12345678')).toBeInTheDocument()
    })

    it('should show "Guardar" button in edit mode', () => {
      render(
        <UserForm
          user={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="edit"
        />
      )

      expect(screen.getByRole('button', { name: /guardar/i })).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /crear/i })).not.toBeInTheDocument()
    })
  })

  describe('Form Actions', () => {
    it('should call onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup()
      
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
        />
      )

      const cancelButton = screen.getByRole('button', { name: /cancelar/i })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(1)
    })

    it('should disable form when loading', () => {
      render(
        <UserForm
          user={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          mode="create"
          isLoading={true}
        />
      )

      // Check that inputs are disabled
      expect(screen.getByLabelText(/nombre \*/i)).toBeDisabled()
      expect(screen.getByLabelText(/apellido \*/i)).toBeDisabled()
      expect(screen.getByRole('button', { name: /crear/i })).toBeDisabled()
    })
  })
})