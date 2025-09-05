/**
 * Date utility functions
 * Provides consistent date formatting across the application
 */

/**
 * Formats a date to Spanish locale with day, month, and year
 *
 * @param date - The date to format
 * @returns Formatted date string (e.g., "15 dic 2023")
 */
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
};

/**
 * Formats a date to ISO string format
 *
 * @param date - The date to format
 * @returns ISO date string
 */
export const formatDateISO = (date: Date): string => {
  return date.toISOString();
};

/**
 * Formats a date to relative time (e.g., "hace 2 días")
 *
 * @param date - The date to format
 * @returns Relative time string
 */
export const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return "Hoy";
  if (diffInDays === 1) return "Ayer";
  if (diffInDays < 7) return `Hace ${diffInDays} días`;
  if (diffInDays < 30) return `Hace ${Math.floor(diffInDays / 7)} semanas`;
  if (diffInDays < 365) return `Hace ${Math.floor(diffInDays / 30)} meses`;

  return `Hace ${Math.floor(diffInDays / 365)} años`;
};

/**
 * Checks if a date is today
 *
 * @param date - The date to check
 * @returns True if the date is today
 */
export const isToday = (date: Date): boolean => {
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
};

/**
 * Checks if a date is within the last week
 *
 * @param date - The date to check
 * @returns True if the date is within the last week
 */
export const isWithinLastWeek = (date: Date): boolean => {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  return date >= weekAgo && date <= now;
};
