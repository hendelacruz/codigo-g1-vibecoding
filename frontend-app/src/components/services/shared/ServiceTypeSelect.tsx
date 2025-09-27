import React from 'react';
import { TIPO_TRABAJO_CHOICES, type TipoTrabajoChoice } from '../../../shared/utils/services/serviceConstants';

interface ServiceTypeSelectProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export const ServiceTypeSelect: React.FC<ServiceTypeSelectProps> = ({ 
  value, 
  onChange,
  placeholder = "Seleccionar tipo de trabajo",
  className = "",
  disabled = false
}) => {
  return (
    <select 
      value={value || ''} 
      onChange={(e) => onChange(e.target.value)}
      className={`px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${className}`}
      disabled={disabled}
    >
      <option value="">{placeholder}</option>
      {TIPO_TRABAJO_CHOICES.map((tipo: TipoTrabajoChoice) => (
         <option key={tipo.value} value={tipo.value}>
           {tipo.label}
         </option>
       ))}
    </select>
  );
};

export default ServiceTypeSelect;