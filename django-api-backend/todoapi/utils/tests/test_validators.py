"""
Tests comprehensivos para los validators de todoapi.utils.validators
"""

import tempfile
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, Mock

from todoapi.utils.validators import (
    validate_ruc_peruano, validate_dni_peruano, validate_imei, validate_icc,
    validate_celular_peruano, validate_placa_peruana, get_all_validators,
    InputSanitizer, FileValidator, TextValidator, URLValidator,
    sanitize_input, sanitize_html_input, validate_safe_text,
    validate_file_upload, validate_safe_url, _validate_ruc_check_digit,
    _validate_luhn_algorithm
)


class ValidateRucPeruanoTest(TestCase):
    """Tests para validate_ruc_peruano"""
    
    def test_valid_ruc(self):
        """Test con RUC válido"""
        # RUC válido de ejemplo
        valid_ruc = "20123456789"
        try:
            validate_ruc_peruano(valid_ruc)
        except ValidationError:
            self.fail("validate_ruc_peruano raised ValidationError unexpectedly!")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_ruc_peruano("")
        validate_ruc_peruano(None)
    
    def test_invalid_length_short(self):
        """Test con RUC muy corto"""
        with self.assertRaises(ValidationError) as cm:
            validate_ruc_peruano("123456789")
        self.assertEqual(cm.exception.code, 'invalid_ruc_length')
    
    def test_invalid_length_long(self):
        """Test con RUC muy largo"""
        with self.assertRaises(ValidationError) as cm:
            validate_ruc_peruano("123456789012")
        self.assertEqual(cm.exception.code, 'invalid_ruc_length')
    
    def test_all_same_digits(self):
        """Test con todos los dígitos iguales"""
        with self.assertRaises(ValidationError) as cm:
            validate_ruc_peruano("11111111111")
        self.assertEqual(cm.exception.code, 'invalid_ruc_pattern')
    
    def test_ruc_with_non_digits(self):
        """Test con RUC que contiene caracteres no numéricos"""
        with self.assertRaises(ValidationError):
            validate_ruc_peruano("201-234-567-89")
    
    def test_invalid_check_digit(self):
        """Test con dígito verificador inválido"""
        with self.assertRaises(ValidationError) as cm:
            validate_ruc_peruano("20123456780")  # Último dígito incorrecto
        self.assertEqual(cm.exception.code, 'invalid_ruc_checksum')


class ValidateRucCheckDigitTest(TestCase):
    """Tests para _validate_ruc_check_digit"""
    
    def test_valid_check_digit(self):
        """Test con dígito verificador válido"""
        # Usar un RUC conocido válido
        result = _validate_ruc_check_digit("20123456789")
        self.assertTrue(result)
    
    def test_invalid_check_digit(self):
        """Test con dígito verificador inválido"""
        result = _validate_ruc_check_digit("20123456780")
        self.assertFalse(result)


class ValidateDniPeruanoTest(TestCase):
    """Tests para validate_dni_peruano"""
    
    def test_valid_dni(self):
        """Test con DNI válido"""
        validate_dni_peruano("12345678")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_dni_peruano("")
        validate_dni_peruano(None)
    
    def test_invalid_length_short(self):
        """Test con DNI muy corto"""
        with self.assertRaises(ValidationError) as cm:
            validate_dni_peruano("1234567")
        self.assertEqual(cm.exception.code, 'invalid_dni_length')
    
    def test_invalid_length_long(self):
        """Test con DNI muy largo"""
        with self.assertRaises(ValidationError) as cm:
            validate_dni_peruano("123456789")
        self.assertEqual(cm.exception.code, 'invalid_dni_length')
    
    def test_all_same_digits(self):
        """Test con todos los dígitos iguales"""
        with self.assertRaises(ValidationError) as cm:
            validate_dni_peruano("11111111")
        self.assertEqual(cm.exception.code, 'invalid_dni_pattern')
    
    def test_dni_with_non_digits(self):
        """Test con DNI que contiene caracteres no numéricos"""
        with self.assertRaises(ValidationError):
            validate_dni_peruano("1234-5678")


class ValidateImeiTest(TestCase):
    """Tests para validate_imei"""
    
    def test_valid_imei(self):
        """Test con IMEI válido"""
        # IMEI válido de ejemplo (usando algoritmo Luhn)
        validate_imei("123456789012345")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_imei("")
        validate_imei(None)
    
    def test_invalid_length_short(self):
        """Test con IMEI muy corto"""
        with self.assertRaises(ValidationError) as cm:
            validate_imei("12345678901234")
        self.assertEqual(cm.exception.code, 'invalid_imei_length')
    
    def test_invalid_length_long(self):
        """Test con IMEI muy largo"""
        with self.assertRaises(ValidationError) as cm:
            validate_imei("1234567890123456")
        self.assertEqual(cm.exception.code, 'invalid_imei_length')
    
    def test_imei_with_non_digits(self):
        """Test con IMEI que contiene caracteres no numéricos"""
        with self.assertRaises(ValidationError):
            validate_imei("123456789012abc")
    
    @patch('todoapi.utils.validators._validate_luhn_algorithm')
    def test_invalid_luhn_checksum(self, mock_luhn):
        """Test con checksum Luhn inválido"""
        mock_luhn.return_value = False
        with self.assertRaises(ValidationError) as cm:
            validate_imei("123456789012345")
        self.assertEqual(cm.exception.code, 'invalid_imei_checksum')


class ValidateLuhnAlgorithmTest(TestCase):
    """Tests para _validate_luhn_algorithm"""
    
    def test_valid_luhn_number(self):
        """Test con número válido según algoritmo Luhn"""
        # Número de prueba válido
        result = _validate_luhn_algorithm("4532015112830366")
        self.assertTrue(result)
    
    def test_invalid_luhn_number(self):
        """Test con número inválido según algoritmo Luhn"""
        result = _validate_luhn_algorithm("4532015112830367")
        self.assertFalse(result)


class ValidateIccTest(TestCase):
    """Tests para validate_icc"""
    
    def test_valid_icc_19_digits(self):
        """Test con ICC válido de 19 dígitos"""
        validate_icc("1234567890123456789")
    
    def test_valid_icc_20_digits(self):
        """Test con ICC válido de 20 dígitos"""
        validate_icc("12345678901234567890")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_icc("")
        validate_icc(None)
    
    def test_invalid_length_short(self):
        """Test con ICC muy corto"""
        with self.assertRaises(ValidationError) as cm:
            validate_icc("123456789012345678")
        self.assertEqual(cm.exception.code, 'invalid_icc_length')
    
    def test_invalid_length_long(self):
        """Test con ICC muy largo"""
        with self.assertRaises(ValidationError) as cm:
            validate_icc("123456789012345678901")
        self.assertEqual(cm.exception.code, 'invalid_icc_length')
    
    def test_icc_with_non_digits(self):
        """Test con ICC que contiene caracteres no numéricos"""
        with self.assertRaises(ValidationError):
            validate_icc("123456789012345678a")


class ValidateCelularPeruanoTest(TestCase):
    """Tests para validate_celular_peruano"""
    
    def test_valid_celular_9_digits(self):
        """Test con celular válido de 9 dígitos"""
        validate_celular_peruano("987654321")
    
    def test_valid_celular_with_prefix(self):
        """Test con celular válido con prefijo +51"""
        validate_celular_peruano("+51987654321")
    
    def test_valid_celular_with_country_code(self):
        """Test con celular válido con código de país 51"""
        validate_celular_peruano("51987654321")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_celular_peruano("")
        validate_celular_peruano(None)
    
    def test_invalid_first_digit(self):
        """Test con primer dígito inválido"""
        with self.assertRaises(ValidationError) as cm:
            validate_celular_peruano("187654321")
        self.assertEqual(cm.exception.code, 'invalid_celular_format')
    
    def test_invalid_length(self):
        """Test con longitud inválida"""
        with self.assertRaises(ValidationError) as cm:
            validate_celular_peruano("98765432")
        self.assertEqual(cm.exception.code, 'invalid_celular_format')
    
    def test_celular_with_letters(self):
        """Test con celular que contiene letras"""
        with self.assertRaises(ValidationError):
            validate_celular_peruano("987654abc")


class ValidatePlacaPeruanaTest(TestCase):
    """Tests para validate_placa_peruana"""
    
    def test_valid_placa_old_format(self):
        """Test con placa válida formato antiguo"""
        validate_placa_peruana("ABC-123")
    
    def test_valid_placa_new_format(self):
        """Test con placa válida formato nuevo"""
        validate_placa_peruana("ABC-1234")
    
    def test_empty_value(self):
        """Test con valor vacío"""
        validate_placa_peruana("")
        validate_placa_peruana(None)
    
    def test_invalid_format(self):
        """Test con formato inválido"""
        with self.assertRaises(ValidationError) as cm:
            validate_placa_peruana("AB-123")
        self.assertEqual(cm.exception.code, 'invalid_placa_format')
    
    def test_invalid_characters(self):
        """Test con caracteres inválidos"""
        with self.assertRaises(ValidationError):
            validate_placa_peruana("ABC-12@")


class GetAllValidatorsTest(TestCase):
    """Tests para get_all_validators"""
    
    def test_returns_dict_with_validators(self):
        """Test que retorna diccionario con todos los validators"""
        validators = get_all_validators()
        
        self.assertIsInstance(validators, dict)
        self.assertIn('ruc', validators)
        self.assertIn('dni', validators)
        self.assertIn('imei', validators)
        self.assertIn('icc', validators)
        self.assertIn('celular', validators)
        self.assertIn('placa', validators)
    
    def test_validators_are_callable(self):
        """Test que todos los validators son callable"""
        validators = get_all_validators()
        
        for name, validator in validators.items():
            self.assertTrue(callable(validator), f"Validator {name} is not callable")


class InputSanitizerTest(TestCase):
    """Tests para InputSanitizer"""
    
    def test_sanitize_html_basic(self):
        """Test sanitización HTML básica"""
        html = "<p>Hello <strong>world</strong></p>"
        result = InputSanitizer.sanitize_html(html)
        self.assertEqual(result, "<p>Hello <strong>world</strong></p>")
    
    def test_sanitize_html_removes_script(self):
        """Test que remueve scripts"""
        html = "<p>Hello</p><script>alert('xss')</script>"
        result = InputSanitizer.sanitize_html(html)
        self.assertNotIn("<script>", result)
        self.assertIn("<p>Hello</p>", result)
    
    def test_sanitize_html_empty_input(self):
        """Test con input vacío"""
        result = InputSanitizer.sanitize_html("")
        self.assertEqual(result, "")
        
        result = InputSanitizer.sanitize_html(None)
        self.assertEqual(result, "")
    
    def test_sanitize_text_basic(self):
        """Test sanitización de texto básica"""
        text = "Hello world!"
        result = InputSanitizer.sanitize_text(text)
        self.assertEqual(result, "Hello world!")
    
    def test_sanitize_text_removes_html(self):
        """Test que remueve HTML del texto"""
        text = "Hello <script>alert('xss')</script> world"
        result = InputSanitizer.sanitize_text(text)
        self.assertEqual(result, "Hello  world")
    
    def test_sanitize_text_empty_input(self):
        """Test sanitize_text con input vacío"""
        result = InputSanitizer.sanitize_text("")
        self.assertEqual(result, "")
        
        result = InputSanitizer.sanitize_text(None)
        self.assertEqual(result, "")
    
    def test_sanitize_filename_basic(self):
        """Test sanitización de nombre de archivo básica"""
        filename = "document.pdf"
        result = InputSanitizer.sanitize_filename(filename)
        self.assertEqual(result, "document.pdf")
    
    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test que remueve caracteres peligrosos del filename"""
        filename = "../../../etc/passwd"
        result = InputSanitizer.sanitize_filename(filename)
        self.assertNotIn("../", result)
        self.assertNotIn("/", result)
    
    def test_sanitize_filename_empty_input(self):
        """Test sanitize_filename con input vacío"""
        result = InputSanitizer.sanitize_filename("")
        self.assertEqual(result, "")
        
        result = InputSanitizer.sanitize_filename(None)
        self.assertEqual(result, "")


class FileValidatorTest(TestCase):
    """Tests para FileValidator"""
    
    def setUp(self):
        # Crear archivo de prueba
        self.test_file = SimpleUploadedFile(
            "test.txt",
            b"file content",
            content_type="text/plain"
        )
    
    def test_validate_file_type_allowed(self):
        """Test validación de tipo de archivo permitido"""
        # Mock file with allowed type
        mock_file = Mock()
        mock_file.content_type = "image/jpeg"
        mock_file.name = "test.jpg"
        
        try:
            FileValidator.validate_file_type(mock_file)
        except ValidationError:
            self.fail("validate_file_type raised ValidationError unexpectedly!")
    
    def test_validate_file_type_not_allowed(self):
        """Test validación de tipo de archivo no permitido"""
        mock_file = Mock()
        mock_file.content_type = "application/x-executable"
        mock_file.name = "malware.exe"
        
        with self.assertRaises(ValidationError) as cm:
            FileValidator.validate_file_type(mock_file)
        self.assertEqual(cm.exception.code, 'invalid_file_type')
    
    def test_validate_file_size_allowed(self):
        """Test validación de tamaño de archivo permitido"""
        mock_file = Mock()
        mock_file.size = 1024 * 1024  # 1MB
        
        try:
            FileValidator.validate_file_size(mock_file)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError unexpectedly!")
    
    def test_validate_file_size_too_large(self):
        """Test validación de archivo muy grande"""
        mock_file = Mock()
        mock_file.size = 100 * 1024 * 1024  # 100MB
        
        with self.assertRaises(ValidationError) as cm:
            FileValidator.validate_file_size(mock_file)
        self.assertEqual(cm.exception.code, 'file_too_large')


class TextValidatorTest(TestCase):
    """Tests para TextValidator"""
    
    def test_validate_no_sql_injection_safe_text(self):
        """Test texto seguro sin SQL injection"""
        safe_text = "Hello world, this is safe text"
        try:
            TextValidator.validate_no_sql_injection(safe_text)
        except ValidationError:
            self.fail("validate_no_sql_injection raised ValidationError unexpectedly!")
    
    def test_validate_no_sql_injection_detects_union(self):
        """Test detección de SQL injection con UNION"""
        malicious_text = "Hello UNION SELECT * FROM users"
        with self.assertRaises(ValidationError) as cm:
            TextValidator.validate_no_sql_injection(malicious_text)
        self.assertEqual(cm.exception.code, 'sql_injection_detected')
    
    def test_validate_no_sql_injection_detects_comments(self):
        """Test detección de comentarios SQL"""
        malicious_text = "Hello -- comment"
        with self.assertRaises(ValidationError) as cm:
            TextValidator.validate_no_sql_injection(malicious_text)
        self.assertEqual(cm.exception.code, 'sql_injection_detected')
    
    def test_validate_no_xss_safe_text(self):
        """Test texto seguro sin XSS"""
        safe_text = "Hello world, this is safe text"
        try:
            TextValidator.validate_no_xss(safe_text)
        except ValidationError:
            self.fail("validate_no_xss raised ValidationError unexpectedly!")
    
    def test_validate_no_xss_detects_script(self):
        """Test detección de XSS con script"""
        malicious_text = "Hello <script>alert('xss')</script>"
        with self.assertRaises(ValidationError) as cm:
            TextValidator.validate_no_xss(malicious_text)
        self.assertEqual(cm.exception.code, 'xss_detected')
    
    def test_validate_no_xss_detects_javascript(self):
        """Test detección de javascript: URLs"""
        malicious_text = "Click here: javascript:alert('xss')"
        with self.assertRaises(ValidationError) as cm:
            TextValidator.validate_no_xss(malicious_text)
        self.assertEqual(cm.exception.code, 'xss_detected')
    
    def test_validate_safe_text_combines_validations(self):
        """Test que validate_safe_text combina todas las validaciones"""
        safe_text = "Hello world, this is safe text"
        try:
            TextValidator.validate_safe_text(safe_text)
        except ValidationError:
            self.fail("validate_safe_text raised ValidationError unexpectedly!")
        
        # Test SQL injection detection
        with self.assertRaises(ValidationError):
            TextValidator.validate_safe_text("Hello UNION SELECT")
        
        # Test XSS detection
        with self.assertRaises(ValidationError):
            TextValidator.validate_safe_text("Hello <script>alert('xss')</script>")


class URLValidatorTest(TestCase):
    """Tests para URLValidator"""
    
    def test_validate_safe_url_https(self):
        """Test URL HTTPS válida"""
        safe_url = "https://example.com/path"
        try:
            URLValidator.validate_safe_url(safe_url)
        except ValidationError:
            self.fail("validate_safe_url raised ValidationError unexpectedly!")
    
    def test_validate_safe_url_http(self):
        """Test URL HTTP válida"""
        safe_url = "http://example.com/path"
        try:
            URLValidator.validate_safe_url(safe_url)
        except ValidationError:
            self.fail("validate_safe_url raised ValidationError unexpectedly!")
    
    def test_validate_safe_url_invalid_scheme(self):
        """Test URL con esquema inválido"""
        unsafe_url = "ftp://example.com/file"
        with self.assertRaises(ValidationError) as cm:
            URLValidator.validate_safe_url(unsafe_url)
        self.assertEqual(cm.exception.code, 'invalid_url_scheme')
    
    def test_validate_safe_url_blocked_domain_localhost(self):
        """Test URL con dominio bloqueado (localhost)"""
        unsafe_url = "http://localhost/admin"
        with self.assertRaises(ValidationError) as cm:
            URLValidator.validate_safe_url(unsafe_url)
        self.assertEqual(cm.exception.code, 'blocked_domain')
    
    def test_validate_safe_url_blocked_domain_private_ip(self):
        """Test URL con IP privada bloqueada"""
        unsafe_url = "http://192.168.1.1/admin"
        with self.assertRaises(ValidationError) as cm:
            URLValidator.validate_safe_url(unsafe_url)
        self.assertEqual(cm.exception.code, 'blocked_domain')
    
    def test_validate_safe_url_malformed(self):
        """Test URL malformada"""
        malformed_url = "not-a-url"
        with self.assertRaises(ValidationError) as cm:
            URLValidator.validate_safe_url(malformed_url)
        self.assertEqual(cm.exception.code, 'invalid_url_format')


class UtilityFunctionsTest(TestCase):
    """Tests para funciones utilitarias"""
    
    def test_sanitize_input(self):
        """Test función sanitize_input"""
        result = sanitize_input("Hello <script>alert('xss')</script> world")
        self.assertNotIn("<script>", result)
    
    def test_sanitize_html_input(self):
        """Test función sanitize_html_input"""
        result = sanitize_html_input("<p>Hello <strong>world</strong></p>")
        self.assertEqual(result, "<p>Hello <strong>world</strong></p>")
    
    def test_validate_safe_text_function(self):
        """Test función validate_safe_text"""
        try:
            validate_safe_text("Hello world")
        except ValidationError:
            self.fail("validate_safe_text raised ValidationError unexpectedly!")
    
    def test_validate_file_upload(self):
        """Test función validate_file_upload"""
        mock_file = Mock()
        mock_file.content_type = "image/jpeg"
        mock_file.name = "test.jpg"
        mock_file.size = 1024
        
        try:
            validate_file_upload(mock_file)
        except ValidationError:
            self.fail("validate_file_upload raised ValidationError unexpectedly!")
    
    def test_validate_safe_url_function(self):
        """Test función validate_safe_url"""
        result = validate_safe_url("https://example.com")
        self.assertEqual(result, "https://example.com")