import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../shared/components/ui/Button';
import { Card, CardContent, CardHeader } from '../shared/components/ui/Card';

/**
 * UnauthorizedPage - Página de acceso denegado
 * 
 * Características:
 * - Diseño centrado y responsivo
 * - Integración con componentes Card para UI consistente
 * - Navegación hacia Dashboard o página anterior
 * - Iconografía clara para indicar acceso denegado
 * - Optimizado para accesibilidad
 * - Diferenciado de RoleGuard (página vs componente inline)
 * 
 * Casos de uso:
 * - Redirección desde rutas protegidas por permisos
 * - Acceso directo a /unauthorized
 * - Fallback para errores de autorización a nivel de aplicación
 * 
 * @author Frontend Team
 * @version 1.0.0
 */
export const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <Card className="shadow-lg">
          <CardHeader className="text-center pb-4">
            {/* Icono de acceso denegado */}
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg 
                className="w-8 h-8 text-red-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
                />
              </svg>
            </div>
            
            {/* Título principal */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Acceso Denegado
            </h1>
            
            {/* Descripción */}
            <p className="text-gray-600 text-sm leading-relaxed">
              No tienes permisos para acceder a esta página. 
              Si crees que esto es un error, contacta con tu administrador.
            </p>
          </CardHeader>
          
          <CardContent className="space-y-3 pt-2">
            {/* Botón principal - Ir al Dashboard */}
            <Button 
              onClick={handleGoToDashboard} 
              className="w-full"
              size="lg"
            >
              Ir al Dashboard
            </Button>
            
            {/* Botón secundario - Volver atrás */}
            <Button 
              onClick={handleGoBack} 
              variant="secondary"
              className="w-full"
              size="lg"
            >
              Volver Atrás
            </Button>
          </CardContent>
        </Card>
        
        {/* Información adicional */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Si necesitas acceso a esta sección, contacta con tu supervisor
          </p>
        </div>
      </div>
    </div>
  );
};

export default UnauthorizedPage;