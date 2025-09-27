/**
 * SIM Cards Page - Main page for SIM card management
 * Uses the SIMCardsManager component following the entities pattern
 */

import React from 'react'
import { SIMCardsManager } from './SIMCardsManager'

export const SIMCardsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <SIMCardsManager />
      </div>
    </div>
  )
}

export default SIMCardsPage