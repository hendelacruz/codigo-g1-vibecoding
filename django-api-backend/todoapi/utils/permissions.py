"""
Sistema de permisos personalizado para la API Django.
Incluye decoradores y clases de permisos basados en roles de usuario.
"""

from functools import wraps
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Definición de roles del sistema
ROLES = {
    'ADMIN': 'ADMIN',
    'administrador': 'administrador',
    'supervisor': 'supervisor',
    'tecnico': 'tecnico'
}

# Permisos por rol
ROLE_PERMISSIONS = {
    'ADMIN': {
        'can_create': True,
        'can_read': True,
        'can_update': True,
        'can_delete': True,
        'can_manage_users': True,
        'can_view_reports': True,
        'can_manage_inventory': True,
        'can_manage_services': True,
        'can_manage_sales': True
    },
    'administrador': {
        'can_create': True,
        'can_read': True,
        'can_update': True,
        'can_delete': True,
        'can_manage_users': True,
        'can_view_reports': True,
        'can_manage_inventory': True,
        'can_manage_services': True,
        'can_manage_sales': True
    },
    'supervisor': {
        'can_create': True,
        'can_read': True,
        'can_update': True,
        'can_delete': False,  # Supervisores no pueden eliminar
        'can_manage_users': True,  # Pueden gestionar usuarios
        'can_view_reports': True,
        'can_manage_inventory': True,
        'can_manage_services': True,
        'can_manage_sales': True
    },
    'tecnico': {
        'can_create': True,  # Solo en servicios
        'can_read': True,
        'can_update': True,  # Solo en servicios
        'can_delete': False,
        'can_manage_users': False,
        'can_view_reports': False,
        'can_manage_inventory': False,  # Solo lectura
        'can_manage_services': True,  # Acceso completo
        'can_manage_sales': False  # Solo lectura
    }
}


def require_role(allowed_roles):
    """
    Decorador para requerir roles específicos en vistas basadas en funciones.
    
    Args:
        allowed_roles (list): Lista de roles permitidos
        
    Usage:
        @require_role(['administrador', 'supervisor'])
        def my_view(request):
            return Response({'message': 'Success'})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Autenticación requerida'}, 
                    status=401
                )
            
            # Check if user has a role
            if not hasattr(request.user, 'rol') or not request.user.rol:
                return JsonResponse(
                    {'error': 'Usuario sin rol asignado'}, 
                    status=403
                )
            
            # Check if user's role is in allowed roles
            user_role = request.user.rol.nombre
            if user_role not in allowed_roles:
                return JsonResponse({
                    'error': 'Permisos insuficientes',
                    'required_roles': allowed_roles,
                    'user_role': user_role
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission_name):
    """
    Decorador para requerir permisos específicos basados en el rol del usuario.
    
    Args:
        permission_name (str): Nombre del permiso requerido
        
    Usage:
        @require_permission('can_delete')
        def delete_view(request):
            return Response({'message': 'Deleted'})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Autenticación requerida'}, 
                    status=401
                )
            
            if not hasattr(request.user, 'rol') or not request.user.rol:
                return JsonResponse(
                    {'error': 'Usuario sin rol asignado'}, 
                    status=403
                )
            
            user_role = request.user.rol.nombre
            role_permissions = ROLE_PERMISSIONS.get(user_role, {})
            
            if not role_permissions.get(permission_name, False):
                return JsonResponse({
                    'error': f'Permiso insuficiente: {permission_name}',
                    'user_role': user_role
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class IsAuthenticated(permissions.BasePermission):
    """
    Permiso que requiere que el usuario esté autenticado.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite acceso completo a administradores y solo lectura a otros.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        # Write permissions only for administrators
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        return request.user.rol.nombre == 'administrador'


class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Permiso que permite acceso a administradores y supervisores.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        # Roles permitidos: administradores y supervisores
        allowed_roles = [
            'ADMIN',           # Administrador del sistema con acceso completo
            'administrador',   # Acceso completo al sistema
            'supervisor',      # Supervisor con acceso a gestión de usuarios y reportes
        ]
        
        return request.user.rol.nombre in allowed_roles


class IsAdminOnly(permissions.BasePermission):
    """
    Permiso que permite acceso solo a administradores.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        # Accept both 'administrador' and 'ADMIN' role names
        return request.user.rol.nombre.lower() in ['administrador', 'admin']


class IsTechnicianForServices(permissions.BasePermission):
    """
    Permiso especial para técnicos en el módulo de servicios.
    Permite acceso completo a servicios, solo lectura en otros módulos.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        user_role = request.user.rol.nombre
        
        # Administradores y operadores tienen acceso completo
        if user_role in ['administrador', 'supervisor']:
            return True
            
        # Técnicos tienen acceso especial
        if user_role == 'tecnico':
            # Determinar si es un ViewSet de servicios
            view_name = view.__class__.__name__.lower()
            if 'servicio' in view_name or 'tipotrabajo' in view_name:
                return True  # Acceso completo a servicios
            else:
                # Solo lectura en otros módulos
                return request.method in permissions.SAFE_METHODS
                
        return False


class CanDeletePermission(permissions.BasePermission):
    """
    Permiso para operaciones de eliminación.
    Solo administradores pueden eliminar registros.
    """
    def has_permission(self, request, view):
        if request.method != 'DELETE':
            return True  # No es una operación de eliminación
            
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        return request.user.rol.nombre == 'administrador'


class RoleBasedPermission(permissions.BasePermission):
    """
    Permiso basado en roles con configuración flexible.
    """
    def __init__(self, allowed_roles=None, required_permission=None):
        self.allowed_roles = allowed_roles or []
        self.required_permission = required_permission
        
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
            
        user_role = request.user.rol.nombre
        
        # Check role-based access
        if self.allowed_roles and user_role not in self.allowed_roles:
            return False
            
        # Check permission-based access
        if self.required_permission:
            role_permissions = ROLE_PERMISSIONS.get(user_role, {})
            if not role_permissions.get(self.required_permission, False):
                return False
                
        return True


def get_user_permissions(user):
    """
    Obtiene los permisos del usuario basado en su rol.
    
    Args:
        user: Usuario autenticado
        
    Returns:
        dict: Diccionario con los permisos del usuario
    """
    if not user.is_authenticated:
        return {}
        
    if not hasattr(user, 'rol') or not user.rol:
        return {}
        
    user_role = user.rol.nombre
    return ROLE_PERMISSIONS.get(user_role, {})


def has_permission(user, permission_name):
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user: Usuario a verificar
        permission_name (str): Nombre del permiso
        
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    permissions = get_user_permissions(user)
    return permissions.get(permission_name, False)


def get_allowed_actions(user, module_name=None):
    """
    Obtiene las acciones permitidas para un usuario en un módulo específico.
    
    Args:
        user: Usuario autenticado
        module_name (str): Nombre del módulo (opcional)
        
    Returns:
        list: Lista de acciones permitidas
    """
    if not user.is_authenticated:
        return []
        
    if not hasattr(user, 'rol') or not user.rol:
        return []
        
    user_role = user.rol.nombre
    permissions = ROLE_PERMISSIONS.get(user_role, {})
    
    actions = []
    
    if permissions.get('can_read', False):
        actions.append('read')
        
    if permissions.get('can_create', False):
        # Técnicos solo pueden crear en servicios
        if user_role == 'tecnico' and module_name and 'service' not in module_name.lower():
            pass  # No agregar create
        else:
            actions.append('create')
            
    if permissions.get('can_update', False):
        # Técnicos solo pueden actualizar en servicios
        if user_role == 'tecnico' and module_name and 'service' not in module_name.lower():
            pass  # No agregar update
        else:
            actions.append('update')
            
    if permissions.get('can_delete', False):
        actions.append('delete')
        
    return actions