import React, { useState } from 'react'
import { SIMCardList } from './SIMCardList'
import { SIMCardForm } from './SIMCardForm'
import { useInventory } from '../hooks/useInventory'
import type { SIMCard } from '../inventoryTypes'

type ViewMode = 'list' | 'create' | 'edit'

export const SIMCardsManager: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [selectedSIMCard, setSelectedSIMCard] = useState<SIMCard | undefined>(undefined)
  const { loadSIMCards } = useInventory()

  const handleAdd = () => {
    setSelectedSIMCard(undefined)
    setViewMode('create')
  }

  const handleEdit = (simCard: SIMCard) => {
    setSelectedSIMCard(simCard)
    setViewMode('edit')
  }

  const handleSave = async () => {
    // Reload SIM cards data to reflect changes in the list
    await loadSIMCards()
    setViewMode('list')
    setSelectedSIMCard(undefined)
  }

  const handleCancel = () => {
    setViewMode('list')
    setSelectedSIMCard(undefined)
  }

  const renderContent = () => {
    switch (viewMode) {
      case 'create':
        return (
          <SIMCardForm
            onSave={handleSave}
            onCancel={handleCancel}
          />
        )
      case 'edit':
        return (
          <SIMCardForm
            {...(selectedSIMCard ? { simCard: selectedSIMCard } : {})}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        )
      default:
        return (
          <SIMCardList
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
                Tarjetas SIM
              </button>
            </li>
            <li>
              <svg className="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </li>
            <li>
              <span className="text-gray-500 font-medium">
                {viewMode === 'create' ? 'Nueva Tarjeta SIM' : 'Editar Tarjeta SIM'}
              </span>
            </li>
          </ol>
        </nav>
      )}

      {/* Content */}
      {renderContent()}
    </div>
  )
};