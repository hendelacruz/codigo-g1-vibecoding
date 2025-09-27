import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ClientSelect } from '../ClientSelect';



// Create a wrapper with QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const QueryWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

// Demo component
export const ClientSelectDemo: React.FC = () => {
  const [selectedValue, setSelectedValue] = useState<string>('');
  const [variant, setVariant] = useState<'default' | 'error' | 'success'>('default');
  const [disabled, setDisabled] = useState(false);
  const [includeInactive, setIncludeInactive] = useState(false);

  return (
    <QueryWrapper>
      <div className="max-w-2xl mx-auto p-6 space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            ClientSelect Component Demo
          </h1>
          
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">Funcionalidades:</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• <strong>Búsqueda por nombre:</strong> Escribe "ABC" o "XYZ"</li>
              <li>• <strong>Búsqueda por RUC:</strong> Escribe "20987654321"</li>
              <li>• <strong>Filtrado en tiempo real:</strong> Los resultados se actualizan mientras escribes</li>
              <li>• <strong>Botón de limpiar:</strong> Usa el ícono X para limpiar la búsqueda</li>
              <li>• <strong>Solo nombre y RUC:</strong> Display optimizado sin información extra</li>
            </ul>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Variant
              </label>
              <select 
                value={variant} 
                onChange={(e) => setVariant(e.target.value as 'default' | 'error' | 'success')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="default">Default</option>
                <option value="error">Error</option>
                <option value="success">Success</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={disabled}
                  onChange={(e) => setDisabled(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Disabled</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Include Inactive</span>
              </label>
            </div>
          </div>

          {/* Component Demo */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cliente *
              </label>
              <ClientSelect
                value={selectedValue}
                onValueChange={setSelectedValue}
                placeholder="Buscar y seleccionar cliente..."
                variant={variant}
                disabled={disabled}
                includeInactive={includeInactive}
                {...(variant === 'error' ? { error: 'Este campo es requerido' } : {})}
              />
            </div>

            {/* Selected Value Display */}
            <div className="p-3 bg-gray-100 rounded-md">
              <p className="text-sm text-gray-600">
                <strong>Valor seleccionado:</strong> {selectedValue || 'Ninguno'}
              </p>
            </div>
          </div>
        </div>

        {/* Form Context Example */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            En contexto de formulario
          </h2>
          
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cliente *
              </label>
              <ClientSelect
                placeholder="Seleccionar cliente"
                onValueChange={(value) => console.log('Cliente seleccionado:', value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción del servicio
              </label>
              <textarea 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Describe el servicio a realizar..."
              />
            </div>
            
            <button 
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              Crear Servicio
            </button>
          </form>
        </div>
      </div>
    </QueryWrapper>
  );
};

export default ClientSelectDemo;