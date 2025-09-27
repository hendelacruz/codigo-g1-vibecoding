from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import GPS, SIMCard, Otros
from entities.models import Proveedor, Cliente
from todoapi.utils.validators import validate_imei, validate_icc


class ProveedorBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información del proveedor en inventario
    """
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'ruc']
        read_only_fields = ['id', 'nombre', 'ruc']


class ClienteBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información del cliente en inventario
    """
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'ruc', 'celular']
        read_only_fields = ['id', 'nombre', 'ruc', 'celular']


class GPSSerializer(serializers.ModelSerializer):
    """
    Serializer para dispositivos GPS con validaciones personalizadas.
    
    Incluye validación de IMEI único, estado de asignación y proceso operativo.
    La nueva estructura separa el estado de asignación (asignado/no_asignado) 
    del proceso operativo (disponible, dañado, en_reparacion, etc.).
    """
    proveedor_info = ProveedorBasicSerializer(source='proveedor', read_only=True)
    cliente_info = ClienteBasicSerializer(source='cliente', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    proceso_display = serializers.CharField(source='get_proceso_display', read_only=True)
    estado_info = serializers.ReadOnlyField()
    
    class Meta:
        model = GPS
        fields = [
            'id', 'fecha_compra', 'imei', 'marca', 'modelo', 
            'numero_factura', 'proveedor', 'proveedor_info', 
            'cliente', 'cliente_info', 'estado', 'estado_display',
            'proceso', 'proceso_display', 'estado_info', 'is_active',
            'precio_compra', 'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'proveedor_info', 
            'cliente_info', 'estado_display', 'proceso_display', 'estado_info'
        ]
    
    def validate_imei(self, value):
        """
        Validación personalizada para IMEI único y formato correcto
        """
        # Validar formato IMEI usando la función personalizada
        try:
            validate_imei(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = GPS.objects.filter(imei=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un dispositivo GPS con este IMEI"
            )
        
        return value
    
    def validate_numero_factura(self, value):
        """
        Validación para número de factura único por proveedor
        """
        # Obtener el proveedor del contexto
        proveedor_id = None
        if self.instance:
            # En actualizaciones, usar el proveedor actual o el nuevo si se está cambiando
            proveedor_id = self.instance.proveedor.id
            if 'proveedor' in self.initial_data:
                proveedor_id = self.initial_data['proveedor']
        else:
            # En creaciones, obtener el proveedor de los datos iniciales
            if 'proveedor' in self.initial_data:
                proveedor_id = self.initial_data['proveedor']
        
        if proveedor_id:
            try:
                proveedor = Proveedor.objects.get(pk=proveedor_id)
                
                # Construir la consulta base
                queryset = GPS.objects.filter(
                    numero_factura=value, 
                    proveedor=proveedor
                )
                
                # En actualizaciones, excluir la instancia actual
                if self.instance:
                    queryset = queryset.exclude(pk=self.instance.pk)
                
                if queryset.exists():
                    raise serializers.ValidationError(
                        f"Ya existe una factura {value} para el proveedor {proveedor.nombre}"
                    )
            except Proveedor.DoesNotExist:
                # Si el proveedor no existe, la validación del campo proveedor se encargará
                pass
        
        return value
    
    def validate_precio_compra(self, value):
        """
        Validación para precio de compra positivo
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El precio de compra debe ser mayor a 0"
            )
        return value
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto para GPS.
        
        Incluye validaciones de proveedor, cliente, estado y proceso.
        Verifica la consistencia entre estado de asignación y cliente.
        """
        # Validar que el proveedor existe y está activo
        if 'proveedor' in attrs:
            proveedor = attrs['proveedor']
            if not proveedor.is_active:
                raise serializers.ValidationError({
                    'proveedor': "El proveedor seleccionado no está activo"
                })
        
        # Validar que el cliente existe y está activo (si se proporciona)
        if 'cliente' in attrs and attrs['cliente'] is not None:
            cliente = attrs['cliente']
            if not cliente.is_active:
                raise serializers.ValidationError({
                    'cliente': "El cliente seleccionado no está activo"
                })
        
        # Validar consistencia entre estado y cliente
        estado = attrs.get('estado', getattr(self.instance, 'estado', None))
        cliente = attrs.get('cliente', getattr(self.instance, 'cliente', None))
        
        if estado == 'asignado' and cliente is None:
            raise serializers.ValidationError({
                'cliente': "Un GPS con estado 'asignado' debe tener un cliente asociado"
            })
        
        if estado == 'no_asignado' and cliente is not None:
            raise serializers.ValidationError({
                'estado': "Un GPS con cliente asociado debe tener estado 'asignado'"
            })
        
        # Validar que el proceso es válido para GPS asignados
        proceso = attrs.get('proceso', getattr(self.instance, 'proceso', None))
        if estado == 'asignado' and proceso in ['en_desarrollo', 'descontinuado']:
            raise serializers.ValidationError({
                'proceso': "Un GPS asignado no puede tener proceso 'en_desarrollo' o 'descontinuado'"
            })
        
        return attrs


class SIMCardSerializer(serializers.ModelSerializer):
    """
    Serializer para tarjetas SIM con validaciones personalizadas.
    
    Incluye validación de ICC único, número de chip y gestión de estado activo/inactivo.
    La nueva estructura incluye asignación a clientes y separación entre estado y proceso.
    """
    proveedor_info = ProveedorBasicSerializer(source='proveedor', read_only=True)
    cliente_info = ClienteBasicSerializer(source='cliente', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    proceso_display = serializers.CharField(source='get_proceso_display', read_only=True)
    estado_info = serializers.ReadOnlyField()
    
    class Meta:
        model = SIMCard
        fields = [
            'id', 'fecha_compra', 'numero_factura', 'numero_chip', 
            'icc', 'proveedor', 'proveedor_info', 'cliente', 'cliente_info',
            'estado', 'estado_display', 'proceso', 'proceso_display', 
            'estado_info', 'is_active', 'plan', 'precio_compra', 
            'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'proveedor_info', 
            'cliente_info', 'estado_display', 'proceso_display', 'estado_info'
        ]
    
    def validate_icc(self, value):
        """
        Validación personalizada para ICC único y formato correcto
        """
        # Validar formato ICC usando la función personalizada
        try:
            validate_icc(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = SIMCard.objects.filter(icc=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una tarjeta SIM con este ICC"
            )
        
        return value
    
    def validate_numero_chip(self, value):
        """
        Validación para número de chip único
        """
        # Verificar unicidad excluyendo la instancia actual
        queryset = SIMCard.objects.filter(numero_chip=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una tarjeta SIM con este número de chip"
            )
        
        return value
    
    def validate_precio_compra(self, value):
        """
        Validación para precio de compra positivo
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El precio de compra debe ser mayor a 0"
            )
        return value
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto para SIMCard.
        
        Incluye validaciones de proveedor, cliente, estado y proceso.
        Verifica la consistencia entre estado de asignación y cliente.
        """
        # Validar que el proveedor existe y está activo
        if 'proveedor' in attrs:
            proveedor = attrs['proveedor']
            if not proveedor.is_active:
                raise serializers.ValidationError({
                    'proveedor': "El proveedor seleccionado no está activo"
                })
        
        # Validar que el cliente existe y está activo (si se proporciona)
        if 'cliente' in attrs and attrs['cliente'] is not None:
            cliente = attrs['cliente']
            if not cliente.is_active:
                raise serializers.ValidationError({
                    'cliente': "El cliente seleccionado no está activo"
                })
        
        # Validar consistencia entre estado y cliente
        estado = attrs.get('estado', getattr(self.instance, 'estado', None))
        cliente = attrs.get('cliente', getattr(self.instance, 'cliente', None))
        
        if estado == 'asignado' and cliente is None:
            raise serializers.ValidationError({
                'cliente': "Una SIM con estado 'asignado' debe tener un cliente asociado"
            })
        
        if estado == 'no_asignado' and cliente is not None:
            raise serializers.ValidationError({
                'estado': "Una SIM con cliente asociado debe tener estado 'asignado'"
            })
        
        # Validar que el proceso es válido para SIMs asignadas
        proceso = attrs.get('proceso', getattr(self.instance, 'proceso', None))
        if estado == 'asignado' and proceso in ['en_desarrollo', 'descontinuado']:
            raise serializers.ValidationError({
                'proceso': "Una SIM asignada no puede tener proceso 'en_desarrollo' o 'descontinuado'"
            })
        
        return attrs


class OtrosSerializer(serializers.ModelSerializer):
    """
    Serializer para otros productos del inventario
    Incluye validaciones de stock y cálculos automáticos
    """
    proveedor_info = ProveedorBasicSerializer(source='proveedor', read_only=True)
    precio_total_calculado = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Otros
        fields = [
            'id', 'fecha_compra', 'numero_factura', 'cantidad', 
            'descripcion', 'proveedor', 'proveedor_info', 'categoria',
            'precio_unitario', 'precio_total', 'precio_total_calculado',
            'stock_actual', 'stock_minimo', 'stock_status',
            'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'proveedor_info', 
            'precio_total_calculado', 'stock_status'
        ]
    
    def get_precio_total_calculado(self, obj):
        """
        Calcula el precio total basado en cantidad y precio unitario
        """
        if obj.cantidad and obj.precio_unitario:
            return obj.cantidad * obj.precio_unitario
        return None
    
    def get_stock_status(self, obj):
        """
        Determina el estado del stock
        """
        if obj.stock_actual <= 0:
            return 'sin_stock'
        elif obj.stock_actual <= obj.stock_minimo:
            return 'stock_bajo'
        else:
            return 'stock_normal'
    
    def validate_cantidad(self, value):
        """
        Validación para cantidad positiva
        """
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad debe ser mayor a 0"
            )
        return value
    
    def validate_precio_unitario(self, value):
        """
        Validación para precio unitario positivo
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El precio unitario debe ser mayor a 0"
            )
        return value
    
    def validate_precio_total(self, value):
        """
        Validación para precio total positivo
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El precio total debe ser mayor a 0"
            )
        return value
    
    def validate_stock_actual(self, value):
        """
        Validación para stock actual no negativo
        """
        if value < 0:
            raise serializers.ValidationError(
                "El stock actual no puede ser negativo"
            )
        return value
    
    def validate_stock_minimo(self, value):
        """
        Validación para stock mínimo no negativo
        """
        if value < 0:
            raise serializers.ValidationError(
                "El stock mínimo no puede ser negativo"
            )
        return value
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto
        """
        # Validar que el proveedor existe y está activo
        if 'proveedor' in attrs:
            proveedor = attrs['proveedor']
            if not proveedor.is_active:
                raise serializers.ValidationError({
                    'proveedor': "El proveedor seleccionado no está activo"
                })
        
        # Validar coherencia entre precio total y precio unitario/cantidad
        precio_unitario = attrs.get('precio_unitario')
        precio_total = attrs.get('precio_total')
        cantidad = attrs.get('cantidad')
        
        if precio_unitario and precio_total and cantidad:
            precio_calculado = precio_unitario * cantidad
            # Permitir una diferencia mínima por redondeo
            if abs(precio_total - precio_calculado) > 0.01:
                raise serializers.ValidationError({
                    'precio_total': f"El precio total ({precio_total}) no coincide con el cálculo (cantidad: {cantidad} × precio unitario: {precio_unitario} = {precio_calculado})"
                })
        
        return attrs
    
    def create(self, validated_data):
        """
        Crear producto con cálculo automático de precio total si no se proporciona
        """
        # Calcular precio total automáticamente si no se proporciona
        if not validated_data.get('precio_total') and validated_data.get('precio_unitario') and validated_data.get('cantidad'):
            validated_data['precio_total'] = validated_data['precio_unitario'] * validated_data['cantidad']
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Actualizar producto con recálculo automático si es necesario
        """
        # Recalcular precio total si se actualizan precio unitario o cantidad
        if ('precio_unitario' in validated_data or 'cantidad' in validated_data) and not validated_data.get('precio_total'):
            precio_unitario = validated_data.get('precio_unitario', instance.precio_unitario)
            cantidad = validated_data.get('cantidad', instance.cantidad)
            
            if precio_unitario and cantidad:
                validated_data['precio_total'] = precio_unitario * cantidad
        
        return super().update(instance, validated_data)