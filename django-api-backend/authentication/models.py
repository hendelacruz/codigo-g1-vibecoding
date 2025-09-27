from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField


class Role(models.Model):
    """
    Modelo para gestionar roles de usuario con permisos granulares
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador del Sistema'),
        ('administrador', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('tecnico', 'Técnico'),
    ]
    
    nombre = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        unique=True,
        help_text="Nombre del rol del usuario"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del rol y sus responsabilidades"
    )
    permisos = models.JSONField(
        default=dict,
        help_text="Permisos específicos del rol en formato JSON"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si el rol está activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.get_nombre_display()}"


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema logístico
    Extiende AbstractUser con campos específicos del negocio
    """
    
    # Validador para DNI peruano (8 dígitos)
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener exactamente 8 dígitos'
    )
    
    # Validador para licencia de conducir
    licencia_validator = RegexValidator(
        regex=r'^[A-Z]\d{8}$',
        message='La licencia debe tener el formato: 1 letra seguida de 8 dígitos (ej: A12345678)'
    )
    
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[dni_validator],
        help_text="Documento Nacional de Identidad (8 dígitos)"
    )
    licencia = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        validators=[licencia_validator],
        help_text="Licencia de conducir (formato: A12345678)"
    )
    celular = PhoneNumberField(
        region='PE',
        help_text="Número de celular con código de país"
    )
    rol = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='usuarios',
        help_text="Rol asignado al usuario"
    )
    
    # Campos adicionales de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Última dirección IP de inicio de sesión"
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_permission(self, permission_key):
        """
        Verifica si el usuario tiene un permiso específico
        """
        if not self.is_active or not self.rol.is_active:
            return False
        
        # Los administradores tienen todos los permisos
        if self.rol.nombre == 'administrador':
            return True
        
        # Verificar permisos específicos del rol
        return self.rol.permisos.get(permission_key, False)
    
    def get_permissions(self):
        """Retorna todos los permisos del usuario"""
        if not self.is_active or not self.rol.is_active:
            return {}
        
        return self.rol.permisos
    
    @property
    def is_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol.nombre in ['administrador', 'ADMIN'] if self.rol else False
    
    @property
    def is_supervisor(self):
        """Verifica si el usuario es supervisor"""
        return self.rol.nombre == 'supervisor' if self.rol else False
    
    @property
    def is_tecnico(self):
        """Verifica si el usuario es técnico"""
        return self.rol.nombre == 'tecnico' if self.rol else False
