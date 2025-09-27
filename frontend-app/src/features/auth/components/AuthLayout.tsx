import React from 'react';
import { Card, CardContent, CardHeader } from '../../../shared/components/ui/Card';

interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

/**
 * AuthLayout - Layout component para páginas de autenticación
 * 
 * Características:
 * - Diseño centrado y responsivo
 * - Integración con componentes Card para UI consistente
 * - Título y subtítulo personalizables
 * - Logo/branding integrado
 * - Optimizado para accesibilidad
 * 
 * @author Frontend Team
 * @version 1.0.0
 */
export const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title = "Iniciar Sesión",
  subtitle = "Accede a tu cuenta para continuar"
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {title}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {subtitle}
          </p>
        </div>
        
        <Card className="mt-8">
          <CardHeader className="space-y-1">
            <div className="flex justify-center">
              {/* Logo aquí */}
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">G1</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {children}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};