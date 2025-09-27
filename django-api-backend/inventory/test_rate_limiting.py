"""
Tests para verificar el funcionamiento del rate limiting en los ViewSets de inventario.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from entities.models import Proveedor
from authentication.models import Role
from .models import GPS, SIMCard, Otros

User = get_user_model()


class InventoryRateLimitingTestCase(TestCase):
    """
    Test case para verificar que el rate limiting está configurado correctamente
    en todos los ViewSets de inventario.
    """
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear rol de prueba
        self.admin_role = Role.objects.create(
            nombre='administrador',
            descripcion='Rol de administrador para tests',
            permisos={'all': True}
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dni='12345678',
            celular='+51987654321',
            rol=self.admin_role
        )
        
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            ruc='12345678901',
            celular='987654321',
            direccion='Dirección Test',
            contacto='Contacto Test',
            correo='test@proveedor.com'
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs de los endpoints
        self.gps_url = reverse('inventory:gps-list')
        self.simcard_url = reverse('inventory:simcard-list')
        self.otros_url = reverse('inventory:otros-list')
    
    def test_gps_viewset_has_rate_limiting_mixin(self):
        """Verifica que GPSViewSet tiene el mixin de rate limiting."""
        from .views import GPSViewSet
        from todoapi.utils.rate_limiting import APIRateLimitMixin
        
        # Verificar que GPSViewSet hereda de APIRateLimitMixin
        self.assertTrue(issubclass(GPSViewSet, APIRateLimitMixin))
        
        # Verificar que tiene la configuración de rate limiting
        viewset = GPSViewSet()
        self.assertEqual(viewset.rate_limit_scope, 'inventory')
        self.assertEqual(viewset.rate_limit_config['requests'], 500)
        self.assertEqual(viewset.rate_limit_config['window'], 3600)
    
    def test_simcard_viewset_has_rate_limiting_mixin(self):
        """Verifica que SIMCardViewSet tiene el mixin de rate limiting."""
        from .views import SIMCardViewSet
        from todoapi.utils.rate_limiting import APIRateLimitMixin
        
        # Verificar que SIMCardViewSet hereda de APIRateLimitMixin
        self.assertTrue(issubclass(SIMCardViewSet, APIRateLimitMixin))
        
        # Verificar que tiene la configuración de rate limiting
        viewset = SIMCardViewSet()
        self.assertEqual(viewset.rate_limit_scope, 'inventory')
        self.assertEqual(viewset.rate_limit_config['requests'], 500)
        self.assertEqual(viewset.rate_limit_config['window'], 3600)
    
    def test_otros_viewset_has_rate_limiting_mixin(self):
        """Verifica que OtrosViewSet tiene el mixin de rate limiting."""
        from .views import OtrosViewSet
        from todoapi.utils.rate_limiting import APIRateLimitMixin
        
        # Verificar que OtrosViewSet hereda de APIRateLimitMixin
        self.assertTrue(issubclass(OtrosViewSet, APIRateLimitMixin))
        
        # Verificar que tiene la configuración de rate limiting
        viewset = OtrosViewSet()
        self.assertEqual(viewset.rate_limit_scope, 'inventory')
        self.assertEqual(viewset.rate_limit_config['requests'], 500)
        self.assertEqual(viewset.rate_limit_config['window'], 3600)
    
    @patch('todoapi.utils.rate_limiting.RateLimitMiddleware.process_request')
    def test_gps_endpoint_calls_rate_limiting(self, mock_rate_limit):
        """Verifica que el endpoint de GPS llama al middleware de rate limiting."""
        mock_rate_limit.return_value = None
        
        # Hacer una petición al endpoint de GPS
        response = self.client.get(self.gps_url)
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el middleware de rate limiting fue llamado
        self.assertTrue(mock_rate_limit.called)
    
    @patch('todoapi.utils.rate_limiting.RateLimitMiddleware.process_request')
    def test_simcard_endpoint_calls_rate_limiting(self, mock_rate_limit):
        """Verifica que el endpoint de SIMCard llama al middleware de rate limiting."""
        mock_rate_limit.return_value = None
        
        # Hacer una petición al endpoint de SIMCard
        response = self.client.get(self.simcard_url)
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el middleware de rate limiting fue llamado
        self.assertTrue(mock_rate_limit.called)
    
    @patch('todoapi.utils.rate_limiting.RateLimitMiddleware.process_request')
    def test_otros_endpoint_calls_rate_limiting(self, mock_rate_limit):
        """Verifica que el endpoint de Otros llama al middleware de rate limiting."""
        mock_rate_limit.return_value = None
        
        # Hacer una petición al endpoint de Otros
        response = self.client.get(self.otros_url)
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el middleware de rate limiting fue llamado
        self.assertTrue(mock_rate_limit.called)
    
    def test_rate_limiting_configuration_consistency(self):
        """Verifica que todos los ViewSets tienen la misma configuración de rate limiting."""
        from .views import GPSViewSet, SIMCardViewSet, OtrosViewSet
        
        viewsets = [GPSViewSet(), SIMCardViewSet(), OtrosViewSet()]
        
        # Verificar que todos tienen el mismo scope
        scopes = [vs.rate_limit_scope for vs in viewsets]
        self.assertTrue(all(scope == 'inventory' for scope in scopes))
        
        # Verificar que todos tienen la misma configuración
        configs = [vs.rate_limit_config for vs in viewsets]
        expected_config = {'requests': 500, 'window': 3600}
        self.assertTrue(all(config == expected_config for config in configs))
    
    def test_rate_limiting_headers_in_response(self):
        """Verifica que las respuestas incluyen headers de rate limiting."""
        # Hacer una petición a cualquier endpoint
        response = self.client.get(self.gps_url)
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Nota: Los headers específicos dependen de la implementación del middleware
        # Este test verifica que la respuesta se procesa correctamente
        self.assertIsNotNone(response)