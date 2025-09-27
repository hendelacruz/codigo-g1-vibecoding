/**
 * Otros Productos Page - Main page for other products management
 * Uses the OtrosProductosManager component following the entities pattern
 */

import React from 'react'
import { OtrosProductosManager } from './OtrosProductosManager'

export const OtrosProductosPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Otros Productos</h1>
          <p className="mt-2 text-gray-600">
            Gestiona el inventario de productos diversos como cables, accesorios, herramientas y repuestos.
          </p>
        </div>
        <OtrosProductosManager />
      </div>
    </div>
  )
}

export default OtrosProductosPage