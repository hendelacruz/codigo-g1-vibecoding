import React from 'react';
import * as Select from '@radix-ui/react-select';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import { useTipoTrabajos } from '../../hooks/useTipoTrabajo';
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

export interface ServiceTypeSelectProps extends VariantProps<typeof selectVariants> {
  value?: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
  includeInactive?: boolean;
  'data-testid'?: string;
}

export const ServiceTypeSelect: React.FC<ServiceTypeSelectProps> = ({
  value,
  onValueChange,
  placeholder = "Seleccionar tipo de trabajo",
  disabled = false,
  error,
  className,
  variant = "default",
  size = "md",
  includeInactive = false,
  'data-testid': testId,
}) => {
  // Fetch tipos de trabajo with optional inactive filter
  const { 
    data: tiposData, 
    isLoading, 
    error: fetchError 
  } = useTipoTrabajos(
    includeInactive ? {} : { is_active: true }
  );

  // Extract tipos from API response
  const tipos = tiposData?.results || [];

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
      >
        <Select.Trigger
          className={cn(
            selectVariants({ variant: currentVariant, size }),
            className
          )}
          data-testid={testId}
          aria-label="Seleccionar tipo de trabajo"
        >
          <Select.Value placeholder={placeholder} />
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

              {/* Tipos de trabajo options */}
              {tipos.map((tipo) => (
                <Select.Item
                  key={tipo.id}
                  value={tipo.id.toString()}
                  className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                  disabled={!tipo.is_active}
                >
                  <Select.ItemText>
                    <div className="flex flex-col">
                      <span className={cn(
                        "font-medium",
                        !tipo.is_active && "text-gray-400"
                      )}>
                        {tipo.nombre_display || tipo.nombre}
                      </span>
                      {tipo.descripcion && (
                        <span className="text-xs text-gray-500 truncate">
                          {tipo.descripcion}
                        </span>
                      )}
                      {tipo.precio_base && (
                        <span className="text-xs text-green-600">
                          ${tipo.precio_base.toLocaleString()}
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
              {!isLoading && tipos.length === 0 && (
                <div className="py-6 text-center text-sm text-gray-500">
                  No hay tipos de trabajo disponibles
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {(error || fetchError) && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error || 'Error al cargar tipos de trabajo'}
        </p>
      )}
    </div>
  );
};

ServiceTypeSelect.displayName = 'ServiceTypeSelect';

export default ServiceTypeSelect;