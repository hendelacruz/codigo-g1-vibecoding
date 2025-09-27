import React, { useEffect, useCallback } from 'react';
import { useInventory } from '../hooks/useInventory';
import { Button } from '../../../shared/components/ui/Button';

interface InventoryStats {
  totalGPS: number;
  totalSIMCards: number;
  totalOtrosProductos: number;
  gpsDisponibles: number;
  simCardsDisponibles: number;
  productosStockBajo: number;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  action: () => void;
  variant: 'primary' | 'secondary' | 'outline';
}

export const InventoryDashboard: React.FC = () => {
  const {
    gps,
    simCards,
    otrosProductos,
    loadGPSDevices,
    loadSIMCards,
    loadOtrosProductos
  } = useInventory();



  const loadData = useCallback(async () => {
    try {
      // Load GPS devices first
      await loadGPSDevices()
      
      // Then load SIM cards
      await loadSIMCards()
      
      // Then load other products
      await loadOtrosProductos()
      
    } catch (error) {
      console.error('❌ Error during data loading:', error)
    }
  }, [loadGPSDevices, loadSIMCards, loadOtrosProductos])

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Calculate statistics with defensive checks and logging
  const stats: InventoryStats = {
    totalGPS: Array.isArray(gps?.items) ? gps.items.length : 0,
    totalSIMCards: Array.isArray(simCards?.items) ? simCards.items.length : 0,
    totalOtrosProductos: Array.isArray(otrosProductos?.items) ? otrosProductos.items.length : 0,
    gpsDisponibles: Array.isArray(gps?.items) ? gps.items.filter(device => device.estado === 'no_asignado').length : 0,
    simCardsDisponibles: Array.isArray(simCards?.items) ? simCards.items.filter(card => card.estado === 'no_asignado').length : 0,
    productosStockBajo: Array.isArray(otrosProductos?.items) ? otrosProductos.items.filter(producto => producto.stock_actual <= producto.stock_minimo).length : 0,
  };

  // Debug logging for data structure validation
  if (process.env.NODE_ENV === 'development') {
    if (gps && !Array.isArray(gps.items)) {
      console.warn('⚠️ GPS items is not an array:', gps.items);
    }
    if (simCards && !Array.isArray(simCards.items)) {
      console.warn('⚠️ SIM Cards items is not an array:', simCards.items);
    }
    if (otrosProductos && !Array.isArray(otrosProductos.items)) {
      console.warn('⚠️ Otros Productos items is not an array:', otrosProductos.items);
    }
  }

  const quickActions: QuickAction[] = [
    {
      id: 'add-gps',
      title: 'Agregar GPS',
      description: 'Registrar nuevo dispositivo GPS',
      icon: '📍',
      action: () => {}, // TODO: Implement GPS creation
      variant: 'primary'
    },
    {
      id: 'add-sim',
      title: 'Agregar SIM Card',
      description: 'Registrar nueva tarjeta SIM',
      icon: '📱',
      action: () => {}, // TODO: Implement SIM creation
      variant: 'primary'
    },
    {
      id: 'add-product',
      title: 'Agregar Producto',
      description: 'Registrar nuevo producto',
      icon: '📦',
      action: () => {}, // TODO: Implement product creation
      variant: 'primary'
    },
    {
      id: 'manage-providers',
      title: 'Gestionar Proveedores',
      description: 'Administrar proveedores',
      icon: '🏢',
      action: () => {}, // TODO: Implement provider management
      variant: 'secondary'
    }
  ];

  const refreshData = useCallback(async () => {
    try {
      // Refresh GPS devices first
      await loadGPSDevices();
      await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay for refresh
      
      // Refresh SIM cards
      await loadSIMCards();
      await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay
      
      // Refresh otros productos
      await loadOtrosProductos();
      await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay
      
    } catch (error) {
      console.error('❌ Error refreshing data:', error)
    }
  }, [loadGPSDevices, loadSIMCards, loadOtrosProductos]);

  const isLoading = gps.isLoading || simCards.isLoading || otrosProductos.isLoading;
  const isRateLimited = [gps.error, simCards.error, otrosProductos.error]
    .some(error => error?.includes('Rate limit exceeded'));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard de Inventario</h1>
          <p className="text-gray-600 mt-1">
            Gestión completa de dispositivos GPS, SIM Cards y productos
          </p>
        </div>
        <Button 
          onClick={refreshData} 
          variant="outline"
          disabled={isLoading}
        >
          {isLoading ? '🔄' : '↻'} Actualizar
        </Button>
      </div>



      {/* Rate Limiting Warning */}
      {isRateLimited && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-yellow-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Límite de consultas alcanzado
              </h3>
              <p className="text-sm text-yellow-700 mt-1">
                El sistema está reintentando automáticamente las consultas. Los datos se cargarán gradualmente.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !isRateLimited && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-blue-400 text-xl animate-spin">🔄</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Cargando datos del inventario...
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                Obteniendo información de dispositivos GPS, SIM Cards y productos.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error States */}
      {!isLoading && (gps.error || simCards.error || otrosProductos.error) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-red-400 text-xl">❌</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error al cargar algunos datos
              </h3>
              <div className="text-sm text-red-700 mt-1 space-y-1">
                {gps.error && (
                  <p>• GPS: {gps.error}</p>
                )}
                {simCards.error && (
                  <p>• SIM Cards: {simCards.error}</p>
                )}
                {otrosProductos.error && (
                  <p>• Otros Productos: {otrosProductos.error}</p>
                )}
              </div>
              <div className="mt-3">
                <Button 
                  onClick={refreshData} 
                  variant="outline"
                  size="sm"
                  className="text-red-700 border-red-300 hover:bg-red-100"
                >
                  🔄 Reintentar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dispositivos GPS</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalGPS}</p>
              <p className="text-xs text-green-600 mt-1">
                {stats.gpsDisponibles} disponibles
              </p>
            </div>
            <div className="text-3xl">📍</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">SIM Cards</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalSIMCards}</p>
              <p className="text-xs text-green-600 mt-1">
                {stats.simCardsDisponibles} disponibles
              </p>
            </div>
            <div className="text-3xl">📱</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Otros Productos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalOtrosProductos}</p>
              <p className="text-xs text-red-600 mt-1">
                {stats.productosStockBajo} stock bajo
              </p>
            </div>
            <div className="text-3xl">📦</div>
          </div>
      </div>

    </div>








    </div>
  );
};