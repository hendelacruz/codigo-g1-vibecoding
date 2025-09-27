import React from 'react';
import { createPortal } from 'react-dom';
import { HiXMark, HiEye, HiPencil, HiPlus } from 'react-icons/hi2';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import ServicioForm from './ServicioForm';
import ServiceStatusBadge from '../shared/ServiceStatusBadge';
import type { Servicio } from '../../../../shared/types/services/servicio';

type ModalMode = 'view' | 'edit' | 'create';

interface ServicioModalProps {
  mode: ModalMode;
  servicio?: Servicio | null;
  onClose: () => void;
  onSuccess?: () => void;
}

export const ServicioModal: React.FC<ServicioModalProps> = ({ 
  mode,
  servicio,
  onClose,
  onSuccess
}) => {
  const getModalTitle = () => {
    switch (mode) {
      case 'view':
        return 'Ver Servicio';
      case 'edit':
        return 'Editar Servicio';
      case 'create':
        return 'Crear Nuevo Servicio';
      default:
        return 'Servicio';
    }
  };

  const getModalIcon = () => {
    switch (mode) {
      case 'view':
        return <HiEye className="w-6 h-6" />;
      case 'edit':
        return <HiPencil className="w-6 h-6" />;
      case 'create':
        return <HiPlus className="w-6 h-6" />;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string): string => {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es });
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(price);
  };

  const handleSuccess = () => {
    onSuccess?.();
    onClose();
  };

  const modalContent = (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal Container */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className="relative w-full max-w-4xl bg-white rounded-lg shadow-xl max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                {getModalIcon()}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {getModalTitle()}
                </h2>
                {servicio && (
                  <p className="text-sm text-gray-500">
                    ID: {servicio.id} - {servicio.tipo_trabajo_nombre}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <HiXMark className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {mode === 'view' && servicio ? (
              // View Mode - Display service details
              <div className="space-y-6">
                {/* Status and Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Estado
                      </label>
                      <ServiceStatusBadge estado={servicio.estado_servicio} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Fecha del Servicio
                      </label>
                      <p className="text-gray-900">{formatDate(servicio.fecha)}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo de Trabajo
                      </label>
                      <p className="text-gray-900">{servicio.tipo_trabajo_nombre}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Precio
                      </label>
                      <p className="text-gray-900 font-semibold">{formatPrice(servicio.precio)}</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Cliente
                      </label>
                      <p className="text-gray-900">{servicio.cliente_nombre}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Técnico
                      </label>
                      <p className="text-gray-900">{servicio.tecnico_nombre}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Unidad
                      </label>
                      <p className="text-gray-900">{servicio.unidad_placa}</p>
                    </div>
                    {servicio.gps_codigo && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          GPS
                        </label>
                        <p className="text-gray-900">{servicio.gps_codigo}</p>
                      </div>
                    )}
                    {servicio.sim_numero && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          SIM Card
                        </label>
                        <p className="text-gray-900">{servicio.sim_numero}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Description and Observations */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Descripción
                    </label>
                    <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                      {servicio.descripcion}
                    </p>
                  </div>
                  {servicio.observaciones && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Observaciones
                      </label>
                      <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {servicio.observaciones}
                      </p>
                    </div>
                  )}
                </div>

                {/* Timestamps */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-200">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha de Creación
                    </label>
                    <p className="text-sm text-gray-600">{formatDate(servicio.created_at)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Última Actualización
                    </label>
                    <p className="text-sm text-gray-600">{formatDate(servicio.updated_at)}</p>
                  </div>
                </div>
              </div>
            ) : (
              // Edit/Create Mode - Show form
              <ServicioForm
                servicio={servicio ?? null}
                onSuccess={handleSuccess}
                onCancel={onClose}
              />
            )}
          </div>

          {/* Footer for view mode */}
          {mode === 'view' && (
            <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Cerrar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default ServicioModal;