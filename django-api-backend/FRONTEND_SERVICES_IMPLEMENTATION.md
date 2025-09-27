# 🛠️ Fases de Implementación Frontend - Módulo Services
## React + Vite Implementation Guide

### 📋 Resumen del Módulo Services

El módulo **Services** gestiona servicios técnicos realizados a clientes, incluyendo:

- **TipoTrabajo**: Categorías de servicios (instalación, mantenimiento, etc.)
- **Servicio**: Trabajos realizados en unidades vehiculares
- **Estados**: pendiente, en_proceso, completado, cancelado, reprogramado
- **Relaciones**: Cliente, Unidad, Técnico, GPS, SIM Card

---

## 🎯 FASE 1: Setup Inicial y Configuración Base

### 1.1 Estructura de Carpetas
```
src/
├── components/
│   └── services/
│       ├── TipoTrabajo/
│       │   ├── TipoTrabajoList.jsx
│       │   ├── TipoTrabajoForm.jsx
│       │   ├── TipoTrabajoCard.jsx
│       │   └── TipoTrabajoModal.jsx
│       ├── Servicio/
│       │   ├── ServicioList.jsx
│       │   ├── ServicioForm.jsx
│       │   ├── ServicioCard.jsx
│       │   ├── ServicioModal.jsx
│       │   ├── ServicioFilters.jsx
│       │   └── ServicioDashboard.jsx
│       └── shared/
│           ├── ServiceStatusBadge.jsx
│           ├── ServiceTypeSelect.jsx
│           └── ServiceDatePicker.jsx
├── services/
│   └── api/
│       ├── servicesApi.js
│       ├── tipoTrabajoApi.js
│       └── servicioApi.js
├── hooks/
│   └── services/
│       ├── useTipoTrabajo.js
│       ├── useServicio.js
│       └── useServiceFilters.js
├── utils/
│   └── services/
│       ├── serviceHelpers.js
│       ├── serviceValidations.js
│       └── serviceConstants.js
└── pages/
    └── services/
        ├── ServicesPage.jsx
        ├── TipoTrabajoPage.jsx
        └── ServicioDashboard.jsx
```

### 1.2 Dependencias Necesarias
```bash
npm install @tanstack/react-query axios react-hook-form @hookform/resolvers yup
npm install react-router-dom @headlessui/react @heroicons/react
npm install date-fns react-datepicker tailwindcss
npm install react-select react-hot-toast
```

### 1.3 Configuración de Constants
```javascript
// src/utils/services/serviceConstants.js
export const ESTADO_SERVICIO_CHOICES = [
  { value: 'pendiente', label: 'Pendiente', color: 'yellow' },
  { value: 'en_proceso', label: 'En Proceso', color: 'blue' },
  { value: 'completado', label: 'Completado', color: 'green' },
  { value: 'cancelado', label: 'Cancelado', color: 'red' },
  { value: 'reprogramado', label: 'Reprogramado', color: 'orange' }
];

export const TIPO_TRABAJO_CHOICES = [
  { value: 'instalacion_nueva', label: 'Instalación Nueva' },
  { value: 'mantenimiento_preventivo', label: 'Mantenimiento Preventivo' },
  { value: 'mantenimiento_correctivo', label: 'Mantenimiento Correctivo' },
  { value: 'otro', label: 'Otro' }
];
```

---

## 🔌 FASE 2: Configuración de API y Servicios

### 2.1 API Base Configuration
```javascript
// src/services/api/servicesApi.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const servicesApi = axios.create({
  baseURL: `${API_BASE_URL}/services`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
servicesApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default servicesApi;
```

### 2.2 TipoTrabajo API Service
```javascript
// src/services/api/tipoTrabajoApi.js
import servicesApi from './servicesApi';

export const tipoTrabajoApi = {
  // GET /api/services/tipos-trabajo/
  getAll: (params = {}) => 
    servicesApi.get('/tipos-trabajo/', { params }),

  // GET /api/services/tipos-trabajo/{id}/
  getById: (id) => 
    servicesApi.get(`/tipos-trabajo/${id}/`),

  // POST /api/services/tipos-trabajo/
  create: (data) => 
    servicesApi.post('/tipos-trabajo/', data),

  // PUT /api/services/tipos-trabajo/{id}/
  update: (id, data) => 
    servicesApi.put(`/tipos-trabajo/${id}/`, data),

  // PATCH /api/services/tipos-trabajo/{id}/
  partialUpdate: (id, data) => 
    servicesApi.patch(`/tipos-trabajo/${id}/`, data),

  // DELETE /api/services/tipos-trabajo/{id}/
  delete: (id) => 
    servicesApi.delete(`/tipos-trabajo/${id}/`),

  // PATCH /api/services/tipos-trabajo/{id}/toggle_active/
  toggleActive: (id) => 
    servicesApi.patch(`/tipos-trabajo/${id}/toggle_active/`),

  // GET /api/services/tipos-trabajo/{id}/servicios/
  getServicios: (id, params = {}) => 
    servicesApi.get(`/tipos-trabajo/${id}/servicios/`, { params }),

  // GET /api/services/tipos-trabajo/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get('/tipos-trabajo/estadisticas/', { params })
};
```

### 2.3 Servicio API Service
```javascript
// src/services/api/servicioApi.js
import servicesApi from './servicesApi';

export const servicioApi = {
  // GET /api/services/servicios/
  getAll: (params = {}) => 
    servicesApi.get('/servicios/', { params }),

  // GET /api/services/servicios/{id}/
  getById: (id) => 
    servicesApi.get(`/servicios/${id}/`),

  // POST /api/services/servicios/
  create: (data) => 
    servicesApi.post('/servicios/', data),

  // PUT /api/services/servicios/{id}/
  update: (id, data) => 
    servicesApi.put(`/servicios/${id}/`, data),

  // PATCH /api/services/servicios/{id}/
  partialUpdate: (id, data) => 
    servicesApi.patch(`/servicios/${id}/`, data),

  // DELETE /api/services/servicios/{id}/
  delete: (id) => 
    servicesApi.delete(`/servicios/${id}/`),

  // PATCH /api/services/servicios/{id}/cambiar_estado/
  cambiarEstado: (id, estado) => 
    servicesApi.patch(`/servicios/${id}/cambiar_estado/`, { estado }),

  // PATCH /api/services/servicios/{id}/toggle_active/
  toggleActive: (id) => 
    servicesApi.patch(`/servicios/${id}/toggle_active/`),

  // GET /api/services/servicios/estadisticas/
  getEstadisticas: (params = {}) => 
    servicesApi.get('/servicios/estadisticas/', { params }),

  // GET /api/services/servicios/dashboard/
  getDashboard: (params = {}) => 
    servicesApi.get('/servicios/dashboard/', { params })
};
```

---

## 🎣 FASE 3: Custom Hooks con React Query

### 3.1 TipoTrabajo Hooks
```javascript
// src/hooks/services/useTipoTrabajo.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tipoTrabajoApi } from '../../services/api/tipoTrabajoApi';
import { toast } from 'react-hot-toast';

export const useTipoTrabajos = (params = {}) => {
  return useQuery({
    queryKey: ['tipoTrabajos', params],
    queryFn: () => tipoTrabajoApi.getAll(params),
    select: (data) => data.data,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useTipoTrabajo = (id) => {
  return useQuery({
    queryKey: ['tipoTrabajo', id],
    queryFn: () => tipoTrabajoApi.getById(id),
    select: (data) => data.data,
    enabled: !!id,
  });
};

export const useCreateTipoTrabajo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: tipoTrabajoApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tipoTrabajos'] });
      toast.success('Tipo de trabajo creado exitosamente');
    },
    onError: (error) => {
      toast.error('Error al crear tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const useUpdateTipoTrabajo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => tipoTrabajoApi.update(id, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tipoTrabajos'] });
      queryClient.invalidateQueries({ queryKey: ['tipoTrabajo', variables.id] });
      toast.success('Tipo de trabajo actualizado exitosamente');
    },
    onError: (error) => {
      toast.error('Error al actualizar tipo de trabajo');
      console.error('Error:', error);
    },
  });
};

export const useDeleteTipoTrabajo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: tipoTrabajoApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tipoTrabajos'] });
      toast.success('Tipo de trabajo eliminado exitosamente');
    },
    onError: (error) => {
      toast.error('Error al eliminar tipo de trabajo');
      console.error('Error:', error);
    },
  });
};
```

### 3.2 Servicio Hooks
```javascript
// src/hooks/services/useServicio.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { servicioApi } from '../../services/api/servicioApi';
import { toast } from 'react-hot-toast';

export const useServicios = (params = {}) => {
  return useQuery({
    queryKey: ['servicios', params],
    queryFn: () => servicioApi.getAll(params),
    select: (data) => data.data,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useServicio = (id) => {
  return useQuery({
    queryKey: ['servicio', id],
    queryFn: () => servicioApi.getById(id),
    select: (data) => data.data,
    enabled: !!id,
  });
};

export const useCreateServicio = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: servicioApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servicios'] });
      toast.success('Servicio creado exitosamente');
    },
    onError: (error) => {
      toast.error('Error al crear servicio');
      console.error('Error:', error);
    },
  });
};

export const useCambiarEstadoServicio = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, estado }) => servicioApi.cambiarEstado(id, estado),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['servicios'] });
      queryClient.invalidateQueries({ queryKey: ['servicio', variables.id] });
      toast.success('Estado del servicio actualizado');
    },
    onError: (error) => {
      toast.error('Error al cambiar estado del servicio');
      console.error('Error:', error);
    },
  });
};
```

---

## 🧩 FASE 4: Componentes Base y Reutilizables

### 4.1 Service Status Badge
```javascript
// src/components/services/shared/ServiceStatusBadge.jsx
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';

const ServiceStatusBadge = ({ estado, size = 'sm' }) => {
  const estadoInfo = ESTADO_SERVICIO_CHOICES.find(e => e.value === estado);
  
  if (!estadoInfo) return null;

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const colorClasses = {
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    green: 'bg-green-100 text-green-800 border-green-200',
    red: 'bg-red-100 text-red-800 border-red-200',
    orange: 'bg-orange-100 text-orange-800 border-orange-200'
  };

  return (
    <span className={`
      inline-flex items-center rounded-full border font-medium
      ${sizeClasses[size]}
      ${colorClasses[estadoInfo.color]}
    `}>
      {estadoInfo.label}
    </span>
  );
};

export default ServiceStatusBadge;
```

### 4.2 Service Type Select
```javascript
// src/components/services/shared/ServiceTypeSelect.jsx
import { useTipoTrabajos } from '../../../hooks/services/useTipoTrabajo';
import Select from 'react-select';

const ServiceTypeSelect = ({ value, onChange, placeholder = "Seleccionar tipo...", isDisabled = false }) => {
  const { data: tipoTrabajos, isLoading } = useTipoTrabajos({ is_active: true });

  const options = tipoTrabajos?.results?.map(tipo => ({
    value: tipo.id,
    label: tipo.nombre_display
  })) || [];

  const selectedOption = options.find(option => option.value === value);

  return (
    <Select
      value={selectedOption}
      onChange={(option) => onChange(option?.value || null)}
      options={options}
      placeholder={placeholder}
      isLoading={isLoading}
      isDisabled={isDisabled}
      isClearable
      className="react-select-container"
      classNamePrefix="react-select"
    />
  );
};

export default ServiceTypeSelect;
```

### 4.3 Service Filters Component
```javascript
// src/components/services/Servicio/ServicioFilters.jsx
import { useState } from 'react';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';
import ServiceTypeSelect from '../shared/ServiceTypeSelect';
import ServiceStatusBadge from '../shared/ServiceStatusBadge';
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';

const ServicioFilters = ({ filters, onFiltersChange, onSearch }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key, value) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      {/* Búsqueda principal */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar servicios..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <FunnelIcon className="h-5 w-5" />
          Filtros
        </button>
      </div>

      {/* Filtros expandidos */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado
            </label>
            <select
              value={filters.estado_servicio || ''}
              onChange={(e) => handleFilterChange('estado_servicio', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los estados</option>
              {ESTADO_SERVICIO_CHOICES.map(estado => (
                <option key={estado.value} value={estado.value}>
                  {estado.label}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo de Trabajo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Trabajo
            </label>
            <ServiceTypeSelect
              value={filters.tipo_trabajo || null}
              onChange={(value) => handleFilterChange('tipo_trabajo', value)}
              placeholder="Todos los tipos"
            />
          </div>

          {/* Fecha Desde */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fecha Desde
            </label>
            <input
              type="date"
              value={filters.fecha_desde || ''}
              onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fecha Hasta */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fecha Hasta
            </label>
            <input
              type="date"
              value={filters.fecha_hasta || ''}
              onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Botón limpiar filtros */}
          <div className="md:col-span-2 lg:col-span-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Limpiar filtros
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ServicioFilters;
```

---

## 📋 FASE 5: Componentes de Lista y Tarjetas

### 5.1 Servicio Card Component
```javascript
// src/components/services/Servicio/ServicioCard.jsx
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  CalendarIcon, 
  UserIcon, 
  TruckIcon,
  CurrencyDollarIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import ServiceStatusBadge from '../shared/ServiceStatusBadge';

const ServicioCard = ({ servicio, onView, onEdit, onChangeStatus }) => {
  const formatDate = (dateString) => {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(price);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {servicio.tipo_trabajo_nombre}
            </h3>
            <p className="text-sm text-gray-500">
              ID: {servicio.id}
            </p>
          </div>
          <ServiceStatusBadge estado={servicio.estado_servicio} />
        </div>

        {/* Información principal */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <CalendarIcon className="h-4 w-4 mr-2" />
            {formatDate(servicio.fecha)}
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <UserIcon className="h-4 w-4 mr-2" />
            <span className="font-medium">{servicio.tecnico_nombre}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <TruckIcon className="h-4 w-4 mr-2" />
            {servicio.cliente_nombre} - {servicio.unidad_placa}
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <CurrencyDollarIcon className="h-4 w-4 mr-2" />
            <span className="font-semibold text-green-600">
              {formatPrice(servicio.precio)}
            </span>
          </div>
        </div>

        {/* Descripción */}
        {servicio.descripcion && (
          <div className="mb-4">
            <p className="text-sm text-gray-700 line-clamp-2">
              {servicio.descripcion}
            </p>
          </div>
        )}

        {/* Acciones */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="flex space-x-2">
            <button
              onClick={() => onView(servicio)}
              className="flex items-center px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-md"
            >
              <EyeIcon className="h-4 w-4 mr-1" />
              Ver
            </button>
            <button
              onClick={() => onEdit(servicio)}
              className="flex items-center px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded-md"
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              Editar
            </button>
          </div>
          
          {/* Cambio rápido de estado */}
          {servicio.estado_servicio === 'pendiente' && (
            <button
              onClick={() => onChangeStatus(servicio.id, 'en_proceso')}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Iniciar
            </button>
          )}
          {servicio.estado_servicio === 'en_proceso' && (
            <button
              onClick={() => onChangeStatus(servicio.id, 'completado')}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Completar
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ServicioCard;
```

### 5.2 Servicio List Component
```javascript
// src/components/services/Servicio/ServicioList.jsx
import { useState } from 'react';
import { useServicios } from '../../../hooks/services/useServicio';
import { useCambiarEstadoServicio } from '../../../hooks/services/useServicio';
import ServicioCard from './ServicioCard';
import ServicioFilters from './ServicioFilters';
import ServicioModal from './ServicioModal';
import LoadingSpinner from '../../common/LoadingSpinner';
import Pagination from '../../common/Pagination';

const ServicioList = () => {
  const [filters, setFilters] = useState({});
  const [selectedServicio, setSelectedServicio] = useState(null);
  const [modalMode, setModalMode] = useState(null); // 'view', 'edit', 'create'
  const [currentPage, setCurrentPage] = useState(1);

  const { data: serviciosData, isLoading, error } = useServicios({
    ...filters,
    page: currentPage,
    page_size: 12
  });

  const cambiarEstadoMutation = useCambiarEstadoServicio();

  const handleView = (servicio) => {
    setSelectedServicio(servicio);
    setModalMode('view');
  };

  const handleEdit = (servicio) => {
    setSelectedServicio(servicio);
    setModalMode('edit');
  };

  const handleCreate = () => {
    setSelectedServicio(null);
    setModalMode('create');
  };

  const handleChangeStatus = (servicioId, nuevoEstado) => {
    cambiarEstadoMutation.mutate({ id: servicioId, estado: nuevoEstado });
  };

  const closeModal = () => {
    setSelectedServicio(null);
    setModalMode(null);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div>Error al cargar servicios</div>;

  const servicios = serviciosData?.results || [];
  const totalPages = Math.ceil((serviciosData?.count || 0) / 12);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Servicios</h1>
          <p className="text-gray-600">
            {serviciosData?.count || 0} servicios encontrados
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Nuevo Servicio
        </button>
      </div>

      {/* Filtros */}
      <ServicioFilters
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Lista de servicios */}
      {servicios.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No se encontraron servicios</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servicios.map((servicio) => (
              <ServicioCard
                key={servicio.id}
                servicio={servicio}
                onView={handleView}
                onEdit={handleEdit}
                onChangeStatus={handleChangeStatus}
              />
            ))}
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          )}
        </>
      )}

      {/* Modal */}
      {modalMode && (
        <ServicioModal
          mode={modalMode}
          servicio={selectedServicio}
          onClose={closeModal}
        />
      )}
    </div>
  );
};

export default ServicioList;
```

---

## 📝 FASE 6: Formularios y Modales

### 6.1 Servicio Form Component
```javascript
// src/components/services/Servicio/ServicioForm.jsx
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useCreateServicio, useUpdateServicio } from '../../../hooks/services/useServicio';
import ServiceTypeSelect from '../shared/ServiceTypeSelect';
import { ESTADO_SERVICIO_CHOICES } from '../../../utils/services/serviceConstants';

const schema = yup.object({
  fecha: yup.date().required('La fecha es requerida'),
  tipo_trabajo: yup.number().required('El tipo de trabajo es requerido'),
  tecnico_dni: yup.string().required('El técnico es requerido'),
  cliente: yup.number().required('El cliente es requerido'),
  unidad: yup.number().required('La unidad es requerida'),
  descripcion: yup.string().required('La descripción es requerida'),
  precio: yup.number().positive('El precio debe ser positivo').required('El precio es requerido'),
  estado_servicio: yup.string().required('El estado es requerido'),
});

const ServicioForm = ({ servicio, onSuccess, onCancel }) => {
  const isEditing = !!servicio;
  const createMutation = useCreateServicio();
  const updateMutation = useUpdateServicio();

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      fecha: servicio?.fecha ? new Date(servicio.fecha).toISOString().slice(0, 16) : '',
      tipo_trabajo: servicio?.tipo_trabajo || '',
      tecnico_dni: servicio?.tecnico_dni || '',
      cliente: servicio?.cliente || '',
      unidad: servicio?.unidad || '',
      gps: servicio?.gps || '',
      sim_card: servicio?.sim_card || '',
      descripcion: servicio?.descripcion || '',
      precio: servicio?.precio || '',
      estado_servicio: servicio?.estado_servicio || 'pendiente',
      observaciones: servicio?.observaciones || '',
    }
  });

  const onSubmit = async (data) => {
    try {
      if (isEditing) {
        await updateMutation.mutateAsync({ id: servicio.id, data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onSuccess?.();
    } catch (error) {
      console.error('Error al guardar servicio:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Fecha */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha y Hora *
          </label>
          <Controller
            name="fecha"
            control={control}
            render={({ field }) => (
              <input
                type="datetime-local"
                {...field}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            )}
          />
          {errors.fecha && (
            <p className="text-red-500 text-sm mt-1">{errors.fecha.message}</p>
          )}
        </div>

        {/* Tipo de Trabajo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Trabajo *
          </label>
          <Controller
            name="tipo_trabajo"
            control={control}
            render={({ field }) => (
              <ServiceTypeSelect
                value={field.value}
                onChange={field.onChange}
                placeholder="Seleccionar tipo de trabajo"
              />
            )}
          />
          {errors.tipo_trabajo && (
            <p className="text-red-500 text-sm mt-1">{errors.tipo_trabajo.message}</p>
          )}
        </div>

        {/* Técnico DNI */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            DNI del Técnico *
          </label>
          <Controller
            name="tecnico_dni"
            control={control}
            render={({ field }) => (
              <input
                type="text"
                {...field}
                placeholder="12345678"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            )}
          />
          {errors.tecnico_dni && (
            <p className="text-red-500 text-sm mt-1">{errors.tecnico_dni.message}</p>
          )}
        </div>

        {/* Estado */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estado *
          </label>
          <Controller
            name="estado_servicio"
            control={control}
            render={({ field }) => (
              <select
                {...field}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              >
                {ESTADO_SERVICIO_CHOICES.map(estado => (
                  <option key={estado.value} value={estado.value}>
                    {estado.label}
                  </option>
                ))}
              </select>
            )}
          />
          {errors.estado_servicio && (
            <p className="text-red-500 text-sm mt-1">{errors.estado_servicio.message}</p>
          )}
        </div>

        {/* Precio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Precio (S/) *
          </label>
          <Controller
            name="precio"
            control={control}
            render={({ field }) => (
              <input
                type="number"
                step="0.01"
                {...field}
                placeholder="0.00"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              />
            )}
          />
          {errors.precio && (
            <p className="text-red-500 text-sm mt-1">{errors.precio.message}</p>
          )}
        </div>
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Descripción del Trabajo *
        </label>
        <Controller
          name="descripcion"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={4}
              placeholder="Describe el trabajo a realizar..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          )}
        />
        {errors.descripcion && (
          <p className="text-red-500 text-sm mt-1">{errors.descripcion.message}</p>
        )}
      </div>

      {/* Observaciones */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Observaciones
        </label>
        <Controller
          name="observaciones"
          control={control}
          render={({ field }) => (
            <textarea
              {...field}
              rows={3}
              placeholder="Observaciones adicionales..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          )}
        />
      </div>

      {/* Botones */}
      <div className="flex justify-end space-x-4 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear')}
        </button>
      </div>
    </form>
  );
};

export default ServicioForm;
```

---

## 📊 FASE 7: Dashboard y Estadísticas

### 7.1 Services Dashboard
```javascript
// src/components/services/Servicio/ServicioDashboard.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { servicioApi } from '../../../services/api/servicioApi';
import { 
  ChartBarIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

const ServicioDashboard = () => {
  const [dateRange, setDateRange] = useState({
    fecha_desde: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    fecha_hasta: new Date().toISOString().split('T')[0]
  });

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['servicios-dashboard', dateRange],
    queryFn: () => servicioApi.getDashboard(dateRange),
    select: (data) => data.data
  });

  const { data: estadisticas } = useQuery({
    queryKey: ['servicios-estadisticas', dateRange],
    queryFn: () => servicioApi.getEstadisticas(dateRange),
    select: (data) => data.data
  });

  if (isLoading) {
    return <div>Cargando dashboard...</div>;
  }

  const stats = [
    {
      name: 'Servicios Pendientes',
      value: estadisticas?.pendientes || 0,
      icon: ClockIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    },
    {
      name: 'En Proceso',
      value: estadisticas?.en_proceso || 0,
      icon: ChartBarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Completados',
      value: estadisticas?.completados || 0,
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Cancelados',
      value: estadisticas?.cancelados || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard de Servicios</h1>
        
        {/* Filtro de fechas */}
        <div className="flex space-x-4">
          <input
            type="date"
            value={dateRange.fecha_desde}
            onChange={(e) => setDateRange(prev => ({ ...prev, fecha_desde: e.target.value }))}
            className="border border-gray-300 rounded-lg px-3 py-2"
          />
          <input
            type="date"
            value={dateRange.fecha_hasta}
            onChange={(e) => setDateRange(prev => ({ ...prev, fecha_hasta: e.target.value }))}
            className="border border-gray-300 rounded-lg px-3 py-2"
          />
        </div>
      </div>

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Gráficos y métricas adicionales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Servicios por tipo */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Servicios por Tipo
          </h3>
          {dashboardData?.servicios_por_tipo?.map((item) => (
            <div key={item.tipo} className="flex justify-between items-center py-2">
              <span className="text-gray-600">{item.tipo_display}</span>
              <span className="font-semibold">{item.count}</span>
            </div>
          ))}
        </div>

        {/* Técnicos más activos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Técnicos Más Activos
          </h3>
          {dashboardData?.tecnicos_activos?.map((tecnico) => (
            <div key={tecnico.id} className="flex justify-between items-center py-2">
              <span className="text-gray-600">{tecnico.nombre}</span>
              <span className="font-semibold">{tecnico.servicios_count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ServicioDashboard;
```

---

## 🛣️ FASE 8: Routing y Páginas Principales

### 8.1 Services Page
```javascript
// src/pages/services/ServicesPage.jsx
import { useState } from 'react';
import { Tab } from '@headlessui/react';
import ServicioList from '../../components/services/Servicio/ServicioList';
import TipoTrabajoPage from './TipoTrabajoPage';
import ServicioDashboard from '../../components/services/Servicio/ServicioDashboard';

const tabs = [
  { name: 'Dashboard', component: ServicioDashboard },
  { name: 'Servicios', component: ServicioList },
  { name: 'Tipos de Trabajo', component: TipoTrabajoPage }
];

const ServicesPage = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
          <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8">
            {tabs.map((tab, index) => (
              <Tab
                key={tab.name}
                className={({ selected }) =>
                  `w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-blue-700
                   ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2
                   ${selected
                     ? 'bg-white shadow'
                     : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                   }`
                }
              >
                {tab.name}
              </Tab>
            ))}
          </Tab.List>
          
          <Tab.Panels>
            {tabs.map((tab, index) => (
              <Tab.Panel key={index}>
                <tab.component />
              </Tab.Panel>
            ))}
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
};

export default ServicesPage;
```

### 8.2 App Router Configuration
```javascript
// src/App.jsx (fragmento de routing)
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ServicesPage from './pages/services/ServicesPage';

function App() {
  return (
    <Router>
      <Routes>
        {/* Otras rutas */}
        <Route path="/services/*" element={<ServicesPage />} />
      </Routes>
    </Router>
  );
}
```

---

## 🧪 FASE 9: Testing y Validación

### 9.1 Test de Componentes
```javascript
// src/components/services/__tests__/ServicioCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ServicioCard from '../Servicio/ServicioCard';

const mockServicio = {
  id: 1,
  tipo_trabajo_nombre: 'Instalación Nueva',
  fecha: '2024-01-15T10:00:00Z',
  tecnico_nombre: 'Juan Pérez',
  cliente_nombre: 'Empresa ABC',
  unidad_placa: 'ABC-123',
  precio: 150.00,
  estado_servicio: 'pendiente',
  descripcion: 'Instalación de GPS en vehículo'
};

const renderWithQueryClient = (component) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('ServicioCard', () => {
  const mockOnView = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnChangeStatus = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders service information correctly', () => {
    renderWithQueryClient(
      <ServicioCard
        servicio={mockServicio}
        onView={mockOnView}
        onEdit={mockOnEdit}
        onChangeStatus={mockOnChangeStatus}
      />
    );

    expect(screen.getByText('Instalación Nueva')).toBeInTheDocument();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('Empresa ABC - ABC-123')).toBeInTheDocument();
    expect(screen.getByText('S/ 150.00')).toBeInTheDocument();
  });

  test('calls onView when view button is clicked', () => {
    renderWithQueryClient(
      <ServicioCard
        servicio={mockServicio}
        onView={mockOnView}
        onEdit={mockOnEdit}
        onChangeStatus={mockOnChangeStatus}
      />
    );

    fireEvent.click(screen.getByText('Ver'));
    expect(mockOnView).toHaveBeenCalledWith(mockServicio);
  });
});
```

---

## 🚀 FASE 10: Optimización y Deploy

### 10.1 Performance Optimizations
```javascript
// src/utils/services/serviceHelpers.js
import { useMemo } from 'react';

// Memoización de filtros complejos
export const useFilteredServicios = (servicios, filters) => {
  return useMemo(() => {
    if (!servicios) return [];
    
    return servicios.filter(servicio => {
      if (filters.estado_servicio && servicio.estado_servicio !== filters.estado_servicio) {
        return false;
      }
      if (filters.tipo_trabajo && servicio.tipo_trabajo !== filters.tipo_trabajo) {
        return false;
      }
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        return (
          servicio.descripcion?.toLowerCase().includes(searchTerm) ||
          servicio.cliente_nombre?.toLowerCase().includes(searchTerm) ||
          servicio.tecnico_nombre?.toLowerCase().includes(searchTerm)
        );
      }
      return true;
    });
  }, [servicios, filters]);
};

// Formateo de datos optimizado
export const formatServiceData = (servicio) => ({
  ...servicio,
  fechaFormatted: new Intl.DateTimeFormat('es-PE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(servicio.fecha)),
  precioFormatted: new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN'
  }).format(servicio.precio)
});
```

### 10.2 Build Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          forms: ['react-hook-form', '@hookform/resolvers', 'yup'],
          ui: ['@headlessui/react', '@heroicons/react']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@tanstack/react-query']
  }
});
```

---

## 📋 Checklist de Implementación

### ✅ Fase 1: Setup Inicial
- [ ] Crear estructura de carpetas
- [ ] Instalar dependencias
- [ ] Configurar constants y helpers

### ✅ Fase 2: API Services
- [ ] Configurar axios y interceptors
- [ ] Implementar tipoTrabajoApi
- [ ] Implementar servicioApi

### ✅ Fase 3: Custom Hooks
- [ ] Crear hooks para TipoTrabajo
- [ ] Crear hooks para Servicio
- [ ] Configurar React Query

### ✅ Fase 4: Componentes Base
- [ ] ServiceStatusBadge
- [ ] ServiceTypeSelect
- [ ] ServicioFilters

### ✅ Fase 5: Lista y Tarjetas
- [ ] ServicioCard
- [ ] ServicioList
- [ ] Paginación

### ✅ Fase 6: Formularios
- [ ] ServicioForm
- [ ] ServicioModal
- [ ] Validaciones

### ✅ Fase 7: Dashboard
- [ ] ServicioDashboard
- [ ] Estadísticas
- [ ] Gráficos

### ✅ Fase 8: Routing
- [ ] ServicesPage
- [ ] Configurar rutas
- [ ] Navegación

### ✅ Fase 9: Testing
- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] E2E tests

### ✅ Fase 10: Deploy
- [ ] Optimizaciones
- [ ] Build configuration
- [ ] Deploy a producción

---

## 🎯 Próximos Pasos Sugeridos

1. **Empezar con Fase 1-2**: Setup y API configuration
2. **Implementar hooks básicos**: useTipoTrabajos y useServicios
3. **Crear componentes simples**: ServiceStatusBadge y ServiceTypeSelect
4. **Desarrollar lista básica**: ServicioList sin filtros avanzados
5. **Agregar formularios**: ServicioForm básico
6. **Expandir funcionalidades**: Filtros, dashboard, etc.

## 🔧 Technical Decisions

- **Pattern used**: Component composition con custom hooks para separar lógica de UI
- **Performance**: React Query para caching, memoización de filtros, code splitting
- **Maintainability**: Estructura modular, TypeScript opcional, testing comprehensivo

## 💡 Suggested Improvements

- Implementar TypeScript para mayor type safety
- Agregar Storybook para documentación de componentes
- Implementar PWA capabilities
- Agregar notificaciones push para cambios de estado
- Implementar drag & drop para cambio de estados
- Agregar exportación de reportes en PDF/Excel