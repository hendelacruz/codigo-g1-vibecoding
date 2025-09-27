"""
Utilidades para el sistema de importación de Excel.
Contiene funciones comunes para validación y procesamiento de datos.
"""
import pandas as pd
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import transaction
import re


class ImportError(Exception):
    """Excepción personalizada para errores de importación"""
    pass


class BaseImporter:
    """
    Clase base para todos los importadores.
    Proporciona funcionalidades comunes para validación y procesamiento.
    """
    
    def __init__(self):
        self.errors = []
        self.success_count = 0
        self.total_rows = 0
    
    def validate_file_structure(self, df, required_columns):
        """
        Valida que el archivo Excel tenga las columnas requeridas.
        
        Args:
            df (DataFrame): DataFrame de pandas con los datos
            required_columns (list): Lista de columnas requeridas
            
        Raises:
            ImportError: Si faltan columnas requeridas
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ImportError(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
    
    def validate_ruc(self, ruc):
        """
        Valida formato de RUC peruano (11 dígitos).
        
        Args:
            ruc (str): RUC a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not ruc or not isinstance(ruc, str):
            return False
        return bool(re.match(r'^\d{11}$', str(ruc).strip()))
    
    def validate_dni(self, dni):
        """
        Valida formato de DNI peruano (8 dígitos).
        
        Args:
            dni (str): DNI a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not dni or not isinstance(dni, str):
            return False
        return bool(re.match(r'^\d{8}$', str(dni).strip()))
    
    def validate_imei(self, imei):
        """
        Valida formato de IMEI (15 dígitos).
        
        Args:
            imei (str): IMEI a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not imei or not isinstance(imei, str):
            return False
        return bool(re.match(r'^\d{15}$', str(imei).strip()))
    
    def validate_celular(self, celular):
        """
        Valida formato de celular peruano (9 dígitos).
        
        Args:
            celular (str): Celular a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not celular or not isinstance(celular, str):
            return False
        return bool(re.match(r'^\d{9}$', str(celular).strip()))
    
    def parse_date(self, date_value):
        """
        Convierte diferentes formatos de fecha a datetime.
        
        Args:
            date_value: Valor de fecha en diferentes formatos
            
        Returns:
            datetime: Fecha parseada o None si no es válida
        """
        if pd.isna(date_value):
            return None
            
        if isinstance(date_value, datetime):
            return date_value
            
        if isinstance(date_value, str):
            # Intentar diferentes formatos de fecha
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value.strip(), fmt)
                except ValueError:
                    continue
        
        return None
    
    def clean_string(self, value):
        """
        Limpia y normaliza strings.
        
        Args:
            value: Valor a limpiar
            
        Returns:
            str: String limpio o None si está vacío
        """
        if pd.isna(value) or value is None:
            return None
        
        cleaned = str(value).strip()
        return cleaned if cleaned else None
    
    def clean_decimal(self, value):
        """
        Limpia y convierte valores decimales.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Decimal: Valor decimal o None si no es válido
        """
        if pd.isna(value) or value is None:
            return None
            
        try:
            from decimal import Decimal
            return Decimal(str(value).replace(',', '.'))
        except:
            return None
    
    def add_error(self, row_number, field, message):
        """
        Agrega un error a la lista de errores.
        
        Args:
            row_number (int): Número de fila donde ocurrió el error
            field (str): Campo que causó el error
            message (str): Mensaje de error
        """
        self.errors.append({
            'row': row_number,
            'field': field,
            'message': message
        })
    
    def get_summary(self):
        """
        Retorna un resumen del proceso de importación.
        
        Returns:
            dict: Resumen con estadísticas del proceso
        """
        return {
            'total_rows': self.total_rows,
            'success_count': self.success_count,
            'error_count': len(self.errors),
            'errors': self.errors
        }