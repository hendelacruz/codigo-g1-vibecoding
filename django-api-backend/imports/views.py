"""
Views para el sistema de importación de Excel.
Proporciona endpoints para importar datos desde archivos Excel.
"""
import os
import tempfile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .importers import (
    GPSImporter, 
    SIMCardImporter, 
    ClienteImporter, 
    ProveedorImporter,
    VentasImporter
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_excel(request):
    """
    Endpoint principal para importar datos desde archivos Excel.
    
    Parámetros:
    - file: Archivo Excel a importar
    - module: Módulo a importar ('gps', 'simcard', 'cliente', 'proveedor')
    
    Respuesta:
    - success: Número de registros importados exitosamente
    - errors: Lista de errores encontrados
    - total_rows: Total de filas procesadas
    """
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'rol') or request.user.rol.nombre != 'administrador':
        return Response(
            {'error': 'Solo los administradores pueden importar datos'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validar parámetros
    if 'file' not in request.FILES:
        return Response(
            {'error': 'Debe proporcionar un archivo Excel'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    module = request.data.get('module')
    if not module:
        return Response(
            {'error': 'Debe especificar el módulo a importar'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar tipo de archivo
    file = request.FILES['file']
    if not file.name.endswith(('.xlsx', '.xls')):
        return Response(
            {'error': 'El archivo debe ser un Excel (.xlsx o .xls)'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Guardar archivo temporalmente
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Seleccionar importador según el módulo
        importers = {
            'gps': GPSImporter,
            'simcard': SIMCardImporter,
            'cliente': ClienteImporter,
            'proveedor': ProveedorImporter,
            'ventas': VentasImporter,
        }
        
        if module not in importers:
            return Response(
                {'error': f'Módulo "{module}" no válido. Opciones: {", ".join(importers.keys())}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ejecutar importación
        importer = importers[module]()
        result = importer.import_from_excel(temp_file_path)
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        # Determinar código de respuesta
        if result['error_count'] == 0:
            response_status = status.HTTP_201_CREATED
        elif result['success_count'] > 0:
            response_status = status.HTTP_207_MULTI_STATUS
        else:
            response_status = status.HTTP_400_BAD_REQUEST
        
        return Response(result, status=response_status)
        
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_template(request, module):
    """
    Endpoint para descargar plantillas Excel para importación.
    
    Parámetros:
    - module: Módulo para el cual generar la plantilla
    
    Respuesta:
    - Información sobre las columnas requeridas para cada módulo
    """
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'rol') or request.user.rol.nombre != 'administrador':
        return Response(
            {'error': 'Solo los administradores pueden acceder a las plantillas'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    templates = {
        'gps': {
            'required_columns': [
                'fecha_compra', 'imei', 'marca', 'modelo', 
                'numero_factura', 'proveedor_ruc'
            ],
            'optional_columns': [
                'estado', 'precio_compra', 'observaciones'
            ],
            'example_data': {
                'fecha_compra': '2024-01-15',
                'imei': '123456789012345',
                'marca': 'Teltonika',
                'modelo': 'FMB920',
                'numero_factura': 'F001-123',
                'proveedor_ruc': '20123456789',
                'estado': 'disponible',
                'precio_compra': '250.00',
                'observaciones': 'Dispositivo nuevo'
            }
        },
        'simcard': {
            'required_columns': [
                'fecha_compra', 'numero_factura', 'numero_chip', 
                'icc', 'proveedor_ruc'
            ],
            'optional_columns': [
                'estado', 'operadora', 'plan', 'precio_compra', 'observaciones'
            ],
            'example_data': {
                'fecha_compra': '2024-01-15',
                'numero_factura': 'F001-124',
                'numero_chip': '987654321',
                'icc': '89511234567890123456',
                'proveedor_ruc': '20123456789',
                'estado': 'disponible',
                'operadora': 'Claro',
                'plan': 'Plan Datos 5GB',
                'precio_compra': '15.00'
            }
        },
        'cliente': {
            'required_columns': [
                'nombre', 'ruc', 'direccion', 'contacto', 'celular', 'correo'
            ],
            'optional_columns': [],
            'example_data': {
                'nombre': 'Transportes ABC S.A.C.',
                'ruc': '20987654321',
                'direccion': 'Av. Principal 123, Lima',
                'contacto': 'Juan Pérez',
                'celular': '987654321',
                'correo': 'contacto@transportesabc.com'
            }
        },
        'proveedor': {
            'required_columns': [
                'nombre', 'ruc', 'direccion', 'contacto', 'celular'
            ],
            'optional_columns': [],
            'example_data': {
                'nombre': 'Tecnología GPS S.A.C.',
                'ruc': '20123456789',
                'direccion': 'Jr. Tecnología 456, Lima',
                'contacto': 'María García',
                'celular': '912345678'
            }
        },
        'ventas': {
            'required_columns': [
                'mes', 'fecha_pago', 'numero_operacion', 'tipo_pago', 'banco',
                'numero_factura', 'fecha_generacion_factura', 'cliente_ruc',
                'descripcion', 'unidad_placa', 'precio'
            ],
            'optional_columns': ['estado'],
            'example_data': {
                'mes': '2024-01-01',
                'fecha_pago': '14:30:00',
                'numero_operacion': 'OP123456',
                'tipo_pago': 'transferencia',
                'banco': 'BCP',
                'numero_factura': 'F001-123',
                'fecha_generacion_factura': '2024-01-15 14:30:00',
                'cliente_ruc': '20123456789',
                'descripcion': 'Servicio de GPS mensual',
                'unidad_placa': 'ABC-123',
                'precio': '118.00',
                'estado': 'pendiente'
            },
            'validation_notes': [
                'tipo_pago: efectivo, transferencia, deposito, cheque, tarjeta_credito, tarjeta_debito, yape, plin, otro',
                'estado: pendiente, pagado, parcial, vencido, cancelado, anulado',
                'El cliente debe existir en el sistema',
                'La unidad debe pertenecer al cliente especificado',
                'Los campos importe, igv y total se calculan automáticamente'
            ]
        }
    }
    
    if module not in templates:
        return Response(
            {'error': f'Módulo "{module}" no válido. Opciones: {", ".join(templates.keys())}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(templates[module], status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_status(request):
    """
    Endpoint para obtener información sobre los módulos disponibles para importación.
    
    Respuesta:
    - Lista de módulos disponibles con sus descripciones
    """
    # Verificar que el usuario sea administrador
    if not hasattr(request.user, 'rol') or request.user.rol.nombre != 'administrador':
        return Response(
            {'error': 'Solo los administradores pueden acceder a esta información'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    modules = {
        'gps': {
            'name': 'Dispositivos GPS',
            'description': 'Importar dispositivos GPS del inventario',
            'model': 'inventory.GPS'
        },
        'simcard': {
            'name': 'Tarjetas SIM',
            'description': 'Importar tarjetas SIM del inventario',
            'model': 'inventory.SIMCard'
        },
        'cliente': {
            'name': 'Clientes',
            'description': 'Importar clientes del sistema',
            'model': 'entities.Cliente'
        },
        'proveedor': {
            'name': 'Proveedores',
            'description': 'Importar proveedores del sistema',
            'model': 'entities.Proveedor'
        },
        'ventas': {
            'name': 'Ventas',
            'description': 'Importar ventas y facturación del sistema',
            'model': 'sales.Ventas'
        }
    }
    
    return Response({
        'available_modules': modules,
        'supported_formats': ['.xlsx', '.xls'],
        'max_file_size': '10MB',
        'permissions_required': 'administrador'
    }, status=status.HTTP_200_OK)
