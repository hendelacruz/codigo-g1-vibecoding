#!/usr/bin/env python
"""
Análisis manual de cobertura de tests
"""
import os
import glob
from pathlib import Path

def count_lines_in_file(file_path):
    """Cuenta líneas de código (excluyendo comentarios y líneas vacías)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        code_lines = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                code_lines += 1
        return code_lines
    except:
        return 0

def analyze_app_coverage(app_name):
    """Analiza la cobertura de una app específica"""
    app_path = Path(app_name)
    if not app_path.exists():
        return None
    
    # Archivos principales
    models_file = app_path / 'models.py'
    views_file = app_path / 'views.py'
    serializers_file = app_path / 'serializers.py'
    
    # Archivos de test
    test_files = list(app_path.glob('test*.py')) + [app_path / 'tests.py']
    test_files = [f for f in test_files if f.exists()]
    
    # Contar líneas
    models_lines = count_lines_in_file(models_file) if models_file.exists() else 0
    views_lines = count_lines_in_file(views_file) if views_file.exists() else 0
    serializers_lines = count_lines_in_file(serializers_file) if serializers_file.exists() else 0
    
    total_code_lines = models_lines + views_lines + serializers_lines
    
    test_lines = sum(count_lines_in_file(f) for f in test_files)
    
    # Calcular cobertura estimada
    if total_code_lines == 0:
        coverage_estimate = 0
    else:
        # Estimación: 1 línea de test por cada 2-3 líneas de código es buena cobertura
        coverage_estimate = min(100, (test_lines / total_code_lines) * 100 * 2.5)
    
    return {
        'app': app_name,
        'models_lines': models_lines,
        'views_lines': views_lines,
        'serializers_lines': serializers_lines,
        'total_code_lines': total_code_lines,
        'test_lines': test_lines,
        'test_files': len(test_files),
        'coverage_estimate': coverage_estimate,
        'has_real_tests': test_lines > 10  # Más de 10 líneas indica tests reales
    }

def main():
    print("🔍 ANÁLISIS DE COBERTURA DE TESTS")
    print("=" * 60)
    
    # Apps principales del proyecto
    apps = [
        'authentication',
        'dashboard', 
        'entities',
        'inventory',
        'sales',
        'services',
        'exports',
        'imports'
    ]
    
    total_code_lines = 0
    total_test_lines = 0
    apps_with_tests = 0
    
    results = []
    
    for app in apps:
        result = analyze_app_coverage(app)
        if result:
            results.append(result)
            total_code_lines += result['total_code_lines']
            total_test_lines += result['test_lines']
            if result['has_real_tests']:
                apps_with_tests += 1
    
    # Mostrar resultados por app
    print(f"{'App':<15} {'Código':<8} {'Tests':<8} {'Coverage':<10} {'Estado'}")
    print("-" * 60)
    
    for result in results:
        status = "✅ Con tests" if result['has_real_tests'] else "❌ Sin tests"
        print(f"{result['app']:<15} {result['total_code_lines']:<8} {result['test_lines']:<8} {result['coverage_estimate']:<10.1f}% {status}")
    
    # Resumen general
    print("\n" + "=" * 60)
    print("📊 RESUMEN GENERAL")
    print("=" * 60)
    
    overall_coverage = (total_test_lines / total_code_lines * 100 * 2.5) if total_code_lines > 0 else 0
    overall_coverage = min(100, overall_coverage)
    
    print(f"Total líneas de código: {total_code_lines}")
    print(f"Total líneas de tests: {total_test_lines}")
    print(f"Apps con tests reales: {apps_with_tests}/{len(results)}")
    print(f"Cobertura estimada: {overall_coverage:.1f}%")
    
    # Recomendaciones
    print("\n🎯 RECOMENDACIONES PRIORITARIAS")
    print("=" * 60)
    
    # Apps sin tests
    apps_without_tests = [r for r in results if not r['has_real_tests'] and r['total_code_lines'] > 0]
    apps_without_tests.sort(key=lambda x: x['total_code_lines'], reverse=True)
    
    print("\n1. Apps que necesitan tests urgentemente:")
    for app in apps_without_tests[:5]:
        print(f"   - {app['app']}: {app['total_code_lines']} líneas sin tests")
    
    # Análisis de utils
    utils_path = Path('todoapi/utils')
    if utils_path.exists():
        utils_files = list(utils_path.glob('*.py'))
        utils_lines = sum(count_lines_in_file(f) for f in utils_files if f.name != '__init__.py')
        print(f"\n2. Utils sin tests: {utils_lines} líneas en todoapi/utils/")
    
    print(f"\n3. Para alcanzar 80% de cobertura necesitas:")
    target_coverage = 80
    needed_test_lines = (target_coverage * total_code_lines / 100) / 2.5
    additional_tests_needed = max(0, needed_test_lines - total_test_lines)
    print(f"   - Aproximadamente {additional_tests_needed:.0f} líneas adicionales de tests")
    
    return overall_coverage

if __name__ == "__main__":
    coverage = main()
    print(f"\n🎯 Cobertura actual estimada: {coverage:.1f}%")
    if coverage < 80:
        print("❌ Objetivo: Alcanzar 80% de cobertura")
    else:
        print("✅ Objetivo alcanzado: >80% de cobertura")