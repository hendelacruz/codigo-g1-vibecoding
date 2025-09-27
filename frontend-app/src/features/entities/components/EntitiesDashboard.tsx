import React, { useEffect, useState } from 'react';
import { useEntities } from '../useEntities';
import { Button } from '../../../shared/components/ui/Button';
import { ClientesList } from './ClientesList';
import { ClienteForm } from './ClienteForm';
import { UnidadesList } from './UnidadesList';
import { UnidadForm } from './UnidadForm';
import { ProveedoresManager } from './ProveedoresManager';

interface EntitiesStats {
  totalClientes: number;
  totalUnidades: number;
  totalProveedores: number;
  clientesActivos: number;
  unidadesActivas: number;
  proveedoresActivos: number;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  action: () => void;
  variant: 'default' | 'secondary' | 'outline';
}

type ActiveView = 'dashboard' | 'clientes' | 'unidades' | 'proveedores' | 'create-cliente' | 'create-unidad';

export const EntitiesDashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard');
  
  const {
    clientes,
    unidades,
    proveedores,
    loadClientes,
    loadUnidades,
    loadProveedores
  } = useEntities();

  // Load data on mount with sequential delays to avoid rate limiting
  useEffect(() => {
    const loadDataSequentially = async () => {
      try {
        // Load clientes first
        await loadClientes();
        await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
        
        // Load unidades
        await loadUnidades();
        await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
        
        // Load proveedores
        await loadProveedores();
        
      } catch (error) {
        console.error('❌ Error in entities data loading:', error);
      }
    };
    
    loadDataSequentially();
  }, [loadClientes, loadUnidades, loadProveedores]);

  // Calculate statistics with defensive checks
  const stats: EntitiesStats = {
    totalClientes: Array.isArray(clientes?.items) ? clientes.items.length : 0,
    totalUnidades: Array.isArray(unidades?.items) ? unidades.items.length : 0,
    totalProveedores: Array.isArray(proveedores?.items) ? proveedores.items.length : 0,
    clientesActivos: Array.isArray(clientes?.items) ? clientes.items.filter(cliente => cliente.is_active).length : 0,
    unidadesActivas: Array.isArray(unidades?.items) ? unidades.items.filter(unidad => unidad.is_active).length : 0,
    proveedoresActivos: Array.isArray(proveedores?.items) ? proveedores.items.filter(proveedor => proveedor.is_active).length : 0,
  };

  const quickActions: QuickAction[] = [
    {
      id: 'add-cliente',
      title: 'Agregar Cliente',
      description: 'Registrar nuevo cliente',
      icon: '👤',
      action: () => setActiveView('create-cliente'),
      variant: 'default'
    },
    {
      id: 'add-unidad',
      title: 'Agregar Unidad',
      description: 'Registrar nueva unidad vehicular',
      icon: '🚗',
      action: () => setActiveView('create-unidad'),
      variant: 'default'
    },
    {
      id: 'add-proveedor',
      title: 'Agregar Proveedor',
      description: 'Registrar nuevo proveedor',
      icon: '🏢',
      action: () => setActiveView('proveedores'),
      variant: 'default'
    },
    {
      id: 'view-clientes',
      title: 'Ver Clientes',
      description: 'Gestionar clientes existentes',
      icon: '📋',
      action: () => setActiveView('clientes'),
      variant: 'secondary'
    },
    {
      id: 'view-unidades',
      title: 'Ver Unidades',
      description: 'Gestionar unidades vehiculares',
      icon: '🚛',
      action: () => setActiveView('unidades'),
      variant: 'secondary'
    },
    {
      id: 'view-proveedores',
      title: 'Ver Proveedores',
      description: 'Gestionar proveedores',
      icon: '🏭',
      action: () => setActiveView('proveedores'),
      variant: 'secondary'
    }
  ];

  const renderActiveView = () => {
    switch (activeView) {
      case 'clientes':
        return <ClientesList onAdd={() => setActiveView('create-cliente')} />;
      case 'create-cliente':
        return <ClienteForm onSave={() => setActiveView('clientes')} onCancel={() => setActiveView('dashboard')} />;
      case 'unidades':
        return <UnidadesList onAdd={() => setActiveView('create-unidad')} />;
      case 'create-unidad':
        return <UnidadForm onSave={() => setActiveView('unidades')} onCancel={() => setActiveView('dashboard')} />;
      case 'proveedores':
        return <ProveedoresManager />;
      default:
        return null;
    }
  };

  if (activeView !== 'dashboard') {
    return (
      <div className="p-6">
        {renderActiveView()}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Entidades</h1>
          <p className="text-gray-600 mt-1">Administra clientes, unidades vehiculares y proveedores</p>
        </div>
        <Button
          onClick={() => window.location.reload()}
          variant="outline"
          disabled={clientes?.isLoading || unidades?.isLoading || proveedores?.isLoading}
        >
          {clientes?.isLoading || unidades?.isLoading || proveedores?.isLoading ? 'Cargando...' : 'Actualizar'}
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">👤</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Clientes</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalClientes}</p>
              <p className="text-sm text-green-600">{stats.clientesActivos} activos</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">🚗</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Unidades Vehiculares</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalUnidades}</p>
              <p className="text-sm text-green-600">{stats.unidadesActivas} activas</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">🏢</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Proveedores</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalProveedores}</p>
              <p className="text-sm text-green-600">{stats.proveedoresActivos} activos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <div key={action.id} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">{action.icon}</div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-600 mb-3">{action.description}</p>
                  <Button
                    onClick={action.action}
                    variant={action.variant}
                    size="sm"
                    className="w-full"
                  >
                    {action.title}
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity or Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Resumen del Sistema</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-gray-600">Total de entidades registradas</span>
            <span className="font-semibold">{stats.totalClientes + stats.totalUnidades + stats.totalProveedores}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-gray-600">Entidades activas</span>
            <span className="font-semibold text-green-600">{stats.clientesActivos + stats.unidadesActivas + stats.proveedoresActivos}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-600">Estado del sistema</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              Operativo
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};