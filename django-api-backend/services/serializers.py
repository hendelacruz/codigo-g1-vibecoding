"""
Serializers para la aplicación de servicios.
Maneja la serialización de TipoTrabajo y Servicio con validaciones específicas.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timezone

from .models import TipoTrabajo, Servicio
from authentication.models import CustomUser
from entities.models import Cliente, Unidad
from inventory.models import GPS, SIMCard
from todoapi.utils.security_mixins import (
    SecurityValidationMixin, 
    AuditLogMixin,
    DataSanitizationMixin
)


class TipoTrabajoSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer para TipoTrabajo con validaciones de negocio y seguridad.
    """
    nombre_display = serializers.CharField(source='get_nombre_display', read_only=True)
    servicios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TipoTrabajo
        fields = [
            'id', 'nombre', 'nombre_display', 'descripcion', 
            'is_active', 'servicios_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_servicios_count(self, obj):
        """Return the count of active services for this work type."""
        return obj.servicios.filter(is_active=True).count()
    
    def validate_descripcion(self, value):
        """Validate that description is meaningful."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 10 caracteres."
            )
        return value.strip()


class ServicioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de servicios.
    Optimizado para performance en listados.
    """
    tipo_trabajo_nombre = serializers.CharField(source='tipo_trabajo.get_nombre_display', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico.get_full_name', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    unidad_placa = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_servicio_display', read_only=True)
    
    class Meta:
        model = Servicio
        fields = [
            'id', 'fecha', 'tipo_trabajo_nombre', 'tecnico_nombre',
            'cliente_nombre', 'unidad_placa', 'precio', 'estado_servicio',
            'estado_display', 'created_at'
        ]
    
    def get_unidad_placa(self, obj):
        """Return unidad placa or None if no unidad is assigned."""
        return obj.unidad.placa if obj.unidad else None


class ServicioSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer completo para Servicio con validaciones de negocio y seguridad.
    """
    # Read-only fields for display
    tipo_trabajo_nombre = serializers.CharField(source='tipo_trabajo.get_nombre_display', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico.get_full_name', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    unidad_info = serializers.SerializerMethodField()
    gps_info = serializers.SerializerMethodField()
    sim_card_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_servicio_display', read_only=True)
    
    # Write fields
    tecnico_dni = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Servicio
        fields = [
            'id', 'fecha', 'tipo_trabajo', 'tipo_trabajo_nombre',
            'tecnico', 'tecnico_nombre', 'tecnico_dni',
            'cliente', 'cliente_nombre', 'unidad', 'unidad_info',
            'gps', 'gps_info', 'sim_card', 'sim_card_info',
            'descripcion', 'precio', 'estado_servicio', 'estado_display',
            'observaciones', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_unidad_info(self, obj):
        """Return detailed unit information or None if no unidad is assigned."""
        if obj.unidad:
            return {
                'id': obj.unidad.id,
                'placa': obj.unidad.placa,
                'marca': obj.unidad.marca,
                'modelo': obj.unidad.modelo,
                'tipo': obj.unidad.get_tipo_display()
            }
        return None
    
    def get_gps_info(self, obj):
        """Return GPS device information if assigned."""
        if obj.gps:
            return {
                'id': obj.gps.id,
                'imei': obj.gps.imei,
                'marca': obj.gps.marca,
                'modelo': obj.gps.modelo,
                'estado': obj.gps.get_estado_display()
            }
        return None
    
    def get_sim_card_info(self, obj):
        """Return SIM card information if assigned."""
        if obj.sim_card:
            return {
                'id': obj.sim_card.id,
                'numero_chip': obj.sim_card.numero_chip,
                'icc': obj.sim_card.icc,
                'estado': obj.sim_card.estado,
                'proceso': obj.sim_card.proceso,
                'plan': obj.sim_card.plan
            }
        return None
    
    def validate_fecha(self, value):
        """Validate service date."""
        if value > datetime.now(timezone.utc):
            # Allow future dates for scheduling
            pass
        return value
    
    def validate_precio(self, value):
        """Validate service price."""
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "El precio debe ser mayor a 0."
            )
        if value > Decimal('50000.00'):
            raise serializers.ValidationError(
                "El precio no puede exceder S/ 50,000.00"
            )
        return value
    
    def validate_descripcion(self, value):
        """Validate service description."""
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 20 caracteres."
            )
        return value.strip()
    
    def validate(self, attrs):
        """Cross-field validations."""
        # Validate that unidad belongs to cliente
        if 'unidad' in attrs and 'cliente' in attrs:
            if attrs['unidad'].cliente != attrs['cliente']:
                raise serializers.ValidationError({
                    'unidad': 'La unidad debe pertenecer al cliente seleccionado.'
                })
        
        # Validate tecnico assignment by DNI if provided
        if 'tecnico_dni' in attrs:
            try:
                tecnico = CustomUser.objects.get(
                    dni=attrs['tecnico_dni'],
                    is_active=True,
                    rol__nombre='tecnico'
                )
                attrs['tecnico'] = tecnico
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({
                    'tecnico_dni': 'No se encontró un técnico activo con ese DNI.'
                })
        
        # Validate that GPS and SIM are available if assigned
        if 'gps' in attrs and attrs['gps']:
            if attrs['gps'].estado != 'disponible':
                raise serializers.ValidationError({
                    'gps': 'El dispositivo GPS debe estar disponible para asignación.'
                })
        
        if 'sim_card' in attrs and attrs['sim_card']:
            if attrs['sim_card'].estado != 'disponible':
                raise serializers.ValidationError({
                    'sim_card': 'La tarjeta SIM debe estar disponible para asignación.'
                })
        
        # Validate tipo_trabajo is active
        if 'tipo_trabajo' in attrs:
            if not attrs['tipo_trabajo'].is_active:
                raise serializers.ValidationError({
                    'tipo_trabajo': 'El tipo de trabajo debe estar activo.'
                })
        
        return attrs


class ServicioFlexibleSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer flexible para servicios que permite campos opcionales según el tipo de trabajo.
    
    Tipos de servicio soportados:
    - mantenimiento_sin_equipos: No requiere GPS ni SIM Card
    - instalacion_accesorio: No requiere GPS ni SIM Card
    - revision_tecnica: Solo requiere descripción detallada
    - configuracion_software: Puede requerir GPS pero no SIM Card
    - instalacion_nueva: Requiere todos los campos
    - mantenimiento_preventivo/correctivo: Campos opcionales según necesidad
    """
    
    # Read-only fields for display
    tipo_trabajo_nombre = serializers.CharField(source='tipo_trabajo.get_nombre_display', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico.get_full_name', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    unidad_info = serializers.SerializerMethodField()
    gps_info = serializers.SerializerMethodField()
    sim_card_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_servicio_display', read_only=True)
    
    # Write-only fields for flexible service creation
    tecnico_dni = serializers.CharField(write_only=True, required=False)
    requiere_gps = serializers.BooleanField(write_only=True, required=False, default=False)
    requiere_sim_card = serializers.BooleanField(write_only=True, required=False, default=False)
    motivo_sin_equipos = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Override tecnico field to make it optional (will be set via tecnico_dni)
    tecnico = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Servicio
        fields = [
            'id', 'fecha', 'tipo_trabajo', 'tipo_trabajo_nombre',
            'tecnico', 'tecnico_nombre', 'tecnico_dni',
            'cliente', 'cliente_nombre', 'unidad', 'unidad_info',
            'gps', 'gps_info', 'sim_card', 'sim_card_info',
            'descripcion', 'precio', 'estado_servicio', 'estado_display',
            'observaciones', 'is_active', 'created_at', 'updated_at',
            'requiere_gps', 'requiere_sim_card', 'motivo_sin_equipos'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_unidad_info(self, obj):
        """Return detailed unit information or None if no unidad is assigned."""
        if obj.unidad:
            return {
                'id': obj.unidad.id,
                'placa': obj.unidad.placa,
                'marca': obj.unidad.marca,
                'modelo': obj.unidad.modelo,
                'tipo': obj.unidad.get_tipo_display()
            }
        return None
    
    def get_gps_info(self, obj):
        """Return GPS device information if available."""
        if obj.gps:
            return {
                'id': obj.gps.id,
                'imei': obj.gps.imei,
                'marca': obj.gps.marca,
                'modelo': obj.gps.modelo,
                'estado': obj.gps.estado
            }
        return None
    
    def get_sim_card_info(self, obj):
        """Get SIM card information."""
        if obj.sim_card:
            return {
                'id': obj.sim_card.id,
                'numero_chip': obj.sim_card.numero_chip,
                'icc': obj.sim_card.icc,
                'estado': obj.sim_card.estado,
                'proceso': obj.sim_card.proceso
            }
        return None
    
    def validate_fecha(self, value):
        """Validate service date."""
        if value > datetime.now(timezone.utc):
            # Allow future dates for scheduled services
            pass
        return value
    
    def validate_precio(self, value):
        """Validate service price."""
        if value is not None and value < Decimal('0.00'):
            raise serializers.ValidationError(
                "El precio no puede ser negativo."
            )
        return value
    
    def validate_descripcion(self, value):
        """Validate service description with flexible requirements."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 10 caracteres."
            )
        return value.strip()
    
    def validate_tecnico_dni(self, value):
        """Validate technician DNI if provided."""
        if value:
            try:
                tecnico = CustomUser.objects.get(dni=value, is_active=True)
                if not tecnico.groups.filter(name='Tecnicos').exists():
                    raise serializers.ValidationError(
                        "El usuario especificado no es un técnico válido."
                    )
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    "No se encontró un técnico activo con el DNI especificado."
                )
        return value
    
    def validate(self, attrs):
        """
        Perform comprehensive validation based on service type.
        Enfoque simplificado usando 'otro' + observaciones para casos especiales.
        """
        tipo_trabajo = attrs.get('tipo_trabajo')
        gps = attrs.get('gps')
        sim_card = attrs.get('sim_card')
        requiere_gps = attrs.get('requiere_gps', False)
        requiere_sim_card = attrs.get('requiere_sim_card', False)
        motivo_sin_equipos = attrs.get('motivo_sin_equipos', '')
        observaciones = attrs.get('observaciones', '')
        
        if not tipo_trabajo:
            raise serializers.ValidationError(
                "El tipo de trabajo es requerido."
            )
        
        # Define service types that typically don't require equipment
        tipos_sin_equipos = [
            'mantenimiento_sin_equipos',
            'instalacion_accesorio',
            'revision_tecnica',
            'configuracion_software'
        ]
        
        # Define service types that typically require equipment
        tipos_con_equipos = [
            'instalacion_nueva'
        ]
        
        # Validate equipment requirements based on service type
        if tipo_trabajo.nombre in tipos_sin_equipos:
            # For these types, equipment is optional but must be justified if missing
            if not gps and not sim_card and not motivo_sin_equipos:
                attrs['motivo_sin_equipos'] = f"Servicio de {tipo_trabajo.get_nombre_display()} - no requiere equipos nuevos"
            
            # If equipment is provided, validate it's appropriate
            if gps and tipo_trabajo.nombre == 'instalacion_accesorio':
                # Allow GPS for accessory installation if it's being configured
                pass
            elif sim_card and tipo_trabajo.nombre in ['revision_tecnica', 'mantenimiento_sin_equipos']:
                # Warn but allow SIM card for these services
                if 'observaciones' not in attrs:
                    attrs['observaciones'] = ''
                attrs['observaciones'] += f"\nNota: SIM Card asignada para {tipo_trabajo.get_nombre_display()}"
        
        elif tipo_trabajo.nombre in tipos_con_equipos:
            # For new installations, at least GPS is typically required
            if not gps and not requiere_gps:
                raise serializers.ValidationError({
                    'gps': 'Para instalaciones nuevas se requiere especificar un dispositivo GPS o marcar requiere_gps=False con justificación.'
                })
            
            if not gps and requiere_gps == False and not motivo_sin_equipos:
                raise serializers.ValidationError({
                    'motivo_sin_equipos': 'Debe especificar el motivo por el cual no se asigna GPS en una instalación nueva.'
                })
        
        elif tipo_trabajo.nombre == 'otro':
            # Para tipo "otro", las observaciones son obligatorias y deben ser descriptivas
            if not observaciones or len(observaciones.strip()) < 10:
                raise serializers.ValidationError({
                    'observaciones': 'Para servicios de tipo "Otro", debe especificar detalles descriptivos en las observaciones (mínimo 10 caracteres).'
                })
            
            # Sugerir palabras clave para casos comunes en observaciones
            observaciones_lower = observaciones.lower()
            keywords_sin_equipos = [
                'mantenimiento sin cambio', 'sin equipos', 'accesorio', 'cámara', 
                'revisión técnica', 'diagnóstico', 'configuración software', 
                'limpieza', 'reparación menor', 'calibración'
            ]
            
            # Si las observaciones sugieren que no se necesitan equipos, ajustar flags automáticamente
            if any(keyword in observaciones_lower for keyword in keywords_sin_equipos):
                if not gps and not sim_card:
                    attrs['requiere_gps'] = False
                    attrs['requiere_sim_card'] = False
                    if not motivo_sin_equipos:
                        attrs['motivo_sin_equipos'] = f'Servicio especial: {observaciones[:50]}...'
        
        else:
            # For maintenance services, equipment is flexible
            # Just ensure proper documentation
            if not gps and not sim_card:
                if not motivo_sin_equipos:
                    attrs['motivo_sin_equipos'] = f"Servicio de {tipo_trabajo.get_nombre_display()} - mantenimiento sin cambio de equipos"
        
        # Validate unit belongs to client
        unidad = attrs.get('unidad')
        cliente = attrs.get('cliente')
        if unidad and cliente and unidad.cliente != cliente:
            raise serializers.ValidationError({
                'unidad': 'La unidad debe pertenecer al cliente seleccionado.'
            })
        
        # Validate technician assignment
        tecnico_dni = attrs.get('tecnico_dni')
        if tecnico_dni:
            try:
                tecnico = CustomUser.objects.get(dni=tecnico_dni, is_active=True)
                attrs['tecnico'] = tecnico
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({
                    'tecnico_dni': 'No se encontró un técnico activo con el DNI especificado.'
                })
        
        # Validate GPS availability if specified
        # GPS can be assigned if: estado='no_asignado' and proceso in assignable processes
        if gps:
            if gps.estado == 'asignado' and gps.cliente != cliente:
                raise serializers.ValidationError({
                    'gps': f'El dispositivo GPS ya está asignado a otro cliente ({gps.cliente.nombre}).'
                })
            
            # Check if GPS process allows assignment
            assignable_processes = ['disponible', 'en_produccion', 'en_transito']
            if gps.proceso not in assignable_processes:
                raise serializers.ValidationError({
                    'gps': f'El dispositivo GPS está en proceso "{gps.proceso}" y no puede ser asignado.'
                })
        
        # Validate SIM Card availability if specified
        # SIM can be assigned if: estado='no_asignado' and proceso in assignable processes
        if sim_card:
            if sim_card.estado == 'asignado' and sim_card.cliente != cliente:
                raise serializers.ValidationError({
                    'sim_card': f'La tarjeta SIM ya está asignada a otro cliente ({sim_card.cliente.nombre}).'
                })
            
            # Check if SIM process allows assignment
            assignable_processes = ['en_produccion', 'en_almacen']
            if sim_card.proceso not in assignable_processes:
                raise serializers.ValidationError({
                    'sim_card': f'La tarjeta SIM está en proceso "{sim_card.proceso}" y no puede ser asignada.'
                })
        
        # Clean up write-only fields before saving
        attrs.pop('requiere_gps', None)
        attrs.pop('requiere_sim_card', None)
        attrs.pop('motivo_sin_equipos', None)
        attrs.pop('tecnico_dni', None)
        
        return attrs
    
    def create(self, validated_data):
        """Create a new flexible service with proper audit logging."""
        # Log the creation attempt
        self.log_action('create_attempt', {
            'tipo_trabajo': validated_data.get('tipo_trabajo').nombre if validated_data.get('tipo_trabajo') else None,
            'cliente': validated_data.get('cliente').id if validated_data.get('cliente') else None,
            'has_gps': bool(validated_data.get('gps')),
            'has_sim_card': bool(validated_data.get('sim_card'))
        })
        
        try:
            servicio = Servicio.objects.create(**validated_data)
            
            # Log successful creation
            self.log_action('create_success', {
                'servicio_id': servicio.id,
                'tipo_trabajo': servicio.tipo_trabajo.nombre,
                'cliente': servicio.cliente.nombre
            })
            
            return servicio
            
        except Exception as e:
            # Log creation failure
            self.log_action('create_failure', {
                'error': str(e),
                'validated_data': str(validated_data)
            })
            raise serializers.ValidationError(f"Error al crear el servicio: {str(e)}")
    
    def update(self, instance, validated_data):
        """Update an existing flexible service with proper audit logging."""
        # Store original values for audit
        original_data = {
            'tipo_trabajo': instance.tipo_trabajo.nombre,
            'gps_id': instance.gps.id if instance.gps else None,
            'sim_card_id': instance.sim_card.id if instance.sim_card else None,
            'estado': instance.estado_servicio
        }
        
        # Log the update attempt
        self.log_action('update_attempt', {
            'servicio_id': instance.id,
            'original_data': original_data,
            'new_data': {k: str(v) for k, v in validated_data.items()}
        })
        
        try:
            # Update the instance
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
            
            # Log successful update
            self.log_action('update_success', {
                'servicio_id': instance.id,
                'changes': {k: str(v) for k, v in validated_data.items()}
            })
            
            return instance
            
        except Exception as e:
            # Log update failure
            self.log_action('update_failure', {
                'servicio_id': instance.id,
                'error': str(e)
            })
            raise serializers.ValidationError(f"Error al actualizar el servicio: {str(e)}")
    
    def create(self, validated_data):
        """Create service - equipment assignment is now handled in the model's save method."""
        # Remove tecnico_dni from validated_data as it's not a model field
        validated_data.pop('tecnico_dni', None)
        
        # Create the service - the model's save method will handle equipment assignment
        servicio = super().create(validated_data)
        
        return servicio
    
    def update(self, instance, validated_data):
        """Update service with inventory status management."""
        # Remove tecnico_dni from validated_data
        validated_data.pop('tecnico_dni', None)
        
        # Handle GPS reassignment
        old_gps = instance.gps
        new_gps = validated_data.get('gps')
        
        if old_gps != new_gps:
            # Free old GPS
            if old_gps:
                old_gps.estado = 'disponible'
                old_gps.save()
            
            # Assign new GPS
            if new_gps:
                new_gps.estado = 'asignado'
                new_gps.save()
        
        # Handle SIM card reassignment
        old_sim = instance.sim_card
        new_sim = validated_data.get('sim_card')
        
        if old_sim != new_sim:
            # Free old SIM
            if old_sim:
                old_sim.estado = 'disponible'
                old_sim.save()
            
            # Assign new SIM
            if new_sim:
                new_sim.estado = 'asignado'
                new_sim.save()
        
        return super().update(instance, validated_data)


class ServicioCreateSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer optimizado para creación de servicios con validaciones de seguridad.
    """
    tecnico_dni = serializers.CharField(write_only=True)
    unidad = serializers.PrimaryKeyRelatedField(
        queryset=Unidad.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        help_text="Unidad vehicular (opcional para servicios como instalación de cámaras)"
    )
    
    class Meta:
        model = Servicio
        fields = [
            'fecha', 'tipo_trabajo', 'tecnico_dni', 'cliente', 'unidad',
            'gps', 'sim_card', 'descripcion', 'precio', 'observaciones'
        ]
    
    def validate_tecnico_dni(self, value):
        """Validate and get tecnico by DNI."""
        try:
            tecnico = CustomUser.objects.get(
                dni=value,
                is_active=True,
                rol__nombre='tecnico'
            )
            return tecnico
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontró un técnico activo con ese DNI."
            )
    
    def validate(self, attrs):
        """Cross-field validations for creation."""
        # Convert tecnico_dni to tecnico object if it's still a string
        if 'tecnico_dni' in attrs:
            tecnico_dni_value = attrs.pop('tecnico_dni')
            # If it's already a CustomUser object (from field validation), use it
            if hasattr(tecnico_dni_value, 'dni'):
                attrs['tecnico'] = tecnico_dni_value
            else:
                # If it's still a string, validate it
                attrs['tecnico'] = self.validate_tecnico_dni(tecnico_dni_value)
        
        # Validate unidad belongs to cliente (only if unidad is provided)
        unidad = attrs.get('unidad')
        cliente = attrs.get('cliente')
        
        # Only validate if both unidad and cliente are provided
        if unidad and cliente:
            # If they are IDs, get the objects
            if isinstance(unidad, int):
                from entities.models import Unidad
                try:
                    unidad_obj = Unidad.objects.get(id=unidad)
                except Unidad.DoesNotExist:
                    raise serializers.ValidationError(
                        "La unidad especificada no existe."
                    )
            else:
                unidad_obj = unidad
            
            if isinstance(cliente, int):
                from entities.models import Cliente
                try:
                    cliente_obj = Cliente.objects.get(id=cliente)
                except Cliente.DoesNotExist:
                    raise serializers.ValidationError(
                        "El cliente especificado no existe."
                    )
            else:
                cliente_obj = cliente
            
            # Now compare the objects
            if unidad_obj.cliente != cliente_obj:
                raise serializers.ValidationError(
                    "La unidad debe pertenecer al cliente seleccionado."
                )
        
        return attrs