"""
Configuraciones de seguridad centralizadas para el proyecto Django API.
Este archivo contiene todas las configuraciones relacionadas con seguridad.
"""

import os
from django.conf import settings

# =============================================================================
# CONFIGURACIONES DE SEGURIDAD GENERAL
# =============================================================================

# Configuración de HTTPS y SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de cookies seguras
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hora

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# =============================================================================
# HEADERS DE SEGURIDAD
# =============================================================================

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
}

# Content Security Policy
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]

# =============================================================================
# CONFIGURACIONES DE VALIDACIÓN Y SANITIZACIÓN
# =============================================================================

# Configuración de archivos permitidos
ALLOWED_FILE_TYPES = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'documents': ['pdf', 'doc', 'docx', 'txt'],
    'spreadsheets': ['xls', 'xlsx', 'csv'],
}

# Tamaños máximos de archivos (en bytes)
MAX_FILE_SIZES = {
    'image': 5 * 1024 * 1024,  # 5MB
    'document': 10 * 1024 * 1024,  # 10MB
    'default': 2 * 1024 * 1024,  # 2MB
}

# Configuración de validación de texto
TEXT_VALIDATION = {
    'max_length': 10000,
    'min_length': 1,
    'allowed_tags': ['b', 'i', 'u', 'strong', 'em'],
    'strip_tags': True,
}

# Configuración de validación de URLs
URL_VALIDATION = {
    'allowed_schemes': ['http', 'https'],
    'allowed_domains': [],  # Lista vacía = todos los dominios permitidos
    'max_length': 2048,
}

# =============================================================================
# CONFIGURACIONES DE RATE LIMITING
# =============================================================================

RATE_LIMIT_SETTINGS = {
    'login': '5/min',
    'api': '100/min',
    'password_reset': '3/hour',
    'registration': '10/hour',
}

# =============================================================================
# CONFIGURACIONES DE IP WHITELIST
# =============================================================================

# IPs permitidas para acceso administrativo
ADMIN_ALLOWED_IPS = [
    '127.0.0.1',
    '::1',
    # Agregar IPs de administradores aquí
]

# IPs bloqueadas
BLOCKED_IPS = [
    # Agregar IPs bloqueadas aquí
]

# =============================================================================
# CONFIGURACIONES DE LOGGING DE SEGURIDAD
# =============================================================================

SECURITY_LOG_EVENTS = {
    'login_attempt': True,
    'login_success': True,
    'login_failure': True,
    'password_change': True,
    'permission_denied': True,
    'suspicious_activity': True,
    'file_upload': True,
    'admin_access': True,
}

# =============================================================================
# CONFIGURACIONES DE AUTENTICACIÓN
# =============================================================================

# Configuración de JWT
JWT_SECURITY = {
    'access_token_lifetime': 15,  # minutos
    'refresh_token_lifetime': 7,  # días
    'rotate_refresh_tokens': True,
    'blacklist_after_rotation': True,
}

# Configuración de contraseñas
PASSWORD_SECURITY = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_numbers': True,
    'require_special_chars': True,
    'max_age_days': 90,
}

# =============================================================================
# CONFIGURACIONES DE BRUTE FORCE PROTECTION
# =============================================================================

BRUTE_FORCE_PROTECTION = {
    'max_attempts': 5,
    'lockout_duration': 300,  # 5 minutos en segundos
    'track_ip': True,
    'track_user': True,
}

# =============================================================================
# CONFIGURACIONES DE MONITOREO
# =============================================================================

SECURITY_MONITORING = {
    'log_failed_requests': True,
    'log_suspicious_patterns': True,
    'alert_on_multiple_failures': True,
    'max_request_size': 10 * 1024 * 1024,  # 10MB
}

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_security_setting(key, default=None):
    """
    Obtiene una configuración de seguridad con valor por defecto.
    """
    return globals().get(key, default)

def is_ip_allowed(ip_address, context='general'):
    """
    Verifica si una IP está permitida según el contexto.
    """
    if context == 'admin':
        return ip_address in ADMIN_ALLOWED_IPS
    
    return ip_address not in BLOCKED_IPS

def get_max_file_size(file_type='default'):
    """
    Obtiene el tamaño máximo permitido para un tipo de archivo.
    """
    return MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['default'])

def is_file_type_allowed(extension, category='documents'):
    """
    Verifica si un tipo de archivo está permitido.
    """
    return extension.lower() in ALLOWED_FILE_TYPES.get(category, [])