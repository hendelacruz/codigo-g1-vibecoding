from django.db import models
from django.core.validators import RegexValidator


class Cliente(models.Model):
    """
    Modelo para gestionar clientes del sistema.
    Representa empresas o personas que contratan servicios de GPS.
    """
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre o razón social del cliente"
    )
    ruc = models.CharField(
        max_length=11, 
        unique=True,
        validators=[RegexValidator(r'^\d{11}$', 'RUC debe tener 11 dígitos')],
        help_text="RUC del cliente (11 dígitos)"
    )
    direccion = models.TextField(
        help_text="Dirección completa del cliente"
    )
    contacto = models.CharField(
        max_length=100,
        help_text="Nombre de la persona de contacto"
    )
    celular = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', 'Celular debe tener 9 dígitos')],
        help_text="Número de celular (9 dígitos)"
    )
    correo = models.EmailField(
        help_text="Correo electrónico del cliente"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entities_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['ruc']),  # RUC searches (already unique but for joins)
            models.Index(fields=['nombre']),  # Name searches
            models.Index(fields=['correo']),  # Email searches
            models.Index(fields=['created_at']),  # Date range queries
        ]

    def __str__(self):
        return f"{self.nombre} ({self.ruc})"


class Proveedor(models.Model):
    """
    Modelo para gestionar proveedores del sistema.
    Representa empresas que suministran productos de inventario.
    """
    nombre = models.CharField(
        max_length=100,
        default='Sin nombre',
        help_text="Nombre o razón social del proveedor"
    )
    ruc = models.CharField(
        max_length=11, 
        unique=True,
        validators=[RegexValidator(r'^\d{11}$', 'RUC debe tener 11 dígitos')],
        help_text="RUC del proveedor (11 dígitos)"
    )
    direccion = models.TextField(
        default='Sin dirección',
        help_text="Dirección completa del proveedor"
    )
    contacto = models.CharField(
        max_length=100,
        default='Sin contacto',
        help_text="Nombre de la persona de contacto"
    )
    celular = models.CharField(
        max_length=9,
        default='000000000',
        validators=[RegexValidator(r'^\d{9}$', 'Celular debe tener 9 dígitos')],
        help_text="Número de celular (9 dígitos)"
    )
    correo = models.EmailField(
        default='sin@correo.com',
        help_text="Correo electrónico del proveedor"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entities_proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['ruc']),  # RUC searches (already unique but for joins)
            models.Index(fields=['nombre']),  # Name searches
            models.Index(fields=['created_at']),  # Date range queries
        ]

    def __str__(self):
        return f"{self.nombre} ({self.ruc})"


class Unidad(models.Model):
    """
    Modelo para gestionar unidades vehiculares de los clientes.
    Representa vehículos donde se instalan los dispositivos GPS.
    """
    TIPO_CHOICES = [
        ('bus', 'Bus'),
        ('camion', 'Camión'),
        ('otro', 'Otro'),
    ]
    
    tipo = models.CharField(
        max_length=10, 
        choices=TIPO_CHOICES,
        help_text="Tipo de vehículo"
    )
    placa = models.CharField(
        max_length=10, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9-]{6,10}$', 'Formato de placa inválido')],
        help_text="Placa del vehículo (formato peruano)"
    )
    marca = models.CharField(
        max_length=50,
        help_text="Marca del vehículo"
    )
    modelo = models.CharField(
        max_length=50,
        help_text="Modelo del vehículo"
    )
    serie = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Número de serie del vehículo (VIN)"
    )
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE,
        related_name='unidades',
        help_text="Cliente propietario del vehículo"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entities_unidad'
        verbose_name = 'Unidad Vehicular'
        verbose_name_plural = 'Unidades Vehiculares'
        ordering = ['placa']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['placa']),  # License plate searches (already unique but for joins)
            models.Index(fields=['cliente']),  # Client filtering
            models.Index(fields=['tipo']),  # Vehicle type filtering
            models.Index(fields=['marca', 'modelo']),  # Brand/model searches
            models.Index(fields=['cliente', 'tipo']),  # Combined filtering
        ]

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo} ({self.cliente.nombre})"
