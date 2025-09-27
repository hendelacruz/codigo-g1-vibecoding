// src/features/services/api/servicesApi.ts
import { api } from '../../../shared/lib/api';
import type { AxiosInstance } from 'axios';

// Create a services-specific API instance that extends the centralized configuration
const servicesApi: AxiosInstance = api;

// Services-specific endpoints configuration
export const SERVICES_ENDPOINTS = {
  TIPOS_TRABAJO: '/api/services/tipos-trabajo',
  SERVICIOS: '/api/services/servicios',
  ESTADISTICAS: '/api/services/estadisticas',
} as const;

export default servicesApi;