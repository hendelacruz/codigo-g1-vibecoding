import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { useCreateServicio, useUpdateServicio } from '../../hooks/useServicio';
import ServiceTypeSelect from '../shared/ServiceTypeSelect';
import ClientSelect from '../shared/ClientSelect';
import UnidadSelect from '../shared/UnidadSelect';
import DispositivoGpsSelect from '../shared/DispositivoGpsSelect';
import SimCardSelect from '../shared/SimCardSelect';
import ServiceStatusSelect from '../shared/ServiceStatusSelect';
import TechnicianSelect from '../../../../components/ui/TechnicianSelect';
import { useTechnicians } from '../../../../hooks/useTechnicians';
import { cn } from '../../../../shared/lib/utils';
import type { 
  Servicio, 
  ServicioCreateData, 
  ServicioUpdateData 
} from '../../../../shared/types/services/servicio';

// Zod validation schema
const servicioSchema = z.object({
  fecha: z.string().min(1, 'La fecha es requerida'),
  tipo_trabajo: z.number().refine(val => val > 0, 'El tipo de trabajo es requerido'),
  tecnico_id: z.number().refine(val => val > 0, 'El técnico es requerido'),
  cliente: z.number().refine(val => val > 0, 'El cliente es requerido'),
  unidad: z.number().refine(val => val > 0, 'La unidad es requerida'),
  gps: z.number().optional(),
  sim_card: z.number().optional(),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  precio: z.number().min(0, 'El precio debe ser mayor o igual a 0'),
  estado_servicio: z.enum(['pendiente', 'programado', 'en_proceso', 'completado', 'cancelado', 'reprogramado']),
  observaciones: z.string().optional(),
});

type FormData = z.infer<typeof servicioSchema>;

interface ServicioFormProps {
  servicio?: Servicio | null;
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}

const ServicioForm: React.FC<ServicioFormProps> = ({ 
  servicio, 
  onSuccess, 
  onCancel,
  className 
}) => {
  const isEditing = !!servicio;
  const createMutation = useCreateServicio();
  const updateMutation = useUpdateServicio();
  const { technicians } = useTechnicians();

  // Create default values that match the schema exactly
  const getDefaultValues = (): FormData => {
    const today = new Date().toISOString().split('T')[0];
    const fechaValue = (servicio?.fecha && typeof servicio.fecha === 'string') 
      ? new Date(servicio.fecha).toISOString().split('T')[0] 
      : today;
    
    return {
      fecha: fechaValue as string,
      tipo_trabajo: servicio?.tipo_trabajo || 0, // Cambiar a 0 para forzar selección
      tecnico_id: servicio?.tecnico_id || 0, // Cambiar a 0 para forzar selección
      cliente: servicio?.cliente || 0, // Cambiar a 0 para forzar selección
      unidad: servicio?.unidad || 0, // Cambiar a 0 para forzar selección
      gps: servicio?.gps,
      sim_card: servicio?.sim_card,
      descripcion: servicio?.descripcion || '',
      precio: servicio?.precio || 0,
      estado_servicio: servicio?.estado_servicio || 'pendiente',
      observaciones: servicio?.observaciones || '',
    };
  };

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    register,
    watch,
    setValue
  } = useForm<FormData>({
    resolver: zodResolver(servicioSchema),
    defaultValues: getDefaultValues(),
  });



  const onSubmit = async (data: FormData) => {
    try {
      // Encontrar el técnico seleccionado para obtener su DNI
      const selectedTechnician = technicians?.find(tech => tech.id === data.tecnico_id);
      if (!selectedTechnician || !selectedTechnician.dni) {
        toast.error('Técnico seleccionado no encontrado o sin DNI');
        return;
      }

      // Crear el payload con tecnico_dni en lugar de tecnico_id
      const { tecnico_id, ...restData } = data;
      const payload: ServicioCreateData = {
        fecha: restData.fecha,
        tipo_trabajo: restData.tipo_trabajo,
        tecnico_dni: selectedTechnician.dni,
        cliente: restData.cliente,
        unidad: restData.unidad,
        descripcion: restData.descripcion,
        precio: restData.precio,
        estado_servicio: restData.estado_servicio,
        ...(restData.gps && { gps: restData.gps }),
        ...(restData.sim_card && { sim_card: restData.sim_card }),
        ...(restData.observaciones && { observaciones: restData.observaciones })
      };

      if (isEditing && servicio) {
        await updateMutation.mutateAsync({ 
          id: servicio.id, 
          data: payload as ServicioUpdateData 
        });
        toast.success('Servicio actualizado exitosamente');
      } else {
        await createMutation.mutateAsync(payload);
        toast.success('Servicio creado exitosamente');
      }
      reset();
      onSuccess?.();
    } catch (error) {
      console.error('Error en formulario de servicio:', error);
      toast.error(isEditing ? 'Error al actualizar servicio' : 'Error al crear servicio');
    }
  };

  const handleCancel = () => {
    reset();
    onCancel?.();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={cn('space-y-6', className)}>
      {/* Fecha */}
      <div className="space-y-2">
        <label htmlFor="fecha" className="text-sm font-medium text-gray-700">
          Fecha del Servicio *
        </label>
        <input
          {...register('fecha')}
          type="date"
          id="fecha"
          className={cn(
            'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            errors.fecha ? 'border-red-500' : 'border-gray-300'
          )}
        />
        {errors.fecha && (
          <p className="text-sm text-red-600">{errors.fecha.message}</p>
        )}
      </div>

      {/* Tipo de Trabajo */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Tipo de Trabajo *
        </label>
        <Controller
          name="tipo_trabajo"
          control={control}
          render={({ field }) => (
            <ServiceTypeSelect
              value={field.value?.toString() || ''}
              onValueChange={(value) => field.onChange(parseInt(value, 10))}
              placeholder="Seleccionar tipo de trabajo"
              variant={errors.tipo_trabajo ? 'error' : 'default'}
              data-testid="tipo-trabajo-select"
            />
          )}
        />
        {errors.tipo_trabajo && (
          <p className="text-sm text-red-600">{errors.tipo_trabajo.message}</p>
        )}
      </div>

      {/* Técnico */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Técnico *
        </label>
        <Controller
          name="tecnico_id"
          control={control}
          render={({ field }) => (
            <TechnicianSelect
              value={field.value}
              onChange={(value) => field.onChange(value)}
              {...(errors.tecnico_id?.message && { error: errors.tecnico_id.message })}
              placeholder="Seleccionar técnico"
              name="tecnico_id"
            />
          )}
        />
        {errors.tecnico_id && (
          <p className="text-sm text-red-600">{errors.tecnico_id.message}</p>
        )}
      </div>

      {/* Cliente y Unidad en una fila */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Cliente */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Cliente *
          </label>
          <Controller
            name="cliente"
            control={control}
            render={({ field }) => (
              <ClientSelect
                value={field.value?.toString() || ''}
                onValueChange={(value) => field.onChange(parseInt(value, 10))}
                enablePlateSearch={true}
                placeholder="Seleccionar cliente"
                variant={errors.cliente ? 'error' : 'default'}
                data-testid="cliente-select"
              />
            )}
          />
          {errors.cliente && (
            <p className="text-sm text-red-600">{errors.cliente.message}</p>
          )}
        </div>

        {/* Unidad */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Unidad Vehicular *
          </label>
          <Controller
            name="unidad"
            control={control}
            render={({ field }) => (
              <UnidadSelect
                value={field.value?.toString() || ''}
                onValueChange={(value) => field.onChange(parseInt(value, 10))}
                placeholder="Seleccionar unidad vehicular"
                variant={errors.unidad ? 'error' : 'default'}
                data-testid="unidad-select"
              />
            )}
          />
          {errors.unidad && (
            <p className="text-sm text-red-600">{errors.unidad.message}</p>
          )}
        </div>
      </div>

      {/* GPS y SIM Card en una fila */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* GPS */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Dispositivo GPS (Opcional)
          </label>
          <Controller
            name="gps"
            control={control}
            render={({ field }) => (
              <DispositivoGpsSelect
                value={field.value?.toString() || ''}
                onValueChange={(value) => field.onChange(value ? parseInt(value, 10) : undefined)}
                placeholder="Seleccionar GPS"
                includeAssigned={false}
                data-testid="gps-select"
              />
            )}
          />
        </div>

        {/* SIM Card */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Tarjeta SIM (Opcional)
          </label>
          <Controller
            name="sim_card"
            control={control}
            render={({ field }) => (
              <SimCardSelect
                value={field.value?.toString() || ''}
                onValueChange={(value) => field.onChange(value ? parseInt(value, 10) : undefined)}
                placeholder="Seleccionar SIM Card"
                includeAssigned={false}
                data-testid="sim-card-select"
              />
            )}
          />
        </div>
      </div>

      {/* Descripción */}
      <div className="space-y-2">
        <label htmlFor="descripcion" className="text-sm font-medium text-gray-700">
          Descripción del Servicio *
        </label>
        <textarea
          {...register('descripcion')}
          id="descripcion"
          rows={3}
          placeholder="Describe el servicio a realizar..."
          className={cn(
            'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical',
            errors.descripcion ? 'border-red-500' : 'border-gray-300'
          )}
        />
        {errors.descripcion && (
          <p className="text-sm text-red-600">{errors.descripcion.message}</p>
        )}
      </div>

      {/* Precio y Estado en una fila */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Precio */}
        <div className="space-y-2">
          <label htmlFor="precio" className="text-sm font-medium text-gray-700">
            Precio (S/.) *
          </label>
          <input
            {...register('precio', { valueAsNumber: true })}
            type="number"
            id="precio"
            min="0"
            step="0.01"
            placeholder="0.00"
            className={cn(
              'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              errors.precio ? 'border-red-500' : 'border-gray-300'
            )}
          />
          {errors.precio && (
            <p className="text-sm text-red-600">{errors.precio.message}</p>
          )}
        </div>

        {/* Estado del Servicio */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Estado del Servicio *
          </label>
          <Controller
            name="estado_servicio"
            control={control}
            render={({ field }) => (
              <ServiceStatusSelect
                value={field.value}
                onValueChange={(value) => field.onChange(value)}
                placeholder="Seleccionar estado"
                variant={errors.estado_servicio ? 'error' : 'default'}
                data-testid="service-status-select"
              />
            )}
          />
          {errors.estado_servicio && (
            <p className="text-sm text-red-600">{errors.estado_servicio.message}</p>
          )}
        </div>
      </div>

      {/* Observaciones */}
      <div className="space-y-2">
        <label htmlFor="observaciones" className="text-sm font-medium text-gray-700">
          Observaciones (Opcional)
        </label>
        <textarea
          {...register('observaciones')}
          id="observaciones"
          rows={2}
          placeholder="Observaciones adicionales..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
        />
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={handleCancel}
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting 
            ? (isEditing ? 'Actualizando...' : 'Creando...') 
            : (isEditing ? 'Actualizar Servicio' : 'Crear Servicio')
          }
        </button>
      </div>
    </form>
  );
};

export default ServicioForm;