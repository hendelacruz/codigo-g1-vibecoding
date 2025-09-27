import React, { useState, useMemo } from 'react';
import * as Select from '@radix-ui/react-select';
import { FiSearch, FiX } from 'react-icons/fi';
import { cn } from '../../../../shared/lib/utils';
import { formFieldVariants, type FormFieldVariants } from '../../../../shared/lib/form-styles';
import { ESTADO_SERVICIO_CHOICES } from '../../../../shared/utils/services/serviceConstants';
import type { EstadoServicio } from '../../../../shared/types/services/common';

export interface ServiceStatusSelectProps extends FormFieldVariants {
  value?: EstadoServicio;
  onValueChange: (value: EstadoServicio) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
  'data-testid'?: string;
}

export const ServiceStatusSelect: React.FC<ServiceStatusSelectProps> = ({
  value,
  onValueChange,
  placeholder = "Seleccionar estado",
  disabled = false,
  error,
  className,
  variant = "default",
  size = "md",
  fieldType = "select",
  'data-testid': testId,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  // Determine variant based on error state
  const currentVariant = error ? "error" : variant;

  // Get status badge classes
  const getStatusBadgeClasses = (status: EstadoServicio): string => {
    const badgeClasses: Record<EstadoServicio, string> = {
      pendiente: 'bg-yellow-100 text-yellow-800',
      programado: 'bg-blue-100 text-blue-800',
      en_proceso: 'bg-orange-100 text-orange-800',
      completado: 'bg-green-100 text-green-800',
      cancelado: 'bg-red-100 text-red-800',
      reprogramado: 'bg-purple-100 text-purple-800',
    };
    return badgeClasses[status] || 'bg-gray-100 text-gray-800';
  };

  // Filter status options based on search term
  const filteredStatuses = useMemo(() => {
    if (!searchTerm.trim()) return ESTADO_SERVICIO_CHOICES;
    
    return ESTADO_SERVICIO_CHOICES.filter(choice =>
      choice.label.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm]);

  // Clear search when closing
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) {
      setSearchTerm('');
    }
  };

  // Clear search term
  const clearSearch = () => {
    setSearchTerm('');
  };

  return (
    <div className="w-full">
      <Select.Root
        {...(value ? { value } : {})}
        onValueChange={onValueChange}
        disabled={disabled}
        open={isOpen}
        onOpenChange={handleOpenChange}
      >
        <Select.Trigger
          className={cn(
            formFieldVariants({ variant: currentVariant, size, fieldType }),
            className
          )}
          data-testid={testId}
          aria-label="Seleccionar estado del servicio"
        >
          <Select.Value placeholder={placeholder}>
            {value && (
              <div className="flex items-center space-x-2">
                <span className={cn(
                  'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                  getStatusBadgeClasses(value)
                )}>
                  {ESTADO_SERVICIO_CHOICES.find(choice => choice.value === value)?.label}
                </span>
              </div>
            )}
          </Select.Value>
          <Select.Icon>
            <svg className="h-4 w-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </Select.Icon>
        </Select.Trigger>

        <Select.Portal>
          <Select.Content 
            className="overflow-hidden rounded-md bg-white text-gray-900 shadow-lg border border-gray-200 z-50 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
            position="popper"
            sideOffset={4}
          >
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Buscar estado..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onClick={(e) => e.stopPropagation()}
                />
                {searchTerm && (
                  <button
                    type="button"
                    onClick={clearSearch}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <FiX className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            <Select.Viewport className="p-1 max-h-[200px] overflow-y-auto">
              {/* Status options */}
              {filteredStatuses.length > 0 ? (
                filteredStatuses.map((choice) => (
                  <Select.Item
                    key={choice.value}
                    value={choice.value}
                    className="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-gray-100"
                  >
                    <Select.ItemText>
                      <div className="flex items-center space-x-2">
                        <span className={cn(
                          'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                          getStatusBadgeClasses(choice.value as EstadoServicio)
                        )}>
                          {choice.label}
                        </span>
                      </div>
                    </Select.ItemText>
                    <Select.ItemIndicator className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </Select.ItemIndicator>
                  </Select.Item>
                ))
              ) : (
                <div className="py-6 text-center text-sm text-gray-500">
                  No se encontraron estados
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};

ServiceStatusSelect.displayName = 'ServiceStatusSelect';

export default ServiceStatusSelect;