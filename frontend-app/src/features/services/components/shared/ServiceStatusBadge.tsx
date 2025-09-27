import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import type { EstadoServicio } from '../../../../shared/types/services/common';
import { ESTADO_SERVICIO_CHOICES } from '../../../../shared/utils/services/serviceConstants';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border font-medium',
  {
    variants: {
      size: {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-2 text-base'
      },
      color: {
        yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        blue: 'bg-blue-100 text-blue-800 border-blue-200',
        green: 'bg-green-100 text-green-800 border-green-200',
        red: 'bg-red-100 text-red-800 border-red-200',
        orange: 'bg-orange-100 text-orange-800 border-orange-200',
        purple: 'bg-purple-100 text-purple-800 border-purple-200'
      }
    },
    defaultVariants: {
      size: 'sm',
      color: 'blue'
    }
  }
);

interface ServiceStatusBadgeProps extends VariantProps<typeof badgeVariants> {
  estado: EstadoServicio;
  className?: string;
}

export const ServiceStatusBadge: React.FC<ServiceStatusBadgeProps> = ({ 
  estado, 
  size = 'sm', 
  className 
}) => {
  const estadoInfo = ESTADO_SERVICIO_CHOICES.find(e => e.value === estado);
  
  if (!estadoInfo) return null;

  return (
    <span className={cn(badgeVariants({ size, color: estadoInfo.color }), className)}>
      {estadoInfo.label}
    </span>
  );
};

export default ServiceStatusBadge;