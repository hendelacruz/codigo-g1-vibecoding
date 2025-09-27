#!/bin/bash

# Pruebas para crear SIM cards usando curl
# Este script contiene ejemplos de cómo crear SIM cards via API usando curl

BASE_URL="http://127.0.0.1:8000"
API_ENDPOINT="${BASE_URL}/api/inventory/simcards/"

echo "============================================================"
echo " 🧪 PRUEBAS PARA CREAR SIM CARDS VIA API (CURL)"
echo "============================================================"
echo "API Endpoint: ${API_ENDPOINT}"
echo ""

# Function to print separator
print_separator() {
    echo ""
    echo "============================================================"
    echo " $1"
    echo "============================================================"
}

# Test 1: Create SIM card with minimal data
print_separator "TEST 1: Crear SIM card con datos mínimos"
echo "📋 Creando SIM card con datos mínimos requeridos..."

curl -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_compra": "2025-01-15T10:30:00Z",
    "numero_factura": "F001-2025-001",
    "numero_chip": "123456789",
    "icc": "89511234567890123456",
    "proveedor": 1
  }' \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "✅ Si ves status code 201, la SIM card se creó exitosamente!"

# Test 2: Create SIM card with complete data
print_separator "TEST 2: Crear SIM card con datos completos"
echo "📋 Creando SIM card con todos los campos..."

curl -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_compra": "2025-01-15T14:45:00Z",
    "numero_factura": "F001-2025-002",
    "numero_chip": "987654321",
    "icc": "89511234567890123457",
    "proveedor": 1,
    "cliente": null,
    "estado": "no_asignado",
    "proceso": "en_produccion",
    "is_active": true,
    "observaciones": "SIM card de prueba con datos completos"
  }' \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "✅ Si ves status code 201, la SIM card se creó exitosamente!"

# Test 3: Test validation with invalid ICC
print_separator "TEST 3: Probar validación con ICC inválido"
echo "📋 Intentando crear SIM card con ICC inválido (muy corto)..."

curl -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_compra": "2025-01-15T16:00:00Z",
    "numero_factura": "F001-2025-003",
    "numero_chip": "555666777",
    "icc": "123456789",
    "proveedor": 1
  }' \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "✅ Si ves status code 400, la validación está funcionando correctamente!"

# Test 4: Test validation with missing fields
print_separator "TEST 4: Probar validación con campos faltantes"
echo "📋 Intentando crear SIM card sin campos requeridos..."

curl -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_chip": "111222333"
  }' \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "✅ Si ves status code 400, la validación está funcionando correctamente!"

# Test 5: List all SIM cards
print_separator "TEST 5: Listar todas las SIM cards"
echo "📋 Obteniendo lista de SIM cards creadas..."

curl -X GET "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "✅ Si ves status code 200, puedes ver todas las SIM cards creadas!"

# Test 6: Create SIM card with different ICC
print_separator "TEST 6: Crear otra SIM card con ICC diferente"
echo "📋 Creando SIM card adicional para demostrar múltiples creaciones..."

curl -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_compra": "2025-01-15T18:00:00Z",
    "numero_factura": "F001-2025-004",
    "numero_chip": "444555666",
    "icc": "89511234567890123458",
    "proveedor": 1,
    "observaciones": "Tercera SIM card de prueba"
  }' \
  -w "\n\nStatus Code: %{http_code}\n" \
  -s

print_separator "🎉 PRUEBAS COMPLETADAS"
echo "Todas las pruebas han sido ejecutadas."
echo ""
echo "📊 Códigos de estado esperados:"
echo "  - 201: Creación exitosa"
echo "  - 400: Error de validación (esperado para pruebas de validación)"
echo "  - 200: Consulta exitosa"
echo ""
echo "🔍 Para ver detalles de una SIM card específica:"
echo "curl -X GET \"${API_ENDPOINT}1/\" -H \"Content-Type: application/json\""
echo ""
echo "✏️  Para actualizar una SIM card:"
echo "curl -X PATCH \"${API_ENDPOINT}1/\" -H \"Content-Type: application/json\" -d '{\"observaciones\": \"Actualizada\"}'"
echo ""
echo "🗑️  Para eliminar una SIM card:"
echo "curl -X DELETE \"${API_ENDPOINT}1/\" -H \"Content-Type: application/json\""