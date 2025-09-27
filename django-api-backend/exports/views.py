"""
Views for data export functionality.

This module provides API endpoints for exporting data to Excel and PDF formats
using Celery for asynchronous processing.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .tasks import export_to_excel, export_to_pdf
from todoapi.utils.rate_limiting import rate_limit

logger = logging.getLogger(__name__)


class ExportDataView(APIView):
    """
    API endpoint for initiating data exports.
    
    Supports both Excel and PDF formats with various filtering options.
    Returns a task ID for tracking the export progress.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Export data to Excel or PDF",
        description="Initiate an asynchronous export task for the specified module and format",
        parameters=[
            OpenApiParameter(
                name="module",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Module to export (inventory, entities, services, sales)",
                required=True
            ),
            OpenApiParameter(
                name="format",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Export format (excel or pdf)",
                required=True
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {"type": "string"},
                    "message": {"type": "string"}
                }
            },
            400: {"description": "Invalid parameters"},
            401: {"description": "Authentication required"}
        }
    )
    @rate_limit(requests_per_hour=10, requests_per_minute=2)
    def post(self, request):
        """
        Initiate data export task with strict rate limiting.
        Limited to 10 exports per hour and 2 per minute per user.
        """
        
        # Validate required parameters
        module = request.data.get('module')
        format_type = request.data.get('format')
        
        if not module or not format_type:
            return Response(
                {'error': 'Both module and format parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate module
        valid_modules = ['inventory', 'entities', 'services', 'sales', 'authentication']
        if module not in valid_modules:
            return Response(
                {'error': f'Invalid module. Must be one of: {", ".join(valid_modules)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate format
        valid_formats = ['excel', 'pdf']
        if format_type not in valid_formats:
            return Response(
                {'error': f'Invalid format. Must be one of: {", ".join(valid_formats)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional parameters
        filters = request.data.get('filters', {})
        template_name = request.data.get('template', 'default')
        include_charts = request.data.get('include_charts', True)
        email_notification = request.data.get('email_notification', True)
        
        try:
            # Initiate appropriate export task
            if format_type == 'excel':
                task = export_to_excel.delay(
                    module_name=module,
                    filters=filters,
                    user_id=request.user.id,
                    include_charts=include_charts,
                    email_notification=email_notification
                )
            else:  # PDF
                task = export_to_pdf.delay(
                    module_name=module,
                    template_name=template_name,
                    filters=filters,
                    user_id=request.user.id,
                    email_notification=email_notification
                )
            
            logger.info(f"Export task initiated: {task.id} for user {request.user.id}")
            
            return Response({
                'task_id': task.id,
                'status': 'initiated',
                'message': f'{format_type.upper()} export task has been started',
                'module': module,
                'format': format_type
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to initiate export task: {str(e)}")
            return Response(
                {'error': 'Failed to initiate export task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportStatusView(APIView):
    """
    API endpoint for checking export task status.
    
    Returns the current status of an export task and download link when complete.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Check export task status",
        description="Get the current status of an export task",
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Task ID returned from export initiation",
                required=True
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {"type": "string"},
                    "result": {"type": "object"},
                    "download_url": {"type": "string"}
                }
            },
            404: {"description": "Task not found"}
        }
    )
    def get(self, request, task_id):
        """Get export task status."""
        
        try:
            # Get task result
            task_result = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task_result.status,
            }
            
            if task_result.ready():
                if task_result.successful():
                    result = task_result.result
                    response_data['result'] = result
                    
                    # Add download URL if file exists
                    if 'file_path' in result:
                        filename = os.path.basename(result['file_path'])
                        response_data['download_url'] = f"/api/exports/download/{filename}/"
                        
                else:
                    response_data['error'] = str(task_result.result)
            else:
                response_data['message'] = 'Task is still processing'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            return Response(
                {'error': 'Failed to get task status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadExportView(APIView):
    """
    API endpoint for downloading exported files.
    
    Provides secure file download with authentication and access control.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Download exported file",
        description="Download an exported file by filename",
        parameters=[
            OpenApiParameter(
                name="filename",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Name of the file to download",
                required=True
            ),
        ],
        responses={
            200: {"description": "File download"},
            404: {"description": "File not found"},
            403: {"description": "Access denied"}
        }
    )
    def get(self, request, filename):
        """Download exported file."""
        
        try:
            # Construct file path
            file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise Http404("File not found")
            
            # Check file age (delete files older than 7 days)
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
            if file_age > timedelta(days=7):
                os.remove(file_path)
                raise Http404("File has expired")
            
            # Determine content type
            content_type = 'application/octet-stream'
            if filename.endswith('.xlsx'):
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.endswith('.pdf'):
                content_type = 'application/pdf'
            
            # Read and return file
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = os.path.getsize(file_path)
                
                logger.info(f"File downloaded: {filename} by user {request.user.id}")
                return response
                
        except Http404:
            raise
        except Exception as e:
            logger.error(f"Failed to download file {filename}: {str(e)}")
            return Response(
                {'error': 'Failed to download file'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportTemplatesView(APIView):
    """
    API endpoint for managing export templates.
    
    Returns available templates for different modules and formats.
    """
    
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @extend_schema(
        summary="Get available export templates",
        description="List all available export templates for different modules",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "templates": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """Get available export templates."""
        
        templates = {
            'inventory': {
                'excel': ['standard', 'detailed', 'summary'],
                'pdf': ['report', 'list', 'cards']
            },
            'entities': {
                'excel': ['clients', 'providers', 'contacts'],
                'pdf': ['directory', 'summary', 'detailed']
            },
            'services': {
                'excel': ['services', 'technicians', 'schedule'],
                'pdf': ['report', 'invoice', 'summary']
            },
            'sales': {
                'excel': ['sales', 'revenue', 'analysis'],
                'pdf': ['invoice', 'report', 'summary']
            }
        }
        
        return Response({'templates': templates}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get export statistics",
    description="Get statistics about recent exports",
    responses={
        200: {
            "type": "object",
            "properties": {
                "total_exports": {"type": "integer"},
                "recent_exports": {"type": "array"},
                "popular_modules": {"type": "array"}
            }
        }
    }
)
def export_statistics(request):
    """Get export statistics for the current user."""
    
    try:
        # This would typically query a database of export logs
        # For now, return mock data
        stats = {
            'total_exports': 0,
            'recent_exports': [],
            'popular_modules': ['inventory', 'sales', 'entities'],
            'formats_used': {
                'excel': 0,
                'pdf': 0
            }
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get export statistics: {str(e)}")
        return Response(
            {'error': 'Failed to get statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Cancel export task",
    description="Cancel a running export task",
    parameters=[
        OpenApiParameter(
            name="task_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Task ID to cancel",
            required=True
        ),
    ],
    responses={
        200: {"description": "Task cancelled successfully"},
        404: {"description": "Task not found"},
        400: {"description": "Task cannot be cancelled"}
    }
)
def cancel_export_task(request, task_id):
    """Cancel an export task."""
    
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.ready():
            return Response(
                {'error': 'Task has already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Revoke the task
        task_result.revoke(terminate=True)
        
        logger.info(f"Export task cancelled: {task_id} by user {request.user.id}")
        
        return Response(
            {'message': 'Task cancelled successfully'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {str(e)}")
        return Response(
            {'error': 'Failed to cancel task'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
