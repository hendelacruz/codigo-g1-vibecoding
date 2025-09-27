#!/bin/bash

# Script para corregir archivos de test que usan createWrapper

# Lista de archivos a corregir
files=(
    "src/features/services/components/shared/__tests__/ServiceTypeSelect.test.tsx"
    "src/features/services/components/shared/__tests__/DispositivoGpsSelect.test.tsx"
    "src/features/services/components/shared/__tests__/ClientSelect.enhanced.test.tsx"
    "src/features/services/components/Servicio/__tests__/ServicioDashboard.test.tsx"
)

for file in "${files[@]}"; do
    echo "Corrigiendo $file..."
    
    # Verificar si el archivo existe
    if [ ! -f "$file" ]; then
        echo "Archivo no encontrado: $file"
        continue
    fi
    
    # Agregar importaciones necesarias si no existen
    if ! grep -q "renderWithProviders" "$file"; then
        # Reemplazar la línea de import de render
        sed -i '' 's/import { render, screen/import { screen/g' "$file"
        
        # Agregar la nueva importación después de la línea de vitest
        sed -i '' '/import.*vitest/a\
import { renderWithProviders, createTestStore } from '"'"'../../../../../tests/utils'"'"';
' "$file"
    fi
    
    # Reemplazar createWrapper con renderWithAllProviders
    sed -i '' 's/const createWrapper = () => {/const renderWithAllProviders = (ui: React.ReactElement) => {/g' "$file"
    
    # Reemplazar el contenido de la función
    sed -i '' '/const renderWithAllProviders = (ui: React.ReactElement) => {/,/};/{
        /const renderWithAllProviders = (ui: React.ReactElement) => {/!{
            /};/!d
        }
    }' "$file"
    
    # Insertar el nuevo contenido de la función
    sed -i '' '/const renderWithAllProviders = (ui: React.ReactElement) => {/a\
  const queryClient = new QueryClient({\
    defaultOptions: {\
      queries: {\
        retry: false,\
      },\
    },\
  });\
\
  const store = createTestStore();\
\
  return renderWithProviders(\
    <QueryClientProvider client={queryClient}>\
      {ui}\
    </QueryClientProvider>,\
    { store }\
  );
' "$file"
    
    # Reemplazar todas las instancias de render( con renderWithAllProviders(
    sed -i '' 's/render(/renderWithAllProviders(/g' "$file"
    
    # Remover las referencias a wrapper
    sed -i '' 's/,[ ]*{ wrapper: createWrapper() }//g' "$file"
    sed -i '' '/{ wrapper: createWrapper() }/d' "$file"
    
    # Para ServicioDashboard.test.tsx, también reemplazar const Wrapper = createWrapper();
    if [[ "$file" == *"ServicioDashboard.test.tsx"* ]]; then
        sed -i '' 's/const Wrapper = createWrapper();/const Wrapper = renderWithAllProviders;/g' "$file"
        sed -i '' 's/wrapper: Wrapper/wrapper: undefined/g' "$file"
        sed -i '' 's/, { wrapper: undefined }//g' "$file"
    fi
    
    echo "✅ Corregido: $file"
done

echo "🎉 Todos los archivos han sido corregidos!"