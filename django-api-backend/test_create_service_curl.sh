#!/bin/bash

# Script para probar la creación de servicios usando curl
# Basado en el modelo Servicio y sus dependencias

echo "🚀 TESTING SERVICE CREATION WITH CURL"
echo "======================================"

BASE_URL="http://127.0.0.1:8000/api"

# Configuración de autenticación
USERNAME="admin"
PASSWORD="admin123"

echo ""
echo "🔐 1. AUTENTICACIÓN"
echo "------------------"

# Obtener token JWT
echo "🔑 Obteniendo token de autenticación..."
AUTH_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  "$BASE_URL/auth/login/")

# Extraer el token de acceso
ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ ERROR: No se pudo obtener el token de acceso"
    echo "Respuesta de autenticación:"
    echo "$AUTH_RESPONSE"
    exit 1
fi

echo "✅ Token obtenido exitosamente"

# Headers de autorización
AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

echo ""
echo "📋 2. OBTENIENDO DATOS DISPONIBLES"
echo "---------------------------------"

echo "🔧 Tipos de trabajo disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/services/tipos-trabajo/" | python3 -m json.tool

echo ""
echo "👥 Clientes disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/entities/clientes/" | python3 -m json.tool

echo ""
echo "🚗 Unidades disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/entities/unidades/" | python3 -m json.tool

echo ""
echo "👨‍🔧 Técnicos disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/auth/users/" | python3 -m json.tool

echo ""
echo "📡 GPS disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/inventory/gps/" | python3 -m json.tool

echo ""
echo "📱 SIM Cards disponibles:"
curl -s -H "$AUTH_HEADER" "$BASE_URL/inventory/simcards/" | python3 -m json.tool

echo ""
echo "🎯 3. CREANDO UN NUEVO SERVICIO"
echo "-------------------------------"

# Datos para crear un servicio de ejemplo
SERVICE_DATA='{
  "fecha": "2024-01-15",
  "tipo_trabajo": 1,
  "tecnico_dni": "12345678",
  "cliente": 1,
  "unidad": 1,
  "gps": 1,
  "sim_card": 1,
  "descripcion": "Servicio de instalación de GPS y configuración de SIM card para monitoreo vehicular",
  "precio": "150.00",
  "observaciones": "Cliente solicita configuración especial para alertas de velocidad"
}'

echo "📝 Datos del servicio a crear:"
echo "$SERVICE_DATA" | python3 -m json.tool

echo ""
echo "🔄 Enviando petición POST para crear servicio..."

# Crear servicio y capturar respuesta
CREATE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "$SERVICE_DATA" \
  "$BASE_URL/services/servicios/")

echo "📄 Respuesta del servidor:"
echo "$CREATE_RESPONSE" | python3 -m json.tool

# Verificar si la creación fue exitosa
SERVICE_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ ! -z "$SERVICE_ID" ]; then
    echo ""
    echo "✅ ¡SERVICIO CREADO EXITOSAMENTE!"
    echo "🆔 ID del servicio creado: $SERVICE_ID"
    
    echo ""
    echo "🔍 4. VERIFICANDO EL SERVICIO CREADO"
    echo "-----------------------------------"
    
    echo "📖 Obteniendo detalles del servicio creado:"
    curl -s -H "$AUTH_HEADER" "$BASE_URL/services/servicios/$SERVICE_ID/" | python3 -m json.tool
else
    echo ""
    echo "❌ ERROR AL CREAR EL SERVICIO"
    echo "Revisa los datos enviados y los IDs de las entidades relacionadas"
fi

echo ""
echo "🎯 5. COMANDOS CURL INDIVIDUALES PARA COPIAR Y PEGAR"
echo "===================================================="

echo ""
echo "# 1. Autenticación (obtener token):"
echo "curl -X POST -H \"Content-Type: application/json\" -d '{\"username\":\"admin\",\"password\":\"admin123\"}' \"$BASE_URL/auth/login/\""

echo ""
echo "# 2. Obtener tipos de trabajo:"
echo "curl -s -H \"Authorization: Bearer YOUR_TOKEN\" \"$BASE_URL/services/tipos-trabajo/\" | python3 -m json.tool"

echo ""
echo "# 3. Obtener clientes:"
echo "curl -s -H \"Authorization: Bearer YOUR_TOKEN\" \"$BASE_URL/entities/clientes/\" | python3 -m json.tool"

echo ""
echo "# 4. Crear servicio (ejemplo):"
cat << 'EOF'
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "fecha": "2024-01-15",
    "tipo_trabajo": 1,
    "tecnico_dni": "12345678",
    "cliente": 1,
    "unidad": 1,
    "gps": 1,
    "sim_card": 1,
    "descripcion": "Servicio de instalación de GPS",
    "precio": "150.00",
    "observaciones": "Observaciones del servicio"
  }' \
  "http://127.0.0.1:8000/api/services/servicios/"
EOF

echo ""
echo "# 5. Obtener todos los servicios:"
echo "curl -s -H \"Authorization: Bearer YOUR_TOKEN\" \"$BASE_URL/services/servicios/\" | python3 -m json.tool"

echo ""
echo "🏁 SCRIPT COMPLETADO"
echo "==================="