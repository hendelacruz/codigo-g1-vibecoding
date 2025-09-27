import React, { useState } from 'react'
import { Button } from '../shared/components/ui/Button'
import { Sidebar } from '../shared/components/layout/Sidebar'
import { GeneralDashboard } from '../components/dashboard/GeneralDashboard'
import { InventoryDashboard } from '../features/inventory/components/InventoryDashboard'
import { GPSDevicesPage } from '../features/inventory/components/GPSDevicesPage'
import { SIMCardsManager } from '../features/inventory/components/SIMCardsManager'
import { OtrosProductosManager } from '../features/inventory/components/OtrosProductosManager'
import { ClientesManager } from '../features/entities/components/ClientesManager'
import { ProveedoresManager } from '../features/entities/components/ProveedoresManager'
import { EntitiesPage } from '../features/entities/components/EntitiesPage'
import { ServicesPage } from '../features/services/pages/ServicesPage'
import { AuthDashboard } from '../components/auth/AuthDashboard'
import { UserProfile } from '../components/auth/UserProfile'







type ModuleType = 'dashboard' | 'auth' | 'inventory' | 'inventory-general' | 'gps' | 'simcards' | 'otros-productos' | 'clientes' | 'proveedores' | 'unidades' | 'services' | 'sales' | 'reports'

export const DashboardPage: React.FC = () => {
  const [activeModule, setActiveModule] = useState<ModuleType>('dashboard')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Check if mobile on mount and resize
  React.useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      if (mobile) {
        setSidebarCollapsed(true)
      }
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])



  const handleModuleChange = (module: string) => {
    setActiveModule(module as ModuleType)
  }

  const renderModuleContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return <GeneralDashboard onModuleSelect={handleModuleChange} />
      case 'auth':
        return <AuthDashboard />
      case 'inventory':
      case 'inventory-general':
        return (
          <div className="space-y-4">
            <InventoryDashboard />
          </div>
        )
      case 'gps':
        return <GPSDevicesPage />
      case 'simcards':
        return <SIMCardsManager />
      case 'otros-productos':
        return <OtrosProductosManager />
      case 'clientes':
        return (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Gestión de Clientes</h2>
              <p className="text-gray-600 mb-6">Administra la información de tus clientes.</p>
              <ClientesManager />
            </div>
          </div>
        )
      case 'proveedores':
        return (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Gestión de Proveedores</h2>
              <p className="text-gray-600 mb-6">Administra la información de tus proveedores.</p>
              <ProveedoresManager />
            </div>
          </div>
        )
      case 'unidades':
        return (
          <div className="space-y-6">
            <EntitiesPage initialTab="unidades" />
          </div>
        )
      case 'services':
        return <ServicesPage />
      case 'sales':
        return (
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Módulo de Ventas</h2>
            <p className="text-gray-600">Este módulo estará disponible próximamente.</p>
          </div>
        )
      case 'reports':
        return (
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Módulo de Reportes</h2>
            <p className="text-gray-600">Este módulo estará disponible próximamente.</p>
          </div>
        )
      default:
        return <InventoryDashboard />
    }
  }

  // Si estamos en el dashboard general, mostrar solo el contenido sin sidebar ni header
  if (activeModule === 'dashboard') {
    return (
      <div className="min-h-screen">
        {renderModuleContent()}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        isOpen={!sidebarCollapsed}
        onClose={() => setSidebarCollapsed(true)}
        activeModule={activeModule}
        onModuleChange={handleModuleChange}
      />

      {/* Overlay for mobile */}
      {!sidebarCollapsed && isMobile && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}

      {/* Main Content Area */}
      <div className={`flex flex-col min-h-screen transition-all duration-300 ${
        isMobile ? 'ml-0' : sidebarCollapsed ? 'ml-16' : 'ml-64'
      }`}>
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-2 sm:space-x-4">
                {(sidebarCollapsed || isMobile) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSidebarCollapsed(false)}
                    className="p-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </Button>
                )}
                <h1 className="text-lg sm:text-xl font-semibold text-gray-900 truncate">
                  {isMobile ? 'Dashboard' : 'Sistema de Gestión e Inventario'}
                </h1>
              </div>
              <div className="flex items-center space-x-2 sm:space-x-4">
                <UserProfile className="ml-auto" />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto w-full">
            <div className="w-full">
              {renderModuleContent()}
            </div>
          </div>
        </main>
      </div>
      

    </div>
  )
}