"""
Serializers para la aplicación de ventas.
Maneja la serialización de Ventas con cálculos automáticos de IGV y validaciones.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, date, time

from .models import Ventas, TIPO_PAGO_CHOICES, ESTADO_VENTA_CHOICES
from entities.models import Cliente, Unidad


class VentasListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de ventas.
    Optimizado para performance en listados.
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_ruc = serializers.CharField(source='cliente.ruc', read_only=True)
    unidad_placa = serializers.CharField(source='unidad.placa', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    
    class Meta:
        model = Ventas
        fields = [
            'id', 'numero_factura', 'fecha_generacion_factura', 'mes',
            'cliente_nombre', 'cliente_ruc', 'unidad_placa',
            'precio', 'total', 'estado', 'estado_display',
            'tipo_pago', 'tipo_pago_display'
        ]


class VentasSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Ventas con cálculos automáticos de IGV.
    """
    # Read-only fields for display
    cliente_info = serializers.SerializerMethodField()
    unidad_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    
    # Calculated fields (read-only by default, can be overridden)
    importe_calculado = serializers.SerializerMethodField()
    igv_calculado = serializers.SerializerMethodField()
    total_calculado = serializers.SerializerMethodField()
    
    class Meta:
        model = Ventas
        fields = [
            'id', 'mes', 'fecha_pago', 'numero_operacion', 'tipo_pago', 'tipo_pago_display',
            'banco', 'numero_factura', 'fecha_generacion_factura',
            'cliente', 'cliente_info', 'descripcion', 'unidad', 'unidad_info',
            'precio', 'importe', 'igv', 'total',
            'importe_calculado', 'igv_calculado', 'total_calculado',
            'estado', 'estado_display', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cliente_info(self, obj):
        """Return detailed client information."""
        if obj.cliente:
            return {
                'id': obj.cliente.id,
                'nombre': obj.cliente.nombre,
                'ruc': obj.cliente.ruc,
                'direccion': obj.cliente.direccion,
                'contacto': obj.cliente.contacto,
                'celular': obj.cliente.celular,
                'correo': obj.cliente.correo
            }
        return None
    
    def get_unidad_info(self, obj):
        """Return detailed unit information."""
        if obj.unidad:
            return {
                'id': obj.unidad.id,
                'placa': obj.unidad.placa,
                'tipo': obj.unidad.get_tipo_display(),
                'marca': obj.unidad.marca,
                'modelo': obj.unidad.modelo,
                'serie': obj.unidad.serie
            }
        return None
    
    def get_importe_calculado(self, obj):
        """Calculate importe from precio."""
        if obj.precio:
            return (obj.precio / Decimal('1.18')).quantize(Decimal('0.01'))
        return None
    
    def get_igv_calculado(self, obj):
        """Calculate IGV from precio."""
        if obj.precio:
            importe = obj.precio / Decimal('1.18')
            return (importe * Decimal('0.18')).quantize(Decimal('0.01'))
        return None
    
    def get_total_calculado(self, obj):
        """Calculate total (should equal precio)."""
        if obj.precio:
            importe = obj.precio / Decimal('1.18')
            igv = importe * Decimal('0.18')
            return (importe + igv).quantize(Decimal('0.01'))
        return None
    
    def validate_numero_factura(self, value):
        """Validate invoice number format and uniqueness."""
        if not value.strip():
            raise serializers.ValidationError("El número de factura es requerido.")
        
        # Check format (example: F001-00001234)
        if len(value) < 5:
            raise serializers.ValidationError(
                "El número de factura debe tener al menos 5 caracteres."
            )
        
        return value.strip().upper()
    
    def validate_numero_operacion(self, value):
        """Validate operation number."""
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El número de operación debe tener al menos 3 caracteres."
            )
        return value.strip() if value else value
    
    def validate_precio(self, value):
        """Validate sale price."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        
        if value > Decimal('100000.00'):
            raise serializers.ValidationError(
                "El precio no puede exceder S/ 100,000.00"
            )
        
        return value
    
    def validate_descripcion(self, value):
        """Validate sale description."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 10 caracteres."
            )
        return value.strip()
    
    def validate_mes(self, value):
        """Validate month field."""
        if value > date.today():
            raise serializers.ValidationError(
                "El mes no puede ser futuro."
            )
        return value
    
    def validate_fecha_generacion_factura(self, value):
        """Validate invoice generation date."""
        if value.date() > date.today():
            raise serializers.ValidationError(
                "La fecha de generación no puede ser futura."
            )
        return value
    
    def validate(self, attrs):
        """Cross-field validations."""
        # Validate that unidad belongs to cliente
        if 'unidad' in attrs and 'cliente' in attrs:
            if attrs['unidad'].cliente != attrs['cliente']:
                raise serializers.ValidationError({
                    'unidad': 'La unidad debe pertenecer al cliente seleccionado.'
                })
        
        # Validate numero_factura uniqueness on update
        if self.instance:
            numero_factura = attrs.get('numero_factura', self.instance.numero_factura)
            if (numero_factura != self.instance.numero_factura and 
                Ventas.objects.filter(numero_factura=numero_factura).exists()):
                raise serializers.ValidationError({
                    'numero_factura': 'Ya existe una venta con este número de factura.'
                })
        
        # Validate payment details consistency
        tipo_pago = attrs.get('tipo_pago')
        numero_operacion = attrs.get('numero_operacion')
        banco = attrs.get('banco')
        
        if tipo_pago in ['transferencia', 'deposito', 'tarjeta_credito', 'tarjeta_debito']:
            if not numero_operacion:
                raise serializers.ValidationError({
                    'numero_operacion': f'El número de operación es requerido para {tipo_pago}.'
                })
            if not banco:
                raise serializers.ValidationError({
                    'banco': f'El banco es requerido para {tipo_pago}.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create sale with automatic calculations."""
        # The model's save method will handle automatic calculations
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update sale with automatic recalculations if precio changes."""
        # If precio is being updated, clear calculated fields to force recalculation
        if 'precio' in validated_data and validated_data['precio'] != instance.precio:
            validated_data['importe'] = None
            validated_data['igv'] = None
            validated_data['total'] = None
        
        return super().update(instance, validated_data)


class VentasCreateSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para creación rápida de ventas.
    Solo requiere campos esenciales, el resto se calcula automáticamente.
    """
    class Meta:
        model = Ventas
        fields = [
            'mes', 'fecha_pago', 'numero_operacion', 'tipo_pago', 'banco',
            'numero_factura', 'fecha_generacion_factura', 'cliente', 'unidad',
            'descripcion', 'precio', 'estado'
        ]
    
    def validate(self, attrs):
        """Simplified validations for creation."""
        # Validate unidad belongs to cliente
        if attrs['unidad'].cliente != attrs['cliente']:
            raise serializers.ValidationError(
                "La unidad debe pertenecer al cliente seleccionado."
            )
        
        # Validate numero_factura uniqueness
        if Ventas.objects.filter(numero_factura=attrs['numero_factura']).exists():
            raise serializers.ValidationError({
                'numero_factura': 'Ya existe una venta con este número de factura.'
            })
        
        return attrs


class VentasReportSerializer(serializers.ModelSerializer):
    """
    Serializer para reportes de ventas con información resumida.
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_ruc = serializers.CharField(source='cliente.ruc', read_only=True)
    unidad_placa = serializers.CharField(source='unidad.placa', read_only=True)
    mes_display = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_pago_display = serializers.CharField(source='get_tipo_pago_display', read_only=True)
    
    class Meta:
        model = Ventas
        fields = [
            'id', 'numero_factura', 'fecha_generacion_factura', 'mes', 'mes_display',
            'cliente_nombre', 'cliente_ruc', 'unidad_placa', 'descripcion',
            'precio', 'importe', 'igv', 'total', 'estado', 'estado_display',
            'tipo_pago', 'tipo_pago_display', 'banco', 'numero_operacion'
        ]
    
    def get_mes_display(self, obj):
        """Return formatted month."""
        if obj.mes:
            return obj.mes.strftime('%B %Y')
        return None


class VentasStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de ventas.
    """
    total_ventas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_igv = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_importe = serializers.DecimalField(max_digits=15, decimal_places=2)
    cantidad_ventas = serializers.IntegerField()
    promedio_venta = serializers.DecimalField(max_digits=10, decimal_places=2)
    ventas_por_estado = serializers.DictField()
    ventas_por_tipo_pago = serializers.DictField()
    mes = serializers.DateField(required=False)
    cliente = serializers.CharField(required=False)