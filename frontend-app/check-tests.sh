#!/bin/bash

echo "🧪 Verificando estado de los tests..."
echo "=================================="

# Ejecutar tests con output básico
npx vitest run --reporter=basic 2>&1 | tee test-results.txt

# Mostrar resumen
echo ""
echo "📊 Resumen de resultados:"
echo "========================"
grep -E "(Test Files|Tests|Duration)" test-results.txt || echo "No se pudo obtener resumen"

echo ""
echo "✅ Tests completados. Revisa test-results.txt para más detalles."