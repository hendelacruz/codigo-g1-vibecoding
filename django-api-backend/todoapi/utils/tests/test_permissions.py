"""
Tests para el sistema de permisos personalizado.
Verifica que los decoradores, clases de permisos y configuraciones funcionen correctamente.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import Mock, patch

from authentication.models import Role
from todoapi.utils.permissions import (
    require_role, require_permission,
    IsAdminOrReadOnly, IsAdminOrSupervisor, IsAdminOnly,
    IsTechnicianForServices, CanDeletePermission,
    get_user_permissions, has_permission, get_allowed_actions
)
from todoapi.utils.permission_config import (
    get_permission_classes_for_viewset, get_permission_classes_for_action,
    user_can_perform_action, get_allowed_actions_for_user,
    get_user_role_permissions, get_queryset_filters_for_user
)

User = get_user_model()


class PermissionDecoratorsTestCase(TestCase):
    """
    Tests para los decoradores de permisos.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.factory = RequestFactory()
        
        # Crear roles
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        self.supervisor_role = Role.objects.create(
            nombre='supervisor',
            descripcion='Supervisor del sistema',
            permisos=['read', 'write']
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema',
            permisos=['read', 'services']
        )
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.admin_role
        )
        self.supervisor_user = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            dni='87654321',
            celular='+51987654322',
            rol=self.supervisor_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='11223344',
            celular='+51987654323',
            rol=self.tech_role
        )
        self.no_role_user = User.objects.create_user(
            username='norole',
            email='norole@test.com',
            password='testpass123',
            dni='44332211',
            celular='+51987654324',
            rol=self.tech_role  # Asignar un rol por defecto para evitar errores
        )
    
    def test_require_permission_decorator_success(self):
        """
        Test que el decorador require_permission permite acceso a usuarios con permisos.
        """
        @require_permission('can_delete')
        def test_view(request):
            return "Success"
        
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = test_view(request)
        self.assertEqual(result, "Success")
    
    def test_require_permission_decorator_forbidden(self):
        """
        Test que el decorador require_permission niega acceso a usuarios sin permisos.
        """
        @require_permission('can_delete')
        def test_view(request):
            return "Success"
        
        request = self.factory.get('/')
        request.user = self.supervisor_user
        
        response = test_view(request)
        # El decorador devuelve JsonResponse con status 403
        self.assertEqual(response.status_code, 403)
    
    def test_require_role_decorator_success(self):
        """
        Test que el decorador require_role funciona correctamente.
        """
        @require_role(['administrador', 'supervisor'])
        def test_view(request):
            return "Success"
        
        # Test con administrador
        request = self.factory.get('/')
        request.user = self.admin_user
        result = test_view(request)
        self.assertEqual(result, "Success")
        
        # Test con supervisor
        request.user = self.supervisor_user
        result = test_view(request)
        self.assertEqual(result, "Success")
    
    def test_require_role_decorator_forbidden(self):
        """
        Test que el decorador require_role niega acceso a roles no permitidos.
        """
        @require_role(['administrador'])
        def test_view(request):
            return "Success"
        
        request = self.factory.get('/')
        request.user = self.tech_user
        
        response = test_view(request)
        # El decorador devuelve JsonResponse con status 403
        self.assertEqual(response.status_code, 403)


class PermissionClassesTestCase(TestCase):
    """
    Tests para las clases de permisos de DRF.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.factory = RequestFactory()
        
        # Crear roles y usuarios (reutilizar del test anterior)
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        self.supervisor_role = Role.objects.create(
            nombre='supervisor',
            descripcion='Supervisor del sistema',
            permisos=['read', 'write']
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema',
            permisos=['read', 'services']
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='12345679',
            celular='+51987654325',
            rol=self.admin_role
        )
        self.supervisor_user = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            dni='87654322',
            celular='+51987654326',
            rol=self.supervisor_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='11223345',
            celular='+51987654327',
            rol=self.tech_role
        )
    
    def test_is_admin_only_permission(self):
        """
        Test que IsAdminOnly solo permite acceso a administradores.
        """
        permission = IsAdminOnly()
        
        # Mock request y view
        request = Mock()
        view = Mock()
        
        # Test con administrador
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con supervisor
        request.user = self.supervisor_user
        self.assertFalse(permission.has_permission(request, view))
        
        # Test con técnico
        request.user = self.tech_user
        self.assertFalse(permission.has_permission(request, view))
    
    def test_is_admin_or_supervisor_permission(self):
        """
        Test que IsAdminOrSupervisor permite acceso a admin y supervisores.
        """
        permission = IsAdminOrSupervisor()
        
        request = Mock()
        view = Mock()
        
        # Test con administrador
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con supervisor
        request.user = self.supervisor_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con técnico
        request.user = self.tech_user
        self.assertFalse(permission.has_permission(request, view))
    
    def test_is_admin_or_read_only_permission(self):
        """
        Test que IsAdminOrReadOnly permite lectura a todos y escritura solo a admin.
        """
        permission = IsAdminOrReadOnly()
        
        request = Mock()
        view = Mock()
        
        # Test lectura con técnico
        request.user = self.tech_user
        request.method = 'GET'
        self.assertTrue(permission.has_permission(request, view))
        
        # Test escritura con técnico
        request.method = 'POST'
        self.assertFalse(permission.has_permission(request, view))
        
        # Test escritura con administrador
        request.user = self.admin_user
        request.method = 'POST'
        self.assertTrue(permission.has_permission(request, view))
    
    def test_is_technician_for_services_permission(self):
        """
        Test que IsTechnicianForServices permite acceso a técnicos en servicios.
        """
        permission = IsTechnicianForServices()
        
        request = Mock()
        view = Mock()
        
        # Simular un ViewSet de servicios
        view.__class__.__name__ = 'ServicioViewSet'
        
        # Test con técnico en servicios
        request.user = self.tech_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con administrador
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con supervisor
        request.user = self.supervisor_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con técnico en módulo no-servicios (solo lectura)
        view.__class__.__name__ = 'ClienteViewSet'
        request.method = 'GET'  # Método seguro
        request.user = self.tech_user
        self.assertTrue(permission.has_permission(request, view))
        
        # Test con técnico en módulo no-servicios (método no seguro)
        request.method = 'POST'  # Método no seguro
        self.assertFalse(permission.has_permission(request, view))


class PermissionUtilsTestCase(TestCase):
    """
    Tests para las funciones utilitarias de permisos.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        # Crear roles y usuarios
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema',
            permisos=['read', 'services']
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='12345680',
            celular='+51987654328',
            rol=self.admin_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='11223346',
            celular='+51987654329',
            rol=self.tech_role
        )
    
    def test_get_user_permissions(self):
        """
        Test que get_user_permissions retorna los permisos correctos.
        """
        # Test con administrador
        admin_permissions = get_user_permissions(self.admin_user)
        self.assertIn('can_create', admin_permissions)
        self.assertIn('can_read', admin_permissions)
        self.assertIn('can_update', admin_permissions)
        self.assertIn('can_delete', admin_permissions)
        self.assertTrue(admin_permissions['can_delete'])
        
        # Test con técnico
        tech_permissions = get_user_permissions(self.tech_user)
        self.assertIn('can_read', tech_permissions)
        self.assertIn('can_manage_services', tech_permissions)
        self.assertTrue(tech_permissions['can_read'])
        self.assertTrue(tech_permissions['can_manage_services'])
        self.assertFalse(tech_permissions['can_delete'])
    
    def test_has_permission(self):
        """
        Test que has_permission verifica correctamente los permisos.
        """
        # Test administrador tiene todos los permisos
        self.assertTrue(has_permission(self.admin_user, 'can_delete'))
        self.assertTrue(has_permission(self.admin_user, 'can_read'))
        self.assertTrue(has_permission(self.admin_user, 'can_manage_users'))
        
        # Test técnico tiene permisos específicos
        self.assertTrue(has_permission(self.tech_user, 'can_read'))
        self.assertTrue(has_permission(self.tech_user, 'can_manage_services'))
        self.assertFalse(has_permission(self.tech_user, 'can_delete'))
        self.assertFalse(has_permission(self.tech_user, 'can_manage_users'))
    
    def test_get_allowed_actions(self):
        """
        Test que get_allowed_actions retorna las acciones correctas.
        """
        # Test con administrador en servicios
        admin_actions = get_allowed_actions(self.admin_user, 'servicio')
        self.assertIn('create', admin_actions)
        self.assertIn('update', admin_actions)
        self.assertIn('delete', admin_actions)
        self.assertIn('read', admin_actions)
        
        # Test con técnico en servicios (puede crear y actualizar)
        tech_service_actions = get_allowed_actions(self.tech_user, 'service')
        self.assertIn('create', tech_service_actions)
        self.assertIn('read', tech_service_actions)
        self.assertIn('update', tech_service_actions)
        self.assertNotIn('delete', tech_service_actions)
        
        # Test con técnico en clientes (solo lectura)
        tech_client_actions = get_allowed_actions(self.tech_user, 'cliente')
        self.assertIn('read', tech_client_actions)
        self.assertNotIn('create', tech_client_actions)
        self.assertNotIn('update', tech_client_actions)
        self.assertNotIn('delete', tech_client_actions)


class PermissionConfigTestCase(TestCase):
    """
    Tests para la configuración de permisos.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema',
            permisos=['read', 'services']
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='12345681',
            celular='+51987654330',
            rol=self.admin_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='11223347',
            celular='+51987654331',
            rol=self.tech_role
        )
    
    def test_user_can_perform_action(self):
        """
        Test que user_can_perform_action verifica correctamente las acciones.
        """
        # Test administrador puede eliminar
        self.assertTrue(user_can_perform_action(self.admin_user, 'cliente', 'destroy'))
        
        # Test técnico no puede eliminar
        self.assertFalse(user_can_perform_action(self.tech_user, 'cliente', 'destroy'))
        
        # Test técnico puede leer
        self.assertTrue(user_can_perform_action(self.tech_user, 'cliente', 'list'))
        self.assertTrue(user_can_perform_action(self.tech_user, 'cliente', 'retrieve'))
        
        # Test técnico no puede crear en clientes
        self.assertFalse(user_can_perform_action(self.tech_user, 'cliente', 'create'))
        
        # Test técnico puede crear en servicios
        self.assertTrue(user_can_perform_action(self.tech_user, 'servicio', 'create'))
    
    def test_get_allowed_actions_for_user(self):
        """
        Test que get_allowed_actions_for_user retorna las acciones correctas.
        """
        # Test acciones para administrador en clientes
        admin_actions = get_allowed_actions_for_user(self.admin_user, 'cliente')
        self.assertIn('create', admin_actions)
        self.assertIn('destroy', admin_actions)
        self.assertIn('list', admin_actions)
        self.assertIn('retrieve', admin_actions)
        self.assertIn('update', admin_actions)
        self.assertIn('partial_update', admin_actions)
        self.assertIn('get_units', admin_actions)
        self.assertIn('get_services', admin_actions)
        
        # Test acciones para técnico en clientes (solo lectura y acciones específicas)
        tech_actions = get_allowed_actions_for_user(self.tech_user, 'cliente')
        self.assertIn('list', tech_actions)
        self.assertIn('retrieve', tech_actions)
        self.assertIn('get_units', tech_actions)
        self.assertIn('get_services', tech_actions)
        self.assertNotIn('create', tech_actions)
        self.assertNotIn('update', tech_actions)
        self.assertNotIn('destroy', tech_actions)
    
    def test_get_user_role_permissions(self):
        """
        Test que get_user_role_permissions retorna el resumen correcto.
        """
        # Test resumen para administrador
        admin_summary = get_user_role_permissions(self.admin_user)
        self.assertIn('cliente', admin_summary)
        self.assertIn('servicio', admin_summary)
        
        # Test resumen para técnico
        tech_summary = get_user_role_permissions(self.tech_user)
        self.assertIn('cliente', tech_summary)
        self.assertIn('servicio', tech_summary)
        
        # Verificar que técnico tiene menos permisos que admin
        self.assertGreater(
            len(admin_summary['cliente']), 
            len(tech_summary['cliente'])
        )
    
    def test_get_queryset_filters_for_user(self):
        """
        Test que get_queryset_filters_for_user retorna los filtros correctos.
        """
        # Test filtros para administrador (sin filtros)
        admin_filters = get_queryset_filters_for_user(self.admin_user, 'cliente')
        self.assertEqual(admin_filters, {})
        
        # Test filtros para técnico (solo activos)
        tech_filters = get_queryset_filters_for_user(self.tech_user, 'cliente')
        self.assertEqual(tech_filters, {'is_active': True})
        
        # Test filtros para técnico en servicios (solo suyos)
        tech_service_filters = get_queryset_filters_for_user(self.tech_user, 'servicio')
        self.assertEqual(tech_service_filters, {
            'is_active': True,
            'tecnico': self.tech_user
        })


class PermissionIntegrationTestCase(APITestCase):
    """
    Tests de integración para el sistema de permisos completo.
    """
    
    def setUp(self):
        """
        Configuración inicial para las pruebas de integración.
        """
        self.client = APIClient()
        
        # Crear roles
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema',
            permisos=['all']
        )
        self.tech_role = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico del sistema',
            permisos=['read', 'services']
        )
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            dni='12345682',
            celular='+51987654332',
            rol=self.admin_role
        )
        self.tech_user = User.objects.create_user(
            username='tech',
            email='tech@test.com',
            password='testpass123',
            dni='11223348',
            celular='+51987654333',
            rol=self.tech_role
        )
    
    def test_permission_system_integration(self):
        """
        Test de integración completo del sistema de permisos.
        """
        # Test que el sistema funciona end-to-end
        # Este test se puede expandir cuando se implementen los ViewSets
        
        # Por ahora, verificar que las funciones básicas funcionan
        self.assertTrue(user_can_perform_action(self.admin_user, 'cliente', 'create'))
        self.assertFalse(user_can_perform_action(self.tech_user, 'cliente', 'destroy'))
        
        # Verificar que los permisos se obtienen correctamente
        admin_permissions = get_user_role_permissions(self.admin_user)
        tech_permissions = get_user_role_permissions(self.tech_user)
        
        self.assertIsInstance(admin_permissions, dict)
        self.assertIsInstance(tech_permissions, dict)
        
        # Verificar que admin tiene más permisos que técnico
        for module in admin_permissions:
            if module in tech_permissions:
                self.assertGreaterEqual(
                    len(admin_permissions[module]),
                    len(tech_permissions[module])
                )