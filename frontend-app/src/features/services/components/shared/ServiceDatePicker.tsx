import React from 'react';

interface ServiceDatePickerProps {
  value?: Date;
  onChange: (date: Date) => void;
  // Additional props interface to be defined
}

export const ServiceDatePicker: React.FC<ServiceDatePickerProps> = ({ 
  value, 
  onChange 
}) => {
  return (
    <input 
      type="date" 
      value={value?.toISOString().split('T')[0] || ''} 
      onChange={(e) => onChange(new Date(e.target.value))}
    />
  );
};

export default ServiceDatePicker;