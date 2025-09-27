import React, { useState } from 'react'
import { GPSList } from './GPSList'
import { GPSForm } from './GPSForm'
import { useInventory } from '../hooks/useInventory'
import type { GPS } from '../inventoryTypes'

type ViewMode = 'list' | 'create' | 'edit'

export const GPSManager: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [selectedGPS, setSelectedGPS] = useState<GPS | undefined>(undefined)
  const { loadGPSDevices } = useInventory()

  const handleAdd = () => {
    setSelectedGPS(undefined)
    setViewMode('create')
  }

  const handleEdit = (gps: GPS) => {
    setSelectedGPS(gps)
    setViewMode('edit')
  }

  const handleSave = async () => {
    // Reload GPS data to reflect changes in the list
    await loadGPSDevices()
    setViewMode('list')
    setSelectedGPS(undefined)
  }

  const handleCancel = () => {
    setViewMode('list')
    setSelectedGPS(undefined)
  }

  const renderContent = () => {
    switch (viewMode) {
      case 'create':
        return (
          <GPSForm
            onSave={handleSave}
            onCancel={handleCancel}
          />
        )
      case 'edit':
        return selectedGPS ? (
          <GPSForm
            gps={selectedGPS}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        ) : null
      default:
        return (
          <GPSList
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
                Dispositivos GPS
              </button>
            </li>
            <li>
              <svg className="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </li>
            <li>
              <span className="text-gray-500 font-medium">
                {viewMode === 'create' ? 'Nuevo Dispositivo GPS' : 'Editar Dispositivo GPS'}
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