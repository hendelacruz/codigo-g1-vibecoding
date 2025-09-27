import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UserTable } from '../UserTable'
import type { User } from '../../../shared/types/common'

// Mock data simplificado que cumple con la estructura del backend
const mockUsers: User[] = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    first_name: 'Juan',
    last_name: 'Pérez',
    password: 'hashed_password',
    is_staff: true,
    is_active: true,
    is_superuser: true,
    date_joined: '2023-01-15T10:30:00Z',
    last_login: '2024-01-15T14:20:00Z',
    dni: '12345678',
    licencia: 'A12345678',
    celular: '+51987654321',
    rol: {
      id: 1,
      name: 'Administradores'
    },
    rol_nombre: 'Administradores',
    created_at: '2023-01-15T10:30:00Z',
    updated_at: '2024-01-15T14:20:00Z',
    last_login_ip: '192.168.1.100'
  },
  {
    id: 2,
    username: 'supervisor01',
    email: 'supervisor@example.com',
    first_name: 'María',
    last_name: 'García',
    password: 'hashed_password',
    is_staff: false,
    is_active: true,
    is_superuser: false,
    date_joined: '2023-02-20T09:15:00Z',
    last_login: '2024-01-14T16:45:00Z',
    dni: '87654321',
    licencia: null,
    celular: '+51912345678',
    rol: {
      id: 2,
      name: 'Supervisores'
    },
    rol_nombre: 'Supervisores',
    created_at: '2023-02-20T09:15:00Z',
    updated_at: '2024-01-14T16:45:00Z',
    last_login_ip: '192.168.1.101'
  }
]

const defaultProps = {
  users: mockUsers,
  loading: false,
  canEdit: true,
  canDelete: true,
  canView: true,
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  onView: jest.fn()
}

describe('UserTable', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the user table with all users', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('Juan Pérez')).toBeInTheDocument()
      expect(screen.getByText('María García')).toBeInTheDocument()
    })

    it('should display user information correctly', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('admin@example.com')).toBeInTheDocument()
      expect(screen.getByText('DNI: 12345678')).toBeInTheDocument()
      expect(screen.getByText('Lic: A12345678')).toBeInTheDocument()
      expect(screen.getByText('+51987654321')).toBeInTheDocument()
      expect(screen.getByText('Administradores')).toBeInTheDocument()
    })

    it('should show empty state when no users', () => {
      render(<UserTable {...defaultProps} users={[]} />)
      
      expect(screen.getByText('No se encontraron usuarios')).toBeInTheDocument()
    })
  })

  describe('Filtering', () => {
    it('should filter users by search term', async () => {
      const user = userEvent.setup()
      render(<UserTable {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Buscar por nombre, email, DNI, celular...')
      await user.type(searchInput, 'Juan')
      
      expect(screen.getByText('Juan Pérez')).toBeInTheDocument()
      expect(screen.queryByText('María García')).not.toBeInTheDocument()
    })

    it('should filter users by role', async () => {
      const user = userEvent.setup()
      render(<UserTable {...defaultProps} />)
      
      const roleSelect = screen.getByDisplayValue('Todos los roles')
      await user.selectOptions(roleSelect, 'Supervisores')
      
      expect(screen.getByText('María García')).toBeInTheDocument()
      expect(screen.queryByText('Juan Pérez')).not.toBeInTheDocument()
    })

    it('should clear all filters', async () => {
      const user = userEvent.setup()
      render(<UserTable {...defaultProps} />)
      
      const searchInput = screen.getByPlaceholderText('Buscar por nombre, email, DNI, celular...')
      await user.type(searchInput, 'Juan')
      
      const clearButton = screen.getByText('Limpiar filtros')
      await user.click(clearButton)
      
      expect(screen.getByText('Juan Pérez')).toBeInTheDocument()
      expect(screen.getByText('María García')).toBeInTheDocument()
    })
  })

  describe('Sorting', () => {
    it('should sort users by first name', async () => {
      const user = userEvent.setup()
      render(<UserTable {...defaultProps} />)
      
      const nameHeader = screen.getByText('Usuario')
      await user.click(nameHeader)
      
      const userRows = screen.getAllByRole('row')
      expect(userRows[1]).toHaveTextContent('Juan Pérez')
      expect(userRows[2]).toHaveTextContent('María García')
    })
  })

  describe('Actions', () => {
    it('should call onView when view button is clicked', async () => {
      const user = userEvent.setup()
      const onView = jest.fn()
      render(<UserTable {...defaultProps} onView={onView} />)
      
      const viewButtons = screen.getAllByTitle('Ver detalles')
      if (viewButtons[0]) {
        await user.click(viewButtons[0])
        expect(onView).toHaveBeenCalledWith(mockUsers[0])
      }
    })

    it('should call onEdit when edit button is clicked', async () => {
      const user = userEvent.setup()
      const onEdit = jest.fn()
      render(<UserTable {...defaultProps} onEdit={onEdit} />)
      
      const editButtons = screen.getAllByTitle('Editar usuario')
      if (editButtons[0]) {
        await user.click(editButtons[0])
        expect(onEdit).toHaveBeenCalledWith(mockUsers[0])
      }
    })

    it('should call onDelete when delete button is clicked', async () => {
      const user = userEvent.setup()
      const onDelete = jest.fn()
      render(<UserTable {...defaultProps} onDelete={onDelete} />)
      
      const deleteButtons = screen.getAllByTitle('Eliminar usuario')
      if (deleteButtons[0]) {
        await user.click(deleteButtons[0])
        expect(onDelete).toHaveBeenCalledWith(2)
      }
    })
  })

  describe('Role Colors', () => {
    it('should apply correct colors for different roles', () => {
      render(<UserTable {...defaultProps} />)
      
      const adminRole = screen.getByText('Administradores')
      const supervisorRole = screen.getByText('Supervisores')
      
      expect(adminRole).toHaveClass('bg-purple-100', 'text-purple-800')
      expect(supervisorRole).toHaveClass('bg-blue-100', 'text-blue-800')
    })
  })

  describe('Date Formatting', () => {
    it('should format dates correctly', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('15 ene 2023')).toBeInTheDocument()
      expect(screen.getByText('15 ene 2024, 14:20')).toBeInTheDocument()
    })
  })

  describe('User Initials', () => {
    it('should generate correct user initials', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('JP')).toBeInTheDocument()
      expect(screen.getByText('MG')).toBeInTheDocument()
    })
  })

  describe('Special Indicators', () => {
    it('should show superuser indicator', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('SUPERUSUARIO')).toBeInTheDocument()
    })

    it('should show staff indicator', () => {
      render(<UserTable {...defaultProps} />)
      
      expect(screen.getByText('Staff')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should handle undefined users gracefully', () => {
      render(<UserTable {...defaultProps} users={undefined as any} />)
      
      expect(screen.getByText('No se encontraron usuarios')).toBeInTheDocument()
    })
  })
})