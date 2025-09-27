import React, { useState } from 'react';
import { useServicios } from '../../hooks/useServicio';
import { LoadingSpinner } from '../../../../shared/components/ui/LoadingSpinner';
import Pagination from '../../../../shared/components/ui/Pagination';
import ServicioCard from './ServicioCard';
import ServicioModal from './ServicioModal';
import type { Servicio } from '../../../../shared/types/services/servicio';

type ModalMode = 'view' | 'edit' | 'create';

interface ServicioListProps {
  className?: string;
}

const ServicioList: React.FC<ServicioListProps> = ({ className }) => {
  // State management
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedServicio, setSelectedServicio] = useState<Servicio | null>(null);
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);

  // Hooks
  const { 
    data: serviciosResponse, 
    isLoading, 
    error,
    refetch
  } = useServicios({
    page: currentPage
  });

  // Event handlers
  const handleView = (servicio: Servicio) => {
    setSelectedServicio(servicio);
    setModalMode('view');
  };

  const handleEdit = (servicio: Servicio) => {
    setSelectedServicio(servicio);
    setModalMode('edit');
  };

  const handleCreate = () => {
    setSelectedServicio(null);
    setModalMode('create');
  };

  const handleCloseModal = () => {
    setModalMode(null);
    setSelectedServicio(null);
  };

  const handleModalSuccess = () => {
    refetch();
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">
          Error al cargar los servicios
        </div>
        <p className="text-gray-600">
          {error instanceof Error ? error.message : 'Ha ocurrido un error inesperado'}
        </p>
      </div>
    );
  }

  const servicios = serviciosResponse?.results || [];
  const totalPages = Math.ceil((serviciosResponse?.count || 0) / 12);

  return (
    <div className={`space-y-6 ${className || ''}`}>
      {/* Header with create button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          Servicios
        </h2>
        <button
          onClick={handleCreate}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Crear Servicio
        </button>
      </div>

      {/* Services grid */}
      {servicios.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-2">
            No se encontraron servicios
          </div>
          <p className="text-gray-400">
            Ajusta los filtros o crea un nuevo servicio
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {servicios.map((servicio: Servicio) => (
              <ServicioCard
                key={servicio.id}
                servicio={servicio}
                onView={handleView}
                onEdit={handleEdit}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-8">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                maxVisiblePages={5}
              />
            </div>
          )}
        </>
      )}

      {/* Modal */}
      {modalMode && (
        <ServicioModal
          mode={modalMode}
          servicio={selectedServicio}
          onClose={handleCloseModal}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
  );
};

export { ServicioList };
export default ServicioList;