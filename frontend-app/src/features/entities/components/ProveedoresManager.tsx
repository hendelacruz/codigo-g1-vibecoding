import React, { useState } from 'react'
import { ProveedoresList } from './ProveedoresList'
import { ProveedorForm } from './ProveedorForm'
import type { ProveedorEntity } from '../entitiesTypes'

type ViewMode = 'list' | 'create' | 'edit'

export const ProveedoresManager: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [selectedProveedor, setSelectedProveedor] = useState<ProveedorEntity | undefined>(undefined)

  const handleAdd = () => {
    setSelectedProveedor(undefined)
    setViewMode('create')
  }

  const handleEdit = (proveedor: ProveedorEntity) => {
    setSelectedProveedor(proveedor)
    setViewMode('edit')
  }

  const handleSave = () => {
    setViewMode('list')
    setSelectedProveedor(undefined)
  }

  const handleCancel = () => {
    setViewMode('list')
    setSelectedProveedor(undefined)
  }

  const renderContent = () => {
    switch (viewMode) {
      case 'create':
        return (
          <ProveedorForm
            onSave={handleSave}
            onCancel={handleCancel}
          />
        )
      case 'edit':
        return selectedProveedor ? (
          <ProveedorForm
            proveedor={selectedProveedor}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        ) : null
      default:
        return (
          <ProveedoresList
            onAdd={handleAdd}
            onEdit={handleEdit}
          />
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      {viewMode !== 'list' && (
        <nav className="flex" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-4">
            <li>
              <button
                onClick={() => setViewMode('list')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Proveedores
              </button>
            </li>
            <li>
              <svg className="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </li>
            <li>
              <span className="text-gray-500 font-medium">
                {viewMode === 'create' ? 'Nuevo Proveedor' : 'Editar Proveedor'}
              </span>
            </li>
          </ol>
        </nav>
      )}

      {/* Content */}
      {renderContent()}
    </div>
  )
}