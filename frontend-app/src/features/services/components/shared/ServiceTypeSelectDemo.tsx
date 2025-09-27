import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ServiceTypeSelect } from './ServiceTypeSelect';

// Create a query client for the demo
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

/**
 * Demo component to showcase ServiceTypeSelect functionality
 * This component demonstrates all the features and variants of ServiceTypeSelect
 */
export const ServiceTypeSelectDemo: React.FC = () => {
  const [selectedValue, setSelectedValue] = useState<string>('');
  const [selectedValueWithInactive, setSelectedValueWithInactive] = useState<string>('');
  const [selectedValueError, setSelectedValueError] = useState<string>('');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="p-8 space-y-8 max-w-2xl mx-auto">
        <div className="space-y-4">
          <h1 className="text-2xl font-bold text-gray-900">
            ServiceTypeSelect Component Demo
          </h1>
          <p className="text-gray-600">
            Demonstrating the ServiceTypeSelect component with different configurations and states.
          </p>
        </div>

        {/* Basic Usage */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Basic Usage</h2>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Select Service Type
            </label>
            <ServiceTypeSelect
              value={selectedValue}
              onValueChange={setSelectedValue}
              placeholder="Choose a service type..."
            />
            {selectedValue && (
              <p className="text-sm text-green-600">
                Selected: {selectedValue}
              </p>
            )}
          </div>
        </div>

        {/* With Inactive Services */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Including Inactive Services</h2>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Select Service Type (including inactive)
            </label>
            <ServiceTypeSelect
              value={selectedValueWithInactive}
              onValueChange={setSelectedValueWithInactive}
              includeInactive={true}
              placeholder="Choose any service type..."
            />
            {selectedValueWithInactive && (
              <p className="text-sm text-green-600">
                Selected: {selectedValueWithInactive}
              </p>
            )}
          </div>
        </div>

        {/* Different Sizes */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Different Sizes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Small</label>
              <ServiceTypeSelect
                value=""
                onValueChange={() => {}}
                size="sm"
                placeholder="Small size"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Medium (Default)</label>
              <ServiceTypeSelect
                value=""
                onValueChange={() => {}}
                size="md"
                placeholder="Medium size"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Large</label>
              <ServiceTypeSelect
                value=""
                onValueChange={() => {}}
                size="lg"
                placeholder="Large size"
              />
            </div>
          </div>
        </div>

        {/* Different Variants */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Different Variants</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Default</label>
              <ServiceTypeSelect
                value=""
                onValueChange={() => {}}
                variant="default"
                placeholder="Default variant"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Success</label>
              <ServiceTypeSelect
                value=""
                onValueChange={() => {}}
                variant="success"
                placeholder="Success variant"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Error</label>
              <ServiceTypeSelect
                value={selectedValueError}
                onValueChange={setSelectedValueError}
                variant="error"
                error="Please select a valid service type"
                placeholder="Error variant"
              />
            </div>
          </div>
        </div>

        {/* Disabled State */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Disabled State</h2>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Disabled Select
            </label>
            <ServiceTypeSelect
              value=""
              onValueChange={() => {}}
              disabled={true}
              placeholder="This select is disabled"
            />
          </div>
        </div>

        {/* Custom Styling */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Custom Styling</h2>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Custom Styled Select
            </label>
            <ServiceTypeSelect
              value=""
              onValueChange={() => {}}
              className="border-2 border-blue-300 rounded-lg shadow-lg"
              placeholder="Custom styled select"
            />
          </div>
        </div>

        {/* Integration Example */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Form Integration Example</h2>
          <form className="space-y-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Service Type *
                </label>
                <ServiceTypeSelect
                  value={selectedValue}
                  onValueChange={setSelectedValue}
                  placeholder="Select service type"
                  data-testid="service-type-select"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Client Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter client name"
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                disabled={!selectedValue}
              >
                Create Service
              </button>
            </div>
          </form>
        </div>
      </div>
    </QueryClientProvider>
  );
};

export default ServiceTypeSelectDemo;