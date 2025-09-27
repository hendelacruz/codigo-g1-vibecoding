// API types placeholder
// This file will contain API-related TypeScript types

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: unknown;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface ApiEndpoints {
  auth: {
    login: string;
    logout: string;
    refresh: string;
    profile: string;
  };
  inventory: {
    gps: string;
    simcards: string;
    others: string;
  };
  sales: {
    entities: string;
    sales: string;
  };
}