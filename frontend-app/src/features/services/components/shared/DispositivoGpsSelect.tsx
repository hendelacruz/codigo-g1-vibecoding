import React, { useState, useMemo, memo } from 'react';
import * as Select from '@radix-ui/react-select';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import { useInventory } from '../../../inventory/hooks/useInventory';
import { LoadingSpinner } from '../../../../shared/components/ui/LoadingSpinner';
import type { GPS } from '../../../inventory/inventoryTypes';

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

export interface DispositivoGpsSelectProps extends VariantProps<typeof selectVariants> {
  value?: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
  includeAssigned?: boolean;
  'data-testid'?: string;
}

export const DispositivoGpsSelect: React.FC<DispositivoGpsSelectProps> = memo(({
  value,
  onValueChange,
  placeholder = "Seleccionar dispositivo GPS",
  disabled = false,
  error,
  className,
  variant = "default",
  size = "md",
  includeAssigned = false,
  'data-testid': testId,
}) => {
  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  // Fetch GPS devices using the inventory hook
  const { 
    gps,
    loadGPSDevices
  } = useInventory();

  const gpsDevices = gps.items;
  const isLoading = gps.isLoading;
  const fetchError = gps.error;

  // Load GPS devices on mount - simplified approach like SimCardSelect
  React.useEffect(() => {
    loadGPSDevices();
  }, [loadGPSDevices]);

  // Filter and search GPS devices
  const filteredGpsDevices = useMemo(() => {
    let filtered = includeAssigned 
      ? gpsDevices 
      : gpsDevices.filter((gps: GPS) => gps.estado === 'no_asignado');

    // Apply search filter
    if (searchTerm.trim()) {
      filtered = filtered.filter((gps: GPS) => 
        gps.imei?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  }, [gpsDevices, includeAssigned, searchTerm]);

  // Get selected GPS device for display
  const selectedGpsDevice = useMemo(() => {
    return gpsDevices.find((gps: GPS) => gps.id.toString() === value);
  }, [gpsDevices, value]);

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
          aria-label="Seleccionar dispositivo GPS"
        >
          <Select.Value placeholder={placeholder}>
            {selectedGpsDevice ? (
              <div className="flex flex-col text-left">
                <span className="font-medium">{selectedGpsDevice.imei}</span>
                <span className="text-xs text-gray-500">{selectedGpsDevice.marca} {selectedGpsDevice.modelo}</span>
              </div>
            ) : (
              placeholder
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
            className="overflow-hidden rounded-md bg-white shadow-lg border border-gray-200 z-50"
            position="popper"
            sideOffset={4}
          >
            <Select.Viewport className="p-1 max-h-[200px] overflow-y-auto">
              {/* Search input */}
              <div className="p-2 border-b border-gray-200">
                <input
                  type="text"
                  placeholder="Buscar por IMEI..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  onClick={(e) => e.stopPropagation()}
                />
              </div>

              {/* Loading state */}
              {isLoading && (
                <div className="px-3 py-2 text-sm text-gray-500 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                    Cargando dispositivos GPS...
                  </div>
                </div>
              )}

              {/* GPS devices options */}
              {!isLoading && !fetchError && filteredGpsDevices.map((gps: GPS) => (
                <Select.Item
                  key={gps.id}
                  value={gps.id.toString()}
                  className="flex items-center justify-between px-3 py-2 text-sm cursor-pointer hover:bg-gray-100 focus:bg-gray-100 focus:outline-none data-[highlighted]:bg-gray-100"
                >
                  <Select.ItemText>
                    <div className="flex flex-col">
                      <span className="font-medium">{gps.imei}</span>
                      <span className="text-xs text-gray-500">{gps.marca} {gps.modelo}</span>
                    </div>
                  </Select.ItemText>
                  <Select.ItemIndicator>
                    <svg
                      width="15"
                      height="15"
                      viewBox="0 0 15 15"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M11.4669 3.72684C11.7558 3.91574 11.8369 4.30308 11.648 4.59198L7.39799 11.092C7.29783 11.2452 7.13556 11.3467 6.95402 11.3699C6.77247 11.3931 6.58989 11.3355 6.45446 11.2124L3.70446 8.71241C3.44905 8.48022 3.43023 8.08494 3.66242 7.82953C3.89461 7.57412 4.28989 7.55529 4.5453 7.78749L6.75292 9.79441L10.6018 3.90792C10.7907 3.61902 11.178 3.53795 11.4669 3.72684Z"
                        fill="currentColor"
                        fillRule="evenodd"
                        clipRule="evenodd"
                      />
                    </svg>
                  </Select.ItemIndicator>
                </Select.Item>
              ))}

              {/* No data state */}
              {!isLoading && !fetchError && filteredGpsDevices.length === 0 && (
                <div className="px-3 py-2 text-sm text-gray-500 text-center">
                  {searchTerm ? 'No se encontraron dispositivos GPS' : 'No hay dispositivos GPS disponibles'}
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {(error || fetchError) && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error || 'Error al cargar dispositivos GPS'}
        </p>
      )}
    </div>
  );
});

DispositivoGpsSelect.displayName = 'DispositivoGpsSelect';

export default DispositivoGpsSelect;