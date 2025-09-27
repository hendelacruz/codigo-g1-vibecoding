from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from entities.models import Proveedor, Cliente


# Choices para estados de inventario
ESTADO_CHOICES = [
    ('disponible', 'Disponible'),
    ('no_asignado', 'No Asignado'),
    ('activo', 'Activo'),
    ('asignado', 'Asignado'),
    ('suspendido', 'Suspendido'),
    ('en_mantenimiento', 'En Mantenimiento'),
    ('dañado', 'Dañado'),
    ('perdido', 'Perdido'),
    ('dado_de_baja', 'Dado de Baja'),
]


class GPS(models.Model):
    """
    Modelo para gestionar dispositivos GPS del inventario.
    Separamos estado (relación con cliente) y proceso (condición operativa)
    """
    ESTADO_CHOICES = [
        ('asignado', 'Asignado'),
        ('no_asignado', 'No Asignado'),
    ]
    
    PROCESO_CHOICES = [
        ('en_produccion', 'En Producción'),
        ('dañado', 'Dañado'),
        ('garantia', 'Garantía'),
        ('en_mantenimiento', 'En Mantenimiento'),
        ('dado_de_baja', 'Dado de Baja'),
        ('en_transito', 'En Tránsito'),
    ]
    fecha_compra = models.DateTimeField(
        help_text="Fecha de compra del dispositivo GPS"
    )
    imei = models.CharField(
        max_length=15, 
        unique=True,
        validators=[RegexValidator(r'^\d{15}$', 'IMEI debe tener 15 dígitos')],
        help_text="Número IMEI único del dispositivo"
    )
    marca = models.CharField(
        max_length=20,
        help_text="Marca del dispositivo GPS"
    )
    modelo = models.CharField(
        max_length=20,
        help_text="Modelo del dispositivo GPS"
    )
    numero_factura = models.CharField(
        max_length=20,
        help_text="Número de factura de compra"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.PROTECT,
        help_text="Proveedor que vendió el dispositivo"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gps_asignados',
        help_text="Cliente al que está asignado el dispositivo GPS"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='no_asignado',
        help_text="Estado de asignación del GPS (asignado/no_asignado)"
    )
    proceso = models.CharField(
        max_length=20,
        choices=PROCESO_CHOICES,
        default='en_produccion',
        help_text="Proceso o condición operativa del GPS"
    )
    precio_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio de compra del dispositivo"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales sobre el dispositivo"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si el dispositivo GPS está activo en el sistema"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_gps'
        verbose_name = 'GPS'
        verbose_name_plural = 'Dispositivos GPS'
        ordering = ['-fecha_compra']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['imei']),  # Unique identifier searches
            models.Index(fields=['estado']),  # Status filtering
            models.Index(fields=['fecha_compra']),  # Date range queries
            models.Index(fields=['marca', 'modelo']),  # Brand/model searches
            models.Index(fields=['proveedor', 'estado']),  # Combined filtering
            models.Index(fields=['cliente']),  # Client assignment searches
            models.Index(fields=['cliente', 'estado']),  # Client-status filtering
            models.Index(fields=['is_active']),  # Active/inactive filtering
            models.Index(fields=['is_active', 'estado']),  # Combined active-status filtering
        ]

    def __str__(self):
        return f"GPS {self.marca} {self.modelo} - IMEI: {self.imei}"
    
    def clean(self):
        """
        Validaciones personalizadas del modelo GPS
        """
        super().clean()
        
        # Validar consistencia de estado y proceso
        if not hasattr(self, '_skip_validation') or not self._skip_validation:
            self._validate_estado_proceso_consistency()
    
    def _validate_estado_proceso_consistency(self):
        """
        Valida la consistencia entre estado, proceso y cliente
        """
        errors = []
        
        # Si está asignado, debe tener cliente
        if self.estado == 'asignado' and not self.cliente:
            errors.append("GPS asignado debe tener un cliente asociado")
        
        # Si no está asignado, no debe tener cliente
        if self.estado == 'no_asignado' and self.cliente:
            errors.append("GPS no asignado no puede tener cliente asociado")
        
        # Validar procesos que no permiten asignación
        procesos_no_asignables = ['dañado', 'en_reparacion', 'dado_de_baja']
        if self.estado == 'asignado' and self.proceso in procesos_no_asignables:
            errors.append(f"GPS en proceso '{self.proceso}' no puede estar asignado")
        
        if errors:
            raise ValidationError({'estado': errors})
    
    def save(self, *args, **kwargs):
        """
        Override save to handle state validation and auto-updates
        """
        skip_validation = kwargs.pop('skip_validation', False)
        
        if not skip_validation:
            # Auto-update estado based on cliente assignment
            if self.cliente and self.estado != 'asignado':
                self.estado = 'asignado'
            elif not self.cliente and self.estado == 'asignado':
                self.estado = 'no_asignado'
            
            # Perform full validation
            self.full_clean()
        
        super().save(*args, **kwargs)
    
    def change_proceso(self, new_proceso, observaciones=None):
        """
        Change GPS proceso with validation
        """
        # Validate that proceso change doesn't conflict with estado
        if self.estado == 'asignado' and new_proceso in ['dañado', 'garantia', 'dado_de_baja']:
            raise ValidationError(
                f"No se puede cambiar a proceso '{new_proceso}' mientras el GPS esté asignado"
            )
        
        # Update proceso
        self.proceso = new_proceso
        
        # Add observation if provided
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
        
        # Save with validation
        self.save()
    
    def asignar_cliente(self, cliente, observaciones=None):
        """
        Assign GPS to a client
        """
        # Validate that GPS can be assigned
        if self.proceso in ['dañado', 'en_reparacion', 'dado_de_baja']:
            raise ValidationError(
                f"No se puede asignar GPS en proceso '{self.proceso}'"
            )
        
        self.cliente = cliente
        self.estado = 'asignado'
        
        # Add observation if provided
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
        
        self.save()
    
    def desasignar_cliente(self, observaciones=None):
        """
        Unassign GPS from client
        """
        self.cliente = None
        self.estado = 'no_asignado'
        
        # Add observation if provided
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
        
        self.save()
    
    def change_state(self, new_state, observaciones=None):
        """
        Change GPS state with validation
        """
        from .state_manager import GPSStateManager
        
        # Validate the state transition
        is_valid, error_message = GPSStateManager.validate_state_transition(
            self.estado, new_state, self.cliente is not None
        )
        
        if not is_valid:
            raise ValidationError(error_message)
        
        # Update state
        old_state = self.estado
        self.estado = new_state
        
        # Add observation if provided
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
        
        self.save()
        return True
    
    def get_valid_next_states(self):
        """
        Get valid next states for this GPS
        """
        from .state_manager import GPSStateManager
        return GPSStateManager.get_valid_next_states(self.estado, self.cliente is not None)

    def activate(self, observaciones=None):
        """
        Activa el dispositivo GPS
        """
        if not self.is_active:
            self.is_active = True
            if observaciones:
                self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
            self.save()
        return True

    def deactivate(self, observaciones=None):
        """
        Desactiva el dispositivo GPS
        """
        if self.is_active:
            self.is_active = False
            if observaciones:
                self.observaciones = f"{self.observaciones}\n{observaciones}" if self.observaciones else observaciones
            self.save()
        return True

    def toggle_active(self, observaciones=None):
        """
        Cambia el estado activo del dispositivo GPS
        """
        if self.is_active:
            return self.deactivate(observaciones)
        else:
            return self.activate(observaciones)

    @property
    def estado_info(self):
        """
        Get detailed state and process information
        """
        from .state_manager import GPSStateManager, GPSStateValidator
        
        # Validar consistencia del estado
        is_valid, errors = GPSStateValidator.validate_gps_state(self)
        
        return {
            'current_state': self.estado,  # Para compatibilidad con tests
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'proceso': self.proceso,
            'proceso_display': self.get_proceso_display(),
            'is_active': self.is_active,
            'cliente': self.cliente.nombre if self.cliente else None,
            'has_client': self.cliente is not None,  # Para compatibilidad con tests
            'is_consistent': is_valid,  # Para compatibilidad con tests
            'valid_next_states': GPSStateManager.get_valid_proceso_transitions(self.proceso),  # Para compatibilidad con tests
            'puede_asignar': self.proceso in ['en_produccion', 'en_transito'],
            'puede_cambiar_proceso': self.estado == 'no_asignado',
            'es_operativo': self.proceso not in ['dañado', 'dado_de_baja'],
            'requiere_atencion': self.proceso in ['dañado', 'garantia'],
            'descripcion_estado': f"GPS {self.estado} en proceso {self.proceso}"
        }


class SIMCard(models.Model):
    """
    Modelo para gestionar tarjetas SIM del inventario.
    Incluye gestión de estado activo/inactivo y asignación a clientes.
    """
    ESTADO_CHOICES = [
        ('asignado', 'Asignado'),
        ('no_asignado', 'No Asignado'),
    ]
    
    PROCESO_CHOICES = [
        ('en_produccion', 'En Producción'),
        ('dado_de_baja', 'Dado de Baja'),
        ('en_almacen', 'En Almacén'),
    ]
    
    fecha_compra = models.DateTimeField(
        help_text="Fecha de compra de la tarjeta SIM"
    )
    numero_factura = models.CharField(
        max_length=20,
        help_text="Número de factura de compra"
    )
    numero_chip = models.CharField(
        max_length=9, 
        unique=True,
        validators=[RegexValidator(r'^\d{9}$', 'Número de chip debe tener 9 dígitos')],
        help_text="Número de teléfono de la SIM"
    )
    icc = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Código ICC único de la tarjeta SIM"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.PROTECT,
        help_text="Proveedor que vendió la tarjeta SIM"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simcards_asignadas',
        help_text="Cliente al que está asignada la tarjeta SIM"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='no_asignado',
        help_text="Estado de asignación de la SIM (asignado/no_asignado)"
    )
    proceso = models.CharField(
        max_length=20,
        choices=PROCESO_CHOICES,
        default='en_produccion',
        help_text="Proceso o condición operativa de la SIM"
    )
    plan = models.CharField(
        max_length=100,
        blank=True,
        help_text="Plan contratado para la SIM"
    )
    precio_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio de compra de la SIM"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales sobre la SIM"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la tarjeta SIM está activa en el sistema"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_simcard'
        verbose_name = 'Tarjeta SIM'
        verbose_name_plural = 'Tarjetas SIM'
        ordering = ['-fecha_compra']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['numero_chip']),  # Phone number searches
            models.Index(fields=['icc']),  # ICC code searches
            models.Index(fields=['estado']),  # Status filtering
            models.Index(fields=['fecha_compra']),  # Date range queries
            models.Index(fields=['proveedor', 'estado']),  # Combined filtering
            models.Index(fields=['cliente']),  # Client assignment searches
            models.Index(fields=['cliente', 'estado']),  # Client-status filtering
            models.Index(fields=['is_active']),  # Active/inactive filtering
            models.Index(fields=['is_active', 'estado']),  # Combined active-status filtering
        ]

    def __str__(self):
        return f"SIM {self.numero_chip} - ICC: {self.icc}"
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        super().clean()
        self._validate_estado_proceso_consistency()
    
    def _validate_estado_proceso_consistency(self):
        """Valida la consistencia entre estado y proceso"""
        if self.estado == 'asignado' and not self.cliente:
            raise ValidationError({
                'cliente': 'Una SIM asignada debe tener un cliente asociado.'
            })
        
        if self.estado == 'no_asignado' and self.cliente:
            raise ValidationError({
                'estado': 'Una SIM no asignada no puede tener un cliente asociado.'
            })
    
    def save(self, *args, **kwargs):
        """Override save para validaciones automáticas"""
        # Actualizar estado basado en cliente
        if self.cliente and self.estado == 'no_asignado':
            self.estado = 'asignado'
        elif not self.cliente and self.estado == 'asignado':
            self.estado = 'no_asignado'
        
        # Validar antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
    
    def asignar_cliente(self, cliente, observaciones=None):
        """Asigna la SIM a un cliente específico"""
        if self.cliente == cliente:
            return False  # Ya está asignado a este cliente
        
        self.cliente = cliente
        self.estado = 'asignado'
        
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}".strip()
        
        self.save()
        return True
    
    def desasignar_cliente(self, observaciones=None):
        """Desasigna la SIM del cliente actual"""
        if not self.cliente:
            return False  # Ya está desasignado
        
        self.cliente = None
        self.estado = 'no_asignado'
        
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}".strip()
        
        self.save()
        return True
    
    def change_state(self, new_state, observaciones=None):
        """Cambia el estado de la SIM con validaciones"""
        if self.estado == new_state:
            return False  # Ya está en ese estado
        
        old_state = self.estado
        self.estado = new_state
        
        # Si cambia a no_asignado, quitar cliente
        if new_state == 'no_asignado':
            self.cliente = None
        
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}".strip()
        
        self.save()
        return True
    
    def activate(self, observaciones=None):
        """Activa la SIM"""
        if self.is_active:
            return False  # Ya está activa
        
        self.is_active = True
        
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}".strip()
        
        self.save()
        return True
    
    def deactivate(self, observaciones=None):
        """Desactiva la SIM"""
        if not self.is_active:
            return False  # Ya está inactiva
        
        self.is_active = False
        
        if observaciones:
            self.observaciones = f"{self.observaciones}\n{observaciones}".strip()
        
        self.save()
        return True
    
    def toggle_active(self, observaciones=None):
        """Alterna el estado activo/inactivo de la SIM"""
        if self.is_active:
            return self.deactivate(observaciones)
        else:
            return self.activate(observaciones)
    
    @property
    def estado_info(self):
        """Información completa del estado de la SIM"""
        return {
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'proceso': self.proceso,
            'proceso_display': self.get_proceso_display(),
            'is_active': self.is_active,
            'cliente': {
                'id': self.cliente.id if self.cliente else None,
                'nombre': str(self.cliente) if self.cliente else None,
            } if self.cliente else None,
            'proveedor': {
                'id': self.proveedor.id,
                'nombre': str(self.proveedor),
            }
        }


class Otros(models.Model):
    """
    Modelo para gestionar otros productos del inventario.
    Para productos que no son GPS ni SIM cards.
    """
    fecha_compra = models.DateTimeField(
        help_text="Fecha de compra del producto"
    )
    numero_factura = models.CharField(
        max_length=20,
        help_text="Número de factura de compra"
    )
    cantidad = models.IntegerField(
        help_text="Cantidad de productos comprados"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del producto"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.PROTECT,
        help_text="Proveedor que vendió el producto"
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        help_text="Categoría del producto (cables, herramientas, etc.)"
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio unitario del producto"
    )
    precio_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio total de la compra"
    )
    stock_actual = models.IntegerField(
        default=0,
        help_text="Stock actual disponible"
    )
    stock_minimo = models.IntegerField(
        default=0,
        help_text="Stock mínimo requerido"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales sobre el producto"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_otros'
        verbose_name = 'Otro Producto'
        verbose_name_plural = 'Otros Productos'
        ordering = ['-fecha_compra']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['categoria']),  # Category filtering
            models.Index(fields=['fecha_compra']),  # Date range queries
            models.Index(fields=['stock_actual']),  # Stock level queries
            models.Index(fields=['proveedor']),  # Provider filtering
            models.Index(fields=['categoria', 'stock_actual']),  # Combined filtering
        ]

    def __str__(self):
        return f"{self.descripcion} - Cantidad: {self.cantidad}"

    def save(self, *args, **kwargs):
        """
        Override save para calcular precio_total automáticamente
        y establecer stock_actual inicial igual a cantidad solo si no se proporciona
        """
        if self.precio_unitario and self.cantidad:
            self.precio_total = self.precio_unitario * self.cantidad
        
        # Si es un nuevo registro y no se ha establecido stock_actual, usar cantidad
        if not self.pk and self.stock_actual == 0:
            self.stock_actual = self.cantidad
            
        super().save(*args, **kwargs)
