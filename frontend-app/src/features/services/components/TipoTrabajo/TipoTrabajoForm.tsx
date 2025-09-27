import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { useCreateTipoTrabajo, useUpdateTipoTrabajo } from '../../hooks/useTipoTrabajo';
import { cn } from '../../../../shared/lib/utils';
import type { 
  TipoTrabajo, 
  TipoTrabajoCreateData, 
  TipoTrabajoUpdateData 
} from '../../../../shared/types/services/tipoTrabajo';

// Zod validation schema
const schema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  precio_base: z.number().positive('El precio base debe ser positivo'),
  duracion_estimada: z.number().positive('La duración estimada debe ser positiva'),
  requiere_gps: z.boolean(),
  requiere_sim: z.boolean(),
});

type FormData = z.infer<typeof schema>;

interface TipoTrabajoFormProps {
  tipoTrabajo?: TipoTrabajo | null;
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}

export const TipoTrabajoForm: React.FC<TipoTrabajoFormProps> = ({
  tipoTrabajo,
  onSuccess,
  onCancel,
  className
}) => {
  const isEditing = !!tipoTrabajo;
  
  const createMutation = useCreateTipoTrabajo();
  const updateMutation = useUpdateTipoTrabajo();

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      nombre: tipoTrabajo?.nombre || '',
      descripcion: tipoTrabajo?.descripcion || '',
      precio_base: tipoTrabajo?.precio_base || 0,
      duracion_estimada: tipoTrabajo?.duracion_estimada || 0,
      requiere_gps: tipoTrabajo?.requiere_gps || false,
      requiere_sim: tipoTrabajo?.requiere_sim || false,
    }
  });

  const onSubmit = async (data: FormData) => {
    try {
      if (isEditing && tipoTrabajo) {
        const updateData: TipoTrabajoUpdateData = data;
        await updateMutation.mutateAsync({ id: tipoTrabajo.id, data: updateData });
        toast.success('Tipo de trabajo actualizado exitosamente');
      } else {
        const createData: TipoTrabajoCreateData = data;
        await createMutation.mutateAsync(createData);
        toast.success('Tipo de trabajo creado exitosamente');
        reset();
      }
      onSuccess?.();
    } catch (error) {
      console.error('Error al guardar tipo de trabajo:', error);
      toast.error(isEditing ? 'Error al actualizar tipo de trabajo' : 'Error al crear tipo de trabajo');
    }
  };

  return (
    <form 
      onSubmit={handleSubmit(onSubmit)} 
      className={cn("space-y-6", className)}
    >
      {/* Nombre */}
      <div className="space-y-2">
        <label htmlFor="nombre" className="text-sm font-medium text-gray-700">
          Nombre *
        </label>
        <input
          {...register('nombre')}
          type="text"
          id="nombre"
          className={cn(
            "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            errors.nombre && "border-red-500 focus:ring-red-500 focus:border-red-500"
          )}
          placeholder="Ej: mantenimiento_preventivo"
        />
        {errors.nombre && (
          <p className="text-sm text-red-600">{errors.nombre.message}</p>
        )}
      </div>

      {/* Descripción */}
      <div className="space-y-2">
        <label htmlFor="descripcion" className="text-sm font-medium text-gray-700">
          Descripción *
        </label>
        <textarea
          {...register('descripcion')}
          id="descripcion"
          rows={3}
          className={cn(
            "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            errors.descripcion && "border-red-500 focus:ring-red-500 focus:border-red-500"
          )}
          placeholder="Descripción del tipo de trabajo"
        />
        {errors.descripcion && (
          <p className="text-sm text-red-600">{errors.descripcion.message}</p>
        )}
      </div>

      {/* Precio Base */}
      <div className="space-y-2">
        <label htmlFor="precio_base" className="text-sm font-medium text-gray-700">
          Precio Base *
        </label>
        <input
          {...register('precio_base', { valueAsNumber: true })}
          type="number"
          id="precio_base"
          min="0"
          step="0.01"
          className={cn(
            "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            errors.precio_base && "border-red-500 focus:ring-red-500 focus:border-red-500"
          )}
          placeholder="0.00"
        />
        {errors.precio_base && (
          <p className="text-sm text-red-600">{errors.precio_base.message}</p>
        )}
      </div>

      {/* Duración Estimada */}
      <div className="space-y-2">
        <label htmlFor="duracion_estimada" className="text-sm font-medium text-gray-700">
          Duración Estimada (minutos) *
        </label>
        <input
          {...register('duracion_estimada', { valueAsNumber: true })}
          type="number"
          id="duracion_estimada"
          min="1"
          className={cn(
            "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            errors.duracion_estimada && "border-red-500 focus:ring-red-500 focus:border-red-500"
          )}
          placeholder="60"
        />
        {errors.duracion_estimada && (
          <p className="text-sm text-red-600">{errors.duracion_estimada.message}</p>
        )}
      </div>

      {/* Checkboxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Requiere GPS */}
        <div className="flex items-center space-x-2">
          <Controller
            name="requiere_gps"
            control={control}
            render={({ field }) => (
              <input
                type="checkbox"
                id="requiere_gps"
                checked={field.value}
                onChange={field.onChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            )}
          />
          <label htmlFor="requiere_gps" className="text-sm font-medium text-gray-700">
            Requiere GPS
          </label>
        </div>

        {/* Requiere SIM */}
        <div className="flex items-center space-x-2">
          <Controller
            name="requiere_sim"
            control={control}
            render={({ field }) => (
              <input
                type="checkbox"
                id="requiere_sim"
                checked={field.value}
                onChange={field.onChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            )}
          />
          <label htmlFor="requiere_sim" className="text-sm font-medium text-gray-700">
            Requiere SIM Card
          </label>
        </div>
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className={cn(
            "px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
            isSubmitting && "opacity-50 cursor-not-allowed"
          )}
        >
          {isSubmitting 
            ? (isEditing ? 'Actualizando...' : 'Creando...') 
            : (isEditing ? 'Actualizar' : 'Crear')
          }
        </button>
      </div>
    </form>
  );
};

export default TipoTrabajoForm;