"""
Tests comprehensivos para los mixins de todoapi.utils.mixins
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import viewsets, status
from rest_framework.response import Response
from unittest.mock import Mock, patch, MagicMock

from authentication.models import Role
from todoapi.utils.mixins import (
    RoleBasedPermissionMixin, AdminOnlyMixin, AdminOperatorMixin,
    ReadOnlyForTechnicianMixin, ServicePermissionMixin, UserPermissionInfoMixin,
    AuditMixin, FilterByUserMixin, BulkActionsMixin
)

User = get_user_model()


class MockModel:
    """Mock model para testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    class Meta:
        pass


class MockQuerySet:
    """Mock queryset para testing"""
    def __init__(self, model=None, items=None):
        self.model = model or MockModel
        self.items = items or []
    
    def filter(self, **kwargs):
        return MockQuerySet(self.model, self.items)
    
    def update(self, **kwargs):
        return len(self.items)
    
    def none(self):
        return MockQuerySet(self.model, [])
    
    def __iter__(self):
        return iter(self.items)
    
    def count(self):
        return len(self.items)


class MockViewSet(viewsets.ModelViewSet):
    """Mock ViewSet para testing"""
    queryset = MockQuerySet()
    
    def get_queryset(self):
        return self.queryset


class RoleBasedPermissionMixinTest(TestCase):
    """Tests para RoleBasedPermissionMixin"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        self.supervisor_role = Role.objects.create(
            nombre='supervisor',
            descripcion='Supervisor del sistema'
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='30000007',
            celular='3000000007',
            rol=self.admin_role
        )
        
        class TestViewSet(RoleBasedPermissionMixin, MockViewSet):
            pass
        
        self.viewset = TestViewSet()
    
    def test_get_permissions_destroy_action(self):
        """Test permisos para acción destroy"""
        self.viewset.action = 'destroy'
        permissions = self.viewset.get_permissions()
        
        # Debe incluir IsAuthenticated y CanDeletePermission
        self.assertEqual(len(permissions), 2)
    
    def test_get_permissions_create_action_service_viewset(self):
        """Test permisos para acción create en ViewSet de servicios"""
        class ServicioViewSet(RoleBasedPermissionMixin, MockViewSet):
            pass
        
        viewset = ServicioViewSet()
        viewset.action = 'create'
        permissions = viewset.get_permissions()
        
        # Debe incluir IsAuthenticated y IsTechnicianForServices
        self.assertEqual(len(permissions), 2)
    
    def test_get_permissions_create_action_other_viewset(self):
        """Test permisos para acción create en otros ViewSets"""
        self.viewset.action = 'create'
        permissions = self.viewset.get_permissions()
        
        # Debe incluir IsAuthenticated y IsAdminOrSupervisor
        self.assertEqual(len(permissions), 2)
    
    def test_get_permissions_read_action(self):
        """Test permisos para acciones de lectura"""
        self.viewset.action = 'list'
        permissions = self.viewset.get_permissions()
        
        # Solo debe incluir IsAuthenticated
        self.assertEqual(len(permissions), 1)


class AdminOnlyMixinTest(TestCase):
    """Tests para AdminOnlyMixin"""
    
    def test_permission_classes(self):
        """Test que AdminOnlyMixin tiene las clases de permisos correctas"""
        class TestViewSet(AdminOnlyMixin, MockViewSet):
            pass
        
        viewset = TestViewSet()
        self.assertEqual(len(viewset.permission_classes), 2)


class AdminOperatorMixinTest(TestCase):
    """Tests para AdminOperatorMixin"""
    
    def test_permission_classes(self):
        """Test que AdminOperatorMixin tiene las clases de permisos correctas"""
        class TestViewSet(AdminOperatorMixin, MockViewSet):
            pass
        
        viewset = TestViewSet()
        self.assertEqual(len(viewset.permission_classes), 2)


class ReadOnlyForTechnicianMixinTest(TestCase):
    """Tests para ReadOnlyForTechnicianMixin"""
    
    def setUp(self):
        class TestViewSet(ReadOnlyForTechnicianMixin, MockViewSet):
            pass
        
        self.viewset = TestViewSet()
    
    def test_get_permissions_read_action(self):
        """Test permisos para acciones de lectura"""
        self.viewset.action = 'list'
        permissions = self.viewset.get_permissions()
        
        # Solo debe incluir IsAuthenticated
        self.assertEqual(len(permissions), 1)
    
    def test_get_permissions_write_action(self):
        """Test permisos para acciones de escritura"""
        self.viewset.action = 'create'
        permissions = self.viewset.get_permissions()
        
        # Debe incluir IsAuthenticated y IsAdminOrSupervisor
        self.assertEqual(len(permissions), 2)


class ServicePermissionMixinTest(TestCase):
    """Tests para ServicePermissionMixin"""
    
    def test_permission_classes(self):
        """Test que ServicePermissionMixin tiene las clases de permisos correctas"""
        class TestViewSet(ServicePermissionMixin, MockViewSet):
            pass
        
        viewset = TestViewSet()
        self.assertEqual(len(viewset.permission_classes), 2)


class UserPermissionInfoMixinTest(TestCase):
    """Tests para UserPermissionInfoMixin"""
    
    def create_mock_request(self, user=None, path='/test/'):
        """Helper para crear mock request"""
        request = Mock()
        if user:
            request.user = user
        else:
            request.user = Mock()
            request.user.is_authenticated = False
        return request
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            rol=self.admin_role
        )
        
        class TestViewSet(UserPermissionInfoMixin, MockViewSet):
            pass
        
        self.viewset = TestViewSet()
    
    @patch('todoapi.utils.mixins.get_user_permissions')
    @patch('todoapi.utils.mixins.get_allowed_actions')
    def test_get_my_permissions_authenticated_user(self, mock_allowed_actions, mock_user_permissions):
        """Test get_my_permissions con usuario autenticado"""
        mock_user_permissions.return_value = ['read', 'write']
        mock_allowed_actions.return_value = ['list', 'create']
        
        request = self.create_mock_request(self.admin_user)
        self.viewset.request = request
        
        response = self.viewset.get_my_permissions(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertIn('permissions', response.data)
        self.assertIn('allowed_actions', response.data)
    
    def test_get_my_permissions_unauthenticated_user(self):
        """Test get_my_permissions con usuario no autenticado"""
        request = self.create_mock_request()  # Sin usuario
        
        response = self.viewset.get_my_permissions(request)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_role_info_authenticated_user_with_role(self):
        """Test get_role_info con usuario autenticado que tiene rol"""
        request = self.create_mock_request(self.admin_user)
        
        response = self.viewset.get_role_info(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('role_id', response.data)
        self.assertIn('role_name', response.data)
    
    def test_get_role_info_unauthenticated_user(self):
        """Test get_role_info con usuario no autenticado"""
        request = self.create_mock_request()  # Sin usuario
        
        response = self.viewset.get_role_info(request)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_role_info_user_without_role(self):
        """Test get_role_info con usuario sin rol"""
        # Crear un rol temporal para el usuario (ya que el campo es requerido)
        temp_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Rol temporal para test'
        )
        
        user_without_role = User.objects.create_user(
            username='norole',
            email='norole@test.com',
            password='testpass123',
            dni='30000008',
            celular='3000000008',
            rol=temp_role
        )
        
        request = self.create_mock_request(user_without_role)
        
        response = self.viewset.get_role_info(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuditMixinTest(TestCase):
    """Tests para AuditMixin"""
    
    def create_mock_request(self, user=None, method='GET', path='/test/'):
        """Helper para crear request mock con usuario autenticado"""
        request = self.factory.generic(method, path)
        if user:
            request.user = user
        else:
            # Crear un mock user con is_authenticated = False
            mock_user = Mock()
            mock_user.is_authenticated = False
            request.user = mock_user
        return request
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Crear rol para el usuario
        self.role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            dni='30000006',
            celular='3000000006',
            rol=self.role
        )
        
        class TestViewSet(AuditMixin, MockViewSet):
            pass
        
        self.viewset = TestViewSet()
        self.viewset.request = self.create_mock_request(user=self.user, method='POST')
    
    def test_perform_create_with_created_by_field(self):
        """Test perform_create cuando el modelo tiene campo created_by"""
        mock_serializer = Mock()
        mock_serializer.Meta.model = Mock()
        mock_serializer.Meta.model.created_by = True
        
        # Mock hasattr para que retorne True
        with patch('builtins.hasattr', return_value=True):
            self.viewset.perform_create(mock_serializer)
            mock_serializer.save.assert_called_once_with(created_by=self.user)
    
    def test_perform_create_without_created_by_field(self):
        """Test perform_create cuando el modelo no tiene campo created_by"""
        mock_serializer = Mock()
        mock_serializer.Meta.model = Mock()
        
        # Mock hasattr para que retorne False
        with patch('builtins.hasattr', return_value=False):
            self.viewset.perform_create(mock_serializer)
            mock_serializer.save.assert_called_once_with()
    
    def test_perform_update_with_updated_by_field(self):
        """Test perform_update cuando el modelo tiene campo updated_by"""
        mock_serializer = Mock()
        mock_serializer.Meta.model = Mock()
        
        # Configurar el request para update
        self.viewset.request = self.create_mock_request(user=self.user, method='PUT')
        
        with patch('builtins.hasattr', return_value=True):
            self.viewset.perform_update(mock_serializer)
            mock_serializer.save.assert_called_once_with(updated_by=self.user)
    
    def test_perform_update_without_updated_by_field(self):
        """Test perform_update cuando el modelo no tiene campo updated_by"""
        mock_serializer = Mock()
        mock_serializer.Meta.model = Mock()
        
        with patch('builtins.hasattr', return_value=False):
            self.viewset.perform_update(mock_serializer)
            mock_serializer.save.assert_called_once_with()
    
    def test_perform_destroy_soft_delete(self):
        """Test perform_destroy con soft delete"""
        mock_instance = Mock()
        mock_instance.is_active = True
        mock_instance.deleted_by = None
        
        # Configurar el request para destroy
        self.viewset.request = self.create_mock_request(user=self.user, method='DELETE')
        
        with patch('builtins.hasattr') as mock_hasattr:
            # Configurar hasattr para retornar True para is_active y deleted_by
            mock_hasattr.side_effect = lambda obj, attr: attr in ['is_active', 'deleted_by']
            
            self.viewset.perform_destroy(mock_instance)
            
            self.assertFalse(mock_instance.is_active)
            self.assertEqual(mock_instance.deleted_by, self.user)
            mock_instance.save.assert_called_once()
    
    def test_perform_destroy_hard_delete(self):
        """Test perform_destroy con hard delete"""
        mock_instance = Mock()
        
        with patch('builtins.hasattr', return_value=False):
            self.viewset.perform_destroy(mock_instance)
            mock_instance.delete.assert_called_once()


class FilterByUserMixinTest(TestCase):
    """Tests para FilterByUserMixin"""
    
    def create_mock_request(self, user=None):
        """Helper para crear mock request"""
        request = Mock()
        if user:
            request.user = user
        else:
            request.user = Mock()
            request.user.is_authenticated = False
        return request
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Crear roles
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        self.supervisor_role = Role.objects.create(
            nombre='supervisor',
            descripcion='Supervisor del sistema'
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema'
        )
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='10000001',
            celular='+51900000001',
            rol=self.admin_role
        )
        self.supervisor_user = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            dni='10000002',
            celular='+51900000002',
            rol=self.supervisor_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='10000003',
            celular='+51900000003',
            rol=self.tech_role
        )
        
        class TestViewSet(FilterByUserMixin, MockViewSet):
            def get_queryset(self):
                return MockQuerySet()
        
        self.viewset = TestViewSet()
    
    def test_get_queryset_unauthenticated_user(self):
        """Test get_queryset con usuario no autenticado"""
        request = self.create_mock_request()  # Sin usuario
        self.viewset.request = request
        
        queryset = self.viewset.get_queryset()
        # Debe retornar queryset vacío
        self.assertIsInstance(queryset, MockQuerySet)
    
    def test_get_queryset_user_without_role(self):
        """Test get_queryset con usuario sin rol"""
        # Crear un rol temporal para el usuario (ya que el campo es requerido)
        temp_role = Role.objects.create(
            nombre='cliente',
            descripcion='Rol temporal para test'
        )
        
        user_without_role = User.objects.create_user(
            username='norole',
            email='norole@test.com',
            password='testpass123',
            dni='30000009',
            celular='3000000009',
            rol=temp_role
        )
        
        request = self.create_mock_request(user_without_role)
        self.viewset.request = request
        
        queryset = self.viewset.get_queryset()
        # Debe retornar queryset vacío
        self.assertIsInstance(queryset, MockQuerySet)
    
    def test_get_queryset_admin_user(self):
        """Test get_queryset con usuario administrador"""
        request = self.create_mock_request(self.admin_user)
        self.viewset.request = request
        
        queryset = self.viewset.get_queryset()
        # Administradores ven todo
        self.assertIsInstance(queryset, MockQuerySet)
    
    def test_get_queryset_supervisor_user(self):
        """Test get_queryset con usuario supervisor"""
        request = self.create_mock_request(self.supervisor_user)
        self.viewset.request = request
        
        # Mock del modelo con is_active
        mock_model = Mock()
        mock_model.__name__ = 'TestModel'
        mock_model.is_active = True
        
        # Crear un queryset con el modelo mockeado
        mock_queryset = MockQuerySet(model=mock_model)
        
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            with patch('builtins.hasattr', return_value=True):
                queryset = self.viewset.get_queryset()
                self.assertIsInstance(queryset, MockQuerySet)
    
    def test_get_queryset_tech_user_service_model(self):
        """Test get_queryset con usuario técnico en modelo de servicios"""
        request = self.create_mock_request(self.tech_user)
        self.viewset.request = request
        
        # Mock del modelo Servicio
        mock_model = Mock()
        mock_model.__name__ = 'Servicio'
        
        # Crear un queryset con el modelo mockeado
        mock_queryset = MockQuerySet(model=mock_model)
        
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            queryset = self.viewset.get_queryset()
            self.assertIsInstance(queryset, MockQuerySet)


class BulkActionsMixinTest(TestCase):
    """Tests para BulkActionsMixin"""
    
    def create_mock_request(self, user, data=None):
        """Helper para crear un mock request con user y data"""
        class MockRequest:
            def __init__(self, user, data):
                self.user = user
                self.data = data or {}
        
        return MockRequest(user, data)
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Crear roles
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        self.supervisor_role = Role.objects.create(
            nombre='supervisor',
            descripcion='Supervisor del sistema'
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema'
        )
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='30000003',
            celular='3000000003',
            rol=self.admin_role
        )
        self.supervisor_user = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            dni='30000004',
            celular='3000000004',
            rol=self.supervisor_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='30000005',
            celular='3000000005',
            rol=self.tech_role
        )
        
        class TestViewSet(BulkActionsMixin, MockViewSet):
            def get_queryset(self):
                return MockQuerySet(items=[1, 2, 3])
        
        self.viewset = TestViewSet()
    
    def test_bulk_activate_admin_user(self):
        """Test bulk_activate con usuario administrador"""
        request = self.create_mock_request(self.admin_user, {'ids': [1, 2, 3]})
        
        # Mock del modelo con is_active
        mock_model = Mock()
        mock_model.is_active = True
        
        # Crear un queryset con el modelo mockeado
        mock_queryset = MockQuerySet(model=mock_model, items=[1, 2, 3])
        
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            with patch('builtins.hasattr', return_value=True):
                response = self.viewset.bulk_activate(request)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('updated_count', response.data)
    
    def test_bulk_activate_supervisor_user(self):
        """Test bulk_activate con usuario supervisor"""
        request = self.create_mock_request(self.supervisor_user, {'ids': [1, 2, 3]})
        
        # Mock del modelo con is_active
        mock_model = Mock()
        mock_model.is_active = True
        
        # Crear un queryset con el modelo mockeado
        mock_queryset = MockQuerySet(model=mock_model, items=[1, 2, 3])
        
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            with patch('builtins.hasattr', return_value=True):
                response = self.viewset.bulk_activate(request)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_bulk_activate_tech_user_forbidden(self):
        """Test bulk_activate con usuario técnico (debería fallar)"""
        request = self.create_mock_request(self.tech_user, {'ids': [1, 2, 3]})
        
        response = self.viewset.bulk_activate(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_bulk_activate_no_ids(self):
        """Test bulk_activate sin IDs"""
        request = self.create_mock_request(self.admin_user, {})
        
        response = self.viewset.bulk_activate(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_activate_model_without_is_active(self):
        """Test bulk_activate en modelo sin campo is_active"""
        request = self.create_mock_request(self.admin_user, {'ids': [1, 2, 3]})
        
        # Crear un modelo mock sin is_active
        class ModelWithoutIsActive:
            pass
        
        # Crear un queryset mock que use este modelo
        mock_queryset = Mock()
        mock_queryset.model = ModelWithoutIsActive
        mock_queryset.filter.return_value = mock_queryset
        
        # Patchear get_queryset para retornar nuestro mock
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            response = self.viewset.bulk_activate(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_deactivate_admin_user(self):
        """Test bulk_deactivate con usuario administrador"""
        request = self.create_mock_request(self.admin_user, {'ids': [1, 2, 3]})
        
        # Mock del modelo con is_active
        mock_model = Mock()
        mock_model.is_active = True
        
        # Crear un queryset con el modelo mockeado
        mock_queryset = MockQuerySet(model=mock_model, items=[1, 2, 3])
        
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            with patch('builtins.hasattr', return_value=True):
                response = self.viewset.bulk_deactivate(request)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('updated_count', response.data)
    
    def test_bulk_deactivate_supervisor_user_forbidden(self):
        """Test bulk_deactivate con usuario supervisor (debería fallar)"""
        request = self.create_mock_request(self.supervisor_user, {'ids': [1, 2, 3]})
        
        response = self.viewset.bulk_deactivate(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_bulk_deactivate_no_ids(self):
        """Test bulk_deactivate sin IDs"""
        request = self.create_mock_request(self.admin_user, {})
        
        response = self.viewset.bulk_deactivate(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_deactivate_model_without_is_active(self):
        """Test bulk_deactivate en modelo sin campo is_active"""
        request = self.create_mock_request(self.admin_user, {'ids': [1, 2, 3]})
        
        # Crear un modelo mock sin is_active
        class ModelWithoutIsActive:
            pass
        
        # Crear un queryset mock que use este modelo
        mock_queryset = Mock()
        mock_queryset.model = ModelWithoutIsActive
        mock_queryset.filter.return_value = mock_queryset
        
        # Patchear get_queryset para retornar nuestro mock
        with patch.object(self.viewset, 'get_queryset', return_value=mock_queryset):
            response = self.viewset.bulk_deactivate(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)