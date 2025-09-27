import React, { useState } from 'react';
import { Button } from '../../../../shared/components/ui/Button';
import ServicioList from './ServicioList';
import ServicioForm from './ServicioForm';
import TipoTrabajoList from '../TipoTrabajo/TipoTrabajoList';
import TipoTrabajoForm from '../TipoTrabajo/TipoTrabajoForm';
import { useServicios } from '../../hooks/useServicio';
import { useTipoTrabajos } from '../../hooks/useTipoTrabajo';
import type { Servicio } from '../../../../shared/types/services/servicio';
import type { TipoTrabajo } from '../../../../shared/types/services/tipoTrabajo';

interface ServicioDashboardProps {
  className?: string;
}

type ViewMode = 'dashboard' | 'servicios' | 'tipos-trabajo' | 'nuevo-servicio' | 'nuevo-tipo';

export const ServicioDashboard: React.FC<ServicioDashboardProps> = ({ className = '' }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  // Use a large page_size to get all services for dashboard statistics
  const { data: serviciosData, isLoading: serviciosLoading, refetch: refetchServicios } = useServicios({ page_size: 1000 });
  const { data: tipoTrabajosData } = useTipoTrabajos();

  // Extract arrays from API response with memoization
  const servicios: Servicio[] = React.useMemo(() => {
    return Array.isArray(serviciosData?.results) ? serviciosData.results : 
           Array.isArray(serviciosData) ? serviciosData : [];
  }, [serviciosData]);

  const tipoTrabajos: TipoTrabajo[] = React.useMemo(() => {
    return Array.isArray(tipoTrabajosData?.results) ? tipoTrabajosData.results : 
           Array.isArray(tipoTrabajosData) ? tipoTrabajosData : [];
  }, [tipoTrabajosData]);

  // Calculate statistics
  const stats = React.useMemo(() => {
    const totalServicios = servicios.length;
    const serviciosPendientes = servicios.filter((s: Servicio) => s.estado_servicio === 'pendiente').length;
    const serviciosProgramados = servicios.filter((s: Servicio) => s.estado_servicio === 'programado').length;
    const serviciosEnProceso = servicios.filter((s: Servicio) => s.estado_servicio === 'en_proceso').length;
    const serviciosCompletados = servicios.filter((s: Servicio) => s.estado_servicio === 'completado').length;
    const serviciosCancelados = servicios.filter((s: Servicio) => s.estado_servicio === 'cancelado').length;
    const serviciosReprogramados = servicios.filter((s: Servicio) => s.estado_servicio === 'reprogramado').length;
    const totalTipoTrabajos = tipoTrabajos.length;
    const tiposActivos = tipoTrabajos.filter((t: TipoTrabajo) => t.is_active).length;

    return {
      totalServicios,
      serviciosPendientes,
      serviciosProgramados,
      serviciosEnProceso,
      serviciosCompletados,
      serviciosCancelados,
      serviciosReprogramados,
      totalTipoTrabajos,
      tiposActivos
    };
  }, [servicios, tipoTrabajos]);

  const renderDashboardView = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Módulo de Servicios</h1>
        <p className="text-gray-600">Gestiona servicios técnicos y tipos de trabajo</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Servicios</p>
              <p className="text-3xl font-bold text-blue-600">{stats.totalServicios}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <span className="text-2xl">🔧</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pendientes</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.serviciosPendientes}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Programados</p>
              <p className="text-3xl font-bold text-blue-600">{stats.serviciosProgramados}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">En Proceso</p>
              <p className="text-3xl font-bold text-orange-600">{stats.serviciosEnProceso}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <span className="text-2xl">🔄</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completados</p>
              <p className="text-3xl font-bold text-green-600">{stats.serviciosCompletados}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cancelados</p>
              <p className="text-3xl font-bold text-red-600">{stats.serviciosCancelados}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-full">
              <span className="text-2xl">❌</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Reprogramados</p>
              <p className="text-3xl font-bold text-purple-600">{stats.serviciosReprogramados}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <span className="text-2xl">🔄</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tipos de Trabajo</p>
              <p className="text-3xl font-bold text-purple-600">{stats.totalTipoTrabajos}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <span className="text-2xl">📋</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tipos Activos</p>
              <p className="text-3xl font-bold text-indigo-600">{stats.tiposActivos}</p>
            </div>
            <div className="p-3 bg-indigo-100 rounded-full">
              <span className="text-2xl">🎯</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            onClick={() => setViewMode('nuevo-servicio')}
            className="flex items-center justify-center space-x-2 h-12"
          >
            <span>➕</span>
            <span>Nuevo Servicio</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={() => setViewMode('servicios')}
            className="flex items-center justify-center space-x-2 h-12"
          >
            <span>📋</span>
            <span>Ver Servicios</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={() => setViewMode('nuevo-tipo')}
            className="flex items-center justify-center space-x-2 h-12"
          >
            <span>🏷️</span>
            <span>Nuevo Tipo</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={() => setViewMode('tipos-trabajo')}
            className="flex items-center justify-center space-x-2 h-12"
          >
            <span>📂</span>
            <span>Ver Tipos</span>
          </Button>
        </div>
      </div>

      {/* Recent Services Preview */}
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Servicios Recientes</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setViewMode('servicios')}
          >
            Ver todos →
          </Button>
        </div>
        
        {serviciosLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 mt-2">Cargando servicios...</p>
          </div>
        ) : servicios.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No hay servicios registrados</p>
            <Button
              onClick={() => setViewMode('nuevo-servicio')}
              className="mt-4"
            >
              Crear primer servicio
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {servicios.slice(0, 5).map((servicio: Servicio) => (
              <div key={servicio.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    Servicio #{servicio.id} - {servicio.descripcion}
                  </p>
                  <p className="text-sm text-gray-500">
                    Cliente: {servicio.cliente} | Fecha: {new Date(servicio.fecha).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    servicio.estado_servicio === 'completado' ? 'bg-green-100 text-green-800' :
                    servicio.estado_servicio === 'en_proceso' ? 'bg-orange-100 text-orange-800' :
                    servicio.estado_servicio === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {servicio.estado_servicio}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    S/ {servicio.precio}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (viewMode) {
      case 'servicios':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Lista de Servicios</h1>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setViewMode('dashboard')}
                >
                  ← Volver al Dashboard
                </Button>
                <Button onClick={() => setViewMode('nuevo-servicio')}>
                  Nuevo Servicio
                </Button>
              </div>
            </div>
            <ServicioList />
          </div>
        );

      case 'nuevo-servicio':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Nuevo Servicio</h1>
              <Button
                variant="outline"
                onClick={() => setViewMode('servicios')}
              >
                ← Volver a Servicios
              </Button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <ServicioForm
                onSuccess={() => {
                  setViewMode('servicios');
                  refetchServicios(); // Refresh data
                }}
                onCancel={() => setViewMode('servicios')}
              />
            </div>
          </div>
        );

      case 'tipos-trabajo':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Tipos de Trabajo</h1>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setViewMode('dashboard')}
                >
                  ← Volver al Dashboard
                </Button>
                <Button onClick={() => setViewMode('nuevo-tipo')}>
                  Nuevo Tipo
                </Button>
              </div>
            </div>
            <TipoTrabajoList />
          </div>
        );

      case 'nuevo-tipo':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Nuevo Tipo de Trabajo</h1>
              <Button
                variant="outline"
                onClick={() => setViewMode('tipos-trabajo')}
              >
                ← Volver a Tipos
              </Button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <TipoTrabajoForm />
            </div>
          </div>
        );

      default:
        return renderDashboardView();
    }
  };

  return (
    <div className={`services-dashboard ${className}`}>
      {renderContent()}
    </div>
  );
};

export default ServicioDashboard;