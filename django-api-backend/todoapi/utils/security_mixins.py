"""
Security mixins for serializers and views to apply security validations.
"""

from rest_framework import serializers
from rest_framework.permissions import BasePermission
from django.core.exceptions import ValidationError as DjangoValidationError
from .validators import (
    InputSanitizer, TextValidator, FileValidator, URLValidator,
    sanitize_input, sanitize_html_input, validate_safe_text,
    validate_file_upload, validate_safe_url
)


class SecurityValidationMixin:
    """
    Mixin to add security validation to serializers.
    """
    
    # Fields that should be sanitized as plain text
    TEXT_FIELDS = []
    
    # Fields that should be sanitized as HTML
    HTML_FIELDS = []
    
    # Fields that should be validated for security threats
    SECURITY_VALIDATED_FIELDS = []
    
    # Fields that should be validated as URLs
    URL_FIELDS = []
    
    # Fields that should be validated as file uploads
    FILE_FIELDS = []
    
    def validate(self, attrs):
        """
        Apply security validations to the data.
        """
        # Apply parent validation first
        attrs = super().validate(attrs)
        
        # Apply security validations
        self._apply_security_validations(attrs)
        
        return attrs
    
    def _apply_security_validations(self, attrs):
        """
        Apply security validations to specified fields.
        """
        # Sanitize text fields
        for field_name in self.TEXT_FIELDS:
            if field_name in attrs and attrs[field_name]:
                attrs[field_name] = sanitize_input(attrs[field_name])
        
        # Sanitize HTML fields
        for field_name in self.HTML_FIELDS:
            if field_name in attrs and attrs[field_name]:
                attrs[field_name] = sanitize_html_input(attrs[field_name])
        
        # Validate security-sensitive fields
        for field_name in self.SECURITY_VALIDATED_FIELDS:
            if field_name in attrs and attrs[field_name]:
                try:
                    validate_safe_text(attrs[field_name])
                except DjangoValidationError as e:
                    raise serializers.ValidationError({field_name: e.message})
        
        # Validate URL fields
        for field_name in self.URL_FIELDS:
            if field_name in attrs and attrs[field_name]:
                try:
                    validate_safe_url(attrs[field_name])
                except DjangoValidationError as e:
                    raise serializers.ValidationError({field_name: e.message})
        
        # Validate file fields
        for field_name in self.FILE_FIELDS:
            if field_name in attrs and attrs[field_name]:
                try:
                    validate_file_upload(attrs[field_name])
                except DjangoValidationError as e:
                    raise serializers.ValidationError({field_name: e.message})


class SecureModelSerializerMixin(SecurityValidationMixin):
    """
    Enhanced security mixin for model serializers with automatic field detection.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auto_detect_security_fields()
    
    def _auto_detect_security_fields(self):
        """
        Automatically detect fields that need security validation based on field types.
        """
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'model'):
            return
        
        model = self.Meta.model
        
        # Auto-detect text fields that need sanitization
        for field_name, field in self.fields.items():
            if hasattr(model, field_name):
                model_field = model._meta.get_field(field_name)
                
                # Text fields for sanitization
                if hasattr(model_field, 'max_length') and isinstance(field, serializers.CharField):
                    if field_name not in self.TEXT_FIELDS:
                        self.TEXT_FIELDS.append(field_name)
                
                # URL fields
                if isinstance(field, serializers.URLField):
                    if field_name not in self.URL_FIELDS:
                        self.URL_FIELDS.append(field_name)
                
                # File fields
                if isinstance(field, (serializers.FileField, serializers.ImageField)):
                    if field_name not in self.FILE_FIELDS:
                        self.FILE_FIELDS.append(field_name)


class AuditLogMixin:
    """
    Mixin to add audit logging to serializers.
    """
    
    def create(self, validated_data):
        """
        Create with audit logging.
        """
        instance = super().create(validated_data)
        self._log_audit_action('CREATE', instance, validated_data)
        return instance
    
    def update(self, instance, validated_data):
        """
        Update with audit logging.
        """
        old_data = self._get_instance_data(instance)
        updated_instance = super().update(instance, validated_data)
        self._log_audit_action('UPDATE', updated_instance, validated_data, old_data)
        return updated_instance
    
    def _log_audit_action(self, action, instance, new_data, old_data=None):
        """
        Log audit action.
        """
        import logging
        audit_logger = logging.getLogger('security')
        
        user = getattr(self.context.get('request', {}), 'user', None)
        user_info = f"{user.username} (ID: {user.id})" if user and user.is_authenticated else 'anonymous'
        
        log_message = (
            f'AUDIT {action} - Model: {instance.__class__.__name__} | '
            f'ID: {instance.pk} | '
            f'User: {user_info} | '
            f'New Data: {new_data}'
        )
        
        if old_data:
            log_message += f' | Old Data: {old_data}'
        
        audit_logger.info(log_message)
    
    def _get_instance_data(self, instance):
        """
        Get current instance data for audit logging.
        """
        try:
            serializer = self.__class__(instance)
            return serializer.data
        except Exception:
            return str(instance)


class SecurePermissionMixin(BasePermission):
    """
    Base permission mixin with security enhancements.
    """
    
    def has_permission(self, request, view):
        """
        Enhanced permission check with security logging.
        """
        has_perm = super().has_permission(request, view)
        
        if not has_perm:
            self._log_permission_denied(request, view, 'permission')
        
        return has_perm
    
    def has_object_permission(self, request, view, obj):
        """
        Enhanced object permission check with security logging.
        """
        has_perm = super().has_object_permission(request, view, obj)
        
        if not has_perm:
            self._log_permission_denied(request, view, 'object_permission', obj)
        
        return has_perm
    
    def _log_permission_denied(self, request, view, permission_type, obj=None):
        """
        Log permission denied attempts.
        """
        import logging
        security_logger = logging.getLogger('security')
        
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
        
        client_ip = self._get_client_ip(request)
        
        log_message = (
            f'PERMISSION DENIED - Type: {permission_type} | '
            f'View: {view.__class__.__name__} | '
            f'Method: {request.method} | '
            f'Path: {request.path} | '
            f'User: {user_info} | '
            f'IP: {client_ip}'
        )
        
        if obj:
            log_message += f' | Object: {obj.__class__.__name__}({obj.pk})'
        
        security_logger.warning(log_message)
    
    def _get_client_ip(self, request):
        """
        Get client IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecureViewMixin:
    """
    Mixin for views with security enhancements.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Enhanced dispatch with security checks.
        """
        # Log API access
        self._log_api_access(request)
        
        # Check for suspicious patterns in request
        if self._is_suspicious_request(request):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('Suspicious request detected')
        
        return super().dispatch(request, *args, **kwargs)
    
    def _log_api_access(self, request):
        """
        Log API access for audit purposes.
        """
        import logging
        security_logger = logging.getLogger('security')
        
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
        
        security_logger.info(
            f'API ACCESS - View: {self.__class__.__name__} | '
            f'Method: {request.method} | '
            f'Path: {request.path} | '
            f'User: {user_info} | '
            f'IP: {self._get_client_ip(request)}'
        )
    
    def _is_suspicious_request(self, request):
        """
        Check if request contains suspicious patterns.
        """
        # Check query parameters
        for key, value in request.GET.items():
            if self._contains_suspicious_patterns(f"{key}={value}"):
                return True
        
        # Check POST data if available
        if hasattr(request, 'data'):
            for key, value in request.data.items():
                if isinstance(value, str) and self._contains_suspicious_patterns(f"{key}={value}"):
                    return True
        
        return False
    
    def _contains_suspicious_patterns(self, text):
        """
        Check if text contains suspicious patterns.
        """
        suspicious_patterns = [
            '<script', 'javascript:', 'onload=', 'onerror=',
            'union select', 'drop table', 'insert into', 'delete from',
            '../', '..\\', 'cmd.exe', '/bin/bash'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in suspicious_patterns)
    
    def _get_client_ip(self, request):
        """
        Get client IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DataSanitizationMixin:
    """
    Mixin to automatically sanitize data in serializers.
    """
    
    def to_internal_value(self, data):
        """
        Sanitize data before validation.
        """
        # Sanitize data recursively
        sanitized_data = self._sanitize_data(data)
        
        # Call parent method with sanitized data
        return super().to_internal_value(sanitized_data)
    
    def _sanitize_data(self, data):
        """
        Recursively sanitize data.
        """
        if isinstance(data, dict):
            return {key: self._sanitize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return sanitize_input(data)
        else:
            return data