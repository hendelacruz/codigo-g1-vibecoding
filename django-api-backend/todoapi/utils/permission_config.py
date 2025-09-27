"""
Configuración centralizada de permisos por ViewSet y roles.
Define qué acciones puede realizar cada rol en cada módulo del sistema.
"""

from rest_framework import permissions
from .permissions import (
    IsAdminOrReadOnly, IsAdminOrSupervisor, IsAdminOnly,
    IsTechnicianForServices, CanDeletePermission
)


# Configuración de permisos por módulo y acción
PERMISSION_CONFIG = {
    # Configuración de permisos para usuarios
    'customuser': {
        'list': ['administrador', 'supervisor'],
        'retrieve': ['administrador', 'supervisor'],
        'create': ['administrador'],
        'update': ['administrador'],
        'partial_update': ['administrador'],
        'destroy': ['administrador'],
        'change_password': ['administrador', 'supervisor', 'tecnico'],  # Solo su propia contraseña
        'reset_password': ['administrador'],
    },
    
    # Configuración de permisos para roles
    'rol': {
        'list': ['administrador', 'supervisor'],
        'retrieve': ['administrador', 'supervisor'],
        'create': ['administrador'],
        'update': ['administrador'],
        'partial_update': ['administrador'],
        'destroy': ['administrador'],
    },
    
    # Configuración de permisos para GPS
    'gps': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'assign_to_service': ['administrador', 'supervisor', 'tecnico'],
        'mark_available': ['administrador', 'supervisor', 'tecnico'],
    },
    
    # Configuración de permisos para SIM Cards
    'simcard': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'assign_to_service': ['administrador', 'supervisor', 'tecnico'],
        'mark_available': ['administrador', 'supervisor', 'tecnico'],
    },
    
    # Configuración de permisos para otros recursos
    'otros': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
    },
    
    # Configuración de permisos para clientes
    'cliente': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'get_units': ['administrador', 'supervisor', 'tecnico'],
        'get_services': ['administrador', 'supervisor', 'tecnico'],
    },
    
    # Configuración de permisos para proveedores
    'proveedor': {
        'list': ['administrador', 'supervisor'],
        'retrieve': ['administrador', 'supervisor'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'get_products': ['administrador', 'supervisor'],
    },
    
    # Configuración de permisos para unidades
    'unidad': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'get_services': ['administrador', 'supervisor', 'tecnico'],
        'get_gps_history': ['administrador', 'supervisor', 'tecnico'],
    },
    
    # Configuración de permisos para tipos de trabajo
    'tipotrabajo': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
    },
    
    # Configuración de permisos para servicios
    'servicio': {
        'list': ['administrador', 'supervisor', 'tecnico'],
        'retrieve': ['administrador', 'supervisor', 'tecnico'],
        'create': ['administrador', 'supervisor', 'tecnico'],
        'update': ['administrador', 'supervisor', 'tecnico'],
        'partial_update': ['administrador', 'supervisor', 'tecnico'],
        'destroy': ['administrador'],
        'assign_technician': ['administrador', 'supervisor'],
        'complete_service': ['administrador', 'supervisor', 'tecnico'],
        'cancel_service': ['administrador', 'supervisor'],
        'get_my_services': ['tecnico'],  # Solo técnicos ven sus servicios
    },
    
    # Configuración de permisos para ventas
    'ventas': {
        'list': ['administrador', 'supervisor'],
        'retrieve': ['administrador', 'supervisor'],
        'create': ['administrador', 'supervisor'],
        'update': ['administrador', 'supervisor'],
        'partial_update': ['administrador', 'supervisor'],
        'destroy': ['administrador'],
        'generate_invoice': ['administrador', 'supervisor'],
        'mark_paid': ['administrador', 'supervisor'],
        'get_monthly_report': ['administrador', 'supervisor'],
        'get_client_report': ['administrador', 'supervisor'],
    },
}


# Configuración de clases de permisos por ViewSet
VIEWSET_PERMISSION_CLASSES = {
    # ViewSets que requieren solo administradores
    'CustomUserViewSet': [permissions.IsAuthenticated, IsAdminOnly],
    'RolViewSet': [permissions.IsAuthenticated, IsAdminOnly],
    
    # ViewSets que requieren administradores o supervisores
    'GPSViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'SIMCardViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'OtrosViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    
    # ViewSets de entidades que requieren administradores o supervisores
    'ClienteViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'ProveedorViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'UnidadViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    
    # ViewSets de servicios
    'TipoTrabajoViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'ServicioViewSet': [permissions.IsAuthenticated, IsTechnicianForServices],
    
    # ViewSets de ventas
    'VentasViewSet': [permissions.IsAuthenticated, IsAdminOrSupervisor],
}


# Configuración de permisos especiales por acción
ACTION_PERMISSION_OVERRIDES = {
    # Acciones especiales que requieren permisos específicos
    'destroy': [permissions.IsAuthenticated, CanDeletePermission],
    
    # Acciones específicas de servicios para técnicos
    'get_my_services': [permissions.IsAuthenticated, IsTechnicianForServices],
    'complete_service': [permissions.IsAuthenticated, IsTechnicianForServices],
    
    # Acciones de gestión de contraseñas
    'change_password': [permissions.IsAuthenticated],  # Cualquier usuario autenticado
    'reset_password': [permissions.IsAuthenticated, IsAdminOnly],
    
    # Acciones de ventas e informes
    'generate_invoice': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'get_monthly_report': [permissions.IsAuthenticated, IsAdminOrSupervisor],
    'get_client_report': [permissions.IsAuthenticated, IsAdminOrSupervisor],
}


def get_permission_classes_for_viewset(viewset_name):
    """
    Obtiene las clases de permisos para un ViewSet específico.
    
    Args:
        viewset_name (str): Nombre del ViewSet
        
    Returns:
        list: Lista de clases de permisos
    """
    return VIEWSET_PERMISSION_CLASSES.get(
        viewset_name, 
        [permissions.IsAuthenticated, IsAdminOrReadOnly]
    )


def get_permission_classes_for_action(action_name, viewset_name=None):
    """
    Obtiene las clases de permisos para una acción específica.
    
    Args:
        action_name (str): Nombre de la acción
        viewset_name (str): Nombre del ViewSet (opcional)
        
    Returns:
        list: Lista de clases de permisos
    """
    # Verificar si hay override específico para la acción
    if action_name in ACTION_PERMISSION_OVERRIDES:
        return ACTION_PERMISSION_OVERRIDES[action_name]
    
    # Si no hay override, usar permisos del ViewSet
    if viewset_name:
        return get_permission_classes_for_viewset(viewset_name)
    
    # Permisos por defecto
    return [permissions.IsAuthenticated, IsAdminOrReadOnly]


def user_can_perform_action(user, module, action):
    """
    Verifica si un usuario puede realizar una acción específica en un módulo.
    
    Args:
        user: Usuario de Django
        module (str): Nombre del módulo
        action (str): Nombre de la acción
        
    Returns:
        bool: True si el usuario puede realizar la acción
    """
    if not user.is_authenticated:
        return False
    
    if not hasattr(user, 'rol') or not user.rol:
        return False
    
    user_role = user.rol.nombre
    module_config = PERMISSION_CONFIG.get(module.lower(), {})
    allowed_roles = module_config.get(action, [])
    
    return user_role in allowed_roles


def get_allowed_actions_for_user(user, module):
    """
    Obtiene todas las acciones que un usuario puede realizar en un módulo.
    
    Args:
        user: Usuario de Django
        module (str): Nombre del módulo
        
    Returns:
        list: Lista de acciones permitidas
    """
    if not user.is_authenticated:
        return []
    
    if not hasattr(user, 'rol') or not user.rol:
        return []
    
    user_role = user.rol.nombre
    module_config = PERMISSION_CONFIG.get(module.lower(), {})
    
    allowed_actions = []
    for action, allowed_roles in module_config.items():
        if user_role in allowed_roles:
            allowed_actions.append(action)
    
    return allowed_actions


def get_user_role_permissions(user):
    """
    Obtiene un resumen completo de los permisos del usuario por módulo.
    
    Args:
        user: Usuario de Django
        
    Returns:
        dict: Diccionario con permisos por módulo
    """
    if not user.is_authenticated:
        return {}
    
    if not hasattr(user, 'rol') or not user.rol:
        return {}
    
    permissions_summary = {}
    
    for module in PERMISSION_CONFIG.keys():
        permissions_summary[module] = get_allowed_actions_for_user(user, module)
    
    return permissions_summary


# Configuración de filtros por rol
ROLE_FILTERS = {
    'administrador': {
        # Administradores ven todo
        'filter_active_only': False,
        'filter_own_records': False,
    },
    'supervisor': {
        # Supervisores ven solo registros activos
        'filter_active_only': True,
        'filter_own_records': False,
    },
    'tecnico': {
        # Técnicos ven solo registros activos y algunos propios
        'filter_active_only': True,
        'filter_own_records': True,
        'own_record_modules': ['servicio'],  # Solo en servicios ven solo los suyos
    },
}


def get_queryset_filters_for_user(user, module):
    """
    Obtiene los filtros que se deben aplicar al queryset según el rol del usuario.
    
    Args:
        user: Usuario de Django
        module (str): Nombre del módulo
        
    Returns:
        dict: Filtros a aplicar
    """
    if not user.is_authenticated:
        return {'id__in': []}  # No mostrar nada
    
    if not hasattr(user, 'rol') or not user.rol:
        return {'id__in': []}  # No mostrar nada
    
    user_role = user.rol.nombre
    role_config = ROLE_FILTERS.get(user_role, {})
    
    filters = {}
    
    # Filtrar solo registros activos
    if role_config.get('filter_active_only', False):
        filters['is_active'] = True
    
    # Filtrar solo registros propios
    if (role_config.get('filter_own_records', False) and 
        module.lower() in role_config.get('own_record_modules', [])):
        
        if module.lower() == 'servicio':
            filters['tecnico'] = user
    
    return filters