import React from 'react';
import * as Select from '@radix-ui/react-select';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../../shared/lib/utils';
import { useInventory } from '../../../inventory/hooks/useInventory';
import { LoadingSpinner } from '../../../../shared/components/ui/LoadingSpinner';
import type { SIMCard } from '../../../inventory/inventoryTypes';

// Component variants using CVA
const selectVariants = cva(
  'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border-gray-300',
        error: 'border-red-500 focus:ring-red-500',
      },
      size: {
        default: 'h-10',
        sm: 'h-8 text-xs',
        lg: 'h-12',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

// Component props interface
interface SimCardSelectProps extends VariantProps<typeof selectVariants> {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  includeAssigned?: boolean; // Include SIM cards that are already assigned
  className?: string;
  error?: string;
}

/**
 * SimCardSelect Component
 * 
 * A select component for choosing SIM cards from the inventory.
 * Supports filtering by availability status and displays relevant SIM card information.
 */
export const SimCardSelect: React.FC<SimCardSelectProps> = ({
  value,
  onValueChange,
  placeholder = "Seleccionar SIM Card...",
  disabled = false,
  includeAssigned = false,
  variant,
  size,
  className,
  error,
}) => {
  // Search state
  const [searchTerm, setSearchTerm] = React.useState('');
  const [isOpen, setIsOpen] = React.useState(false);

  // Fetch SIM cards using the inventory hook
  const { 
    simCards,
    loadSIMCards
  } = useInventory();

  const simCardItems = simCards.items;
  const isLoading = simCards.isLoading;
  const fetchError = simCards.error;

  // Load SIM cards on mount
  React.useEffect(() => {
    loadSIMCards();
  }, [loadSIMCards]);

  // Filter and search SIM cards
  const filteredSimCards = React.useMemo(() => {
    let filtered = includeAssigned 
      ? simCardItems 
      : simCardItems.filter((simCard: SIMCard) => simCard.estado === 'no_asignado');

    // Apply search filter
    if (searchTerm.trim()) {
      filtered = filtered.filter((simCard: SIMCard) => 
        simCard.numero_chip?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  }, [simCardItems, includeAssigned, searchTerm]);

  // Determine if component should be disabled
  const isDisabled = disabled || isLoading || !!fetchError;

  // Find selected SIM card for display
  const selectedSimCard = simCardItems.find((simCard: SIMCard) => simCard.id.toString() === value);

  return (
    <div className="w-full">
      <Select.Root
        {...(value ? { value } : {})}
        {...(onValueChange ? { onValueChange } : {})}
        disabled={isDisabled}
        open={isOpen}
        onOpenChange={setIsOpen}
      >
        <Select.Trigger
          className={cn(
            selectVariants({ variant: error ? 'error' : variant, size }),
            className
          )}
        >
          <Select.Value placeholder={placeholder}>
            {selectedSimCard ? selectedSimCard.numero_chip : placeholder}
          </Select.Value>
          <Select.Icon className="h-4 w-4 opacity-50">
            <svg
              width="15"
              height="15"
              viewBox="0 0 15 15"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="m4.93179 5.43179c.20264-.20264.53284-.20264.73548 0L7.5 7.26339 9.33173 5.43179c.20264-.20264.53284-.20264.73548 0 .20264.20264.20264.53284 0 .73548L8.23548 8.06727c-.20264.20264-.53284.20264-.73548 0L5.66821 6.16727c-.20264-.20264-.20264-.53284 0-.73548Z"
                fill="currentColor"
                fillRule="evenodd"
                clipRule="evenodd"
              />
            </svg>
          </Select.Icon>
        </Select.Trigger>

        <Select.Portal>
          <Select.Content className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white text-gray-900 shadow-lg animate-in fade-in-80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2">
            {/* Search input */}
            <div className="p-2 border-b border-gray-200">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Buscar por número de chip..."
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
                  Cargando SIM cards...
                </div>
              )}

              {/* Error state */}
              {fetchError && (
                <div className="py-6 text-center text-sm text-red-500">
                  Error al cargar SIM cards
                </div>
              )}

              {/* SIM cards options */}
              {!isLoading && !fetchError && filteredSimCards.map((simCard: SIMCard) => (
                <Select.Item
                  key={simCard.id}
                  value={simCard.id.toString()}
                  className="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-2 text-sm outline-none hover:bg-gray-100 focus:bg-blue-50 focus:text-blue-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                >
                  <Select.ItemIndicator className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </Select.ItemIndicator>
                  <Select.ItemText>
                    <span className="font-medium">{simCard.numero_chip}</span>
                  </Select.ItemText>
                </Select.Item>
              ))}

              {/* No data state */}
              {!isLoading && !fetchError && filteredSimCards.length === 0 && (
                <div className="py-6 text-center text-sm text-gray-500">
                  {searchTerm 
                    ? 'No se encontraron SIM cards' 
                    : (includeAssigned 
                        ? "No hay SIM cards disponibles" 
                        : "No hay SIM cards disponibles sin asignar"
                      )
                  }
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-500">
          {error}
        </p>
      )}
    </div>
  );
};

SimCardSelect.displayName = 'SimCardSelect';

export default SimCardSelect;