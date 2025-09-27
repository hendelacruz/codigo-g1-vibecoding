import { memo } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { FiCalendar, FiUser, FiTruck, FiDollarSign, FiEdit, FiEye, FiTrash2 } from 'react-icons/fi';
import type { Servicio } from '../../../../shared/types/services/servicio';
import ServiceStatusBadge from '../shared/ServiceStatusBadge';
import { formatCurrency } from '../../../../shared/lib/utils';

interface ServicioCardProps {
  servicio: Servicio;
  onView?: (servicio: Servicio) => void;
  onEdit?: (servicio: Servicio) => void;
  onDelete?: (servicio: Servicio) => void;
  className?: string;
}

// Función para formatear fecha
const formatDate = (dateString: string): string => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy', { locale: es });
  } catch {
    return 'Fecha inválida';
  }
};

// Función para formatear precio
const formatPrice = (price: number): string => {
  return formatCurrency(price);
};

// Lógica para determinar acciones según estado
const getStatusActions = (estado: Servicio['estado_servicio']) => {
  switch (estado) {
    case 'pendiente':
      return {
        canEdit: true,
        canDelete: true,
        canView: true,
        primaryAction: 'edit' as const,
      };
    case 'en_proceso':
      return {
        canEdit: true,
        canDelete: false,
        canView: true,
        primaryAction: 'view' as const,
      };
    case 'completado':
      return {
        canEdit: false,
        canDelete: false,
        canView: true,
        primaryAction: 'view' as const,
      };
    case 'cancelado':
    case 'reprogramado':
      return {
        canEdit: true,
        canDelete: true,
        canView: true,
        primaryAction: 'edit' as const,
      };
    default:
      return {
        canEdit: false,
        canDelete: false,
        canView: true,
        primaryAction: 'view' as const,
      };
  }
};

export const ServicioCard = memo<ServicioCardProps>(({
  servicio,
  onView,
  onEdit,
  onDelete,
  className = '',
}) => {
  const statusActions = getStatusActions(servicio.estado_servicio);

  const handleAction = (action: 'view' | 'edit' | 'delete') => {
    switch (action) {
      case 'view':
        onView?.(servicio);
        break;
      case 'edit':
        onEdit?.(servicio);
        break;
      case 'delete':
        onDelete?.(servicio);
        break;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
              {servicio.tipo_trabajo_nombre}
            </h3>
            <div className="flex items-center text-sm text-gray-600">
              <FiCalendar className="w-4 h-4 mr-1 flex-shrink-0" />
              <span className="truncate">{formatDate(servicio.fecha)}</span>
            </div>
          </div>
          <div className="flex-shrink-0">
            <ServiceStatusBadge estado={servicio.estado_servicio} size="sm" />
          </div>
        </div>
      </div>

      {/* Main Information */}
      <div className="p-4 space-y-3">
        <div className="grid grid-cols-1 gap-3">
          <div className="flex items-start text-sm min-w-0">
            <FiUser className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <span className="text-gray-600">Técnico:</span>
              <span className="ml-1 font-medium text-gray-900 block truncate">{servicio.tecnico_nombre}</span>
            </div>
          </div>
          
          <div className="flex items-start text-sm min-w-0">
            <FiTruck className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <span className="text-gray-600">Unidad:</span>
              <span className="ml-1 font-medium text-gray-900 block truncate">{servicio.unidad_placa}</span>
            </div>
          </div>
          
          <div className="flex items-start text-sm min-w-0">
            <FiUser className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <span className="text-gray-600">Cliente:</span>
              <span className="ml-1 font-medium text-gray-900 block truncate">{servicio.cliente_nombre}</span>
            </div>
          </div>
          
          <div className="flex items-start text-sm min-w-0">
            <FiDollarSign className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <span className="text-gray-600">Precio:</span>
              <span className="ml-1 font-semibold text-green-600 block truncate">{formatPrice(servicio.precio)}</span>
            </div>
          </div>
        </div>

        {/* Description */}
        {servicio.descripcion && (
          <div className="pt-2 border-t border-gray-100">
            <p 
              className="text-sm text-gray-600 overflow-hidden"
              style={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                wordBreak: 'break-word',
                hyphens: 'auto'
              }}
            >
              {servicio.descripcion}
            </p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-lg">
        <div className="flex items-center justify-end space-x-2 flex-wrap gap-1">
          {statusActions.canView && (
            <button
              onClick={() => handleAction('view')}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-100 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 transition-colors flex-shrink-0"
              title="Ver detalles"
            >
              <FiEye className="w-3 h-3 mr-1" />
              Ver
            </button>
          )}
          
          {statusActions.canEdit && (
            <button
              onClick={() => handleAction('edit')}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-100 rounded-md hover:bg-amber-200 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-1 transition-colors flex-shrink-0"
              title="Editar servicio"
            >
              <FiEdit className="w-3 h-3 mr-1" />
              Editar
            </button>
          )}
          
          {statusActions.canDelete && (
            <button
              onClick={() => handleAction('delete')}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-red-700 bg-red-100 rounded-md hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1 transition-colors flex-shrink-0"
              title="Eliminar servicio"
            >
              <FiTrash2 className="w-3 h-3 mr-1" />
              Eliminar
            </button>
          )}
        </div>
      </div>
    </div>
  );
});

ServicioCard.displayName = 'ServicioCard';

export default ServicioCard;