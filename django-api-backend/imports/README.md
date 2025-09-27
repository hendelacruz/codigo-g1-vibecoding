# Sistema de Importación Excel

## 🎯 Objetivo
Sistema completo para importar datos desde archivos Excel hacia los modelos del sistema logístico.

## 📋 Funcionalidades

### Módulos Soportados
- **GPS**: Dispositivos GPS del inventario
- **SIMCard**: Tarjetas SIM del inventario  
- **Cliente**: Clientes del sistema
- **Proveedor**: Proveedores del sistema
- **Ventas**: Importación de registros de ventas

### Validaciones Implementadas
- ✅ Formato de archivo Excel (.xlsx, .xls)
- ✅ Estructura de columnas requeridas
- ✅ Validación de RUC (11 dígitos)
- ✅ Validación de IMEI (15 dígitos)
- ✅ Validación de números de celular
- ✅ Validación de fechas
- ✅ Verificación de existencia de proveedores

## 🚀 Endpoints Disponibles

### 1. Importar Excel
```
POST /api/imports/excel/
```

**Parámetros:**
- `file`: Archivo Excel a importar
- `module`: Módulo a importar ('gps', 'simcard', 'cliente', 'proveedor')

**Permisos:** Solo administradores

**Respuesta:**
```json
{
    "success_count": 5,
    "error_count": 2,
    "total_rows": 7,
    "errors": [
        {
            "row": 3,
            "error": "IMEI debe tener exactamente 15 dígitos"
        }
    ]
}
```

### 2. Obtener Plantilla
```
GET /api/imports/template/{module}/
```

**Respuesta:**
```json
{
    "required_columns": ["fecha_compra", "imei", "marca", "modelo"],
    "optional_columns": ["estado", "precio_compra"],
    "example_data": {
        "fecha_compra": "2024-01-15",
        "imei": "123456789012345"
    }
}
```

### 3. Estado del Sistema
```
GET /api/imports/status/
```

**Respuesta:**
```json
{
    "available_modules": {
        "gps": {
            "name": "Dispositivos GPS",
            "description": "Importar dispositivos GPS del inventario"
        }
    },
    "supported_formats": [".xlsx", ".xls"],
    "max_file_size": "10MB"
}
```

## 📊 Estructura de Excel por Módulo

### GPS
**Columnas Requeridas:**
- `fecha_compra`: Fecha de compra (YYYY-MM-DD)
- `imei`: IMEI del dispositivo (15 dígitos)
- `marca`: Marca del dispositivo
- `modelo`: Modelo del dispositivo
- `numero_factura`: Número de factura
- `proveedor_ruc`: RUC del proveedor (11 dígitos)

**Columnas Opcionales:**
- `estado`: Estado del dispositivo (disponible, asignado, dañado)
- `precio_compra`: Precio de compra
- `observaciones`: Observaciones adicionales

### SIMCard
**Columnas Requeridas:**
- `fecha_compra`: Fecha de compra (YYYY-MM-DD)
- `numero_factura`: Número de factura
- `numero_chip`: Número del chip
- `icc`: Código ICC de la SIM
- `proveedor_ruc`: RUC del proveedor (11 dígitos)

**Columnas Opcionales:**
- `estado`: Estado de la SIM
- `operadora`: Operadora telefónica
- `plan`: Plan de datos
- `precio_compra`: Precio de compra

### Cliente
**Columnas Requeridas:**
- `nombre`: Nombre del cliente
- `ruc`: RUC del cliente (11 dígitos)
- `direccion`: Dirección del cliente
- `contacto`: Persona de contacto
- `celular`: Número de celular (9 dígitos)
- `correo`: Correo electrónico

### Proveedor
**Columnas Requeridas:**
- `nombre`: Nombre del proveedor
- `ruc`: RUC del proveedor (11 dígitos)
- `direccion`: Dirección del proveedor
- `contacto`: Persona de contacto
- `celular`: Número de celular (9 dígitos)
- `correo`: Correo electrónico

**Columnas Opcionales:**
- `banco`: Banco del proveedor
- `numero_cuenta`: Número de cuenta bancaria
- `cci`: Código de cuenta interbancaria

### Ventas
**Columnas Requeridas:**
- `mes`: Mes de la venta (YYYY-MM-DD)
- `fecha_pago`: Hora de pago (HH:MM:SS)
- `numero_operacion`: Número de operación
- `tipo_pago`: Tipo de pago (efectivo, transferencia, deposito, cheque)
- `banco`: Banco
- `numero_factura`: Número de factura (único)
- `fecha_generacion_factura`: Fecha y hora de generación (YYYY-MM-DD HH:MM:SS)
- `cliente_ruc`: RUC del cliente (debe existir en el sistema)
- `descripcion`: Descripción del servicio
- `unidad_placa`: Placa de la unidad (debe pertenecer al cliente)
- `precio`: Precio con IGV (decimal)

**Columnas Opcionales:**
- `estado`: Estado de la venta (pendiente, pagado, anulado, default: pendiente)

## 🔧 Uso Programático

### Importar desde código
```python
from imports.importers import GPSImporter

importer = GPSImporter()
result = importer.import_from_excel('archivo.xlsx')

print(f"Importados: {result['success_count']}")
print(f"Errores: {result['error_count']}")
```

### Validaciones personalizadas
```python
from imports.utils import BaseImporter

class MiImporter(BaseImporter):
    def validate_custom_field(self, value):
        # Lógica de validación personalizada
        return True
```

## 🛡️ Seguridad

- **Autenticación requerida**: Todos los endpoints requieren autenticación
- **Permisos de administrador**: Solo usuarios con rol 'administrador' pueden importar
- **Validación de archivos**: Solo se aceptan archivos Excel válidos
- **Manejo seguro de archivos**: Los archivos temporales se eliminan automáticamente

## 🧪 Testing

Ejecutar tests:
```bash
python manage.py test imports
```

Los tests cubren:
- Importación exitosa de cada módulo
- Validaciones de datos
- Permisos de endpoints
- Manejo de errores

## 📝 Logs y Monitoreo

El sistema registra:
- Número de registros procesados
- Errores de validación por fila
- Tiempo de procesamiento
- Usuario que ejecutó la importación

## 🔄 Próximas Mejoras

- [ ] Importación asíncrona para archivos grandes
- [ ] Previsualización antes de importar
- [ ] Plantillas Excel descargables
- [ ] Historial de importaciones
- [ ] Rollback de importaciones