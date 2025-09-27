import React, { useState } from 'react';
import { FiPlus, FiSearch, FiFilter } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { useTipoTrabajos, useDeleteTipoTrabajo } from '../../hooks/useTipoTrabajo';
import TipoTrabajoCard from './TipoTrabajoCard';
import TipoTrabajoModal from './TipoTrabajoModal';
import { cn } from '../../../../shared/lib/utils';
import type { TipoTrabajo } from '../../../../shared/types/services/tipoTrabajo';

type ModalMode = 'view' | 'edit' | 'create';

interface TipoTrabajoListProps {
  className?: string;
}

export const TipoTrabajoList: React.FC<TipoTrabajoListProps> = ({ className }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>('view');
  const [selectedTipoTrabajo, setSelectedTipoTrabajo] = useState<TipoTrabajo | null>(null);

  const { data: tiposTrabajoResponse, isLoading, error, refetch } = useTipoTrabajos();
  const deleteMutation = useDeleteTipoTrabajo();

  // Extract array from API response
  const tiposTrabajo: TipoTrabajo[] = Array.isArray(tiposTrabajoResponse?.results) 
    ? tiposTrabajoResponse.results 
    : Array.isArray(tiposTrabajoResponse) 
    ? tiposTrabajoResponse 
    : [];

  // Filter tipos de trabajo based on search term and active status
  const filteredTiposTrabajo = tiposTrabajo.filter((tipoTrabajo: TipoTrabajo) => {
    const matchesSearch = tipoTrabajo.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tipoTrabajo.nombre_display.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tipoTrabajo.descripcion.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesActiveFilter = showActiveOnly ? tipoTrabajo.is_active : true;
    
    return matchesSearch && matchesActiveFilter;
  });

  const handleView = (tipoTrabajo: TipoTrabajo) => {
    setSelectedTipoTrabajo(tipoTrabajo);
    setModalMode('view');
    setIsModalOpen(true);
  };

  const handleEdit = (tipoTrabajo: TipoTrabajo) => {
    setSelectedTipoTrabajo(tipoTrabajo);
    setModalMode('edit');
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedTipoTrabajo(null);
    setModalMode('create');
    setIsModalOpen(true);
  };

  const handleDelete = async (tipoTrabajo: TipoTrabajo) => {
    if (window.confirm(`¿Estás seguro de que deseas eliminar el tipo de trabajo "${tipoTrabajo.nombre_display}"?`)) {
      try {
        await deleteMutation.mutateAsync(tipoTrabajo.id);
        toast.success('Tipo de trabajo eliminado exitosamente');
      } catch (error) {
        toast.error('Error al eliminar el tipo de trabajo');
        console.error('Error deleting tipo trabajo:', error);
      }
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedTipoTrabajo(null);
  };

  const handleModalSuccess = () => {
    refetch();
    setIsModalOpen(false);
    setSelectedTipoTrabajo(null);
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Error al cargar los tipos de trabajo</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tipos de Trabajo</h2>
          <p className="text-gray-600">Gestiona los tipos de trabajo disponibles</p>
        </div>
        <button
          onClick={handleCreate}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <FiPlus className="w-4 h-4 mr-2" />
          Nuevo Tipo de Trabajo
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar tipos de trabajo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Active filter */}
          <div className="flex items-center space-x-2">
            <FiFilter className="text-gray-400 w-4 h-4" />
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={showActiveOnly}
                onChange={(e) => setShowActiveOnly(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">Solo activos</span>
            </label>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Cargando tipos de trabajo...</p>
        </div>
      )}

      {/* Results count */}
      {!isLoading && (
        <div className="text-sm text-gray-600">
          Mostrando {filteredTiposTrabajo.length} de {tiposTrabajo.length} tipos de trabajo
        </div>
      )}

      {/* Grid */}
      {!isLoading && filteredTiposTrabajo.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTiposTrabajo.map((tipoTrabajo: TipoTrabajo) => (
            <TipoTrabajoCard
              key={tipoTrabajo.id}
              tipoTrabajo={tipoTrabajo}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && filteredTiposTrabajo.length === 0 && (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <FiFilter className="h-12 w-12" />
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No se encontraron tipos de trabajo</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || !showActiveOnly 
              ? 'Intenta ajustar los filtros de búsqueda'
              : 'Comienza creando un nuevo tipo de trabajo'
            }
          </p>
          {!searchTerm && showActiveOnly && (
            <div className="mt-6">
              <button
                onClick={handleCreate}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <FiPlus className="w-4 h-4 mr-2" />
                Crear Tipo de Trabajo
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      <TipoTrabajoModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        mode={modalMode}
        tipoTrabajo={selectedTipoTrabajo}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
};

export default TipoTrabajoList;