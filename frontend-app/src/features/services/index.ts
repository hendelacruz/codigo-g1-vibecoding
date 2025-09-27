// Services Module - Main exports
// This file serves as the main entry point for the services feature module

// API exports
export * from './api/servicesApi';
export * from './api/servicioApi';
export * from './api/tipoTrabajoApi';

// Hooks exports
export * from './hooks/useServicio';
export * from './hooks/useTipoTrabajo';
export * from './hooks/useServiceFilters';

// Utils exports
export * from './utils/serviceHelpers';

// Components exports
export { default as ServicioCard } from './components/Servicio/ServicioCard';
export { default as TipoTrabajoCard } from './components/TipoTrabajo/TipoTrabajoCard';
export { default as ServiceStatusBadge } from './components/shared/ServiceStatusBadge';
export { default as ServiceTypeSelect } from './components/shared/ServiceTypeSelect';
export { default as ServiceDatePicker } from './components/shared/ServiceDatePicker';

// Pages exports
export { default as ServicesPage } from './pages/ServicesPage';