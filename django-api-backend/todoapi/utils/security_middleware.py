"""
Security middleware for additional security headers and protections.
"""

import logging
import time
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache

# Security logger
security_logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add additional security headers to all responses.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        # Add custom security header
        response['X-API-Version'] = '1.0'
        response['X-Security-Policy'] = 'strict'
        
        return response


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate and sanitize incoming requests.
    """
    
    # Suspicious patterns that might indicate attacks
    SUSPICIOUS_PATTERNS = [
        '<script',
        'javascript:',
        'onload=',
        'onerror=',
        'eval(',
        'document.cookie',
        'union select',
        'drop table',
        'insert into',
        'delete from',
        '../',
        '..\\',
        'cmd.exe',
        '/bin/bash',
        'passwd',
        '/etc/',
    ]
    
    # Maximum request size (10MB)
    MAX_REQUEST_SIZE = 10 * 1024 * 1024
    
    def process_request(self, request):
        """Validate incoming request for security threats."""
        
        # Check request size
        if hasattr(request, 'META') and 'CONTENT_LENGTH' in request.META:
            try:
                content_length = int(request.META['CONTENT_LENGTH'])
                if content_length > self.MAX_REQUEST_SIZE:
                    security_logger.warning(
                        f'Request size too large: {content_length} bytes from {self._get_client_ip(request)}'
                    )
                    return HttpResponseForbidden('Request too large')
            except (ValueError, TypeError):
                pass
        
        # Check for suspicious patterns in URL
        if self._contains_suspicious_patterns(request.path):
            security_logger.warning(
                f'Suspicious URL pattern detected: {request.path} from {self._get_client_ip(request)}'
            )
            return HttpResponseForbidden('Invalid request')
        
        # Check for suspicious patterns in query parameters
        if request.GET:
            for key, value in request.GET.items():
                if self._contains_suspicious_patterns(f"{key}={value}"):
                    security_logger.warning(
                        f'Suspicious query parameter: {key}={value} from {self._get_client_ip(request)}'
                    )
                    return HttpResponseForbidden('Invalid request')
        
        # Check User-Agent for known bad bots
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if self._is_suspicious_user_agent(user_agent):
            security_logger.warning(
                f'Suspicious User-Agent: {user_agent} from {self._get_client_ip(request)}'
            )
            return HttpResponseForbidden('Access denied')
        
        return None
    
    def _contains_suspicious_patterns(self, text):
        """Check if text contains suspicious patterns."""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.SUSPICIOUS_PATTERNS)
    
    def _is_suspicious_user_agent(self, user_agent):
        """Check if User-Agent is suspicious."""
        suspicious_agents = [
            'sqlmap',
            'nikto',
            'nmap',
            'masscan',
            'zap',
            'burp',
            'w3af',
            'havij',
            'pangolin',
        ]
        return any(agent in user_agent for agent in suspicious_agents)
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests for audit purposes.
    """
    
    def process_request(self, request):
        """Log request start time."""
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log request details for audit."""
        
        # Calculate request duration
        duration = 0
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time
        
        # Get user information
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
        
        # Log the request
        security_logger.info(
            f'API Request - Method: {request.method} | '
            f'Path: {request.path} | '
            f'User: {user_info} | '
            f'IP: {self._get_client_ip(request)} | '
            f'Status: {response.status_code} | '
            f'Duration: {duration:.3f}s | '
            f'User-Agent: {request.META.get("HTTP_USER_AGENT", "Unknown")}'
        )
        
        # Log failed authentication attempts
        if response.status_code == 401:
            security_logger.warning(
                f'Authentication failed - Path: {request.path} | '
                f'IP: {self._get_client_ip(request)} | '
                f'User-Agent: {request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )
        
        # Log permission denied attempts
        if response.status_code == 403:
            security_logger.warning(
                f'Permission denied - Path: {request.path} | '
                f'User: {user_info} | '
                f'IP: {self._get_client_ip(request)}'
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access based on IP whitelist for admin endpoints.
    """
    
    # Admin endpoints that require IP whitelisting
    ADMIN_PATHS = [
        '/admin/',
        '/api/admin/',
        '/api/exports/',
        '/api/imports/',
    ]
    
    def process_request(self, request):
        """Check IP whitelist for admin endpoints."""
        
        # Check if this is an admin endpoint
        if any(request.path.startswith(path) for path in self.ADMIN_PATHS):
            client_ip = self._get_client_ip(request)
            
            # Get allowed IPs from settings
            allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
            
            # If whitelist is configured and IP is not allowed
            if allowed_ips and client_ip not in allowed_ips:
                security_logger.warning(
                    f'Admin access denied for IP: {client_ip} | Path: {request.path}'
                )
                return HttpResponseForbidden('Access denied from this IP address')
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BruteForceProtectionMiddleware(MiddlewareMixin):
    """
    Middleware to protect against brute force attacks.
    """
    
    # Maximum failed attempts before blocking
    MAX_FAILED_ATTEMPTS = 5
    
    # Block duration in seconds (30 minutes)
    BLOCK_DURATION = 30 * 60
    
    def process_response(self, request, response):
        """Track failed login attempts."""
        
        # Skip brute force protection during testing
        if getattr(settings, 'TESTING', False):
            return response
        
        # Only track login endpoints
        if request.path in ['/api/auth/login/', '/api/token/', '/admin/login/']:
            client_ip = self._get_client_ip(request)
            cache_key = f'failed_attempts:{client_ip}'
            
            if response.status_code == 401:  # Failed login
                # Increment failed attempts
                failed_attempts = cache.get(cache_key, 0) + 1
                cache.set(cache_key, failed_attempts, self.BLOCK_DURATION)
                
                security_logger.warning(
                    f'Failed login attempt {failed_attempts}/{self.MAX_FAILED_ATTEMPTS} '
                    f'from IP: {client_ip}'
                )
                
                # Block if too many attempts
                if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                    cache.set(f'blocked:{client_ip}', True, self.BLOCK_DURATION)
                    security_logger.error(
                        f'IP blocked due to brute force: {client_ip} '
                        f'for {self.BLOCK_DURATION} seconds'
                    )
            
            elif response.status_code == 200:  # Successful login
                # Clear failed attempts on successful login
                cache.delete(cache_key)
        
        return response
    
    def process_request(self, request):
        """Check if IP is blocked."""
        
        # Skip brute force protection during testing
        if getattr(settings, 'TESTING', False):
            return None
        
        if request.path in ['/api/auth/login/', '/api/token/', '/admin/login/']:
            client_ip = self._get_client_ip(request)
            
            if cache.get(f'blocked:{client_ip}'):
                security_logger.warning(
                    f'Blocked IP attempted login: {client_ip}'
                )
                return HttpResponseForbidden('Too many failed attempts. Try again later.')
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip