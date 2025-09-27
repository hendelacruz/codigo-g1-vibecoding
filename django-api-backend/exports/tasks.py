"""
Celery tasks for data export functionality.

This module contains asynchronous tasks for exporting data to Excel and PDF formats.
Tasks handle large datasets efficiently and send notifications upon completion.
"""

import os
import logging
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db.models import QuerySet

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def export_to_excel(self, module_name: str, filters: Dict[str, Any], user_id: int, 
                   include_charts: bool = True, email_notification: bool = True):
    """
    Export data to Excel format with multiple sheets and corporate formatting.
    
    Args:
        module_name: Name of the Django app/module to export
        filters: Dictionary of filters to apply to the queryset
        user_id: ID of the user requesting the export
        include_charts: Whether to include charts in the Excel file
        email_notification: Whether to send email notification when complete
        
    Returns:
        dict: Export result with file path and statistics
    """
    try:
        logger.info(f"Starting Excel export for module: {module_name}")
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Get the model class
        model_class = _get_model_class(module_name)
        if not model_class:
            raise ValueError(f"Model not found for module: {module_name}")
        
        # Apply filters and get queryset
        queryset = _apply_filters(model_class, filters)
        
        # Create Excel file
        file_path = _create_excel_file(module_name, queryset, include_charts)
        
        # Send email notification if requested
        if email_notification:
            _send_export_notification(user, file_path, 'Excel', module_name)
        
        logger.info(f"Excel export completed successfully: {file_path}")
        
        return {
            'status': 'success',
            'file_path': file_path,
            'record_count': queryset.count(),
            'module': module_name,
            'user_email': user.email
        }
        
    except Exception as exc:
        logger.error(f"Excel export failed: {str(exc)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying Excel export (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=exc)
        
        # Send failure notification
        if 'user' in locals():
            _send_failure_notification(user, module_name, 'Excel', str(exc))
        
        return {
            'status': 'error',
            'error': str(exc),
            'module': module_name
        }


@shared_task(bind=True, max_retries=3)
def export_to_pdf(self, module_name: str, template_name: str, filters: Dict[str, Any], 
                 user_id: int, email_notification: bool = True):
    """
    Export data to PDF format with custom templates and corporate branding.
    
    Args:
        module_name: Name of the Django app/module to export
        template_name: Name of the PDF template to use
        filters: Dictionary of filters to apply to the queryset
        user_id: ID of the user requesting the export
        email_notification: Whether to send email notification when complete
        
    Returns:
        dict: Export result with file path and statistics
    """
    try:
        logger.info(f"Starting PDF export for module: {module_name}")
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Get the model class
        model_class = _get_model_class(module_name)
        if not model_class:
            raise ValueError(f"Model not found for module: {module_name}")
        
        # Apply filters and get queryset
        queryset = _apply_filters(model_class, filters)
        
        # Create PDF file
        file_path = _create_pdf_file(module_name, template_name, queryset)
        
        # Send email notification if requested
        if email_notification:
            _send_export_notification(user, file_path, 'PDF', module_name)
        
        logger.info(f"PDF export completed successfully: {file_path}")
        
        return {
            'status': 'success',
            'file_path': file_path,
            'record_count': queryset.count(),
            'module': module_name,
            'template': template_name,
            'user_email': user.email
        }
        
    except Exception as exc:
        logger.error(f"PDF export failed: {str(exc)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying PDF export (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=exc)
        
        # Send failure notification
        if 'user' in locals():
            _send_failure_notification(user, module_name, 'PDF', str(exc))
        
        return {
            'status': 'error',
            'error': str(exc),
            'module': module_name,
            'template': template_name
        }


def _get_model_class(module_name: str):
    """Get the main model class for a given module."""
    model_mapping = {
        'inventory': 'inventory.GPS',
        'entities': 'entities.Cliente',
        'services': 'services.Servicio',
        'sales': 'sales.Venta',
        'authentication': 'authentication.CustomUser',
    }
    
    model_path = model_mapping.get(module_name)
    if not model_path:
        return None
    
    app_label, model_name = model_path.split('.')
    return apps.get_model(app_label, model_name)


def _apply_filters(model_class, filters: Dict[str, Any]) -> QuerySet:
    """Apply filters to the model queryset."""
    queryset = model_class.objects.all()
    
    # Apply date range filters
    if 'date_from' in filters and 'date_to' in filters:
        date_field = _get_date_field(model_class)
        if date_field:
            queryset = queryset.filter(
                **{f"{date_field}__gte": filters['date_from'],
                   f"{date_field}__lte": filters['date_to']}
            )
    
    # Apply other filters
    for key, value in filters.items():
        if key not in ['date_from', 'date_to'] and value:
            if hasattr(model_class, key):
                queryset = queryset.filter(**{key: value})
    
    return queryset


def _get_date_field(model_class) -> str:
    """Get the primary date field for a model."""
    date_fields = ['created_at', 'fecha', 'date_created', 'timestamp']
    
    for field_name in date_fields:
        if hasattr(model_class, field_name):
            return field_name
    
    return None


def _create_excel_file(module_name: str, queryset: QuerySet, include_charts: bool = True) -> str:
    """Create Excel file with corporate formatting and multiple sheets."""
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module_name}_export_{timestamp}.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    # Ensure exports directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert queryset to DataFrame
    data = list(queryset.values())
    if not data:
        # Create empty file if no data
        workbook = Workbook()
        workbook.save(file_path)
        return file_path
    
    df = pd.DataFrame(data)
    
    # Create workbook with multiple sheets
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        # Summary sheet
        summary_df = _create_summary_data(df, module_name)
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Apply corporate formatting
        _apply_excel_formatting(writer, df, summary_df, include_charts)
    
    return file_path


def _create_summary_data(df: pd.DataFrame, module_name: str) -> pd.DataFrame:
    """Create summary statistics for the exported data."""
    summary_data = {
        'Métrica': ['Total de Registros', 'Fecha de Exportación', 'Módulo'],
        'Valor': [len(df), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), module_name.title()]
    }
    
    # Add module-specific summaries
    if 'precio' in df.columns:
        summary_data['Métrica'].extend(['Precio Promedio', 'Precio Total'])
        summary_data['Valor'].extend([
            f"${df['precio'].mean():.2f}",
            f"${df['precio'].sum():.2f}"
        ])
    
    return pd.DataFrame(summary_data)


def _apply_excel_formatting(writer, main_df: pd.DataFrame, summary_df: pd.DataFrame, include_charts: bool):
    """Apply corporate formatting to Excel sheets."""
    
    # Get workbook and worksheets
    workbook = writer.book
    main_sheet = writer.sheets['Datos']
    summary_sheet = writer.sheets['Resumen']
    
    # Define corporate colors and styles
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Format main data sheet
    for cell in main_sheet[1]:  # Header row
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
    
    # Auto-adjust column widths
    for column in main_sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        adjusted_width = min(max_length + 2, 50)
        main_sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Format summary sheet
    for cell in summary_sheet[1]:  # Header row
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
    
    # Add charts if requested
    if include_charts and len(main_df) > 0:
        _add_excel_charts(main_sheet, main_df)


def _add_excel_charts(sheet, df: pd.DataFrame):
    """Add charts to Excel sheet based on data type."""
    try:
        # Only add charts if we have numeric data
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) > 0:
            chart = BarChart()
            chart.title = "Resumen de Datos"
            chart.x_axis.title = "Categorías"
            chart.y_axis.title = "Valores"
            
            # Add chart to sheet (position it to the right of data)
            sheet.add_chart(chart, f"H2")
            
    except Exception as e:
        logger.warning(f"Could not add charts to Excel: {str(e)}")


def _create_pdf_file(module_name: str, template_name: str, queryset: QuerySet) -> str:
    """Create PDF file with custom template and corporate branding."""
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module_name}_{template_name}_{timestamp}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    
    # Ensure exports directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#366092'),
        alignment=1  # Center alignment
    )
    
    # Add title
    title = Paragraph(f"Reporte de {module_name.title()}", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Convert queryset to table data
    data = list(queryset.values())
    if data:
        # Create table
        table_data = _prepare_pdf_table_data(data)
        table = Table(table_data)
        
        # Apply table styling
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        # No data message
        no_data = Paragraph("No hay datos para mostrar", styles['Normal'])
        story.append(no_data)
    
    # Add footer with export info
    story.append(Spacer(1, 30))
    footer_text = f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total de registros: {len(data)}"
    footer = Paragraph(footer_text, styles['Normal'])
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    return file_path


def _prepare_pdf_table_data(data: List[Dict]) -> List[List]:
    """Prepare data for PDF table format."""
    if not data:
        return []
    
    # Get headers (limit to reasonable number for PDF width)
    headers = list(data[0].keys())[:8]  # Limit to 8 columns for readability
    
    # Prepare table data
    table_data = [headers]
    
    for row in data[:50]:  # Limit to 50 rows for PDF
        row_data = []
        for header in headers:
            value = row.get(header, '')
            # Truncate long values
            if isinstance(value, str) and len(value) > 20:
                value = value[:17] + "..."
            row_data.append(str(value))
        table_data.append(row_data)
    
    return table_data


def _send_export_notification(user, file_path: str, format_type: str, module_name: str):
    """Send email notification when export is complete."""
    try:
        subject = f"Exportación {format_type} Completada - {module_name.title()}"
        
        message = f"""
        Hola {user.get_full_name() or user.username},
        
        Tu exportación de datos ha sido completada exitosamente.
        
        Detalles:
        - Módulo: {module_name.title()}
        - Formato: {format_type}
        - Archivo: {os.path.basename(file_path)}
        - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        El archivo estará disponible para descarga en el sistema.
        
        Saludos,
        Sistema Logístico
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        # Attach file if it's small enough (< 10MB)
        if os.path.exists(file_path) and os.path.getsize(file_path) < 10 * 1024 * 1024:
            email.attach_file(file_path)
        
        email.send()
        logger.info(f"Export notification sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send export notification: {str(e)}")


def _send_failure_notification(user, module_name: str, format_type: str, error_message: str):
    """Send email notification when export fails."""
    try:
        subject = f"Error en Exportación {format_type} - {module_name.title()}"
        
        message = f"""
        Hola {user.get_full_name() or user.username},
        
        Lamentablemente, tu exportación de datos ha fallado.
        
        Detalles:
        - Módulo: {module_name.title()}
        - Formato: {format_type}
        - Error: {error_message}
        - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Por favor, intenta nuevamente o contacta al administrador del sistema.
        
        Saludos,
        Sistema Logístico
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        
        email.send()
        logger.info(f"Export failure notification sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send failure notification: {str(e)}")