import React, { useState } from 'react'
import type { Cliente, UnidadVehicular, ProveedorEntity } from '../entitiesTypes'
import { ClientesList } from './ClientesList'
import { ClienteForm } from './ClienteForm'
import { UnidadesList } from './UnidadesList'
import { UnidadForm } from './UnidadForm'
import { ProveedoresList } from './ProveedoresList'
import { ProveedorForm } from './ProveedorForm'

type ActiveTab = 'clientes' | 'unidades' | 'proveedores'
type FormMode = 'list' | 'create' | 'edit'

interface FormState {
  mode: FormMode
  editingItem?: Cliente | UnidadVehicular | ProveedorEntity
}

interface EntitiesPageProps {
  initialTab?: ActiveTab
}

export const EntitiesPage: React.FC<EntitiesPageProps> = ({ initialTab = 'clientes' }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>(initialTab)
  const [clientesForm, setClientesForm] = useState<FormState>({ mode: 'list' })
  const [unidadesForm, setUnidadesForm] = useState<FormState>({ mode: 'list' })
  const [proveedoresForm, setProveedoresForm] = useState<FormState>({ mode: 'list' })

  const tabs = [
    { id: 'clientes' as const, name: 'Clientes', icon: '👥' },
    { id: 'unidades' as const, name: 'Unidades Vehiculares', icon: '🚛' },
    { id: 'proveedores' as const, name: 'Proveedores', icon: '🏢' }
  ]

  // Clientes handlers
  const handleClienteAdd = () => {
    setClientesForm({ mode: 'create' })
  }

  const handleClienteEdit = (cliente: Cliente) => {
    setClientesForm({ mode: 'edit', editingItem: cliente })
  }

  const handleClienteFormSave = () => {
    setClientesForm({ mode: 'list' })
  }

  const handleClienteFormCancel = () => {
    setClientesForm({ mode: 'list' })
  }

  // Unidades handlers
  const handleUnidadAdd = () => {
    setUnidadesForm({ mode: 'create' })
  }

  const handleUnidadEdit = (unidad: UnidadVehicular) => {
    setUnidadesForm({ mode: 'edit', editingItem: unidad })
  }

  const handleUnidadFormSave = () => {
    setUnidadesForm({ mode: 'list' })
  }

  const handleUnidadFormCancel = () => {
    setUnidadesForm({ mode: 'list' })
  }

  // Proveedores handlers
  const handleProveedorAdd = () => {
    setProveedoresForm({ mode: 'create' })
  }

  const handleProveedorEdit = (proveedor: ProveedorEntity) => {
    setProveedoresForm({ mode: 'edit', editingItem: proveedor })
  }

  const handleProveedorFormSave = () => {
    setProveedoresForm({ mode: 'list' })
  }

  const handleProveedorFormCancel = () => {
    setProveedoresForm({ mode: 'list' })
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'clientes':
        if (clientesForm.mode === 'list') {
          return (
            <ClientesList
              onAdd={handleClienteAdd}
              onEdit={handleClienteEdit}
            />
          )
        }
        return clientesForm.mode === 'edit' && clientesForm.editingItem ? (
          <ClienteForm
            cliente={clientesForm.editingItem as Cliente}
            onSave={handleClienteFormSave}
            onCancel={handleClienteFormCancel}
          />
        ) : (
          <ClienteForm
            onSave={handleClienteFormSave}
            onCancel={handleClienteFormCancel}
          />
        )

      case 'unidades':
        if (unidadesForm.mode === 'list') {
          return (
            <UnidadesList
              onAdd={handleUnidadAdd}
              onEdit={handleUnidadEdit}
            />
          )
        }
        return unidadesForm.mode === 'edit' && unidadesForm.editingItem ? (
          <UnidadForm
            unidad={unidadesForm.editingItem as UnidadVehicular}
            onSave={handleUnidadFormSave}
            onCancel={handleUnidadFormCancel}
          />
        ) : (
          <UnidadForm
            onSave={handleUnidadFormSave}
            onCancel={handleUnidadFormCancel}
          />
        )

      case 'proveedores':
        if (proveedoresForm.mode === 'list') {
          return (
            <ProveedoresList
              onAdd={handleProveedorAdd}
              onEdit={handleProveedorEdit}
            />
          )
        }
        return proveedoresForm.mode === 'edit' && proveedoresForm.editingItem ? (
          <ProveedorForm
            proveedor={proveedoresForm.editingItem as ProveedorEntity}
            onSave={handleProveedorFormSave}
            onCancel={handleProveedorFormCancel}
          />
        ) : (
          <ProveedorForm
            onSave={handleProveedorFormSave}
            onCancel={handleProveedorFormCancel}
          />
        )

      default:
        return null
    }
  }

  const getCurrentFormMode = () => {
    switch (activeTab) {
      case 'clientes':
        return clientesForm.mode
      case 'unidades':
        return unidadesForm.mode
      case 'proveedores':
        return proveedoresForm.mode
      default:
        return 'list'
    }
  }

  const handleTabChange = (tabId: ActiveTab) => {
    // Reset all forms to list mode when changing tabs
    setClientesForm({ mode: 'list' })
    setUnidadesForm({ mode: 'list' })
    setProveedoresForm({ mode: 'list' })
    setActiveTab(tabId)
  }

  const currentFormMode = getCurrentFormMode()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Entidades</h1>
          <p className="text-gray-600 mt-2">
            Administra clientes, unidades vehiculares y proveedores de tu empresa
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Breadcrumb for forms */}
        {currentFormMode !== 'list' && (
          <div className="mb-6">
            <nav className="flex" aria-label="Breadcrumb">
              <ol className="flex items-center space-x-4">
                <li>
                  <div className="flex items-center">
                    <button
                      onClick={() => handleTabChange(activeTab)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      {tabs.find(tab => tab.id === activeTab)?.name}
                    </button>
                  </div>
                </li>
                <li>
                  <div className="flex items-center">
                    <svg
                      className="flex-shrink-0 h-5 w-5 text-gray-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="ml-4 text-sm font-medium text-gray-900">
                      {currentFormMode === 'create' ? 'Nuevo' : 'Editar'}
                    </span>
                  </div>
                </li>
              </ol>
            </nav>
          </div>
        )}

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  )
}