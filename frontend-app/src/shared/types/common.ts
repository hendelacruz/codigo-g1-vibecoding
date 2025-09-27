// Common types placeholder
// This file will contain common TypeScript types used across the application

export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface User extends BaseEntity {
  // Campos heredados de Django AbstractUser
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password?: string; // Solo para creación/actualización, no se devuelve en consultas
  is_staff: boolean;
  is_active: boolean;
  is_superuser: boolean;
  date_joined: string; // ISO string format
  last_login?: string | null; // ISO string format, puede ser null
  
  // Campos personalizados
  dni?: string; // 8 dígitos
  celular?: string; // Número de celular peruano
  licencia?: string; // Formato: A12345678 (1 letra + 8 dígitos)
  rol_nombre?: string;
  
  // Campos para sistema de permisos basado en Django
  groups?: string[]; // Grupos/roles del usuario
  user_permissions?: string[]; // Permisos específicos del usuario
}

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], item: T) => React.ReactNode;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea';
  required?: boolean;
  options?: SelectOption[];
  validation?: Record<string, unknown>;
}