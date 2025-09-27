"""
Importadores específicos para cada modelo del sistema.
Cada importador maneja la lógica específica de validación e importación.
"""
import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from .utils import BaseImporter, ImportError
from inventory.models import GPS, SIMCard, Otros
from entities.models import Cliente, Proveedor, Unidad
from services.models import Servicio, TipoTrabajo
from sales.models import Ventas, TIPO_PAGO_CHOICES, ESTADO_VENTA_CHOICES
from authentication.models import CustomUser


class GPSImporter(BaseImporter):
    """
    Importador para dispositivos GPS desde archivos Excel.
    
    Estructura esperada del Excel:
    - fecha_compra: Fecha de compra (YYYY-MM-DD o DD/MM/YYYY)
    - imei: IMEI del dispositivo (15 dígitos)
    - marca: Marca del dispositivo
    - modelo: Modelo del dispositivo
    - numero_factura: Número de factura
    - proveedor_ruc: RUC del proveedor (11 dígitos)
    - estado: Estado del dispositivo (opcional, default: disponible)
    - precio_compra: Precio de compra (opcional)
    - observaciones: Observaciones (opcional)
    """
    
    REQUIRED_COLUMNS = [
        'fecha_compra', 'imei', 'marca', 'modelo', 
        'numero_factura', 'proveedor_ruc'
    ]
    
    OPTIONAL_COLUMNS = [
        'estado', 'precio_compra', 'observaciones'
    ]
    
    def import_from_excel(self, file_path):
        """
        Importa dispositivos GPS desde un archivo Excel.
        
        Args:
            file_path (str): Ruta al archivo Excel
            
        Returns:
            dict: Resumen del proceso de importación
        """
        try:
            # Leer archivo Excel
            df = pd.read_excel(file_path)
            self.total_rows = len(df)
            
            # Validar estructura del archivo
            self.validate_file_structure(df, self.REQUIRED_COLUMNS)
            
            # Procesar cada fila
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_gps_row(index + 2, row)  # +2 porque Excel empieza en 1 y tiene header
                    except Exception as e:
                        self.add_error(index + 2, 'general', str(e))
            
            return self.get_summary()
            
        except ImportError as e:
            self.add_error(0, 'file', str(e))
            return self.get_summary()
        except Exception as e:
            self.add_error(0, 'file', f"Error inesperado: {str(e)}")
            return self.get_summary()
    
    def _process_gps_row(self, row_number, row):
        """
        Procesa una fila individual del Excel para crear un GPS.
        
        Args:
            row_number (int): Número de fila en el Excel
            row (Series): Datos de la fila
        """
        # Validar y limpiar datos
        fecha_compra = self.parse_date(row.get('fecha_compra'))
        if not fecha_compra:
            self.add_error(row_number, 'fecha_compra', 'Fecha de compra inválida')
            return
        
        imei = self.clean_string(row.get('imei'))
        if not self.validate_imei(imei):
            self.add_error(row_number, 'imei', 'IMEI debe tener 15 dígitos')
            return
        
        # Verificar si el IMEI ya existe
        if GPS.objects.filter(imei=imei).exists():
            self.add_error(row_number, 'imei', f'IMEI {imei} ya existe en el sistema')
            return
        
        marca = self.clean_string(row.get('marca'))
        if not marca:
            self.add_error(row_number, 'marca', 'Marca es requerida')
            return
        
        modelo = self.clean_string(row.get('modelo'))
        if not modelo:
            self.add_error(row_number, 'modelo', 'Modelo es requerido')
            return
        
        numero_factura = self.clean_string(row.get('numero_factura'))
        if not numero_factura:
            self.add_error(row_number, 'numero_factura', 'Número de factura es requerido')
            return
        
        proveedor_ruc = self.clean_string(row.get('proveedor_ruc'))
        if not self.validate_ruc(proveedor_ruc):
            self.add_error(row_number, 'proveedor_ruc', 'RUC del proveedor debe tener 11 dígitos')
            return
        
        # Buscar o crear proveedor
        try:
            proveedor = Proveedor.objects.get(ruc=proveedor_ruc)
        except Proveedor.DoesNotExist:
            self.add_error(row_number, 'proveedor_ruc', f'Proveedor con RUC {proveedor_ruc} no existe')
            return
        
        # Campos opcionales
        estado = self.clean_string(row.get('estado', 'disponible'))
        if estado not in dict(GPS._meta.get_field('estado').choices):
            estado = 'disponible'
        
        precio_compra = self.clean_decimal(row.get('precio_compra'))
        observaciones = self.clean_string(row.get('observaciones', ''))
        
        # Crear el GPS
        try:
            gps = GPS.objects.create(
                fecha_compra=fecha_compra,
                imei=imei,
                marca=marca,
                modelo=modelo,
                numero_factura=numero_factura,
                proveedor=proveedor,
                estado=estado,
                precio_compra=precio_compra,
                observaciones=observaciones
            )
            self.success_count += 1
            
        except ValidationError as e:
            self.add_error(row_number, 'validation', str(e))
        except Exception as e:
            self.add_error(row_number, 'creation', f'Error al crear GPS: {str(e)}')


class SIMCardImporter(BaseImporter):
    """
    Importador para tarjetas SIM desde archivos Excel.
    
    Estructura esperada del Excel:
    - fecha_compra: Fecha de compra
    - numero_factura: Número de factura
    - numero_chip: Número de teléfono (9 dígitos)
    - icc: Código ICC único
    - proveedor_ruc: RUC del proveedor
    - estado: Estado de la SIM (opcional)
    - operadora: Operadora (opcional)
    - plan: Plan contratado (opcional)
    - precio_compra: Precio de compra (opcional)
    - observaciones: Observaciones (opcional)
    """
    
    REQUIRED_COLUMNS = [
        'fecha_compra', 'numero_factura', 'numero_chip', 
        'icc', 'proveedor_ruc'
    ]
    
    def import_from_excel(self, file_path):
        """Importa tarjetas SIM desde un archivo Excel."""
        try:
            df = pd.read_excel(file_path)
            self.total_rows = len(df)
            
            self.validate_file_structure(df, self.REQUIRED_COLUMNS)
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_simcard_row(index + 2, row)
                    except Exception as e:
                        self.add_error(index + 2, 'general', str(e))
            
            return self.get_summary()
            
        except ImportError as e:
            self.add_error(0, 'file', str(e))
            return self.get_summary()
        except Exception as e:
            self.add_error(0, 'file', f"Error inesperado: {str(e)}")
            return self.get_summary()
    
    def _process_simcard_row(self, row_number, row):
        """Procesa una fila individual para crear una SIM."""
        # Validaciones básicas
        fecha_compra = self.parse_date(row.get('fecha_compra'))
        if not fecha_compra:
            self.add_error(row_number, 'fecha_compra', 'Fecha de compra inválida')
            return
        
        numero_chip = self.clean_string(row.get('numero_chip'))
        if not self.validate_celular(numero_chip):
            self.add_error(row_number, 'numero_chip', 'Número de chip debe tener 9 dígitos')
            return
        
        # Verificar si el número ya existe
        if SIMCard.objects.filter(numero_chip=numero_chip).exists():
            self.add_error(row_number, 'numero_chip', f'Número {numero_chip} ya existe')
            return
        
        icc = self.clean_string(row.get('icc'))
        if not icc:
            self.add_error(row_number, 'icc', 'ICC es requerido')
            return
        
        # Verificar si el ICC ya existe
        if SIMCard.objects.filter(icc=icc).exists():
            self.add_error(row_number, 'icc', f'ICC {icc} ya existe')
            return
        
        numero_factura = self.clean_string(row.get('numero_factura'))
        if not numero_factura:
            self.add_error(row_number, 'numero_factura', 'Número de factura es requerido')
            return
        
        proveedor_ruc = self.clean_string(row.get('proveedor_ruc'))
        if not self.validate_ruc(proveedor_ruc):
            self.add_error(row_number, 'proveedor_ruc', 'RUC del proveedor inválido')
            return
        
        # Buscar proveedor
        try:
            proveedor = Proveedor.objects.get(ruc=proveedor_ruc)
        except Proveedor.DoesNotExist:
            self.add_error(row_number, 'proveedor_ruc', f'Proveedor con RUC {proveedor_ruc} no existe')
            return
        
        # Campos opcionales
        estado = self.clean_string(row.get('estado', 'disponible'))
        operadora = self.clean_string(row.get('operadora', ''))
        plan = self.clean_string(row.get('plan', ''))
        precio_compra = self.clean_decimal(row.get('precio_compra'))
        observaciones = self.clean_string(row.get('observaciones', ''))
        
        # Crear la SIM
        try:
            simcard = SIMCard.objects.create(
                fecha_compra=fecha_compra,
                numero_factura=numero_factura,
                numero_chip=numero_chip,
                icc=icc,
                proveedor=proveedor,
                estado=estado,
                operadora=operadora,
                plan=plan,
                precio_compra=precio_compra,
                observaciones=observaciones
            )
            self.success_count += 1
            
        except ValidationError as e:
            self.add_error(row_number, 'validation', str(e))
        except Exception as e:
            self.add_error(row_number, 'creation', f'Error al crear SIM: {str(e)}')


class ClienteImporter(BaseImporter):
    """
    Importador para clientes desde archivos Excel.
    
    Estructura esperada del Excel:
    - nombre: Nombre o razón social
    - ruc: RUC del cliente (11 dígitos)
    - direccion: Dirección completa
    - contacto: Persona de contacto
    - celular: Número de celular (9 dígitos)
    - correo: Correo electrónico
    """
    
    REQUIRED_COLUMNS = [
        'nombre', 'ruc', 'direccion', 'contacto', 'celular', 'correo'
    ]
    
    def import_from_excel(self, file_path):
        """Importa clientes desde un archivo Excel."""
        try:
            df = pd.read_excel(file_path)
            self.total_rows = len(df)
            
            self.validate_file_structure(df, self.REQUIRED_COLUMNS)
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_cliente_row(index + 2, row)
                    except Exception as e:
                        self.add_error(index + 2, 'general', str(e))
            
            return self.get_summary()
            
        except ImportError as e:
            self.add_error(0, 'file', str(e))
            return self.get_summary()
        except Exception as e:
            self.add_error(0, 'file', f"Error inesperado: {str(e)}")
            return self.get_summary()
    
    def _process_cliente_row(self, row_number, row):
        """Procesa una fila individual para crear un cliente."""
        nombre = self.clean_string(row.get('nombre'))
        if not nombre:
            self.add_error(row_number, 'nombre', 'Nombre es requerido')
            return
        
        ruc = self.clean_string(row.get('ruc'))
        if not self.validate_ruc(ruc):
            self.add_error(row_number, 'ruc', 'RUC debe tener 11 dígitos')
            return
        
        # Verificar si el RUC ya existe
        if Cliente.objects.filter(ruc=ruc).exists():
            self.add_error(row_number, 'ruc', f'Cliente con RUC {ruc} ya existe')
            return
        
        direccion = self.clean_string(row.get('direccion'))
        if not direccion:
            self.add_error(row_number, 'direccion', 'Dirección es requerida')
            return
        
        contacto = self.clean_string(row.get('contacto'))
        if not contacto:
            self.add_error(row_number, 'contacto', 'Contacto es requerido')
            return
        
        celular = self.clean_string(row.get('celular'))
        if not self.validate_celular(celular):
            self.add_error(row_number, 'celular', 'Celular debe tener 9 dígitos')
            return
        
        correo = self.clean_string(row.get('correo'))
        if not correo:
            self.add_error(row_number, 'correo', 'Correo es requerido')
            return
        
        # Crear el cliente
        try:
            cliente = Cliente.objects.create(
                nombre=nombre,
                ruc=ruc,
                direccion=direccion,
                contacto=contacto,
                celular=celular,
                correo=correo
            )
            self.success_count += 1
            
        except ValidationError as e:
            self.add_error(row_number, 'validation', str(e))
        except Exception as e:
            self.add_error(row_number, 'creation', f'Error al crear cliente: {str(e)}')


class ProveedorImporter(BaseImporter):
    """
    Importador para proveedores desde archivos Excel.
    
    Estructura esperada del Excel:
    - nombre: Nombre o razón social
    - ruc: RUC del proveedor (11 dígitos)
    - direccion: Dirección completa
    - contacto: Persona de contacto
    - celular: Número de celular (9 dígitos)
    """
    
    REQUIRED_COLUMNS = [
        'nombre', 'ruc', 'direccion', 'contacto', 'celular'
    ]
    
    def import_from_excel(self, file_path):
        """Importa proveedores desde un archivo Excel."""
        try:
            df = pd.read_excel(file_path)
            self.total_rows = len(df)
            
            self.validate_file_structure(df, self.REQUIRED_COLUMNS)
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_proveedor_row(index + 2, row)
                    except Exception as e:
                        self.add_error(index + 2, 'general', str(e))
            
            return self.get_summary()
            
        except ImportError as e:
            self.add_error(0, 'file', str(e))
            return self.get_summary()
        except Exception as e:
            self.add_error(0, 'file', f"Error inesperado: {str(e)}")
            return self.get_summary()
    
    def _process_proveedor_row(self, row_number, row):
        """Procesa una fila individual para crear un proveedor."""
        nombre = self.clean_string(row.get('nombre'))
        if not nombre:
            self.add_error(row_number, 'nombre', 'Nombre es requerido')
            return
        
        ruc = self.clean_string(row.get('ruc'))
        if not self.validate_ruc(ruc):
            self.add_error(row_number, 'ruc', 'RUC debe tener 11 dígitos')
            return
        
        # Verificar si el RUC ya existe
        if Proveedor.objects.filter(ruc=ruc).exists():
            self.add_error(row_number, 'ruc', f'Proveedor con RUC {ruc} ya existe')
            return
        
        direccion = self.clean_string(row.get('direccion'))
        if not direccion:
            self.add_error(row_number, 'direccion', 'Dirección es requerida')
            return
        
        contacto = self.clean_string(row.get('contacto'))
        if not contacto:
            self.add_error(row_number, 'contacto', 'Contacto es requerido')
            return
        
        celular = self.clean_string(row.get('celular'))
        if not self.validate_celular(celular):
            self.add_error(row_number, 'celular', 'Celular debe tener 9 dígitos')
            return
        
        # Crear el proveedor
        try:
            proveedor = Proveedor.objects.create(
                nombre=nombre,
                ruc=ruc,
                direccion=direccion,
                contacto=contacto,
                celular=celular
            )
            self.success_count += 1
            
        except ValidationError as e:
            self.add_error(row_number, 'validation', str(e))
        except Exception as e:
            self.add_error(row_number, 'creation', f'Error al crear proveedor: {str(e)}')


class VentasImporter(BaseImporter):
    """
    Importador para ventas desde archivos Excel.
    
    Estructura esperada del Excel:
    - mes: Mes de la venta (YYYY-MM-DD)
    - fecha_pago: Hora del pago (HH:MM:SS o HH:MM)
    - numero_operacion: Número de operación bancaria
    - tipo_pago: Tipo de pago (efectivo, transferencia, etc.)
    - banco: Banco donde se realizó la operación
    - numero_factura: Número único de factura
    - fecha_generacion_factura: Fecha y hora de generación (YYYY-MM-DD HH:MM:SS)
    - cliente_ruc: RUC del cliente (11 dígitos)
    - descripcion: Descripción de la venta
    - unidad_placa: Placa de la unidad vehicular
    - precio: Precio total con IGV incluido
    - estado: Estado de la venta (opcional, default: pendiente)
    """
    
    REQUIRED_COLUMNS = [
        'mes', 'fecha_pago', 'numero_operacion', 'tipo_pago', 'banco',
        'numero_factura', 'fecha_generacion_factura', 'cliente_ruc',
        'descripcion', 'unidad_placa', 'precio'
    ]
    
    OPTIONAL_COLUMNS = [
        'estado'
    ]
    
    def __init__(self):
        super().__init__()
        self.required_columns = self.REQUIRED_COLUMNS
        self.optional_columns = self.OPTIONAL_COLUMNS
    
    def import_from_excel(self, file_path):
        """Importa ventas desde un archivo Excel."""
        try:
            df = pd.read_excel(file_path)
            self.total_rows = len(df)
            
            self.validate_file_structure(df, self.REQUIRED_COLUMNS)
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_venta_row(index + 2, row)
                    except Exception as e:
                        self.add_error(index + 2, 'general', str(e))
            
            return self.get_summary()
            
        except ImportError as e:
            self.add_error(0, 'file', str(e))
            return self.get_summary()
        except Exception as e:
            self.add_error(0, 'file', f"Error inesperado: {str(e)}")
            return self.get_summary()
    
    def _process_venta_row(self, row_number, row):
        """Procesa una fila individual para crear una venta."""
        # Validar mes
        mes = self.parse_date(row.get('mes'))
        if not mes:
            self.add_error(row_number, 'mes', 'Mes inválido (formato: YYYY-MM-DD)')
            return
        
        # Validar fecha_pago (hora)
        fecha_pago = self._parse_time(row.get('fecha_pago'))
        if not fecha_pago:
            self.add_error(row_number, 'fecha_pago', 'Hora de pago inválida (formato: HH:MM:SS)')
            return
        
        # Validar número de operación
        numero_operacion = self.clean_string(row.get('numero_operacion'))
        if not numero_operacion:
            self.add_error(row_number, 'numero_operacion', 'Número de operación es requerido')
            return
        
        # Validar tipo de pago
        tipo_pago = self.clean_string(row.get('tipo_pago'))
        if not tipo_pago:
            self.add_error(row_number, 'tipo_pago', 'Tipo de pago es requerido')
            return
        
        # Verificar que el tipo de pago sea válido
        tipos_validos = [choice[0] for choice in TIPO_PAGO_CHOICES]
        if tipo_pago not in tipos_validos:
            self.add_error(row_number, 'tipo_pago', f'Tipo de pago inválido. Opciones: {", ".join(tipos_validos)}')
            return
        
        # Validar banco
        banco = self.clean_string(row.get('banco'))
        if not banco:
            self.add_error(row_number, 'banco', 'Banco es requerido')
            return
        
        # Validar número de factura
        numero_factura = self.clean_string(row.get('numero_factura'))
        if not numero_factura:
            self.add_error(row_number, 'numero_factura', 'Número de factura es requerido')
            return
        
        # Verificar si el número de factura ya existe
        if Ventas.objects.filter(numero_factura=numero_factura).exists():
            self.add_error(row_number, 'numero_factura', f'Factura {numero_factura} ya existe')
            return
        
        # Validar fecha de generación de factura
        fecha_generacion_factura = self._parse_datetime(row.get('fecha_generacion_factura'))
        if not fecha_generacion_factura:
            self.add_error(row_number, 'fecha_generacion_factura', 'Fecha de generación inválida (formato: YYYY-MM-DD HH:MM:SS)')
            return
        
        # Validar cliente por RUC
        cliente_ruc = self.clean_string(row.get('cliente_ruc'))
        if not self.validate_ruc(cliente_ruc):
            self.add_error(row_number, 'cliente_ruc', 'RUC del cliente debe tener 11 dígitos')
            return
        
        try:
            cliente = Cliente.objects.get(ruc=cliente_ruc)
        except Cliente.DoesNotExist:
            self.add_error(row_number, 'cliente_ruc', f'Cliente con RUC {cliente_ruc} no existe')
            return
        
        # Validar descripción
        descripcion = self.clean_string(row.get('descripcion'))
        if not descripcion:
            self.add_error(row_number, 'descripcion', 'Descripción es requerida')
            return
        
        # Validar unidad por placa
        unidad_placa = self.clean_string(row.get('unidad_placa'))
        if not unidad_placa:
            self.add_error(row_number, 'unidad_placa', 'Placa de unidad es requerida')
            return
        
        try:
            unidad = Unidad.objects.get(placa=unidad_placa)
        except Unidad.DoesNotExist:
            self.add_error(row_number, 'unidad_placa', f'Unidad con placa {unidad_placa} no existe')
            return
        
        # Verificar que la unidad pertenezca al cliente
        if unidad.cliente != cliente:
            self.add_error(row_number, 'unidad_placa', f'La unidad {unidad_placa} no pertenece al cliente {cliente.nombre}')
            return
        
        # Validar precio
        precio = self.clean_decimal(row.get('precio'))
        if not precio or precio <= 0:
            self.add_error(row_number, 'precio', 'Precio debe ser mayor a 0')
            return
        
        # Validar estado (opcional)
        estado = self.clean_string(row.get('estado', 'pendiente'))
        estados_validos = [choice[0] for choice in ESTADO_VENTA_CHOICES]
        if estado not in estados_validos:
            estado = 'pendiente'  # Default si es inválido
        
        # Crear la venta
        try:
            venta = Ventas.objects.create(
                mes=mes,
                fecha_pago=fecha_pago,
                numero_operacion=numero_operacion,
                tipo_pago=tipo_pago,
                banco=banco,
                numero_factura=numero_factura,
                fecha_generacion_factura=fecha_generacion_factura,
                cliente=cliente,
                descripcion=descripcion,
                unidad=unidad,
                precio=precio,
                estado=estado
            )
            # Los campos importe, igv y total se calculan automáticamente en el modelo
            self.success_count += 1
            
        except ValidationError as e:
            self.add_error(row_number, 'validation', str(e))
        except Exception as e:
            self.add_error(row_number, 'creation', f'Error al crear venta: {str(e)}')
    
    def _parse_time(self, time_value):
        """
        Parsea un valor de tiempo desde Excel.
        Acepta formatos: HH:MM:SS, HH:MM
        """
        if pd.isna(time_value):
            return None
        
        try:
            # Si es un string
            if isinstance(time_value, str):
                time_value = time_value.strip()
                # Intentar formato HH:MM:SS
                try:
                    from datetime import datetime
                    parsed = datetime.strptime(time_value, '%H:%M:%S').time()
                    return parsed
                except ValueError:
                    # Intentar formato HH:MM
                    try:
                        parsed = datetime.strptime(time_value, '%H:%M').time()
                        return parsed
                    except ValueError:
                        return None
            
            # Si es un objeto time de pandas/datetime
            elif hasattr(time_value, 'time'):
                return time_value.time()
            
            # Si es un objeto time directo
            elif hasattr(time_value, 'hour'):
                return time_value
            
            return None
            
        except Exception:
            return None
    
    def _parse_datetime(self, datetime_value):
        """
        Parsea un valor de fecha y hora desde Excel.
        Acepta formatos: YYYY-MM-DD HH:MM:SS, DD/MM/YYYY HH:MM:SS
        """
        if pd.isna(datetime_value):
            return None
        
        try:
            # Si es un string
            if isinstance(datetime_value, str):
                datetime_value = datetime_value.strip()
                # Intentar varios formatos
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%d/%m/%Y %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%d/%m/%Y %H:%M',
                ]
                
                for fmt in formats:
                    try:
                        from datetime import datetime
                        return datetime.strptime(datetime_value, fmt)
                    except ValueError:
                        continue
                return None
            
            # Si es un objeto datetime de pandas
            elif hasattr(datetime_value, 'to_pydatetime'):
                return datetime_value.to_pydatetime()
            
            # Si es un objeto datetime directo
            elif hasattr(datetime_value, 'year'):
                return datetime_value
            
            return None
            
        except Exception:
            return None