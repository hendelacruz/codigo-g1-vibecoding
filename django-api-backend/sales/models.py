from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError


# Choices para tipo de pago
TIPO_PAGO_CHOICES = [
    ('efectivo', 'Efectivo'),
    ('transferencia', 'Transferencia Bancaria'),
    ('deposito', 'Depósito Bancario'),
    ('cheque', 'Cheque'),
    ('tarjeta_credito', 'Tarjeta de Crédito'),
    ('tarjeta_debito', 'Tarjeta de Débito'),
    ('yape', 'Yape'),
    ('plin', 'Plin'),
    ('otro', 'Otro'),
]

# Choices para estado de venta
ESTADO_VENTA_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('pagado', 'Pagado'),
    ('parcial', 'Pago Parcial'),
    ('vencido', 'Vencido'),
    ('cancelado', 'Cancelado'),
    ('anulado', 'Anulado'),
]


class Ventas(models.Model):
    """
    Modelo para gestionar las ventas y facturación del sistema.
    Maneja los pagos, facturación y cálculos automáticos de IGV.
    """
    mes = models.DateField(
        help_text="Mes correspondiente a la venta"
    )
    fecha_pago = models.TimeField(
        help_text="Hora del pago realizado"
    )
    numero_operacion = models.CharField(
        max_length=10,
        help_text="Número de operación bancaria o comprobante"
    )
    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPO_PAGO_CHOICES,
        help_text="Método de pago utilizado"
    )
    banco = models.TextField(
        help_text="Banco donde se realizó la operación"
    )
    numero_factura = models.CharField(
        max_length=10,
        unique=True,
        help_text="Número único de factura"
    )
    fecha_generacion_factura = models.DateTimeField(
        help_text="Fecha y hora de generación de la factura"
    )
    cliente = models.ForeignKey(
        'entities.Cliente',
        on_delete=models.PROTECT,
        related_name='ventas',
        help_text="Cliente que realiza la compra"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada de la venta"
    )
    unidad = models.ForeignKey(
        'entities.Unidad',
        on_delete=models.PROTECT,
        related_name='ventas',
        help_text="Unidad vehicular asociada a la venta"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio total con IGV incluido"
    )
    importe = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Importe sin IGV (precio/1.18)"
    )
    igv = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monto del IGV (importe*0.18)"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total final (importe + igv)"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_VENTA_CHOICES,
        default='pendiente',
        help_text="Estado actual de la venta"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_generacion_factura']
        # Database indexes for performance optimization
        indexes = [
            models.Index(fields=['numero_factura']),  # Invoice number searches (already unique but for joins)
            models.Index(fields=['estado']),  # Status filtering
            models.Index(fields=['fecha_generacion_factura']),  # Date range queries
            models.Index(fields=['cliente']),  # Client filtering
            models.Index(fields=['tipo_pago']),  # Payment type filtering
            models.Index(fields=['cliente', 'estado']),  # Combined filtering
            models.Index(fields=['mes']),  # Monthly reporting
        ]

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente.nombre} (S/ {self.total})"

    def clean(self):
        """
        Validaciones personalizadas del modelo.
        """
        super().clean()
        
        # Validar que la unidad pertenezca al cliente
        # Solo validar si ambos objetos están disponibles y no son solo IDs
        if (self.unidad_id and self.cliente_id and 
            hasattr(self, 'unidad') and hasattr(self, 'cliente') and
            self.unidad and self.cliente and 
            self.unidad.cliente_id != self.cliente_id):
            raise ValidationError("La unidad debe pertenecer al cliente seleccionado")
        
        # Validar que el precio sea consistente con los cálculos
        if self.precio and self.importe and self.igv and self.total:
            # Calcular valores esperados
            expected_importe = self.precio / Decimal('1.18')
            expected_igv = expected_importe * Decimal('0.18')
            expected_total = expected_importe + expected_igv
            
            # Tolerancia para diferencias de redondeo
            tolerance = Decimal('0.01')
            
            if abs(self.importe - expected_importe) > tolerance:
                raise ValidationError(f"El importe debe ser {expected_importe:.2f} (precio/1.18)")
            
            if abs(self.igv - expected_igv) > tolerance:
                raise ValidationError(f"El IGV debe ser {expected_igv:.2f} (importe*0.18)")
            
            if abs(self.total - expected_total) > tolerance:
                raise ValidationError(f"El total debe ser {expected_total:.2f} (importe + igv)")

    def save(self, *args, **kwargs):
        """
        Override save method para cálculos automáticos y validaciones.
        """
        # Calcular automáticamente importe, igv y total si solo se proporciona precio
        if self.precio and not (self.importe and self.igv and self.total):
            self.calculate_amounts()
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)

    def calculate_amounts(self):
        """
        Calcula automáticamente importe, IGV y total basado en el precio.
        """
        if self.precio:
            # Calcular importe (precio sin IGV)
            self.importe = self.precio / Decimal('1.18')
            
            # Calcular IGV (18% del importe)
            self.igv = self.importe * Decimal('0.18')
            
            # Calcular total (importe + IGV)
            self.total = self.importe + self.igv
            
            # Redondear a 2 decimales
            self.importe = self.importe.quantize(Decimal('0.01'))
            self.igv = self.igv.quantize(Decimal('0.01'))
            self.total = self.total.quantize(Decimal('0.01'))

    @property
    def estado_display(self):
        """
        Retorna el estado en formato legible.
        """
        return self.get_estado_display()

    @property
    def tipo_pago_display(self):
        """
        Retorna el tipo de pago en formato legible.
        """
        return self.get_tipo_pago_display()
