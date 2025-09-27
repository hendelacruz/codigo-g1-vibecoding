"""
Tests para el middleware de seguridad personalizado.
"""

from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
import logging

from todoapi.utils.security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    AuditLogMiddleware,
    IPWhitelistMiddleware,
    BruteForceProtectionMiddleware
)

User = get_user_model()


class SecurityHeadersMiddlewareTest(TestCase):
    """Tests para SecurityHeadersMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(Mock())
    
    def test_security_headers_added(self):
        """Test que los headers de seguridad se agregan correctamente."""
        request = self.factory.get('/')
        response = HttpResponse()
        
        result = self.middleware(request)
        
        # Verificar que los headers de seguridad están presentes
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        for header in expected_headers:
            self.assertIn(header, result)
    
    def test_csp_header_added(self):
        """Test que el header CSP se agrega correctamente."""
        request = self.factory.get('/')
        response = HttpResponse()
        
        result = self.middleware(request)
        
        self.assertIn('Content-Security-Policy', result)


class RequestValidationMiddlewareTest(TestCase):
    """Tests para RequestValidationMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestValidationMiddleware(Mock())
    
    def test_valid_request_passes(self):
        """Test que una request válida pasa sin problemas."""
        request = self.factory.get('/')
        
        # Mock del get_response que retorna una respuesta válida
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
    
    def test_oversized_request_rejected(self):
        """Test que requests muy grandes son rechazadas."""
        # Crear una request con contenido muy grande
        large_data = 'x' * (15 * 1024 * 1024)  # 15MB
        request = self.factory.post('/', data={'data': large_data})
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 413)  # Request Entity Too Large
    
    def test_suspicious_patterns_detected(self):
        """Test que patrones sospechosos son detectados."""
        # Request con patrón sospechoso (SQL injection)
        request = self.factory.get('/?id=1; DROP TABLE users;')
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 400)  # Bad Request


class AuditLogMiddlewareTest(TestCase):
    """Tests para AuditLogMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AuditLogMiddleware(Mock())
        
        # Configurar logger mock
        self.logger_patcher = patch('todoapi.utils.security_middleware.logger')
        self.mock_logger = self.logger_patcher.start()
    
    def tearDown(self):
        self.logger_patcher.stop()
    
    def test_audit_log_created(self):
        """Test que se crea un log de auditoría."""
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.username = 'testuser'
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        
        # Verificar que se llamó al logger
        self.mock_logger.info.assert_called()
    
    def test_sensitive_data_logged(self):
        """Test que datos sensibles se loggean apropiadamente."""
        request = self.factory.post('/auth/login/', {
            'username': 'testuser',
            'password': 'secret123'
        })
        request.user = Mock()
        request.user.is_authenticated = False
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        
        # Verificar que se loggeó pero sin la contraseña
        call_args = self.mock_logger.info.call_args[0][0]
        self.assertIn('testuser', call_args)
        self.assertNotIn('secret123', call_args)


class IPWhitelistMiddlewareTest(TestCase):
    """Tests para IPWhitelistMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = IPWhitelistMiddleware(Mock())
    
    @patch('todoapi.utils.security_middleware.settings.ADMIN_ALLOWED_IPS', ['127.0.0.1'])
    def test_allowed_ip_passes(self):
        """Test que IPs permitidas pasan."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
    
    @patch('todoapi.utils.security_middleware.settings.ADMIN_ALLOWED_IPS', ['127.0.0.1'])
    def test_blocked_ip_rejected(self):
        """Test que IPs no permitidas son rechazadas."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)  # Forbidden


class BruteForceProtectionMiddlewareTest(TestCase):
    """Tests para BruteForceProtectionMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = BruteForceProtectionMiddleware(Mock())
    
    @patch('todoapi.utils.security_middleware.cache')
    def test_failed_attempts_tracked(self, mock_cache):
        """Test que los intentos fallidos se rastrean."""
        mock_cache.get.return_value = 3  # 3 intentos previos
        
        request = self.factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        def mock_get_response(req):
            response = HttpResponse("Unauthorized")
            response.status_code = 401
            return response
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        
        # Verificar que se incrementó el contador
        mock_cache.set.assert_called()
    
    @patch('todoapi.utils.security_middleware.cache')
    def test_brute_force_blocked(self, mock_cache):
        """Test que se bloquea después de muchos intentos."""
        mock_cache.get.return_value = 6  # Más de 5 intentos
        
        request = self.factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        def mock_get_response(req):
            return HttpResponse("OK")
        
        self.middleware.get_response = mock_get_response
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)  # Too Many Requests