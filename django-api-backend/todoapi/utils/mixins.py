"""
Mixins para ViewSets con configuración automática de permisos basados en roles.
Facilita la implementación de permisos en los ViewSets de la API.
"""

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .permissions import (
    IsAdminOrReadOnly, IsAdminOrSupervisor, IsAdminOnly,
    IsTechnicianForServices, CanDeletePermission,
    get_user_permissions, get_allowed_actions
)


class RoleBasedPermissionMixin:
    """
    Mixin que configura automáticamente los permisos basados en roles.
    """
    
    def get_permissions(self):
        """
        Configura permisos dinámicamente basado en la acción y el ViewSet.
        """
        permission_classes = []
        
        # Siempre requerir autenticación
        permission_classes.append(permissions.IsAuthenticated)
        
        # Configurar permisos específicos por acción
        if self.action == 'destroy':
            # Solo administradores pueden eliminar
            permission_classes.append(CanDeletePermission)
        elif self.action in ['create', 'update', 'partial_update']:
            # Crear y actualizar según el tipo de ViewSet
            viewset_name = self.__class__.__name__.lower()
            if 'servicio' in viewset_name or 'tipotrabajo' in viewset_name:
                # Servicios: técnicos tienen acceso completo
                permission_classes.append(IsTechnicianForServices)
            else:
                # Otros módulos: solo admin y operadores
                permission_classes.append(IsAdminOrSupervisor)
        else:
            # Lectura: todos los usuarios autenticados
            pass
            
        return [permission() for permission in permission_classes]


class AdminOnlyMixin:
    """
    Mixin para ViewSets que requieren acceso exclusivo de administrador.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]


class AdminOperatorMixin:
    """
    Mixin para ViewSets que permiten acceso a administradores y operadores.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]


class ReadOnlyForTechnicianMixin:
    """
    Mixin para ViewSets donde técnicos solo tienen acceso de lectura.
    """
    
    def get_permissions(self):
        """
        Técnicos solo pueden leer, admin y operadores acceso completo.
        """
        permission_classes = [permissions.IsAuthenticated]
        
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes.append(IsAdminOrSupervisor)
            
        return [permission() for permission in permission_classes]


class ServicePermissionMixin:
    """
    Mixin específico para ViewSets de servicios.
    Técnicos tienen acceso completo, otros según su rol.
    """
    permission_classes = [permissions.IsAuthenticated, IsTechnicianForServices]


class UserPermissionInfoMixin:
    """
    Mixin que agrega endpoints para obtener información de permisos del usuario.
    """
    
    @action(detail=False, methods=['get'], url_path='my-permissions')
    def get_my_permissions(self, request):
        """
        Endpoint para obtener los permisos del usuario actual.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Usuario no autenticado'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        permissions = get_user_permissions(request.user)
        allowed_actions = get_allowed_actions(
            request.user, 
            self.__class__.__name__.replace('ViewSet', '').lower()
        )
        
        user_info = {
            'user_id': request.user.id,
            'username': request.user.username,
            'role': request.user.rol.nombre if hasattr(request.user, 'rol') and request.user.rol else None,
            'permissions': permissions,
            'allowed_actions': allowed_actions,
            'module': self.__class__.__name__.replace('ViewSet', '').lower()
        }
        
        return Response(user_info, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='role-info')
    def get_role_info(self, request):
        """
        Endpoint para obtener información del rol del usuario.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Usuario no autenticado'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return Response(
                {'error': 'Usuario sin rol asignado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        role_info = {
            'role_id': request.user.rol.id,
            'role_name': request.user.rol.nombre,
            'role_display': request.user.rol.get_nombre_display(),
            'role_description': request.user.rol.descripcion,
            'role_permissions': request.user.rol.permisos,
            'is_active': request.user.rol.is_active
        }
        
        return Response(role_info, status=status.HTTP_200_OK)


class AuditMixin:
    """
    Mixin que agrega funcionalidad de auditoría a los ViewSets.
    """
    
    def perform_create(self, serializer):
        """
        Registra quién creó el objeto.
        """
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """
        Registra quién actualizó el objeto.
        """
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """
        Soft delete si el modelo lo soporta, sino eliminación física.
        """
        if hasattr(instance, 'is_active'):
            # Soft delete
            instance.is_active = False
            if hasattr(instance, 'deleted_by'):
                instance.deleted_by = self.request.user
            instance.save()
        else:
            # Hard delete
            instance.delete()


class FilterByUserMixin:
    """
    Mixin que filtra automáticamente los objetos según el usuario y su rol.
    """
    
    def get_queryset(self):
        """
        Filtra el queryset según el rol del usuario.
        """
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        if not hasattr(self.request.user, 'rol') or not self.request.user.rol:
            return queryset.none()
        
        user_role = self.request.user.rol.nombre
        
        # Administradores ven todo
        if user_role == 'administrador':
            return queryset
        
        # Operadores ven todo activo
        elif user_role == 'supervisor':
            if hasattr(queryset.model, 'is_active'):
                return queryset.filter(is_active=True)
            return queryset
        
        # Técnicos ven solo lo relacionado con ellos
        elif user_role == 'tecnico':
            model_name = queryset.model.__name__.lower()
            
            if model_name == 'servicio':
                # Técnicos solo ven servicios asignados a ellos
                return queryset.filter(tecnico=self.request.user)
            elif hasattr(queryset.model, 'is_active'):
                # En otros modelos, solo ven registros activos
                return queryset.filter(is_active=True)
            else:
                return queryset
        
        return queryset.none()


class BulkActionsMixin:
    """
    Mixin que agrega acciones en lote con control de permisos.
    """
    
    @action(detail=False, methods=['post'], url_path='bulk-activate')
    def bulk_activate(self, request):
        """
        Activa múltiples objetos en lote.
        Solo para administradores y operadores.
        """
        if not hasattr(request, 'user') or not hasattr(request.user, 'rol') or request.user.rol.nombre not in ['administrador', 'supervisor']:
            return Response(
                {'error': 'Permisos insuficientes para esta acción'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'Se requiere una lista de IDs'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        
        if hasattr(queryset.model, 'is_active'):
            updated_count = queryset.update(is_active=True)
            return Response({
                'message': f'{updated_count} objetos activados exitosamente',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Este modelo no soporta activación/desactivación'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='bulk-deactivate')
    def bulk_deactivate(self, request):
        """
        Desactiva múltiples objetos en lote.
        Solo para administradores.
        """
        if not hasattr(request, 'user') or not hasattr(request.user, 'rol') or request.user.rol.nombre != 'administrador':
            return Response(
                {'error': 'Solo administradores pueden desactivar objetos'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'Se requiere una lista de IDs'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        
        if hasattr(queryset.model, 'is_active'):
            updated_count = queryset.update(is_active=False)
            return Response({
                'message': f'{updated_count} objetos desactivados exitosamente',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Este modelo no soporta activación/desactivación'}, 
                status=status.HTTP_400_BAD_REQUEST
            )