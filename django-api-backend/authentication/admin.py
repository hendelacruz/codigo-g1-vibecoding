from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Role
    """
    list_display = ['nombre', 'descripcion', 'is_active', 'created_at']
    list_filter = ['nombre', 'is_active', 'created_at']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'is_active')
        }),
        (_('Permisos'), {
            'fields': ('permisos',),
            'classes': ('collapse',)
        }),
        (_('Fechas importantes'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para el modelo CustomUser
    Extiende UserAdmin para incluir campos personalizados
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'dni', 'rol', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'rol', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'dni']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        (_('Información Personal Adicional'), {
            'fields': ('dni', 'licencia', 'celular', 'rol')
        }),
        (_('Información de Auditoría'), {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name', 'email', 'dni', 'celular', 'rol')
        }),
        (_('Información Adicional'), {
            'fields': ('licencia',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']
    
    def get_readonly_fields(self, request, obj=None):
        """
        Hace que ciertos campos sean de solo lectura después de la creación
        """
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editando un usuario existente
            readonly_fields.append('dni')  # DNI no se puede cambiar después de creado
        return readonly_fields
