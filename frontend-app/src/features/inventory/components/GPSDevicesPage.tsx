/**
 * GPS Devices Page - Main page for GPS device management
 * Uses the new GPSManager component following the entities pattern
 */

import React from 'react'
import { GPSManager } from './GPSManager'

export const GPSDevicesPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <GPSManager />
      </div>
    </div>
  )
}

export default GPSDevicesPage