from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Cliente, Proveedor, Unidad
from todoapi.utils.validators import (
    validate_ruc_peruano, 
    validate_celular_peruano,
    validate_placa_peruana
)


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para clientes con validaciones personalizadas
    Incluye validación de RUC peruano y celular
    """
    unidades_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'ruc', 'direccion', 'contacto', 
            'celular', 'correo', 'is_active', 'unidades_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'unidades_count']
    
    def get_unidades_count(self, obj):
        """
        Cuenta el número de unidades vehiculares del cliente
        """
        return obj.unidades.filter(is_active=True).count()
    
    def validate_ruc(self, value):
        """
        Validación personalizada para RUC peruano
        """
        try:
            validate_ruc_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                "El RUC debe ser válido según el algoritmo peruano de verificación"
            )
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = Cliente.objects.filter(ruc=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con este RUC"
            )
        
        return value
    
    def validate_celular(self, value):
        """
        Validación personalizada para celular peruano
        """
        try:
            validate_celular_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                "El celular debe ser un número peruano válido (9 dígitos, iniciando con 9)"
            )
        
        return value
    
    def validate_correo(self, value):
        """
        Validación personalizada para email único
        """
        # Verificar unicidad excluyendo la instancia actual
        queryset = Cliente.objects.filter(correo=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con este correo electrónico"
            )
        
        return value
    
    def validate_nombre(self, value):
        """
        Validación para nombre no vacío y longitud mínima
        """
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres"
            )
        
        return value.strip()
    
    def validate_contacto(self, value):
        """
        Validación para contacto no vacío
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El contacto debe tener al menos 2 caracteres"
            )
        
        return value.strip()


class ProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer para proveedores con validaciones personalizadas
    Incluye validación de RUC peruano y celular
    """
    productos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'ruc', 'direccion', 'contacto', 
            'celular', 'correo', 'is_active', 'productos_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'productos_count']
    
    def get_productos_count(self, obj):
        """
        Cuenta el número de productos del proveedor en inventario
        """
        from inventory.models import GPS, SIMCard, Otros
        
        gps_count = GPS.objects.filter(proveedor=obj).count()
        sim_count = SIMCard.objects.filter(proveedor=obj).count()
        otros_count = Otros.objects.filter(proveedor=obj).count()
        
        return gps_count + sim_count + otros_count
    
    def validate_ruc(self, value):
        """
        Validación personalizada para RUC peruano
        """
        try:
            validate_ruc_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                "El RUC debe ser válido según el algoritmo peruano de verificación"
            )
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = Proveedor.objects.filter(ruc=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un proveedor con este RUC"
            )
        
        return value
    
    def validate_celular(self, value):
        """
        Validación personalizada para celular peruano
        """
        try:
            validate_celular_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                "El celular debe ser un número peruano válido (9 dígitos, iniciando con 9)"
            )
        
        return value
    
    def validate_nombre(self, value):
        """
        Validación para nombre no vacío y longitud mínima
        """
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres"
            )
        
        return value.strip()
    
    def validate_contacto(self, value):
        """
        Validación para contacto no vacío
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El contacto debe tener al menos 2 caracteres"
            )
        
        return value.strip()
    
    def validate_correo(self, value):
        """
        Validación personalizada para email único
        """
        # Verificar unicidad excluyendo la instancia actual
        queryset = Proveedor.objects.filter(correo=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un proveedor con este correo electrónico"
            )
        
        return value


class UnidadSerializer(serializers.ModelSerializer):
    """
    Serializer para unidades vehiculares con validaciones personalizadas
    Incluye validación de placa peruana y relación con cliente
    """
    cliente_info = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    servicios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unidad
        fields = [
            'id', 'tipo', 'tipo_display', 'placa', 'marca', 'modelo', 
            'serie', 'cliente', 'cliente_info', 'is_active', 
            'servicios_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'cliente_info', 
            'tipo_display', 'servicios_count'
        ]
    
    def get_cliente_info(self, obj):
        """
        Información básica del cliente propietario
        """
        return {
            'id': obj.cliente.id,
            'nombre': obj.cliente.nombre,
            'ruc': obj.cliente.ruc
        }
    
    def get_servicios_count(self, obj):
        """
        Cuenta el número de servicios realizados en esta unidad
        """
        from services.models import Servicio
        return Servicio.objects.filter(unidad=obj).count()
    
    def validate_placa(self, value):
        """
        Validación personalizada para placa peruana
        """
        try:
            validate_placa_peruana(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                "La placa debe tener un formato peruano válido (ABC-123 o XYZ-1234)"
            )
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = Unidad.objects.filter(placa=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una unidad con esta placa"
            )
        
        return value.upper()  # Convertir a mayúsculas
    
    def validate_serie(self, value):
        """
        Validación para número de serie único
        """
        # Verificar unicidad excluyendo la instancia actual
        queryset = Unidad.objects.filter(serie=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una unidad con este número de serie"
            )
        
        return value.upper()  # Convertir a mayúsculas
    
    def validate_marca(self, value):
        """
        Validación para marca no vacía
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "La marca debe tener al menos 2 caracteres"
            )
        
        return value.strip().title()  # Formato título
    
    def validate_modelo(self, value):
        """
        Validación para modelo no vacío
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El modelo debe tener al menos 2 caracteres"
            )
        
        return value.strip().title()  # Formato título
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto
        """
        # Validar que el cliente existe y está activo
        if 'cliente' in attrs and attrs['cliente'] is not None:
            cliente = attrs['cliente']
            if not cliente.is_active:
                raise serializers.ValidationError({
                    'cliente': "El cliente seleccionado no está activo"
                })
        
        return attrs


class ClienteBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información del cliente en otras entidades
    """
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'ruc']
        read_only_fields = ['id', 'nombre', 'ruc']


class UnidadBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información de la unidad en otros módulos
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    
    class Meta:
        model = Unidad
        fields = ['id', 'placa', 'marca', 'modelo', 'cliente_nombre']
        read_only_fields = ['id', 'placa', 'marca', 'modelo', 'cliente_nombre']