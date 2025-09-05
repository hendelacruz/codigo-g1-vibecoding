/**
 * CreateTodoPage Component Tests
 * Tests for the todo creation form page
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import '@testing-library/jest-dom'
import { CreateTodoPage } from './CreateTodoPage'

// Mock useNavigate
const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

// Helper function to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <MemoryRouter initialEntries={['/crear-todo']}>
      {component}
    </MemoryRouter>
  )
}

describe('CreateTodoPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the page title and subtitle', () => {
      renderWithRouter(<CreateTodoPage />)
      
      expect(screen.getByText('Crear Nueva Tarea')).toBeInTheDocument()
      expect(screen.getByText('Agrega una nueva tarea a tu lista')).toBeInTheDocument()
    })

    it('should render the form with input and button', () => {
      renderWithRouter(<CreateTodoPage />)
      
      expect(screen.getByLabelText('Descripción de la tarea')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Escribe tu nueva tarea aquí...')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /crear tarea/i })).toBeInTheDocument()
    })

    it('should render navigation link to home', () => {
      renderWithRouter(<CreateTodoPage />)
      
      const homeLink = screen.getByRole('link', { name: /volver al inicio/i })
      expect(homeLink).toBeInTheDocument()
      expect(homeLink).toHaveAttribute('href', '/')
    })

    it('should have proper accessibility attributes', () => {
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      expect(input).toHaveAttribute('aria-describedby', 'todo-help')
      expect(input).toHaveAttribute('required')
      expect(input).toHaveFocus() // autoFocus means the element should have focus
      
      expect(screen.getByText('Describe brevemente la tarea que quieres agregar')).toHaveAttribute('id', 'todo-help')
    })
  })

  describe('Form Interaction', () => {
    it('should update input value when typing', async () => {
      const user = userEvent.setup()
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      await user.type(input, 'Nueva tarea de prueba')
      
      expect(input).toHaveValue('Nueva tarea de prueba')
    })

    it('should disable submit button when input is empty', () => {
      renderWithRouter(<CreateTodoPage />)
      
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      expect(submitButton).toBeDisabled()
    })

    it('should enable submit button when input has text', async () => {
      const user = userEvent.setup()
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      
      await user.type(input, 'Nueva tarea')
      
      expect(submitButton).toBeEnabled()
    })

    it('should disable submit button when input contains only whitespace', async () => {
      const user = userEvent.setup()
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      
      await user.type(input, '   ')
      
      expect(submitButton).toBeDisabled()
    })
  })

  describe('Form Submission', () => {
    it('should handle form submission with valid input', async () => {
      const user = userEvent.setup()
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
      
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      
      await user.type(input, 'Nueva tarea de prueba')
      await user.click(submitButton)
      
      expect(consoleSpy).toHaveBeenCalledWith('Creating todo:', 'Nueva tarea de prueba')
      expect(mockNavigate).toHaveBeenCalledWith('/')
      
      consoleSpy.mockRestore()
    })

    it('should clear input after successful submission', async () => {
      const user = userEvent.setup()
      jest.spyOn(console, 'log').mockImplementation()
      
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      
      await user.type(input, 'Nueva tarea')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(input).toHaveValue('')
      })
    })

    it('should not submit form with empty input', async () => {
      const user = userEvent.setup()
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
      
      renderWithRouter(<CreateTodoPage />)
      
      const form = screen.getByRole('button', { name: /crear tarea/i }).closest('form')
      
      // Try to submit empty form
      if (form) {
        fireEvent.submit(form)
      }
      
      expect(consoleSpy).not.toHaveBeenCalled()
      expect(mockNavigate).not.toHaveBeenCalled()
      
      consoleSpy.mockRestore()
    })

    it('should handle form submission via Enter key', async () => {
      const user = userEvent.setup()
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
      
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      
      await user.type(input, 'Nueva tarea{enter}')
      
      expect(consoleSpy).toHaveBeenCalledWith('Creating todo:', 'Nueva tarea')
      expect(mockNavigate).toHaveBeenCalledWith('/')
      
      consoleSpy.mockRestore()
    })
  })

  describe('Styling and Classes', () => {
    it('should have proper CSS classes for styling', () => {
      renderWithRouter(<CreateTodoPage />)
      
      const input = screen.getByLabelText('Descripción de la tarea')
      expect(input).toHaveClass('w-full', 'px-4', 'py-3', 'border')
      
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      expect(submitButton).toHaveClass('w-full', 'bg-green-500', 'text-white')
    })

    it('should apply disabled styles when button is disabled', () => {
      renderWithRouter(<CreateTodoPage />)
      
      const submitButton = screen.getByRole('button', { name: /crear tarea/i })
      expect(submitButton).toHaveClass('disabled:opacity-50', 'disabled:cursor-not-allowed')
    })
  })
})