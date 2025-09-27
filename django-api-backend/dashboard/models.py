from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Metric(models.Model):
    """
    Model to store system metrics and KPIs
    """
    METRIC_TYPES = [
        ('sales', 'Ventas'),
        ('inventory', 'Inventario'),
        ('users', 'Usuarios'),
        ('performance', 'Rendimiento'),
        ('financial', 'Financiero'),
    ]
    
    PERIOD_TYPES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre de la métrica"
    )
    
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        verbose_name="Tipo de métrica"
    )
    
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor"
    )
    
    period_type = models.CharField(
        max_length=20,
        choices=PERIOD_TYPES,
        verbose_name="Tipo de período"
    )
    
    period_start = models.DateTimeField(
        verbose_name="Inicio del período"
    )
    
    period_end = models.DateTimeField(
        verbose_name="Fin del período"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos adicionales"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_metrics',
        verbose_name="Creado por"
    )
    
    class Meta:
        verbose_name = "Métrica"
        verbose_name_plural = "Métricas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['metric_type', 'period_type']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['name', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.name} - {self.get_period_type_display()} ({self.period_start.date()})"


class Alert(models.Model):
    """
    Model to store system alerts and notifications
    """
    ALERT_TYPES = [
        ('low_stock', 'Stock Bajo'),
        ('high_sales', 'Ventas Altas'),
        ('system_error', 'Error del Sistema'),
        ('performance', 'Rendimiento'),
        ('security', 'Seguridad'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('acknowledged', 'Reconocida'),
        ('resolved', 'Resuelta'),
        ('dismissed', 'Descartada'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    message = models.TextField(
        verbose_name="Mensaje"
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="Tipo de alerta"
    )
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium',
        verbose_name="Severidad"
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Estado"
    )
    
    threshold_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor umbral"
    )
    
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor actual"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de reconocimiento"
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de resolución"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_alerts',
        verbose_name="Creado por"
    )
    
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
        verbose_name="Reconocido por"
    )
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
