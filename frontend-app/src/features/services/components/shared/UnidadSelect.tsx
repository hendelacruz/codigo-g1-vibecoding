import React from 'react';
import * as Select from '@radix-ui/react-select';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import { useUnidades } from '../../../entities/useEntities';
import { LoadingSpinner } from '../../../../shared/components/ui/LoadingSpinner';

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

export interface UnidadSelectProps extends VariantProps<typeof selectVariants> {
  value?: string;
  onValueChange: (value: string) => void;
  clienteId?: string | number | null | undefined;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
  includeInactive?: boolean;
  'data-testid'?: string;
}

export const UnidadSelect: React.FC<UnidadSelectProps> = ({
  value,
  onValueChange,
  placeholder = "Seleccionar unidad",
  disabled = false,
  error,
  className,
  variant = "default",
  size = "md",
  includeInactive = false,
  clienteId,
  'data-testid': testId,
}) => {
  // Search state
  const [searchTerm, setSearchTerm] = React.useState('');
  const [isOpen, setIsOpen] = React.useState(false);

  // Use useUnidades directly to get all units
  const { items: unidades, isLoading, error: fetchError } = useUnidades();

  // Filter and search unidades
  const filteredUnidades = React.useMemo(() => {
    let filtered = unidades || [];

    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter((unidad: any) => 
        unidad.placa?.toLowerCase().includes(term) ||
        unidad.marca?.toLowerCase().includes(term) ||
        unidad.modelo?.toLowerCase().includes(term) ||
        unidad.tipo?.toLowerCase().includes(term)
      );
    }

    return filtered;
  }, [unidades, searchTerm]);

  // Get selected unidad for display
  const selectedUnidad = React.useMemo(() => {
    return unidades?.find((unidad: any) => unidad.id.toString() === value);
  }, [unidades, value]);

  // Determine if component should be disabled
  const isDisabled = disabled || isLoading;

  // Determine variant based on error state
  const currentVariant = error || fetchError ? "error" : variant;

  return (
    <div className="w-full">
      <Select.Root
        {...(value ? { value } : {})}
        onValueChange={onValueChange}
        disabled={isDisabled}
        open={isOpen}
        onOpenChange={setIsOpen}
      >
        <Select.Trigger
          className={cn(
            selectVariants({ variant: currentVariant, size }),
            className
          )}
          data-testid={testId}
          aria-label="Seleccionar unidad vehicular"
        >
          <Select.Value placeholder={placeholder}>
            {selectedUnidad ? selectedUnidad.placa : placeholder}
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
            className="overflow-hidden rounded-md bg-white shadow-lg border border-gray-200 z-50"
            position="popper"
            sideOffset={4}
          >
            {/* Search input */}
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Buscar por placa, marca, modelo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  autoFocus
                />
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm('')}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            </div>

            <Select.Viewport className="p-1 max-h-[200px] overflow-y-auto">

              {/* Loading state */}
              {isLoading && (
                <div className="py-6 text-center text-sm text-gray-500">
                  <LoadingSpinner size="sm" className="mx-auto mb-2" />
                  Cargando unidades...
                </div>
              )}

              {/* Unidades options */}
              {!isLoading && filteredUnidades.map((unidad: any) => (
                <Select.Item
                  key={unidad.id}
                  value={unidad.id.toString()}
                  className="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-2 text-sm outline-none hover:bg-gray-100 focus:bg-blue-50 focus:text-blue-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                  disabled={!unidad.is_active}
                >
                  <Select.ItemText>
                    <div className="flex flex-col">
                      <span className={cn(
                        "font-medium",
                        !unidad.is_active && "text-gray-400"
                      )}>
                        {unidad.placa}
                      </span>
                      <span className="text-xs text-gray-500">
                        {unidad.marca} {unidad.modelo} - {unidad.tipo}
                      </span>
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
              {!isLoading && filteredUnidades.length === 0 && (
                <div className="py-6 text-center text-sm text-gray-500">
                  {searchTerm 
                    ? 'No se encontraron unidades con ese criterio' 
                    : 'No hay unidades disponibles'
                  }
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {(error || fetchError) && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error || 'Error al cargar unidades'}
        </p>
      )}
    </div>
  );
};

UnidadSelect.displayName = 'UnidadSelect';

export default UnidadSelect;