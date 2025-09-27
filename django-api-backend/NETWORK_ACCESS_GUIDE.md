# 🌐 Guía de Acceso desde Red Local

Esta guía te ayudará a configurar tu backend Django para que sea accesible desde otras computadoras en la misma red local.

## 🎯 Problema Común

Cuando desarrollas en Django, por defecto solo puedes acceder desde `localhost` o `127.0.0.1`. Si intentas acceder desde otra computadora en la red, obtienes errores de:
- ❌ CORS (Cross-Origin Resource Sharing)
- ❌ Host no permitido
- ❌ Conexión rechazada

## ✅ Solución Implementada

### 1. Configuración de ALLOWED_HOSTS

En el archivo `.env` ya está configurado:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*
```

Esto permite conexiones desde cualquier IP.

### 2. Configuración de CORS

En el archivo `.env` ya está configurado:
```env
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
```

Esto permite requests desde cualquier origen en desarrollo.

### 3. Servidor en Todas las Interfaces

Usa el script `run_server_network.py` que ejecuta el servidor en `0.0.0.0:8000`.

## 🚀 Cómo Usar

### Opción 1: Script Automático (Recomendado)
```bash
python run_server_network.py
```

Este script:
- 🔍 Detecta automáticamente tu IP local
- 📡 Ejecuta el servidor en todas las interfaces
- 📋 Muestra las URLs de acceso

### Opción 2: Comando Manual
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🔗 URLs de Acceso

Una vez ejecutado el servidor, podrás acceder desde:

### Desde la misma computadora:
- `http://localhost:8000` - Acceso local
- `http://127.0.0.1:8000` - Acceso local

### Desde otras computadoras en la red:
- `http://[TU_IP_LOCAL]:8000` - Reemplaza [TU_IP_LOCAL] con tu IP
- Ejemplo: `http://192.168.1.100:8000`

### Endpoints principales:
- `http://[IP]:8000/api/auth/login/` - Login
- `http://[IP]:8000/api/auth/profile/` - Perfil de usuario
- `http://[IP]:8000/api/docs/` - Documentación Swagger
- `http://[IP]:8000/admin/` - Panel de administración

## 🔍 Cómo Encontrar Tu IP Local

### En macOS/Linux:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### En Windows:
```cmd
ipconfig
```

### Usando el script:
El script `run_server_network.py` detecta automáticamente tu IP.

## 🛠️ Configuración del Frontend

Si tu frontend está en otra computadora, asegúrate de configurar la URL base de la API:

### JavaScript/React:
```javascript
// En lugar de:
const API_BASE_URL = 'http://localhost:8000/api';

// Usa:
const API_BASE_URL = 'http://192.168.1.100:8000/api'; // Tu IP real
```

### Variables de entorno del frontend:
```env
REACT_APP_API_URL=http://192.168.1.100:8000/api
VUE_APP_API_URL=http://192.168.1.100:8000/api
```

## 🔐 Autenticación desde Red Local

Los endpoints de autenticación funcionan normalmente:

### Login:
```javascript
fetch('http://192.168.1.100:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'tu_usuario',
    password: 'tu_password'
  })
})
```

### Requests autenticados:
```javascript
fetch('http://192.168.1.100:8000/api/auth/profile/', {
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
  }
})
```

## 🚨 Troubleshooting

### Error: "Invalid HTTP_HOST header"
- ✅ Verifica que `ALLOWED_HOSTS` incluya `*` o tu IP específica

### Error: "CORS policy"
- ✅ Verifica que `CORS_ALLOW_ALL_ORIGINS=True` esté en `.env`

### Error: "Connection refused"
- ✅ Asegúrate de ejecutar el servidor con `0.0.0.0:8000`
- ✅ Verifica que no haya firewall bloqueando el puerto 8000

### Error: "Authentication failed"
- ✅ Verifica que la URL del frontend apunte a la IP correcta
- ✅ Revisa que las cookies/tokens se estén enviando correctamente

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Esta configuración es SOLO para desarrollo.

Para producción:
- ❌ NO uses `CORS_ALLOW_ALL_ORIGINS=True`
- ❌ NO uses `ALLOWED_HOSTS=*`
- ✅ Especifica dominios exactos
- ✅ Usa HTTPS
- ✅ Configura un servidor web (nginx/apache)

## 📱 Acceso desde Móviles

También puedes acceder desde dispositivos móviles en la misma red WiFi:
- `http://192.168.1.100:8000/api/docs/` - Desde el navegador móvil

## 🎉 ¡Listo!

Ahora tu backend Django es accesible desde cualquier dispositivo en tu red local. Perfecto para:
- 👥 Desarrollo en equipo
- 📱 Testing en dispositivos móviles
- 🖥️ Múltiples computadoras de desarrollo