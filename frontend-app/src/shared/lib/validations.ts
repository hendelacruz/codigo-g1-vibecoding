import { z } from 'zod';

/**
 * Validation schemas using Zod for type-safe form validation
 * Includes specific validations for Peruvian documents and phone numbers
 */

/**
 * Validates a Peruvian RUC (Registro Único de Contribuyentes)
 */
const validateRUC = (ruc: string): boolean => {
  // Remove spaces and hyphens
  const cleanRuc = ruc.replace(/[\s-]/g, '')
  
  // Check if it has exactly 11 digits
  if (!/^\d{11}$/.test(cleanRuc)) {
    return false
  }
  
  // Check if it starts with valid prefixes (10, 15, 17, 20)
  const firstTwoDigits = cleanRuc.substring(0, 2)
  if (!['10', '15', '17', '20'].includes(firstTwoDigits)) {
    return false
  }
  
  // Validation algorithm for check digit
  const digits = cleanRuc.split('').map(Number)
  const factors = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  
  let sum = 0
  for (let i = 0; i < 10; i++) {
    const digit = digits[i]
    const factor = factors[i]
    if (digit !== undefined && factor !== undefined) {
      sum += digit * factor
    }
  }
  
  const remainder = sum % 11
  const checkDigit = remainder < 2 ? remainder : 11 - remainder
  
  return checkDigit === digits[10]
}

/**
 * Validates a Peruvian mobile phone number in international format
 */
const validateCelular = (celular: string): boolean => {
  // Remove spaces, hyphens and parentheses
  const cleanCelular = celular.replace(/[\s\-()]/g, '')
  
  // Check for international format (+51 followed by 9 and 8 more digits)
  // or national format (9 followed by 8 digits)
  return /^(\+51)?9\d{8}$/.test(cleanCelular)
}

// Common validation schemas
export const emailSchema = z.string().email('Email inválido');
export const passwordSchema = z.string().min(6, 'Password debe tener al menos 6 caracteres');
export const usernameSchema = z.string().min(3, 'Username debe tener al menos 3 caracteres');

// Peruvian-specific validation schemas
export const rucSchema = z.string()
  .min(11, 'El RUC debe tener 11 dígitos')
  .max(11, 'El RUC debe tener 11 dígitos')
  .refine(validateRUC, {
    message: 'El RUC ingresado no es válido. Debe tener 11 dígitos y comenzar con 10, 15, 17 o 20'
  });

export const celularSchema = z.string()
  .min(9, 'El celular debe tener al menos 9 dígitos')
  .max(13, 'El celular no puede exceder 13 caracteres')
  .refine(validateCelular, {
    message: 'El celular debe ser un número peruano válido (formato: +51987654321 o 987654321)'
  });

export const dniSchema = z.string()
  .min(8, 'El DNI debe tener 8 dígitos')
  .max(8, 'El DNI debe tener 8 dígitos')
  .regex(/^\d{8}$/, 'El DNI debe contener solo números');

// Login validation schema
export const loginSchema = z.object({
  username: usernameSchema,
  password: passwordSchema,
});

// User validation schema
export const userSchema = z.object({
  id: z.number(),
  username: usernameSchema,
  email: emailSchema,
  first_name: z.string().min(1, 'Nombre es requerido'),
  last_name: z.string().min(1, 'Apellido es requerido'),
  dni: z.string().min(8, 'DNI debe tener al menos 8 caracteres'),
});

// Proveedor validation schema
export const proveedorSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  ruc: rucSchema,
  direccion: z.string().min(1, 'La dirección es requerida'),
  telefono: z.string().optional(),
  celular: celularSchema,
  correo: emailSchema.optional(),
  contacto: z.string().optional(),
});

// Cliente validation schema
export const clienteSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  ruc: rucSchema.optional(),
  dni: dniSchema.optional(),
  direccion: z.string().min(1, 'La dirección es requerida'),
  telefono: z.string().optional(),
  celular: celularSchema,
  email: emailSchema.optional(),
});

// Update schemas (partial versions for editing)
export const updateProveedorSchema = proveedorSchema.partial();
export const updateClienteSchema = clienteSchema.partial();

// Type exports
export type LoginFormData = z.infer<typeof loginSchema>;
export type UserFormData = z.infer<typeof userSchema>;
export type ProveedorFormData = z.infer<typeof proveedorSchema>;
export type UpdateProveedorFormData = z.infer<typeof updateProveedorSchema>;
export type ClienteFormData = z.infer<typeof clienteSchema>;
export type UpdateClienteFormData = z.infer<typeof updateClienteSchema>;