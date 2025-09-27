# 📱 Funcionalidad is_active para GPS

## 🎯 Descripción General

Se ha implementado un nuevo campo `is_active` en el modelo GPS que permite gestionar el estado activo/inactivo de los dispositivos GPS de manera independiente del estado de asignación y proceso operativo.

## 🔧 Implementación Técnica

### Modelo GPS
- **Campo**: `is_active` (BooleanField)
- **Valor por defecto**: `True`
- **Descripción**: Indica si el dispositivo GPS está activo y operativo

### Métodos Disponibles
```python
# Activar GPS
gps.activate(observaciones="Motivo de activación")

# Desactivar GPS  
gps.deactivate(observaciones="Motivo de desactivación")

# Alternar estado activo
gps.toggle_active(observaciones="Cambio de estado")
```

## 🌐 API Endpoints

### 1. Obtener GPS con campo is_active
```http
GET /api/inventory/gps/{id}/
```

**Respuesta:**
```json
{
    "id": 1,
    "imei": "123456789012345",
    "marca": "GPS Brand",
    "modelo": "GPS Model",
    "estado": "asignado",
    "proceso": "disponible",
    "is_active": true,
    "observaciones": "GPS activo y funcionando",
    // ... otros campos
}
```

### 2. Cambiar estado incluyendo is_active
```http
PATCH /api/inventory/gps/{id}/cambiar_estado/
```

**Payload:**
```json
{
    "estado": "asignado",           // opcional
    "proceso": "en_transito",       // opcional  
    "is_active": false,             // opcional
    "observaciones": "Desactivando GPS temporalmente"
}
```

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "imei": "123456789012345",
    "estado": "asignado",
    "proceso": "en_transito", 
    "is_active": false,
    "observaciones": "Desactivando GPS temporalmente",
    // ... otros campos actualizados
}
```

## 🎨 Integración Frontend

### Mostrar Estado Activo
```jsx
const GPSCard = ({ gps }) => {
  return (
    <div className="gps-card">
      <h3>{gps.marca} {gps.modelo}</h3>
      
      {/* Indicador visual del estado activo */}
      <div className="status-indicators">
        <span className={`status-badge ${gps.is_active ? 'active' : 'inactive'}`}>
          {gps.is_active ? '🟢 Activo' : '🔴 Inactivo'}
        </span>
        
        <span className="estado-badge">
          {gps.estado_display}
        </span>
        
        <span className="proceso-badge">
          {gps.proceso_display}
        </span>
      </div>
    </div>
  );
};
```

### Toggle de Estado Activo
```jsx
const GPSActiveToggle = ({ gps, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  const handleToggleActive = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/inventory/gps/${gps.id}/cambiar_estado/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          is_active: !gps.is_active,
          observaciones: `${gps.is_active ? 'Desactivado' : 'Activado'} desde interfaz web`
        })
      });

      if (response.ok) {
        const updatedGPS = await response.json();
        onUpdate(updatedGPS);
      }
    } catch (error) {
      console.error('Error al cambiar estado activo:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button 
      onClick={handleToggleActive}
      disabled={loading}
      className={`toggle-btn ${gps.is_active ? 'btn-danger' : 'btn-success'}`}
    >
      {loading ? '⏳' : (gps.is_active ? '🔴 Desactivar' : '🟢 Activar')}
    </button>
  );
};
```

### Filtros por Estado Activo
```jsx
const GPSFilters = ({ filters, onFilterChange }) => {
  return (
    <div className="filters">
      {/* Filtro por estado activo */}
      <select 
        value={filters.is_active || ''} 
        onChange={(e) => onFilterChange('is_active', e.target.value)}
      >
        <option value="">Todos los estados</option>
        <option value="true">Solo activos</option>
        <option value="false">Solo inactivos</option>
      </select>
      
      {/* Otros filtros existentes */}
      <select 
        value={filters.estado || ''} 
        onChange={(e) => onFilterChange('estado', e.target.value)}
      >
        <option value="">Todos los estados</option>
        <option value="asignado">Asignados</option>
        <option value="no_asignado">No asignados</option>
      </select>
    </div>
  );
};
```

## 📊 Casos de Uso

### 1. Mantenimiento Temporal
```javascript
// Desactivar GPS para mantenimiento sin cambiar asignación
await updateGPSState(gpsId, {
  is_active: false,
  observaciones: "GPS en mantenimiento preventivo - 2 horas"
});
```

### 2. Reactivación Post-Reparación
```javascript
// Reactivar GPS después de reparación
await updateGPSState(gpsId, {
  is_active: true,
  proceso: "disponible",
  observaciones: "GPS reparado y reactivado - listo para asignación"
});
```

### 3. Gestión Masiva
```javascript
// Desactivar múltiples GPS
const inactiveGPSIds = [1, 2, 3, 4];
await Promise.all(
  inactiveGPSIds.map(id => 
    updateGPSState(id, {
      is_active: false,
      observaciones: "Desactivación masiva - inventario mensual"
    })
  )
);
```

## ⚠️ Consideraciones Importantes

### Validaciones
- El campo `is_active` es independiente de `estado` y `proceso`
- Un GPS puede estar `asignado` pero `is_active: false` (ej: mantenimiento temporal)
- Un GPS puede estar `no_asignado` pero `is_active: true` (ej: disponible para asignación)

### Reglas de Negocio
- GPS inactivos (`is_active: false`) no deberían aparecer en listas de asignación
- GPS inactivos mantienen su cliente asignado (si lo tienen)
- El cambio de `is_active` no afecta las validaciones de `estado` y `proceso`

### Permisos
- Requiere autenticación (`IsAuthenticated`)
- Requiere permisos de administrador o supervisor (`IsAdminOrSupervisor`)

## 🔄 Migración de Datos

Los GPS existentes automáticamente tendrán `is_active: true` después de ejecutar la migración.

## 🧪 Testing

Se han implementado tests completos que cubren:
- ✅ Creación de GPS con valor por defecto
- ✅ Métodos activate(), deactivate(), toggle_active()
- ✅ API endpoint cambiar_estado con is_active
- ✅ Validaciones y casos edge
- ✅ Integración con estado_info

## 📈 Próximas Mejoras

1. **Dashboard de Estado**: Métricas de GPS activos vs inactivos
2. **Notificaciones**: Alertas cuando GPS se desactivan inesperadamente  
3. **Historial**: Tracking de cambios de estado activo
4. **Automatización**: Reglas para auto-desactivación en ciertos procesos