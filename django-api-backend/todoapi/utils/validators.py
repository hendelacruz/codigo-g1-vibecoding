"""
Custom validators for Peruvian documents, device identifiers, and security validation.
Provides validation for RUC, DNI, IMEI, ICC, Peruvian phone numbers, and security features.
"""

import re
import bleach
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Optional import for file type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


def validate_ruc_peruano(value):
    """
    Validates Peruvian RUC (Registro Único de Contribuyentes).
    RUC must be exactly 11 digits and follow specific format rules.
    
    Args:
        value (str): RUC number to validate
        
    Raises:
        ValidationError: If RUC format is invalid
    """
    if not value:
        return
    
    # Remove any non-digit characters
    ruc = re.sub(r'\D', '', str(value))
    
    # Check if it has exactly 11 digits
    if len(ruc) != 11:
        raise ValidationError(
            _('El RUC debe tener exactamente 11 dígitos.'),
            code='invalid_ruc_length'
        )
    
    # Check if all digits are the same (invalid RUC)
    if len(set(ruc)) == 1:
        raise ValidationError(
            _('El RUC no puede tener todos los dígitos iguales.'),
            code='invalid_ruc_pattern'
        )
    
    # Validate RUC check digit using algorithm
    if not _validate_ruc_check_digit(ruc):
        raise ValidationError(
            _('El RUC ingresado no es válido.'),
            code='invalid_ruc_checksum'
        )


def _validate_ruc_check_digit(ruc):
    """
    Internal function to validate RUC check digit using Peruvian algorithm.
    
    Args:
        ruc (str): 11-digit RUC string
        
    Returns:
        bool: True if check digit is valid
    """
    # RUC validation factors
    factors = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    # Calculate sum
    total = sum(int(ruc[i]) * factors[i] for i in range(10))
    
    # Calculate check digit
    remainder = total % 11
    check_digit = 11 - remainder if remainder >= 2 else remainder
    
    # Compare with last digit
    return check_digit == int(ruc[10])


def validate_dni_peruano(value):
    """
    Validates Peruvian DNI (Documento Nacional de Identidad).
    DNI must be exactly 8 digits.
    
    Args:
        value (str): DNI number to validate
        
    Raises:
        ValidationError: If DNI format is invalid
    """
    if not value:
        return
    
    # Remove any non-digit characters
    dni = re.sub(r'\D', '', str(value))
    
    # Check if it has exactly 8 digits
    if len(dni) != 8:
        raise ValidationError(
            _('El DNI debe tener exactamente 8 dígitos.'),
            code='invalid_dni_length'
        )
    
    # Check if all digits are the same (invalid DNI)
    if len(set(dni)) == 1:
        raise ValidationError(
            _('El DNI no puede tener todos los dígitos iguales.'),
            code='invalid_dni_pattern'
        )
    
    # Check if it starts with 0 (invalid DNI)
    if dni.startswith('0'):
        raise ValidationError(
            _('El DNI no puede comenzar con 0.'),
            code='invalid_dni_start'
        )


def validate_imei(value):
    """
    Validates IMEI (International Mobile Equipment Identity).
    IMEI must be exactly 15 digits and pass Luhn algorithm.
    
    Args:
        value (str): IMEI number to validate
        
    Raises:
        ValidationError: If IMEI format is invalid
    """
    if not value:
        return
    
    # Remove any non-digit characters
    imei = re.sub(r'\D', '', str(value))
    
    # Check if it has exactly 15 digits
    if len(imei) != 15:
        raise ValidationError(
            _('El IMEI debe tener exactamente 15 dígitos.'),
            code='invalid_imei_length'
        )
    
    # Check if all digits are the same (invalid IMEI)
    if len(set(imei)) == 1:
        raise ValidationError(
            _('El IMEI no puede tener todos los dígitos iguales.'),
            code='invalid_imei_pattern'
        )
    
    # Validate using Luhn algorithm
    if not _validate_luhn_algorithm(imei):
        raise ValidationError(
            _('El IMEI ingresado no es válido.'),
            code='invalid_imei_checksum'
        )


def _validate_luhn_algorithm(number):
    """
    Internal function to validate number using Luhn algorithm.
    
    Args:
        number (str): Number string to validate
        
    Returns:
        bool: True if Luhn checksum is valid
    """
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(number) == 0


def validate_icc(value):
    """
    Validates ICC (Integrated Circuit Card Identifier).
    ICC must be exactly 20 characters (digits and letters).
    
    Args:
        value (str): ICC identifier to validate
        
    Raises:
        ValidationError: If ICC format is invalid
    """
    if not value:
        return
    
    # Remove spaces and convert to uppercase
    icc = re.sub(r'\s', '', str(value).upper())
    
    # Check if it has exactly 20 characters
    if len(icc) != 20:
        raise ValidationError(
            _('El ICC debe tener exactamente 20 caracteres.'),
            code='invalid_icc_length'
        )
    
    # Check if it contains only alphanumeric characters
    if not re.match(r'^[A-Z0-9]{20}$', icc):
        raise ValidationError(
            _('El ICC debe contener solo letras y números.'),
            code='invalid_icc_format'
        )
    
    # Check if all characters are the same (invalid ICC)
    if len(set(icc)) == 1:
        raise ValidationError(
            _('El ICC no puede tener todos los caracteres iguales.'),
            code='invalid_icc_pattern'
        )


def validate_celular_peruano(value):
    """
    Validates Peruvian mobile phone numbers.
    Must start with 9 and have exactly 9 digits.
    
    Args:
        value (str): Phone number to validate
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    if not value:
        return
    
    # Remove any non-digit characters
    celular = re.sub(r'\D', '', str(value))
    
    # Check if it has exactly 9 digits
    if len(celular) != 9:
        raise ValidationError(
            _('El número de celular debe tener exactamente 9 dígitos.'),
            code='invalid_celular_length'
        )
    
    # Check if it starts with 9 (Peruvian mobile format)
    if not celular.startswith('9'):
        raise ValidationError(
            _('El número de celular debe comenzar con 9.'),
            code='invalid_celular_start'
        )
    
    # Check if all digits are the same (invalid phone)
    if len(set(celular)) == 1:
        raise ValidationError(
            _('El número de celular no puede tener todos los dígitos iguales.'),
            code='invalid_celular_pattern'
        )
    
    # Validate second digit (must be between 0-9, but typically 0-9 for Peru)
    valid_second_digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if celular[1] not in valid_second_digits:
        raise ValidationError(
            _('El formato del número de celular no es válido.'),
            code='invalid_celular_format'
        )


def validate_placa_peruana(value):
    """
    Validates Peruvian license plates.
    Supports both old format (ABC-123) and new format (ABC-1234).
    
    Args:
        value (str): License plate to validate
        
    Raises:
        ValidationError: If license plate format is invalid
    """
    if not value:
        return
    
    # Remove spaces and convert to uppercase
    placa = re.sub(r'\s', '', str(value).upper())
    
    # Old format: 3 letters + hyphen + 3 digits (ABC-123)
    old_format = re.match(r'^[A-Z]{3}-[0-9]{3}$', placa)
    
    # New format: 3 letters + hyphen + 4 digits (ABC-1234)
    new_format = re.match(r'^[A-Z]{3}-[0-9]{4}$', placa)
    
    if not (old_format or new_format):
        raise ValidationError(
            _('La placa debe tener el formato ABC-123 o ABC-1234.'),
            code='invalid_placa_format'
        )


# Convenience function to get all validators
def get_all_validators():
    """
    Returns a dictionary with all available validators for easy access.
    
    Returns:
        dict: Dictionary mapping validator names to validator functions
    """
    return {
        'ruc_peruano': validate_ruc_peruano,
        'dni_peruano': validate_dni_peruano,
        'imei': validate_imei,
        'icc': validate_icc,
        'celular_peruano': validate_celular_peruano,
        'placa_peruana': validate_placa_peruana,
        'safe_text': validate_safe_text,
        'file_upload': validate_file_upload,
        'safe_url': validate_safe_url,
    }


# ============================================================================
# SECURITY VALIDATORS
# ============================================================================

class InputSanitizer:
    """
    Class to sanitize user input and prevent XSS attacks.
    """
    
    # Allowed HTML tags for rich text fields
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    
    # Allowed HTML attributes
    ALLOWED_ATTRIBUTES = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }
    
    @classmethod
    def sanitize_html(cls, text):
        """
        Sanitize HTML content to prevent XSS attacks.
        """
        if not text:
            return text
        
        return bleach.clean(
            text,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @classmethod
    def sanitize_text(cls, text):
        """
        Sanitize plain text input.
        """
        if not text:
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def sanitize_filename(cls, filename):
        """
        Sanitize filename to prevent directory traversal attacks.
        """
        if not filename:
            return filename
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename


class FileValidator:
    """
    Validator for file uploads.
    """
    
    @staticmethod
    def validate_file_type(file):
        """
        Validate file type using python-magic (if available).
        """
        if not file:
            return
        
        # Get MIME type using python-magic if available
        if HAS_MAGIC:
            try:
                mime_type = magic.from_buffer(file.read(1024), mime=True)
                file.seek(0)  # Reset file pointer
            except Exception:
                raise ValidationError(_('Could not determine file type.'))
        else:
            # Fallback to file extension if magic is not available
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file.name)
            if not mime_type:
                raise ValidationError(_('Could not determine file type.'))
        
        # Check against allowed types
        allowed_types = getattr(settings, 'ALLOWED_FILE_TYPES', [])
        if allowed_types and mime_type not in allowed_types:
            raise ValidationError(
                _('File type not allowed. Allowed types: %(types)s') % {
                    'types': ', '.join(allowed_types)
                }
            )
    
    @staticmethod
    def validate_file_size(file):
        """
        Validate file size.
        """
        if not file:
            return
        
        max_size = getattr(settings, 'MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB default
        
        if file.size > max_size:
            raise ValidationError(
                _('File too large. Maximum size is %(max_size)s MB.') % {
                    'max_size': max_size // (1024 * 1024)
                }
            )


class TextValidator:
    """
    Validator for text input.
    """
    
    # Patterns that might indicate SQL injection attempts
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\b(or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
    ]
    
    # Patterns that might indicate XSS attempts
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
    ]
    
    @classmethod
    def validate_no_sql_injection(cls, text):
        """
        Check for potential SQL injection patterns.
        """
        if not text:
            return
        
        text_lower = text.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                raise ValidationError(_('Invalid input detected.'))
    
    @classmethod
    def validate_no_xss(cls, text):
        """
        Check for potential XSS patterns.
        """
        if not text:
            return
        
        text_lower = text.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                raise ValidationError(_('Invalid input detected.'))
    
    @classmethod
    def validate_safe_text(cls, text):
        """
        Comprehensive text validation.
        """
        cls.validate_no_sql_injection(text)
        cls.validate_no_xss(text)


class URLValidator:
    """
    Validator for URL input.
    """
    
    # Allowed URL schemes
    ALLOWED_SCHEMES = ['http', 'https']
    
    # Blocked domains (for security)
    BLOCKED_DOMAINS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '10.',
        '172.',
        '192.168.',
    ]
    
    @classmethod
    def validate_safe_url(cls, url):
        """
        Validate URL for security.
        """
        if not url:
            return
        
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValidationError(_('Invalid URL format.'))
        
        # Check scheme
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            raise ValidationError(
                _('URL scheme not allowed. Allowed schemes: %(schemes)s') % {
                    'schemes': ', '.join(cls.ALLOWED_SCHEMES)
                }
            )
        
        # Check for blocked domains
        hostname = parsed.hostname or ''
        for blocked in cls.BLOCKED_DOMAINS:
            if hostname.startswith(blocked):
                raise ValidationError(_('URL domain not allowed.'))


# Utility functions for easy use in serializers
def sanitize_input(value):
    """Sanitize text input."""
    return InputSanitizer.sanitize_text(value)


def sanitize_html_input(value):
    """Sanitize HTML input."""
    return InputSanitizer.sanitize_html(value)


def validate_safe_text(value):
    """Validate text for security threats."""
    TextValidator.validate_safe_text(value)
    return value


def validate_file_upload(file):
    """Validate file upload."""
    FileValidator.validate_file_type(file)
    FileValidator.validate_file_size(file)
    return file


def validate_safe_url(url):
    """Validate URL for security."""
    URLValidator.validate_safe_url(url)
    return url