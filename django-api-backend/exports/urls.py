"""
URL configuration for exports app.

This module defines the URL patterns for the export functionality,
including endpoints for initiating exports, checking status, and downloading files.
"""

from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    # Export initiation endpoint
    path(
        'export/',
        views.ExportDataView.as_view(),
        name='export_data'
    ),
    
    # Export status checking endpoint
    path(
        'status/<str:task_id>/',
        views.ExportStatusView.as_view(),
        name='export_status'
    ),
    
    # File download endpoint
    path(
        'download/<str:filename>/',
        views.DownloadExportView.as_view(),
        name='download_export'
    ),
    
    # Export templates endpoint
    path(
        'templates/',
        views.ExportTemplatesView.as_view(),
        name='export_templates'
    ),
    
    # Export statistics endpoint
    path(
        'statistics/',
        views.export_statistics,
        name='export_statistics'
    ),
    
    # Cancel export task endpoint
    path(
        'cancel/<str:task_id>/',
        views.cancel_export_task,
        name='cancel_export'
    ),
]