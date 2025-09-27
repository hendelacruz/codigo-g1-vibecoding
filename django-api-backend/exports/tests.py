"""
Tests for exports app functionality.

This module contains comprehensive tests for the export system,
including views, tasks, and file generation.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import default_storage

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from celery.result import AsyncResult

from .tasks import export_to_excel, export_to_pdf
from .views import (
    ExportDataView, ExportStatusView, DownloadExportView,
    ExportTemplatesView, export_statistics, cancel_export_task
)

User = get_user_model()


class ExportTasksTestCase(TestCase):
    """Test cases for export tasks."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('exports.tasks.get_model_data')
    @patch('exports.tasks.create_excel_file')
    @patch('exports.tasks.send_export_notification')
    def test_export_to_excel_task(self, mock_send_notification, mock_create_excel, mock_get_data):
        """Test Excel export task execution."""
        
        # Mock data
        mock_get_data.return_value = [
            {'id': 1, 'name': 'Test Item 1'},
            {'id': 2, 'name': 'Test Item 2'}
        ]
        mock_create_excel.return_value = '/path/to/test_export.xlsx'
        
        # Execute task
        result = export_to_excel(
            module_name='inventory',
            filters={},
            user_id=self.user.id,
            include_charts=True,
            email_notification=True
        )
        
        # Assertions
        self.assertIn('file_path', result)
        self.assertIn('records_count', result)
        self.assertEqual(result['records_count'], 2)
        
        # Verify function calls
        mock_get_data.assert_called_once_with('inventory', {})
        mock_create_excel.assert_called_once()
        mock_send_notification.assert_called_once()
    
    @patch('exports.tasks.get_model_data')
    @patch('exports.tasks.create_pdf_file')
    @patch('exports.tasks.send_export_notification')
    def test_export_to_pdf_task(self, mock_send_notification, mock_create_pdf, mock_get_data):
        """Test PDF export task execution."""
        
        # Mock data
        mock_get_data.return_value = [
            {'id': 1, 'name': 'Test Item 1'},
            {'id': 2, 'name': 'Test Item 2'}
        ]
        mock_create_pdf.return_value = '/path/to/test_export.pdf'
        
        # Execute task
        result = export_to_pdf(
            module_name='entities',
            template_name='default',
            filters={'active': True},
            user_id=self.user.id,
            email_notification=False
        )
        
        # Assertions
        self.assertIn('file_path', result)
        self.assertIn('records_count', result)
        self.assertEqual(result['records_count'], 2)
        
        # Verify function calls
        mock_get_data.assert_called_once_with('entities', {'active': True})
        mock_create_pdf.assert_called_once()
        mock_send_notification.assert_not_called()  # email_notification=False


class ExportViewsTestCase(APITestCase):
    """Test cases for export views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_export_data_view_success(self):
        """Test successful export initiation."""
        
        with patch('exports.views.export_to_excel.delay') as mock_task:
            # Mock task result
            mock_task.return_value.id = 'test-task-id-123'
            
            url = reverse('exports:export_data')
            data = {
                'module': 'inventory',
                'format': 'excel',
                'filters': {'active': True},
                'include_charts': True
            }
            
            response = self.client.post(url, data, format='json')
            
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('task_id', response.data)
            self.assertEqual(response.data['task_id'], 'test-task-id-123')
            self.assertEqual(response.data['status'], 'initiated')
            
            # Verify task was called
            mock_task.assert_called_once()
    
    def test_export_data_view_invalid_module(self):
        """Test export with invalid module."""
        
        url = reverse('exports:export_data')
        data = {
            'module': 'invalid_module',
            'format': 'excel'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_export_data_view_invalid_format(self):
        """Test export with invalid format."""
        
        url = reverse('exports:export_data')
        data = {
            'module': 'inventory',
            'format': 'invalid_format'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_export_data_view_missing_parameters(self):
        """Test export with missing required parameters."""
        
        url = reverse('exports:export_data')
        data = {
            'module': 'inventory'
            # Missing 'format' parameter
        }
        
        response = self.client.post(url, data, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_export_data_view_unauthenticated(self):
        """Test export without authentication."""
        
        # Remove authentication
        self.client.credentials()
        
        url = reverse('exports:export_data')
        data = {
            'module': 'inventory',
            'format': 'excel'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('exports.views.AsyncResult')
    def test_export_status_view_success(self, mock_async_result):
        """Test successful status check."""
        
        # Mock task result
        mock_result = MagicMock()
        mock_result.status = 'SUCCESS'
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {
            'file_path': '/path/to/export.xlsx',
            'records_count': 100
        }
        mock_async_result.return_value = mock_result
        
        url = reverse('exports:export_status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
        self.assertIn('download_url', response.data)
    
    @patch('exports.views.AsyncResult')
    def test_export_status_view_pending(self, mock_async_result):
        """Test status check for pending task."""
        
        # Mock task result
        mock_result = MagicMock()
        mock_result.status = 'PENDING'
        mock_result.ready.return_value = False
        mock_async_result.return_value = mock_result
        
        url = reverse('exports:export_status', kwargs={'task_id': 'test-task-id'})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertIn('message', response.data)
    
    def test_export_templates_view(self):
        """Test export templates endpoint."""
        
        url = reverse('exports:export_templates')
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('templates', response.data)
        self.assertIn('inventory', response.data['templates'])
        self.assertIn('entities', response.data['templates'])
    
    def test_export_statistics_view(self):
        """Test export statistics endpoint."""
        
        url = reverse('exports:export_statistics')
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_exports', response.data)
        self.assertIn('recent_exports', response.data)
        self.assertIn('popular_modules', response.data)
    
    @patch('exports.views.AsyncResult')
    def test_cancel_export_task_success(self, mock_async_result):
        """Test successful task cancellation."""
        
        # Mock task result
        mock_result = MagicMock()
        mock_result.ready.return_value = False
        mock_result.revoke = MagicMock()
        mock_async_result.return_value = mock_result
        
        url = reverse('exports:cancel_export', kwargs={'task_id': 'test-task-id'})
        response = self.client.delete(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        mock_result.revoke.assert_called_once_with(terminate=True)
    
    @patch('exports.views.AsyncResult')
    def test_cancel_export_task_already_completed(self, mock_async_result):
        """Test cancellation of already completed task."""
        
        # Mock task result
        mock_result = MagicMock()
        mock_result.ready.return_value = True
        mock_async_result.return_value = mock_result
        
        url = reverse('exports:cancel_export', kwargs={'task_id': 'test-task-id'})
        response = self.client.delete(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class DownloadExportViewTestCase(APITestCase):
    """Test cases for file download functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create temporary export directory
        self.export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.export_dir):
            shutil.rmtree(self.export_dir)
    
    def test_download_existing_file(self):
        """Test downloading an existing file."""
        
        # Create a test file
        test_filename = 'test_export.xlsx'
        test_file_path = os.path.join(self.export_dir, test_filename)
        
        with open(test_file_path, 'wb') as f:
            f.write(b'Test Excel content')
        
        url = reverse('exports:download_export', kwargs={'filename': test_filename})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_download_nonexistent_file(self):
        """Test downloading a non-existent file."""
        
        url = reverse('exports:download_export', kwargs={'filename': 'nonexistent.xlsx'})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_download_expired_file(self):
        """Test downloading an expired file."""
        
        # Create a test file
        test_filename = 'old_export.xlsx'
        test_file_path = os.path.join(self.export_dir, test_filename)
        
        with open(test_file_path, 'wb') as f:
            f.write(b'Old Excel content')
        
        # Modify file creation time to be older than 7 days
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(test_file_path, (old_time, old_time))
        
        url = reverse('exports:download_export', kwargs={'filename': test_filename})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # File should be deleted
        self.assertFalse(os.path.exists(test_file_path))
    
    def test_download_pdf_file(self):
        """Test downloading a PDF file."""
        
        # Create a test PDF file
        test_filename = 'test_export.pdf'
        test_file_path = os.path.join(self.export_dir, test_filename)
        
        with open(test_file_path, 'wb') as f:
            f.write(b'Test PDF content')
        
        url = reverse('exports:download_export', kwargs={'filename': test_filename})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_download_unauthenticated(self):
        """Test downloading without authentication."""
        
        # Remove authentication
        self.client.credentials()
        
        url = reverse('exports:download_export', kwargs={'filename': 'test.xlsx'})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExportIntegrationTestCase(APITestCase):
    """Integration tests for the complete export workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    @patch('exports.tasks.export_to_excel.delay')
    @patch('exports.views.AsyncResult')
    def test_complete_export_workflow(self, mock_async_result, mock_export_task):
        """Test the complete export workflow from initiation to download."""
        
        # Step 1: Initiate export
        mock_export_task.return_value.id = 'test-task-id-123'
        
        export_url = reverse('exports:export_data')
        export_data = {
            'module': 'inventory',
            'format': 'excel',
            'filters': {'active': True}
        }
        
        export_response = self.client.post(export_url, export_data, format='json')
        
        # Verify export initiation
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        task_id = export_response.data['task_id']
        
        # Step 2: Check status (completed)
        mock_result = MagicMock()
        mock_result.status = 'SUCCESS'
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {
            'file_path': '/path/to/export.xlsx',
            'records_count': 50
        }
        mock_async_result.return_value = mock_result
        
        status_url = reverse('exports:export_status', kwargs={'task_id': task_id})
        status_response = self.client.get(status_url)
        
        # Verify status check
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status'], 'SUCCESS')
        self.assertIn('download_url', status_response.data)
        
        # Step 3: Get templates
        templates_url = reverse('exports:export_templates')
        templates_response = self.client.get(templates_url)
        
        # Verify templates
        self.assertEqual(templates_response.status_code, status.HTTP_200_OK)
        self.assertIn('templates', templates_response.data)
        
        # Step 4: Get statistics
        stats_url = reverse('exports:export_statistics')
        stats_response = self.client.get(stats_url)
        
        # Verify statistics
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertIn('total_exports', stats_response.data)
