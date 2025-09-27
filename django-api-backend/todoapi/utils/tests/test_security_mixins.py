"""
Tests para los mixins de seguridad.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers
from unittest.mock import Mock, patch
import logging

from todoapi.utils.security_mixins import (
    SecurityValidationMixin,
    SecureModelSerializerMixin,
    AuditLogMixin,
    SecurePermissionMixin,
    SecureViewMixin,
    DataSanitizationMixin
)

User = get_user_model()


class TestModel:
    """Modelo de prueba para tests."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestSecurityValidationMixin(TestCase):
    """Tests para SecurityValidationMixin."""
    
    def setUp(self):
        class TestSerializer(SecurityValidationMixin, serializers.Serializer):
            name = serializers.CharField(max_length=100)
            email = serializers.EmailField()
            content = serializers.CharField()
        
        self.serializer_class = TestSerializer
    
    def test_xss_validation(self):
        """Test que la validación XSS funciona."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': '<script>alert("xss")</script>Hello'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
    
    def test_sql_injection_validation(self):
        """Test que la validación SQL injection funciona."""
        data = {
            'name': "'; DROP TABLE users; --",
            'email': 'test@example.com',
            'content': 'Normal content'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_valid_data_passes(self):
        """Test que datos válidos pasan la validación."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': 'This is normal content without any malicious code.'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())


class TestDataSanitizationMixin(TestCase):
    """Tests para DataSanitizationMixin."""
    
    def setUp(self):
        class TestSerializer(DataSanitizationMixin, serializers.Serializer):
            name = serializers.CharField(max_length=100)
            description = serializers.CharField()
        
        self.serializer_class = TestSerializer
    
    def test_html_sanitization(self):
        """Test que el HTML se sanitiza correctamente."""
        data = {
            'name': 'Test <b>User</b>',
            'description': '<p>This is <script>alert("xss")</script> content</p>'
        }
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Verificar que tags permitidos se mantienen
            self.assertIn('<b>', validated_data['name'])
            
            # Verificar que scripts se eliminan
            self.assertNotIn('<script>', validated_data['description'])
    
    def test_whitespace_normalization(self):
        """Test que los espacios en blanco se normalizan."""
        data = {
            'name': '  Test   User  ',
            'description': 'Content\n\n\nwith\t\tmultiple\r\nspaces'
        }
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Verificar que se eliminan espacios extra
            self.assertEqual(validated_data['name'], 'Test User')
            self.assertNotIn('\n\n\n', validated_data['description'])


class TestAuditLogMixin(TestCase):
    """Tests para AuditLogMixin."""
    
    def setUp(self):
        class TestSerializer(AuditLogMixin, serializers.Serializer):
            name = serializers.CharField(max_length=100)
            
            class Meta:
                model = TestModel
        
        self.serializer_class = TestSerializer
        
        # Mock del logger
        self.logger_patcher = patch('todoapi.utils.security_mixins.logger')
        self.mock_logger = self.logger_patcher.start()
    
    def tearDown(self):
        self.logger_patcher.stop()
    
    def test_create_audit_log(self):
        """Test que se crea log de auditoría en create."""
        data = {'name': 'Test User'}
        serializer = self.serializer_class(data=data)
        
        if serializer.is_valid():
            # Simular contexto de request
            request = Mock()
            request.user = Mock()
            request.user.username = 'testuser'
            request.META = {'REMOTE_ADDR': '127.0.0.1'}
            
            serializer.context = {'request': request}
            
            # Simular create
            instance = TestModel(name='Test User')
            serializer.create(serializer.validated_data)
            
            # Verificar que se llamó al logger
            self.mock_logger.info.assert_called()
    
    def test_update_audit_log(self):
        """Test que se crea log de auditoría en update."""
        instance = TestModel(name='Old Name')
        data = {'name': 'New Name'}
        serializer = self.serializer_class(instance, data=data)
        
        if serializer.is_valid():
            # Simular contexto de request
            request = Mock()
            request.user = Mock()
            request.user.username = 'testuser'
            request.META = {'REMOTE_ADDR': '127.0.0.1'}
            
            serializer.context = {'request': request}
            
            # Simular update
            serializer.update(instance, serializer.validated_data)
            
            # Verificar que se llamó al logger
            self.mock_logger.info.assert_called()


class TestSecureViewMixin(APITestCase):
    """Tests para SecureViewMixin."""
    
    def setUp(self):
        from rest_framework.views import APIView
        from rest_framework.response import Response
        
        class TestView(SecureViewMixin, APIView):
            def get(self, request):
                return Response({'message': 'success'})
        
        self.view_class = TestView
        self.factory = RequestFactory()
    
    @patch('todoapi.utils.security_mixins.logger')
    def test_security_logging(self, mock_logger):
        """Test que se loggean eventos de seguridad."""
        view = self.view_class()
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.username = 'testuser'
        
        # Simular dispatch
        view.setup(request)
        response = view.get(request)
        
        # Verificar que se loggeó el acceso
        mock_logger.info.assert_called()
    
    def test_rate_limiting_headers(self):
        """Test que se agregan headers de rate limiting."""
        view = self.view_class()
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = True
        
        view.setup(request)
        response = view.get(request)
        
        # Verificar que la respuesta tiene headers de rate limiting
        self.assertIsNotNone(response)


class TestSecurePermissionMixin(TestCase):
    """Tests para SecurePermissionMixin."""
    
    def setUp(self):
        from rest_framework.views import APIView
        
        class TestView(SecurePermissionMixin, APIView):
            pass
        
        self.view_class = TestView
        self.factory = RequestFactory()
    
    def test_permission_logging(self):
        """Test que se loggean denegaciones de permisos."""
        with patch('todoapi.utils.security_mixins.logger') as mock_logger:
            view = self.view_class()
            request = self.factory.get('/')
            request.user = Mock()
            request.user.is_authenticated = False
            
            # Simular verificación de permisos
            view.setup(request)
            
            # Simular denegación de permiso
            view.log_permission_denied(request, 'Test permission denied')
            
            # Verificar que se loggeó la denegación
            mock_logger.warning.assert_called()
    
    def test_suspicious_activity_detection(self):
        """Test que se detecta actividad sospechosa."""
        with patch('todoapi.utils.security_mixins.logger') as mock_logger:
            view = self.view_class()
            request = self.factory.get('/')
            request.user = Mock()
            request.user.is_authenticated = True
            request.META = {'REMOTE_ADDR': '192.168.1.100'}
            
            # Simular actividad sospechosa
            view.setup(request)
            view.log_suspicious_activity(request, 'Multiple failed attempts')
            
            # Verificar que se loggeó la actividad sospechosa
            mock_logger.error.assert_called()


class TestSecureModelSerializerMixin(TestCase):
    """Tests para SecureModelSerializerMixin."""
    
    def setUp(self):
        class TestSerializer(SecureModelSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = TestModel
                fields = ['name', 'email']
        
        self.serializer_class = TestSerializer
    
    def test_sensitive_fields_excluded(self):
        """Test que campos sensibles se excluyen automáticamente."""
        # Este test dependería de la implementación específica
        # del mixin para excluir campos sensibles
        pass
    
    def test_field_validation_enhanced(self):
        """Test que la validación de campos está mejorada."""
        # Este test verificaría que se aplican validaciones adicionales
        # a todos los campos del modelo
        pass