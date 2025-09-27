import React from 'react';

interface ServiceStatusBadgeProps {
  status: string;
  // Additional props interface to be defined
}

export const ServiceStatusBadge: React.FC<ServiceStatusBadgeProps> = ({ 
  status 
}) => {
  return (
    <span className="badge">
      {/* ServiceStatusBadge component implementation */}
      {status}
    </span>
  );
};

export default ServiceStatusBadge;