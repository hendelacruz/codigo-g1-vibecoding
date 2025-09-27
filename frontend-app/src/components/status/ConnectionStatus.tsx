import React, { useState, useEffect } from 'react';
import { useInventory } from '../../features/inventory/hooks/useInventory';

interface ConnectionStatusProps {
  className?: string;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ className = '' }) => {
  const [lastCheck, setLastCheck] = useState<Date>(new Date());
  
  const {
    gps,
    simCards,
    otrosProductos,
    proveedores
  } = useInventory();

  // Update last check time periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setLastCheck(new Date());
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Determine backend status based on data loading states
  const getBackendStatus = () => {
    const hasData = [gps, simCards, otrosProductos, proveedores].some(data => 
      data && typeof data === 'object' && 'items' in data && Array.isArray(data.items) && data.items.length > 0
    );
    
    const hasErrors = [gps, simCards, otrosProductos, proveedores].some(data => 
      data && typeof data === 'object' && 'error' in data && data.error
    );
    
    const isLoading = [gps, simCards, otrosProductos, proveedores].some(data => 
      data && typeof data === 'object' && 'isLoading' in data && data.isLoading
    );

    if (hasData || isLoading) {
      return 'connected';
    } else if (hasErrors) {
      return 'error';
    } else {
      return 'checking';
    }
  };

  const backendStatus = getBackendStatus();

  const getStatusInfo = () => {
    switch (backendStatus) {
      case 'connected':
        return {
          color: 'bg-green-500',
          text: 'API Conectada',
          icon: '✅'
        };
      case 'error':
        return {
          color: 'bg-red-500',
          text: 'API Desconectada',
          icon: '❌'
        };
      case 'checking':
      default:
        return {
          color: 'bg-gray-500',
          text: 'Verificando...',
          icon: '⏳'
        };
    }
  };

  const getDataStatus = (data: unknown) => {
    if (data && typeof data === 'object' && 'isLoading' in data && data.isLoading) {
      return { color: 'bg-yellow-500', icon: '⏳' };
    }
    if (data && typeof data === 'object' && 'error' in data && data.error) {
      return { color: 'bg-red-500', icon: '❌' };
    }
    if (data && typeof data === 'object' && 'items' in data && Array.isArray(data.items) && data.items.length > 0) {
      return { color: 'bg-green-500', icon: '✅' };
    }
    return { color: 'bg-gray-500', icon: '⚪' };
  };

  const statusInfo = getStatusInfo();
  const gpsStatus = getDataStatus(gps);
  const simStatus = getDataStatus(simCards);
  const productosStatus = getDataStatus(otrosProductos);
  const proveedoresStatus = getDataStatus(proveedores);

  return (
    <div className={`bg-white p-6 rounded-lg shadow border border-gray-200 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Estado del Sistema</h2>
        <span className="text-xs text-gray-500">
          Última verificación: {lastCheck.toLocaleTimeString()}
        </span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Backend Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 ${statusInfo.color} rounded-full`}></div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-700">{statusInfo.text}</span>
            <span className="text-xs text-gray-500">{statusInfo.icon}</span>
          </div>
        </div>

        {/* GPS Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 ${gpsStatus.color} rounded-full`}></div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-700">GPS</span>
            <span className="text-xs text-gray-500">
              {gps?.items?.length || 0} dispositivos {gpsStatus.icon}
            </span>
          </div>
        </div>

        {/* SIM Cards Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 ${simStatus.color} rounded-full`}></div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-700">SIM Cards</span>
            <span className="text-xs text-gray-500">
              {simCards?.items?.length || 0} tarjetas {simStatus.icon}
            </span>
          </div>
        </div>

        {/* Productos Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 ${productosStatus.color} rounded-full`}></div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-700">Productos</span>
            <span className="text-xs text-gray-500">
              {otrosProductos?.items?.length || 0} productos {productosStatus.icon}
            </span>
          </div>
        </div>

        {/* Proveedores Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 ${proveedoresStatus.color} rounded-full`}></div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-700">Proveedores</span>
            <span className="text-xs text-gray-500">
              {proveedores?.items?.length || 0} proveedores {proveedoresStatus.icon}
            </span>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {backendStatus === 'error' && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">
            ❌ No se puede conectar con el backend. Verifica que el servidor esté ejecutándose.
          </p>
        </div>
      )}
    </div>
  );
};