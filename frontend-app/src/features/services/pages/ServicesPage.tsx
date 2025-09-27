import React from 'react';
import { ServicioDashboard } from '../components/Servicio/ServicioDashboard';

interface ServicesPageProps {
  className?: string;
}

/**
 * Main Services Page Component
 * 
 * This component serves as the main entry point for the Services module.
 * It integrates all service-related functionality including:
 * - Service management (CRUD operations)
 * - Work type management
 * - Statistics and metrics dashboard
 * - Quick actions and navigation
 */
export const ServicesPage: React.FC<ServicesPageProps> = ({ className = '' }) => {
  return (
    <div className={`services-page min-h-screen bg-gray-50 ${className}`}>
      <div className="container mx-auto px-4 py-6">
        <ServicioDashboard />
      </div>
    </div>
  );
};

export default ServicesPage;