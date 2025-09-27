import React, { useState, useMemo } from 'react';
import * as Select from '@radix-ui/react-select';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import { useClientes } from '../../../entities/useEntities';
import { useUnidadesByClient } from '../../hooks/useUnidadesByClient';
import { LoadingSpinner } from '../../../../shared/components/ui/LoadingSpinner';
import { FiSearch, FiX } from 'react-icons/fi';

// Component variants using CVA
const selectVariants = cva(
  "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border-gray-300 hover:border-gray-400",
        error: "border-red-500 focus:ring-red-500",
        success: "border-green-500 focus:ring-green-500",
      },
      size: {
        sm: "h-8 px-2 text-xs",
        md: "h-10 px-3 text-sm",
        lg: "h-12 px-4 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface ClientSelectProps extends VariantProps<typeof selectVariants> {
  value?: string;
  onValueChange: (value: string) => void;
  onClienteFromPlate?: (clienteId: number) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
  includeInactive?: boolean;
  enablePlateSearch?: boolean;
  'data-testid'?: string;
}

export const ClientSelect: React.FC<ClientSelectProps> = ({
  value,
  onValueChange,
  onClienteFromPlate,
  placeholder = "Seleccionar cliente",
  disabled = false,
  error,
  className,
  variant = "default",
  size = "md",
  includeInactive = false,
  enablePlateSearch = false,
  'data-testid': testId,
}) => {
  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  // Fetch clientes using the entities hook
  const { 
    items: clientes, 
    isLoading, 
    error: fetchError,
    loadActivos
  } = useClientes();

  // Hook for plate search functionality
  const { findClienteByPlaca } = useUnidadesByClient({
    autoLoad: enablePlateSearch
  });

  // Load active clients on mount
  React.useEffect(() => {
    if (!includeInactive) {
      loadActivos();
    }
  }, [loadActivos, includeInactive]);

  // Filter and search clients
  const filteredClientes = useMemo(() => {
    let filtered = includeInactive 
      ? clientes 
      : clientes.filter(cliente => cliente.is_active);

    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      
      // Standard search by name and RUC
      let standardFiltered = filtered.filter(cliente => 
        cliente.nombre.toLowerCase().includes(term) ||
        (cliente.ruc && cliente.ruc.toLowerCase().includes(term))
      );

      // If plate search is enabled and no standard results, try plate search
      if (enablePlateSearch && standardFiltered.length === 0) {
        const clienteFromPlate = findClienteByPlaca(term);
        if (clienteFromPlate) {
          // Auto-select the client found by plate
          if (onClienteFromPlate) {
            onClienteFromPlate(clienteFromPlate.id);
          }
          return [clienteFromPlate];
        }
      }

      return standardFiltered;
    }

    return filtered;
  }, [clientes, searchTerm, includeInactive, enablePlateSearch, findClienteByPlaca, onClienteFromPlate]);

  // Get selected client for display
  const selectedClient = useMemo(() => {
    if (!value) return null;
    return clientes.find(cliente => cliente.id.toString() === value) || null;
  }, [value, clientes]);

  // Determine if component should be disabled
  const isDisabled = disabled || isLoading;

  // Determine variant based on error state
  const currentVariant = error || fetchError ? "error" : variant;

  return (
    <div className="w-full">
      <Select.Root
        {...(value ? { value } : {})}
        onValueChange={(newValue) => {
          onValueChange(newValue);
          setIsOpen(false);
        }}
        disabled={isDisabled}
        open={isOpen}
        onOpenChange={(open) => {
          setIsOpen(open);
          if (!open) {
            setSearchTerm('');
          }
        }}
      >
        <Select.Trigger
          className={cn(
            selectVariants({ variant: currentVariant, size }),
            className
          )}
          data-testid={testId}
          aria-label="Seleccionar cliente"
        >
          <Select.Value placeholder={placeholder}>
            {selectedClient && (
              <span className="truncate">
                {selectedClient.nombre}
                {selectedClient.ruc && (
                  <span className="text-gray-500 ml-2">
                    • {selectedClient.ruc}
                  </span>
                )}
              </span>
            )}
          </Select.Value>
          <Select.Icon>
            {isLoading ? (
              <LoadingSpinner size="sm" />
            ) : (
              <svg className="h-4 w-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            )}
          </Select.Icon>
        </Select.Trigger>

        <Select.Portal>
          <Select.Content 
            className="overflow-hidden rounded-md bg-white shadow-lg border border-gray-200 z-50 w-[var(--radix-select-trigger-width)]"
            position="popper"
            sideOffset={4}
          >
            {/* Search input */}
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <FiSearch className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={enablePlateSearch ? "Buscar por nombre, RUC o placa..." : "Buscar por nombre o RUC..."}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-8 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                />
                {searchTerm && (
                  <button
                    type="button"
                    onClick={() => setSearchTerm('')}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <FiX className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            <Select.Viewport className="p-1 max-h-[200px] overflow-y-auto">
              {/* Clientes options */}
              {filteredClientes.map((cliente) => (
                <Select.Item
                  key={cliente.id}
                  value={cliente.id.toString()}
                  className="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-2 text-sm outline-none focus:bg-blue-50 focus:text-blue-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-gray-50"
                  disabled={!cliente.is_active}
                >
                  <Select.ItemText>
                    <div className="flex items-center justify-between w-full">
                      <span className={cn(
                        "font-medium truncate",
                        !cliente.is_active && "text-gray-400"
                      )}>
                        {cliente.nombre}
                      </span>
                      {cliente.ruc && (
                        <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                          {cliente.ruc}
                        </span>
                      )}
                    </div>
                  </Select.ItemText>
                  <Select.ItemIndicator className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </Select.ItemIndicator>
                </Select.Item>
              ))}

              {/* No data state */}
              {!isLoading && filteredClientes.length === 0 && (
                <div className="py-6 text-center text-sm text-gray-500">
                  {searchTerm ? 'No se encontraron clientes' : 'No hay clientes disponibles'}
                </div>
              )}

              {/* Loading state */}
              {isLoading && (
                <div className="py-6 text-center">
                  <LoadingSpinner size="sm" />
                  <p className="text-sm text-gray-500 mt-2">Cargando clientes...</p>
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {(error || fetchError) && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error || 'Error al cargar clientes'}
        </p>
      )}
    </div>
  );
};

ClientSelect.displayName = 'ClientSelect';

export default ClientSelect;