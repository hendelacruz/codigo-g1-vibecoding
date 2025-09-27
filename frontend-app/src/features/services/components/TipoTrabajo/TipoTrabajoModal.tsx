import React from 'react';
import { HiXMark } from 'react-icons/hi2';
import TipoTrabajoForm from './TipoTrabajoForm';
import { cn } from '../../../../shared/lib/utils';
import type { TipoTrabajo } from '../../../../shared/types/services/tipoTrabajo';

type ModalMode = 'view' | 'edit' | 'create';

interface TipoTrabajoModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: ModalMode;
  tipoTrabajo?: TipoTrabajo | null;
  onSuccess?: () => void;
}

export const TipoTrabajoModal: React.FC<TipoTrabajoModalProps> = ({ 
  isOpen, 
  onClose,
  mode,
  tipoTrabajo,
  onSuccess
}) => {
  if (!isOpen) return null;

  const handleSuccess = () => {
    onSuccess?.();
    onClose();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours > 0) {
      return `${hours}h ${remainingMinutes}m`;
    }
    return `${minutes}m`;
  };

  const getModalTitle = () => {
    switch (mode) {
      case 'view':
        return 'Detalles del Tipo de Trabajo';
      case 'edit':
        return 'Editar Tipo de Trabajo';
      case 'create':
        return 'Crear Nuevo Tipo de Trabajo';
      default:
        return 'Tipo de Trabajo';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {getModalTitle()}
            </h2>
            <button
               onClick={onClose}
               className="text-gray-400 hover:text-gray-600 transition-colors"
             >
               <HiXMark className="h-6 w-6" />
             </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {mode === 'view' && tipoTrabajo ? (
              <div className="space-y-6">
                {/* Información básica */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Nombre</label>
                    <p className="mt-1 text-sm text-gray-900">{tipoTrabajo.nombre}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Nombre Display</label>
                    <p className="mt-1 text-sm text-gray-900">{tipoTrabajo.nombre_display}</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">Descripción</label>
                  <p className="mt-1 text-sm text-gray-900">{tipoTrabajo.descripcion}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Precio Base</label>
                    <p className="mt-1 text-sm text-gray-900">{formatCurrency(tipoTrabajo.precio_base)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Duración Estimada</label>
                    <p className="mt-1 text-sm text-gray-900">{formatDuration(tipoTrabajo.duracion_estimada)}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Requiere GPS</label>
                    <p className="mt-1 text-sm text-gray-900">
                      <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                        tipoTrabajo.requiere_gps 
                          ? "bg-green-100 text-green-800" 
                          : "bg-gray-100 text-gray-800"
                      )}>
                        {tipoTrabajo.requiere_gps ? 'Sí' : 'No'}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Requiere SIM Card</label>
                    <p className="mt-1 text-sm text-gray-900">
                      <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                        tipoTrabajo.requiere_sim 
                          ? "bg-green-100 text-green-800" 
                          : "bg-gray-100 text-gray-800"
                      )}>
                        {tipoTrabajo.requiere_sim ? 'Sí' : 'No'}
                      </span>
                    </p>
                  </div>
                </div>

                {tipoTrabajo.servicios_count !== undefined && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Servicios Asociados</label>
                    <p className="mt-1 text-sm text-gray-900">{tipoTrabajo.servicios_count} servicios</p>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Estado</label>
                    <p className="mt-1 text-sm text-gray-900">
                      <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                        tipoTrabajo.is_active 
                          ? "bg-green-100 text-green-800" 
                          : "bg-red-100 text-red-800"
                      )}>
                        {tipoTrabajo.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Fecha de Creación</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(tipoTrabajo.created_at).toLocaleDateString('es-CO')}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <TipoTrabajoForm
                tipoTrabajo={mode === 'edit' ? (tipoTrabajo ?? null) : null}
                onSuccess={handleSuccess}
                onCancel={onClose}
              />
            )}
          </div>

          {/* Footer para modo view */}
          {mode === 'view' && (
            <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cerrar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TipoTrabajoModal;