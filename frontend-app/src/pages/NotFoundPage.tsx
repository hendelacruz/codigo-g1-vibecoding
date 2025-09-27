import React from 'react';
import { Button } from '../shared/components/ui/Button';

// NotFoundPage component
// 404 error page for unmatched routes
export const NotFoundPage: React.FC = () => {
  const handleGoToDashboard = () => {
    window.location.href = '/dashboard';
  };

  const handleGoToLogin = () => {
    window.location.href = '/login';
  };

  return (
    <div className="not-found-page min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300">404</h1>
        </div>
        
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Página no encontrada
          </h2>
          <p className="text-gray-600 text-lg">
            Lo sentimos, la página que buscas no existe o ha sido movida.
          </p>
        </div>

        <div className="space-x-4">
          <Button variant="default" onClick={handleGoToDashboard}>
            Ir al Dashboard
          </Button>
          
          <Button variant="outline" onClick={handleGoToLogin}>
            Iniciar Sesión
          </Button>
        </div>
      </div>
    </div>
  );
};