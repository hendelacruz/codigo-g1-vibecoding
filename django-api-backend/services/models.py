from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


# Choices para estado de servicio
ESTADO_SERVICIO_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('programado', 'Programado'),
    ('en_proceso', 'En Proceso'),
    ('completado', 'Completado'),
    ('cancelado', 'Cancelado'),
    ('reprogramado', 'Reprogramado'),
]


class TipoTrabajo(models.Model):
    """
    Modelo para gestionar tipos de trabajo disponibles en el sistema.
    Define las categorías de servicios que se pueden realizar.
    """
    TIPO_CHOICES = [
        ('instalacion_nueva', 'Instalación Nueva'),
        ('mantenimiento_preventivo', 'Mantenimiento Preventivo'),
        ('mantenimiento_correctivo', 'Mantenimiento Correctivo'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(
        max_length=30, 
        choices=TIPO_CHOICES, 
        unique=True,
        help_text="Tipo de trabajo a realizar"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del tipo de trabajo"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services_tipo_trabajo'
        verbose_name = 'Tipo de Trabajo'
        verbose_name_plural = 'Tipos de Trabajo'
        ordering = ['nombre']

    def __str__(self):
        return self.get_nombre_display()


class Servicio(models.Model):
    """
    Modelo para gestionar servicios realizados a clientes.
    Representa trabajos técnicos realizados en unidades vehiculares.
    """
    fecha = models.DateTimeField(
        help_text="Fecha y hora del servicio"
    )
    tipo_trabajo = models.ForeignKey(
        TipoTrabajo, 
        on_delete=models.PROTECT,
        related_name='servicios',
        help_text="Tipo de trabajo a realizar"
    )
    tecnico = models.ForeignKey(
        'authentication.CustomUser', 
        on_delete=models.PROTECT,
        related_name='servicios_asignados',
        help_text="Técnico asignado al servicio"
    )
    cliente = models.ForeignKey(
        'entities.Cliente', 
        on_delete=models.PROTECT,
        related_name='servicios',
        help_text="Cliente que solicita el servicio"
    )
    unidad = models.ForeignKey(
        'entities.Unidad', 
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='servicios',
        help_text="Unidad vehicular donde se realiza el servicio (opcional para servicios como instalación de cámaras)"
    )
    gps = models.ForeignKey(
        'inventory.GPS', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='servicios',
        help_text="Dispositivo GPS utilizado en el servicio (opcional)"
    )
    sim_card = models.ForeignKey(
        'inventory.SIMCard', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='servicios',
        help_text="Tarjeta SIM utilizada en el servicio (opcional)"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del trabajo realizado"
    )
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio del servicio en soles"
    )
    estado_servicio = models.CharField(
        max_length=20, 
        choices=ESTADO_SERVICIO_CHOICES,
        default='pendiente',
        help_text="Estado actual del servicio"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales del servicio"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services_servicio'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo_trabajo.get_nombre_display()} - {self.cliente.nombre} ({self.fecha.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        """Override save to validate unit belongs to client and assign equipment."""
        # Validate unit belongs to client
        if self.unidad and self.unidad.cliente != self.cliente:
            raise ValueError("La unidad debe pertenecer al cliente del servicio")
        
        # Check if this is a new service (no ID yet)
        is_new_service = self.pk is None
        
        # Save the service first
        super().save(*args, **kwargs)
        
        # If this is a new service, handle equipment assignment
        if is_new_service:
            # Update GPS status and assign to client if assigned
            if self.gps:
                self.gps.estado = 'asignado'
                self.gps.cliente = self.cliente
                self.gps.save()
            
            # Update SIM card status and assign to client if assigned
            if self.sim_card:
                self.sim_card.estado = 'asignado'
                self.sim_card.cliente = self.cliente
                self.sim_card.save()
