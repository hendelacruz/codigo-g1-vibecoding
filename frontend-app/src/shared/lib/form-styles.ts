import { cva, type VariantProps } from 'class-variance-authority';

/**
 * Estilos unificados para campos de formulario
 * Basado en el patrón CVA para consistencia visual
 */
export const formFieldVariants = cva(
  // Base styles - aplicados a todos los campos
  "w-full rounded-md border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors placeholder:text-gray-400",
  {
    variants: {
      // Variantes de estado visual
      variant: {
        default: "border-gray-300 hover:border-gray-400 focus:ring-blue-500 focus:border-blue-500",
        error: "border-red-500 focus:ring-red-500 focus:border-red-500 bg-red-50",
        success: "border-green-500 focus:ring-green-500 focus:border-green-500",
        warning: "border-yellow-500 focus:ring-yellow-500 focus:border-yellow-500 bg-yellow-50",
      },
      // Variantes de tamaño
      size: {
        sm: "h-8 px-2 py-1 text-xs",
        md: "h-10 px-3 py-2 text-sm", // Tamaño estándar
        lg: "h-12 px-4 py-3 text-base",
      },
      // Variantes para diferentes tipos de campo
      fieldType: {
        input: "",
        select: "cursor-pointer",
        textarea: "min-h-[80px] py-2 resize-vertical",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "md",
      fieldType: "input",
    },
  }
);

/**
 * Estilos para labels de formulario
 */
export const formLabelVariants = cva(
  "block text-sm font-medium leading-6",
  {
    variants: {
      variant: {
        default: "text-gray-900",
        error: "text-red-600",
        success: "text-green-600",
        warning: "text-yellow-600",
      },
      required: {
        true: "after:content-['*'] after:ml-0.5 after:text-red-500",
        false: "",
      }
    },
    defaultVariants: {
      variant: "default",
      required: false,
    },
  }
);

/**
 * Estilos para mensajes de error
 */
export const formErrorVariants = cva(
  "mt-1 text-sm",
  {
    variants: {
      variant: {
        error: "text-red-600",
        warning: "text-yellow-600",
        info: "text-blue-600",
      }
    },
    defaultVariants: {
      variant: "error",
    },
  }
);

/**
 * Estilos para contenedores de campos
 */
export const formFieldContainerVariants = cva(
  "space-y-1",
  {
    variants: {
      spacing: {
        tight: "space-y-1",
        normal: "space-y-2",
        loose: "space-y-3",
      }
    },
    defaultVariants: {
      spacing: "normal",
    },
  }
);

// Tipos para TypeScript
export type FormFieldVariants = VariantProps<typeof formFieldVariants>;
export type FormLabelVariants = VariantProps<typeof formLabelVariants>;
export type FormErrorVariants = VariantProps<typeof formErrorVariants>;
export type FormFieldContainerVariants = VariantProps<typeof formFieldContainerVariants>;