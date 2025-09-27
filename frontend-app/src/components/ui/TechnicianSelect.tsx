// src/components/ui/TechnicianSelect.tsx
import React, { useState, useMemo } from 'react';
import * as Select from '@radix-ui/react-select';
import { FiSearch, FiX, FiUser } from 'react-icons/fi';
import { useTechnicians } from '../../hooks/useTechnicians';
import type { User } from '../../shared/types/common';
import { cn } from '../../shared/lib/utils';
import { 
  formFieldVariants, 
  formLabelVariants, 
  formErrorVariants,
  type FormFieldVariants 
} from '../../shared/lib/form-styles';
import { LoadingSpinner } from '../../shared/components/ui/LoadingSpinner';

interface TechnicianSelectProps extends FormFieldVariants {
  value?: number;
  onChange: (technicianId: number | undefined) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  className?: string;
  name?: string;
  label?: string;
  'data-testid'?: string;
}

/**
 * Componente para seleccionar técnicos con filtro de búsqueda
 * Usa Radix UI Select con funcionalidad de búsqueda integrada
 * Sigue el mismo patrón que ClientSelect para consistencia
 */
export const TechnicianSelect: React.FC<TechnicianSelectProps> = ({
  value,
  onChange,
  placeholder = "Seleccionar técnico",
  disabled = false,
  required = false,
  error,
  className = "",
  name,
  label,
  variant = "default",
  size = "md",
  fieldType = "select",
  'data-testid': testId,
}) => {
  const { technicians, isLoading, isEmpty, error: fetchError } = useTechnicians();
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter technicians based on search term
  const filteredTechnicians = useMemo(() => {
    if (!searchTerm.trim()) return technicians;
    
    const term = searchTerm.toLowerCase().trim();
    return technicians.filter((technician: User) => 
      `${technician.first_name} ${technician.last_name}`.toLowerCase().includes(term) ||
      (technician.dni && technician.dni.toLowerCase().includes(term))
    );
  }, [technicians, searchTerm]);

  // Get selected technician for display
  const selectedTechnician = useMemo(() => {
    if (!value) return null;
    return technicians.find((tech: User) => tech.id === value) || null;
  }, [value, technicians]);

  // Determine if component should be disabled
  const isDisabled = disabled || isLoading;

  // Determine variant based on error state
  const currentVariant = error || fetchError ? "error" : variant;

  // Handle value change
  const handleValueChange = (newValue: string) => {
    onChange(newValue ? parseInt(newValue, 10) : undefined);
    setIsOpen(false);
  };

  const selectClasses = cn(
    formFieldVariants({ 
      variant: currentVariant, 
      size, 
      fieldType 
    }),
    className
  );

  return (
    <div className="w-full">
      {/* Label opcional */}
      {label && (
        <label 
          htmlFor={name}
          className={cn(
            formLabelVariants({ 
              variant: error ? "error" : "default",
              required 
            }),
            "mb-2 block"
          )}
        >
          {label}
        </label>
      )}

      <Select.Root
        {...(value ? { value: value.toString() } : {})}
        onValueChange={handleValueChange}
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
          className={selectClasses}
          data-testid={testId}
          aria-label="Seleccionar técnico"
        >
          <Select.Value placeholder={placeholder}>
            {selectedTechnician && (
              <span className="truncate flex items-center space-x-2">
                <FiUser className="h-4 w-4 text-gray-500" />
                <span>
                  {selectedTechnician.first_name} {selectedTechnician.last_name}
                </span>
                {selectedTechnician.dni && (
                  <span className="text-gray-500 ml-2">
                    • {selectedTechnician.dni}
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
                  placeholder="Buscar por nombre o DNI..."
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
              {/* Technicians options */}
              {filteredTechnicians.map((technician: User) => (
                <Select.Item
                  key={technician.id}
                  value={technician.id.toString()}
                  className="relative flex w-full cursor-default select-none items-center rounded-sm py-2 pl-8 pr-2 text-sm outline-none focus:bg-blue-50 focus:text-blue-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-gray-50"
                >
                  <Select.ItemText>
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium truncate flex items-center space-x-2">
                        <FiUser className="h-3 w-3 text-gray-500" />
                        <span>
                          {technician.first_name} {technician.last_name}
                        </span>
                      </span>
                      {technician.dni && (
                        <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                          {technician.dni}
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
              {!isLoading && filteredTechnicians.length === 0 && (
                <div className="py-6 text-center text-sm text-gray-500">
                  {searchTerm ? 'No se encontraron técnicos' : 'No hay técnicos disponibles'}
                </div>
              )}

              {/* Loading state */}
              {isLoading && (
                <div className="py-6 text-center">
                  <LoadingSpinner size="sm" />
                  <p className="text-sm text-gray-500 mt-2">Cargando técnicos...</p>
                </div>
              )}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      {/* Error message */}
      {(error || fetchError) && (
        <p className={cn(formErrorVariants({ variant: "error" }), "mt-1")} role="alert">
          {error || 'Error al cargar técnicos'}
        </p>
      )}
    </div>
  );
};

TechnicianSelect.displayName = 'TechnicianSelect';

export default TechnicianSelect;