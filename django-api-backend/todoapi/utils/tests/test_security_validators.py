"""
Tests para los validadores de seguridad.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import serializers
from unittest.mock import Mock, patch
import tempfile
import os

from todoapi.utils.validators import (
    InputSanitizer,
    FileValidator,
    TextValidator,
    URLValidator,
    EmailValidator,
    PasswordValidator,
    sanitize_input,
    validate_file_content,
    is_safe_url
)


class TestInputSanitizer(TestCase):
    """Tests para InputSanitizer."""
    
    def setUp(self):
        self.sanitizer = InputSanitizer()
    
    def test_html_sanitization(self):
        """Test que el HTML se sanitiza correctamente."""
        dirty_html = '<script>alert("xss")</script><p>Safe content</p>'
        clean_html = self.sanitizer.sanitize_html(dirty_html)
        
        self.assertNotIn('<script>', clean_html)
        self.assertIn('<p>', clean_html)
        self.assertIn('Safe content', clean_html)
    
    def test_sql_injection_detection(self):
        """Test que se detectan intentos de SQL injection."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "admin'/*",
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(ValidationError):
                self.sanitizer.validate_sql_injection(malicious_input)
    
    def test_xss_detection(self):
        """Test que se detectan intentos de XSS."""
        xss_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(1)">',
            '<svg onload="alert(1)">',
        ]
        
        for xss_input in xss_inputs:
            with self.assertRaises(ValidationError):
                self.sanitizer.validate_xss(xss_input)
    
    def test_safe_input_passes(self):
        """Test que input seguro pasa las validaciones."""
        safe_inputs = [
            'Normal text content',
            'Email: user@example.com',
            'Phone: +51 999 888 777',
            'Address: Av. Lima 123, Lima',
        ]
        
        for safe_input in safe_inputs:
            # No debería lanzar excepción
            self.sanitizer.validate_sql_injection(safe_input)
            self.sanitizer.validate_xss(safe_input)
    
    def test_normalize_whitespace(self):
        """Test que los espacios en blanco se normalizan."""
        text_with_spaces = '  Multiple   spaces\n\n\nand\t\ttabs  '
        normalized = self.sanitizer.normalize_whitespace(text_with_spaces)
        
        self.assertEqual(normalized, 'Multiple spaces and tabs')


class TestFileValidator(TestCase):
    """Tests para FileValidator."""
    
    def setUp(self):
        self.validator = FileValidator()
    
    def test_file_extension_validation(self):
        """Test validación de extensiones de archivo."""
        # Extensiones permitidas
        allowed_files = ['document.pdf', 'image.jpg', 'data.csv']
        for filename in allowed_files:
            # No debería lanzar excepción
            self.validator.validate_file_extension(filename, 'documents')
        
        # Extensiones no permitidas
        with self.assertRaises(ValidationError):
            self.validator.validate_file_extension('malware.exe', 'documents')
    
    def test_file_size_validation(self):
        """Test validación de tamaño de archivo."""
        # Crear archivo temporal pequeño
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'Small file content')
            temp_file_path = temp_file.name
        
        try:
            # No debería lanzar excepción para archivo pequeño
            self.validator.validate_file_size(temp_file_path, max_size=1024)
            
            # Debería lanzar excepción para límite muy pequeño
            with self.assertRaises(ValidationError):
                self.validator.validate_file_size(temp_file_path, max_size=1)
        finally:
            os.unlink(temp_file_path)
    
    @patch('magic.from_file')
    def test_file_content_validation(self, mock_magic):
        """Test validación de contenido de archivo."""
        # Mock para simular tipo MIME
        mock_magic.return_value = 'application/pdf'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4 fake pdf content')
            temp_file_path = temp_file.name
        
        try:
            # No debería lanzar excepción para PDF válido
            self.validator.validate_file_content(temp_file_path)
            
            # Simular archivo malicioso
            mock_magic.return_value = 'application/x-executable'
            with self.assertRaises(ValidationError):
                self.validator.validate_file_content(temp_file_path)
        finally:
            os.unlink(temp_file_path)


class TestTextValidator(TestCase):
    """Tests para TextValidator."""
    
    def setUp(self):
        self.validator = TextValidator()
    
    def test_length_validation(self):
        """Test validación de longitud de texto."""
        # Texto válido
        valid_text = 'This is a valid text with appropriate length.'
        self.validator.validate_length(valid_text, min_length=10, max_length=100)
        
        # Texto muy corto
        with self.assertRaises(ValidationError):
            self.validator.validate_length('Short', min_length=10, max_length=100)
        
        # Texto muy largo
        long_text = 'x' * 200
        with self.assertRaises(ValidationError):
            self.validator.validate_length(long_text, min_length=10, max_length=100)
    
    def test_profanity_validation(self):
        """Test validación de contenido inapropiado."""
        # Texto limpio
        clean_text = 'This is appropriate content for all audiences.'
        self.validator.validate_profanity(clean_text)
        
        # Texto con palabras inapropiadas (ejemplo básico)
        inappropriate_words = ['spam', 'scam', 'fraud']
        for word in inappropriate_words:
            text_with_profanity = f'This contains {word} which is inappropriate.'
            with self.assertRaises(ValidationError):
                self.validator.validate_profanity(text_with_profanity)
    
    def test_encoding_validation(self):
        """Test validación de codificación de texto."""
        # Texto UTF-8 válido
        valid_utf8 = 'Texto con acentos: café, niño, corazón'
        self.validator.validate_encoding(valid_utf8)
        
        # Texto con caracteres de control
        with self.assertRaises(ValidationError):
            self.validator.validate_encoding('Text with \x00 null byte')


class TestURLValidator(TestCase):
    """Tests para URLValidator."""
    
    def setUp(self):
        self.validator = URLValidator()
    
    def test_url_scheme_validation(self):
        """Test validación de esquemas de URL."""
        # URLs válidas
        valid_urls = [
            'https://example.com',
            'http://localhost:8000',
            'https://subdomain.example.org/path'
        ]
        
        for url in valid_urls:
            self.validator.validate_url_scheme(url)
        
        # URLs con esquemas no permitidos
        invalid_urls = [
            'ftp://example.com',
            'file:///etc/passwd',
            'javascript:alert(1)'
        ]
        
        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                self.validator.validate_url_scheme(url)
    
    def test_url_domain_validation(self):
        """Test validación de dominios."""
        # Dominio válido
        self.validator.validate_url_domain('https://example.com')
        
        # IP local (debería ser rechazada en producción)
        with self.assertRaises(ValidationError):
            self.validator.validate_url_domain('http://127.0.0.1')
    
    def test_url_length_validation(self):
        """Test validación de longitud de URL."""
        # URL normal
        normal_url = 'https://example.com/path'
        self.validator.validate_url_length(normal_url)
        
        # URL muy larga
        long_path = 'x' * 3000
        long_url = f'https://example.com/{long_path}'
        with self.assertRaises(ValidationError):
            self.validator.validate_url_length(long_url)


class TestPasswordValidator(TestCase):
    """Tests para PasswordValidator."""
    
    def setUp(self):
        self.validator = PasswordValidator()
    
    def test_password_strength_validation(self):
        """Test validación de fortaleza de contraseña."""
        # Contraseña fuerte
        strong_password = 'MyStr0ng!P@ssw0rd'
        self.validator.validate_strength(strong_password)
        
        # Contraseña débil
        weak_passwords = [
            'password',  # Muy común
            '12345678',  # Solo números
            'PASSWORD',  # Solo mayúsculas
            'password123',  # Sin caracteres especiales
            'Pass1!',  # Muy corta
        ]
        
        for weak_password in weak_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate_strength(weak_password)
    
    def test_password_history_validation(self):
        """Test validación de historial de contraseñas."""
        # Simular historial de contraseñas
        password_history = ['OldPassword1!', 'OldPassword2!', 'OldPassword3!']
        
        # Nueva contraseña diferente
        new_password = 'NewPassword4!'
        self.validator.validate_history(new_password, password_history)
        
        # Contraseña repetida
        with self.assertRaises(ValidationError):
            self.validator.validate_history('OldPassword1!', password_history)
    
    def test_password_common_patterns(self):
        """Test validación de patrones comunes."""
        # Patrones comunes que deberían ser rechazados
        common_patterns = [
            'qwerty123',
            'admin123',
            'password123',
            '123456789',
            'abcdefgh',
        ]
        
        for pattern in common_patterns:
            with self.assertRaises(ValidationError):
                self.validator.validate_common_patterns(pattern)


class TestUtilityFunctions(TestCase):
    """Tests para funciones utilitarias."""
    
    def test_sanitize_input_function(self):
        """Test función sanitize_input."""
        dirty_input = '<script>alert("xss")</script>Normal text'
        clean_input = sanitize_input(dirty_input)
        
        self.assertNotIn('<script>', clean_input)
        self.assertIn('Normal text', clean_input)
    
    def test_is_safe_url_function(self):
        """Test función is_safe_url."""
        # URLs seguras
        safe_urls = [
            'https://example.com',
            'http://localhost:8000',
        ]
        
        for url in safe_urls:
            self.assertTrue(is_safe_url(url))
        
        # URLs no seguras
        unsafe_urls = [
            'javascript:alert(1)',
            'ftp://example.com',
            'file:///etc/passwd',
        ]
        
        for url in unsafe_urls:
            self.assertFalse(is_safe_url(url))
    
    @patch('magic.from_file')
    def test_validate_file_content_function(self, mock_magic):
        """Test función validate_file_content."""
        mock_magic.return_value = 'image/jpeg'
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b'fake jpeg content')
            temp_file_path = temp_file.name
        
        try:
            # No debería lanzar excepción para imagen válida
            validate_file_content(temp_file_path)
            
            # Simular archivo ejecutable
            mock_magic.return_value = 'application/x-executable'
            with self.assertRaises(ValidationError):
                validate_file_content(temp_file_path)
        finally:
            os.unlink(temp_file_path)