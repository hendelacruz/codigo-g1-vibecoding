from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import CustomUser, Role
from todoapi.utils.validators import (
    validate_dni_peruano, 
    validate_celular_peruano,
    validate_placa_peruana
)
from todoapi.utils.security_mixins import (
    SecurityValidationMixin, 
    AuditLogMixin,
    DataSanitizationMixin
)


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Role
    """
    class Meta:
        model = Role
        fields = ['id', 'nombre', 'descripcion', 'permisos', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CustomUserSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer para el modelo CustomUser con validaciones personalizadas
    Incluye validaciones de DNI, licencia, celular y manejo seguro de contraseñas
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Contraseña del usuario (mínimo 8 caracteres)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirmación de contraseña"
    )
    rol_nombre = serializers.CharField(
        source='rol.nombre', 
        read_only=True,
        help_text="Nombre del rol asignado"
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'dni', 'licencia', 'celular', 'rol', 'rol_nombre', 'is_active',
            'password', 'password_confirm', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rol_nombre']
        
    def validate_dni(self, value):
        """
        Validación personalizada para DNI peruano
        """
        try:
            validate_dni_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Verificar unicidad excluyendo la instancia actual en actualizaciones
        queryset = CustomUser.objects.filter(dni=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este DNI"
            )
        
        return value
    
    def validate_licencia(self, value):
        """
        Validación personalizada para licencia de conducir
        """
        if value:  # Solo validar si se proporciona (campo opcional)
            # Validación de formato: 1 letra seguida de 8 dígitos
            import re
            if not re.match(r'^[A-Z]\d{8}$', value):
                raise serializers.ValidationError(
                    "La licencia debe tener el formato: 1 letra seguida de 8 dígitos (ej: A12345678)"
                )
            
            # Verificar unicidad excluyendo la instancia actual
            queryset = CustomUser.objects.filter(licencia=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe un usuario con esta licencia"
                )
        
        return value
    
    def validate_celular(self, value):
        """
        Validación personalizada para celular peruano
        """
        # Convertir PhoneNumber a string para validación
        celular_str = str(value.national_number) if hasattr(value, 'national_number') else str(value)
        
        try:
            validate_celular_peruano(celular_str)
        except ValidationError as e:
            raise serializers.ValidationError(str(e.message))
        
        # Verificar unicidad excluyendo la instancia actual
        queryset = CustomUser.objects.filter(celular=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este número de celular"
            )
        
        return value
    
    def validate_email(self, value):
        """
        Validación personalizada para email único
        """
        # Verificar unicidad excluyendo la instancia actual
        queryset = CustomUser.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este email"
            )
        
        return value
        
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto
        """
        # Validar contraseñas coincidentes
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError({
                    'password_confirm': "Las contraseñas no coinciden"
                })
        
        # Validar que el rol existe y está activo
        if 'rol' in attrs:
            rol = attrs['rol']
            if not rol.is_active:
                raise serializers.ValidationError({
                    'rol': "El rol seleccionado no está activo"
                })
        
        return attrs
    
    def create(self, validated_data):
        """
        Crear usuario con contraseña hasheada y validaciones
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        # Crear usuario
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """
        Actualizar usuario, manejando contraseña si se proporciona
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Actualizar contraseña si se proporciona (cifrada)
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class UserToggleActiveSerializer(SecurityValidationMixin, AuditLogMixin, serializers.Serializer):
    """
    Serializer para activar/desactivar usuarios
    Permite cambiar el estado is_active de un usuario
    """
    is_active = serializers.BooleanField(
        required=True,
        help_text="Estado activo del usuario (True para activar, False para desactivar)"
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Razón opcional para el cambio de estado"
    )
    
    def validate(self, attrs):
        """
        Validación personalizada para el cambio de estado
        """
        attrs = super().validate(attrs)
        
        # Obtener el usuario desde el contexto
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("Usuario no encontrado en el contexto")
        
        # Verificar que el estado sea diferente al actual
        if user.is_active == attrs['is_active']:
            action = "activado" if attrs['is_active'] else "desactivado"
            raise serializers.ValidationError(f"El usuario ya está {action}")
        
        # No permitir desactivar al último administrador activo
        if not attrs['is_active'] and user.rol and user.rol.nombre.lower() in ['administrador', 'admin']:
            active_admins = CustomUser.objects.filter(
                rol__nombre__iregex=r'^(administrador|admin)$',
                is_active=True
            ).exclude(id=user.id).count()
            
            if active_admins == 0:
                raise serializers.ValidationError(
                    "No se puede desactivar al último administrador del sistema"
                )
        
        return attrs
    
    def save(self):
        """
        Actualiza el estado del usuario
        """
        user = self.context['user']
        is_active = self.validated_data['is_active']
        reason = self.validated_data.get('reason', '')
        
        # Actualizar el estado
        user.is_active = is_active
        user.save()
        
        # Log de auditoría
        action = "ACTIVATE" if is_active else "DEACTIVATE"
        self._log_audit_action(
            action=f'USER_{action}',
            instance=user,
            new_data={
                'is_active': is_active,
                'reason': reason,
                'changed_by': self.context['request'].user.username
            }
        )
        
        return user


class UserRegistrationSerializer(SecurityValidationMixin, AuditLogMixin, DataSanitizationMixin, serializers.ModelSerializer):
    """
    Serializer for public user registration
    Simplified version without admin-only fields like role assignment
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        validators=[validate_password],
        help_text="User password (minimum 8 characters)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Password confirmation"
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'dni', 'licencia', 'celular', 'password', 'password_confirm'
        ]
        
    def validate_dni(self, value):
        """
        Custom validation for Peruvian DNI
        """
        try:
            validate_dni_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Check uniqueness
        if CustomUser.objects.filter(dni=value).exists():
            raise serializers.ValidationError(
                "A user with this DNI already exists"
            )
        
        return value
    
    def validate_licencia(self, value):
        """
        Custom validation for driver's license
        """
        if value:  # Only validate if provided (optional field)
            # Format validation: 1 letter followed by 8 digits
            import re
            if not re.match(r'^[A-Z]\d{8}$', value):
                raise serializers.ValidationError(
                    "License must have the format: 1 letter followed by 8 digits (e.g: A12345678)"
                )
            
            # Check uniqueness
            if CustomUser.objects.filter(licencia=value).exists():
                raise serializers.ValidationError(
                    "A user with this license already exists"
                )
        
        return value
    
    def validate_celular(self, value):
        """
        Custom validation for Peruvian phone number
        """
        try:
            validate_celular_peruano(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Check uniqueness
        if CustomUser.objects.filter(celular=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists"
            )
        
        return value
    
    def validate_email(self, value):
        """
        Custom validation for email uniqueness
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists"
            )
        
        return value
    
    def validate(self, attrs):
        """
        Validate password confirmation and apply security validations
        """
        # Apply security validations from mixin
        attrs = super().validate(attrs)
        
        # Password confirmation validation
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Password confirmation does not match'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with default role (cliente)
        """
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Hash the password
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        
        # Assign default role (cliente)
        try:
            default_role = Role.objects.get(nombre='cliente')
            validated_data['rol'] = default_role
        except Role.DoesNotExist:
            # If cliente role doesn't exist, create user without role
            # Admin can assign role later
            pass
        
        # Create user
        user = CustomUser.objects.create(**validated_data)
        
        # Log the creation for audit
        self.log_action('CREATE', user, 'User registered successfully')
        
        return user
    
    def update(self, instance, validated_data):
        """
        Actualizar usuario, manejando contraseña si se proporciona
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Actualizar contraseña si se proporciona
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT
    Incluye información adicional del usuario en el token
    """
    
    def validate(self, attrs):
        """
        Valida las credenciales y agrega información del usuario
        """
        data = super().validate(attrs)
        
        # Agregar información del usuario al response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'dni': self.user.dni,
            'rol': {
                'id': self.user.rol.id,
                'nombre': self.user.rol.nombre,
                'permisos': self.user.rol.permisos
            } if self.user.rol else None,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        return data

    @classmethod
    def get_token(cls, user):
        """
        Personaliza el contenido del token JWT
        """
        token = super().get_token(user)
        
        # Agregar claims personalizados
        token['username'] = user.username
        token['email'] = user.email
        token['dni'] = user.dni
        token['rol_id'] = user.rol.id if user.rol else None
        token['rol_nombre'] = user.rol.nombre if user.rol else None
        token['permisos'] = user.rol.permisos if user.rol else {}
        
        return token


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login con username/email y password
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Valida las credenciales de login
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Intentar autenticar con username o email
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            # Si no funciona con username, intentar con email
            if not user:
                try:
                    user_by_email = CustomUser.objects.get(email=username)
                    user = authenticate(
                        request=self.context.get('request'),
                        username=user_by_email.username,
                        password=password
                    )
                except CustomUser.DoesNotExist:
                    pass

            if not user:
                raise serializers.ValidationError(
                    'No se pudo autenticar con las credenciales proporcionadas.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'La cuenta de usuario está desactivada.'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir "username" y "password".'
            )


class ChangePasswordSerializer(SecurityValidationMixin, AuditLogMixin, serializers.Serializer):
    """
    Serializer para cambio de contraseña con validaciones de seguridad
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """
        Valida que la contraseña actual sea correcta
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value

    def validate(self, attrs):
        """
        Valida que las nuevas contraseñas coincidan
        """
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las nuevas contraseñas no coinciden.'
            })

        # Validar la nueva contraseña
        validate_password(new_password)
        
        return attrs

    def save(self):
        """
        Guarda la nueva contraseña
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user