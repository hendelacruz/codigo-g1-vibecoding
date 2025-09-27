"""
Cache utilities for the todoapi project.
Provides decorators and helper functions for caching.
"""

from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.http import urlencode
import hashlib
import json


def make_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix (str): Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        key_parts.append(force_str(arg))
    
    # Add keyword arguments (sorted for consistency)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(urlencode(sorted_kwargs))
    
    # Create hash for long keys
    key_string = ':'.join(key_parts)
    if len(key_string) > 200:  # Redis key length limit
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cache_response(timeout=None, key_prefix='view'):
    """
    Decorator to cache API response data.
    
    Args:
        timeout (int): Cache timeout in seconds (default: CACHE_TTL)
        key_prefix (str): Prefix for cache key
    
    Usage:
        @cache_response(timeout=300, key_prefix='inventory')
        def get_inventory_list(self, request):
            # Your view logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key based on request parameters
            cache_key = make_cache_key(
                key_prefix,
                request.path,
                request.GET.urlencode(),
                getattr(request.user, 'id', 'anonymous')
            )
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Execute the view function
            response = func(self, request, *args, **kwargs)
            
            # Cache successful responses only
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache_timeout = timeout or getattr(settings, 'CACHE_TTL', 900)
                # Solo cachear si la respuesta tiene un renderer configurado
                if (hasattr(response, 'accepted_renderer') and response.accepted_renderer):
                    # Renderizar la respuesta antes de cachearla
                    if hasattr(response, 'render') and callable(response.render):
                        response.render()
                    cache.set(cache_key, response, cache_timeout)
            
            return response
        return wrapper
    return decorator


def cache_queryset(timeout=None, key_prefix='queryset'):
    """
    Decorator to cache queryset results.
    
    Args:
        timeout (int): Cache timeout in seconds
        key_prefix (str): Prefix for cache key
    
    Usage:
        @cache_queryset(timeout=600, key_prefix='clients')
        def get_active_clients(self):
            return Cliente.objects.filter(is_active=True)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = make_cache_key(
                key_prefix,
                func.__name__,
                *args[1:],  # Skip 'self' argument
                **kwargs
            )
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_timeout = timeout or getattr(settings, 'CACHE_TTL', 900)
            cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate cache keys matching a pattern.
    
    Args:
        pattern (str): Pattern to match cache keys
    
    Note:
        This requires django-redis backend for pattern-based deletion
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Get all keys matching pattern
        keys = redis_conn.keys(f"*{pattern}*")
        if keys:
            redis_conn.delete(*keys)
            return len(keys)
        return 0
    except ImportError:
        # Fallback for non-redis backends
        return 0


def cache_model_data(model_class, timeout=None):
    """
    Cache model data with automatic invalidation.
    
    Args:
        model_class: Django model class
        timeout (int): Cache timeout in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            model_name = model_class._meta.label_lower
            cache_key = make_cache_key(
                'model',
                model_name,
                func.__name__,
                *args[1:],  # Skip 'self'
                **kwargs
            )
            
            # Try cache first
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Get fresh data
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_timeout = timeout or getattr(settings, 'CACHE_TTL', 900)
            cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator


class CacheManager:
    """
    Centralized cache management class.
    """
    
    @staticmethod
    def get_stats_cache_key(model_name, date_range=None):
        """Generate cache key for statistics."""
        return make_cache_key('stats', model_name, date_range or 'all')
    
    @staticmethod
    def get_list_cache_key(model_name, filters=None, user_id=None):
        """Generate cache key for model lists."""
        return make_cache_key(
            'list',
            model_name,
            json.dumps(filters or {}, sort_keys=True),
            user_id or 'anonymous'
        )
    
    @staticmethod
    def invalidate_model_cache(model_name):
        """Invalidate all cache entries for a model."""
        patterns = [
            f"*list:{model_name}*",
            f"*stats:{model_name}*",
            f"*model:{model_name}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += invalidate_cache_pattern(pattern)
        
        return total_deleted
    
    @staticmethod
    def warm_cache(cache_key, data_func, timeout=None):
        """
        Warm cache with data from function.
        
        Args:
            cache_key (str): Cache key
            data_func (callable): Function to get data
            timeout (int): Cache timeout
        """
        try:
            data = data_func()
            cache_timeout = timeout or getattr(settings, 'CACHE_TTL', 900)
            cache.set(cache_key, data, cache_timeout)
            return True
        except Exception:
            return False