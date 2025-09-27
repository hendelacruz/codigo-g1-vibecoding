import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(date))
}

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
  }).format(amount)
}

/**
 * Safely formats a price value to a fixed decimal string
 * Handles string, number, null, and undefined values
 */
export const formatPrice = (price: unknown, decimals: number = 2): string => {
  // Handle null, undefined, or empty string
  if (price === null || price === undefined || price === '') {
    return '0.00'
  }
  
  // Convert to number if it's a string
  const numericPrice = typeof price === 'string' ? parseFloat(price) : Number(price)
  
  // Check if conversion resulted in a valid number
  if (isNaN(numericPrice)) {
    return '0.00'
  }
  
  return numericPrice.toFixed(decimals)
}