import React from 'react';
import { FiClock, FiDollarSign, FiEdit, FiEye, FiTrash2, FiWifi, FiSmartphone } from 'react-icons/fi';
import { cn } from '../../../../shared/lib/utils';
import type { TipoTrabajo } from '../../../../shared/types/services/tipoTrabajo';

interface TipoTrabajoCardProps {
  tipoTrabajo: TipoTrabajo;
  onView?: (tipoTrabajo: TipoTrabajo) => void;
  onEdit?: (tipoTrabajo: TipoTrabajo) => void;
  onDelete?: (tipoTrabajo: TipoTrabajo) => void;
  className?: string;
}

export const TipoTrabajoCard: React.FC<TipoTrabajoCardProps> = ({
  tipoTrabajo,
  onView,
  onEdit,
  onDelete,
  className
}) => {
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

  return (
    <div className={cn(
      "bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200",
      className
    )}>
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {tipoTrabajo.nombre_display}
            </h3>
            <p className="text-sm text-gray-500 mb-2">
              {tipoTrabajo.nombre}
            </p>
            <div className="flex items-center space-x-2">
              <span className={cn(
                "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                tipoTrabajo.is_active 
                  ? "bg-green-100 text-green-800" 
                  : "bg-red-100 text-red-800"
              )}>
                {tipoTrabajo.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-1 ml-4">
            {onView && (
              <button
                onClick={() => onView(tipoTrabajo)}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                title="Ver detalles"
              >
                <FiEye className="w-4 h-4" />
              </button>
            )}
            {onEdit && (
              <button
                onClick={() => onEdit(tipoTrabajo)}
                className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors"
                title="Editar"
              >
                <FiEdit className="w-4 h-4" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(tipoTrabajo)}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                title="Eliminar"
              >
                <FiTrash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Descripción */}
        <p 
          className="text-sm text-gray-600 mb-4 overflow-hidden"
          style={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            wordBreak: 'break-word',
            hyphens: 'auto'
          }}
        >
          {tipoTrabajo.descripcion}
        </p>

        {/* Información principal */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center space-x-2">
            <FiDollarSign className="w-4 h-4 text-green-500" />
            <div>
              <p className="text-xs text-gray-500">Precio Base</p>
              <p className="text-sm font-medium text-gray-900">
                {formatCurrency(tipoTrabajo.precio_base)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <FiClock className="w-4 h-4 text-blue-500" />
            <div>
              <p className="text-xs text-gray-500">Duración</p>
              <p className="text-sm font-medium text-gray-900">
                {formatDuration(tipoTrabajo.duracion_estimada)}
              </p>
            </div>
          </div>
        </div>

        {/* Requerimientos */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <FiWifi className={cn(
              "w-4 h-4",
              tipoTrabajo.requiere_gps ? "text-green-500" : "text-gray-300"
            )} />
            <span className={cn(
              "text-xs",
              tipoTrabajo.requiere_gps ? "text-green-700" : "text-gray-400"
            )}>
              GPS
            </span>
          </div>
          
          <div className="flex items-center space-x-1">
            <FiSmartphone className={cn(
              "w-4 h-4",
              tipoTrabajo.requiere_sim ? "text-green-500" : "text-gray-300"
            )} />
            <span className={cn(
              "text-xs",
              tipoTrabajo.requiere_sim ? "text-green-700" : "text-gray-400"
            )}>
              SIM
            </span>
          </div>
        </div>

        {/* Servicios count si está disponible */}
        {tipoTrabajo.servicios_count !== undefined && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500">
              {tipoTrabajo.servicios_count} servicios asociados
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TipoTrabajoCard;