"""
Rate limiting utilities for the todoapi project.
Provides middleware and decorators for API rate limiting.
"""

import time
import json
import logging
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response

# Configure rate limiting logger
rate_limit_logger = logging.getLogger('rate_limiting')


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting for API endpoints.
    
    Uses Redis cache to store request counts per IP/user.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.rate_limits = getattr(settings, 'RATE_LIMITS', {
            'default': {'requests': 100, 'window': 3600},  # 100 requests per hour
            'auth': {'requests': 1000, 'window': 3600},     # 1000 requests per hour for authenticated users
            'strict': {'requests': 10, 'window': 60},       # 10 requests per minute for sensitive endpoints
        })
    
    def process_request(self, request):
        """
        Process incoming request and check rate limits.
        """
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limiting(request):
            return None
        
        # Determine rate limit type
        rate_limit_type = self._get_rate_limit_type(request)
        rate_config = self.rate_limits.get(rate_limit_type, self.rate_limits['default'])
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        is_allowed, remaining, reset_time = self._check_rate_limit(
            client_id, rate_limit_type, rate_config
        )
        
        if not is_allowed:
            return self._rate_limit_exceeded_response(remaining, reset_time)
        
        # Add rate limit headers to response
        request.rate_limit_remaining = remaining
        request.rate_limit_reset = reset_time
        
        return None
    
    def process_response(self, request, response):
        """
        Add rate limit headers to response.
        """
        if hasattr(request, 'rate_limit_remaining'):
            response['X-RateLimit-Remaining'] = str(request.rate_limit_remaining)
            response['X-RateLimit-Reset'] = str(request.rate_limit_reset)
        
        return response
    
    def _should_skip_rate_limiting(self, request):
        """
        Determine if rate limiting should be skipped for this request.
        """
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/schema/',
            '/api/docs/',
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_rate_limit_type(self, request):
        """
        Determine the rate limit type based on the request.
        """
        # Sensitive endpoints get strict rate limiting
        strict_endpoints = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/password-reset/',
        ]
        
        if any(request.path.startswith(endpoint) for endpoint in strict_endpoints):
            return 'strict'
        
        # Authenticated users get higher limits
        if hasattr(request, 'user') and request.user.is_authenticated:
            return 'auth'
        
        return 'default'
    
    def _get_client_identifier(self, request):
        """
        Get unique identifier for the client.
        """
        # Use user ID for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Use IP address for anonymous users
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip:{ip}"
    
    def _check_rate_limit(self, client_id, rate_type, rate_config):
        """
        Check if the client has exceeded the rate limit.
        
        Returns:
            tuple: (is_allowed, remaining_requests, reset_time)
        """
        cache_key = f"rate_limit:{rate_type}:{client_id}"
        window = rate_config['window']
        max_requests = rate_config['requests']
        
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        
        # Get current request count
        request_data = cache.get(cache_key, {'count': 0, 'window_start': window_start})
        
        # Reset if new window
        if request_data['window_start'] != window_start:
            request_data = {'count': 0, 'window_start': window_start}
        
        # Check if limit exceeded
        if request_data['count'] >= max_requests:
            # Log the rate limit violation
            rate_limit_logger.warning(
                f'Rate limit exceeded for client {client_id}',
                extra={
                    'client_id': client_id,
                    'rate_type': rate_type,
                    'current_count': request_data['count'],
                    'max_requests': max_requests,
                    'window': window
                }
            )
            
            remaining = 0
            reset_time = window_start + window
            return False, remaining, reset_time
        
        # Increment counter
        request_data['count'] += 1
        cache.set(cache_key, request_data, window)
        
        remaining = max_requests - request_data['count']
        reset_time = window_start + window
        
        return True, remaining, reset_time
    
    def _rate_limit_exceeded_response(self, remaining, reset_time):
        """
        Return rate limit exceeded response.
        """
        response_data = {
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': reset_time - int(time.time())
        }
        
        response = JsonResponse(response_data, status=429)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(reset_time)
        response['Retry-After'] = str(reset_time - int(time.time()))
        
        return response


def rate_limit(requests_per_hour=100, requests_per_minute=None):
    """
    Decorator to apply rate limiting to specific views.
    
    Args:
        requests_per_hour (int): Maximum requests per hour
        requests_per_minute (int): Maximum requests per minute (optional)
    
    Usage:
        @rate_limit(requests_per_hour=50, requests_per_minute=5)
        def my_view(request):
            # Your view logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip rate limiting during tests
            if getattr(settings, 'TESTING', False):
                return func(*args, **kwargs)
            
            # Handle both function views and ViewSet methods
            if len(args) > 0:
                # For ViewSet methods: args[0] is self, args[1] is request
                if hasattr(args[0], '__class__') and hasattr(args[0], 'request'):
                    # ViewSet method
                    request = args[1] if len(args) > 1 else None
                elif hasattr(args[0], 'META'):
                    # Function view
                    request = args[0]
                else:
                    # Fallback - assume second argument is request
                    request = args[1] if len(args) > 1 else None
            else:
                request = None
            
            if not request or not hasattr(request, 'META'):
                # If we can't get request, skip rate limiting
                return func(*args, **kwargs)
            
            # Get client identifier
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                client_id = f"user:{request.user.id}"
            else:
                client_id = f"ip:{client_ip}"
            
            # Check hourly limit
            if not _check_rate_limit_decorator(client_id, 'hour', requests_per_hour, 3600):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {requests_per_hour} requests per hour allowed'
                }, status=429)
            
            # Check minute limit if specified
            if requests_per_minute and not _check_rate_limit_decorator(
                client_id, 'minute', requests_per_minute, 60
            ):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {requests_per_minute} requests per minute allowed'
                }, status=429)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _check_rate_limit_decorator(client_id, period, max_requests, window):
    """
    Helper function for rate limit decorator.
    """
    cache_key = f"rate_limit_decorator:{period}:{client_id}"
    current_time = int(time.time())
    window_start = current_time - (current_time % window)
    
    request_data = cache.get(cache_key, {'count': 0, 'window_start': window_start})
    
    if request_data['window_start'] != window_start:
        request_data = {'count': 0, 'window_start': window_start}
    
    if request_data['count'] >= max_requests:
        return False
    
    request_data['count'] += 1
    cache.set(cache_key, request_data, window)
    
    return True


class APIRateLimitMixin:
    """
    Mixin to add rate limiting to DRF ViewSets.
    """
    rate_limit_scope = 'default'
    rate_limit_config = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to check rate limits.
        """
        if not self._check_api_rate_limit(request):
            return Response({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'detail': 'API rate limit exceeded for this endpoint.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return super().dispatch(request, *args, **kwargs)
    
    def _check_api_rate_limit(self, request):
        """
        Check rate limit for API endpoint.
        """
        if not self.rate_limit_config:
            return True  # No rate limiting configured
        
        # Get client identifier
        if hasattr(request, 'user') and request.user.is_authenticated:
            client_id = f"user:{request.user.id}"
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', 'unknown')
            client_id = f"ip:{ip}"
        
        # Check rate limit
        cache_key = f"api_rate_limit:{self.rate_limit_scope}:{client_id}"
        window = self.rate_limit_config.get('window', 3600)
        max_requests = self.rate_limit_config.get('requests', 100)
        
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        
        request_data = cache.get(cache_key, {'count': 0, 'window_start': window_start})
        
        if request_data['window_start'] != window_start:
            request_data = {'count': 0, 'window_start': window_start}
        
        if request_data['count'] >= max_requests:
            return False
        
        request_data['count'] += 1
        cache.set(cache_key, request_data, window)
        
        return True


# Rate limiting configurations for different endpoint types
RATE_LIMIT_CONFIGS = {
    'auth': {'requests': 5, 'window': 300},      # 5 requests per 5 minutes for auth
    'sales': {'requests': 200, 'window': 3600},   # 200 requests per hour for sales
    'inventory': {'requests': 300, 'window': 3600}, # 300 requests per hour for inventory
    'dashboard': {'requests': 50, 'window': 3600},  # 50 requests per hour for dashboard
    'exports': {'requests': 10, 'window': 3600},    # 10 exports per hour
    'default': {'requests': 100, 'window': 3600},   # Default: 100 requests per hour
}