#!/usr/bin/env python
"""
Script para ejecutar todos los tests del proyecto con configuración optimizada.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def setup_test_environment():
    """
    Configurar el entorno de testing.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.testing')
    django.setup()


def run_specific_tests():
    """
    Ejecutar tests específicos para las funcionalidades implementadas.
    """
    test_modules = [
        # Tests de filtros
        'inventory.test_filters',
        
        # Tests de ViewSets avanzados
        'todoapi.utils.test_viewsets',
        'entities.test_viewsets',
        
        # Tests específicos por módulo
        'inventory.tests',
        'entities.tests',
        'sales.tests',
        'services.tests',
    ]
    
    return test_modules


def run_all_tests():
    """
    Ejecutar todos los tests del proyecto.
    """
    setup_test_environment()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=True)
    
    # Obtener módulos de test específicos
    test_modules = run_specific_tests()
    
    print("🧪 Ejecutando tests para funcionalidades avanzadas...")
    print("=" * 60)
    
    failures = 0
    
    for module in test_modules:
        print(f"\n📋 Ejecutando tests de: {module}")
        print("-" * 40)
        
        try:
            result = test_runner.run_tests([module])
            if result:
                failures += result
                print(f"❌ {module}: {result} fallos")
            else:
                print(f"✅ {module}: Todos los tests pasaron")
        except Exception as e:
            print(f"⚠️  Error ejecutando {module}: {e}")
            failures += 1
    
    print("\n" + "=" * 60)
    if failures:
        print(f"❌ Total de fallos: {failures}")
        return failures
    else:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        return 0


def run_coverage_report():
    """
    Ejecutar tests con reporte de cobertura.
    """
    try:
        import coverage
        
        cov = coverage.Coverage()
        cov.start()
        
        # Ejecutar tests
        result = run_all_tests()
        
        cov.stop()
        cov.save()
        
        print("\n📊 Reporte de Cobertura:")
        print("=" * 40)
        cov.report()
        
        # Generar reporte HTML
        cov.html_report(directory='htmlcov')
        print("\n📄 Reporte HTML generado en: htmlcov/index.html")
        
        return result
        
    except ImportError:
        print("⚠️  Coverage no está instalado. Ejecutando tests sin cobertura...")
        return run_all_tests()


def main():
    """
    Función principal del script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutar tests del proyecto')
    parser.add_argument(
        '--coverage', 
        action='store_true', 
        help='Ejecutar con reporte de cobertura'
    )
    parser.add_argument(
        '--module', 
        type=str, 
        help='Ejecutar tests de un módulo específico'
    )
    parser.add_argument(
        '--fast', 
        action='store_true', 
        help='Ejecutar solo tests rápidos'
    )
    
    args = parser.parse_args()
    
    if args.module:
        setup_test_environment()
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=True)
        result = test_runner.run_tests([args.module])
        sys.exit(result)
    
    elif args.coverage:
        result = run_coverage_report()
        sys.exit(result)
    
    elif args.fast:
        # Solo tests unitarios rápidos
        setup_test_environment()
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=1, interactive=False, keepdb=True)
        
        fast_tests = [
            'todoapi.utils.test_viewsets.AdvancedSearchViewSetTestCase',
            'inventory.test_filters.GPSFilterTestCase',
            'entities.test_viewsets.ClienteViewSetTestCase'
        ]
        
        result = test_runner.run_tests(fast_tests)
        sys.exit(result)
    
    else:
        result = run_all_tests()
        sys.exit(result)


if __name__ == '__main__':
    main()