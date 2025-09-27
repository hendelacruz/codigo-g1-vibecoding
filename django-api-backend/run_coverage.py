#!/usr/bin/env python
"""
Script para ejecutar coverage de manera controlada
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
    django.setup()
    
    # Configurar coverage
    import coverage
    cov = coverage.Coverage(source=['.'], omit=[
        '*/venv/*',
        '*/env/*',
        '*/migrations/*',
        '*/settings/*',
        '*/static/*',
        '*/templates/*',
        'manage.py',
        '*/tests.py',
        '*/test_*.py',
        '*/__pycache__/*',
        '*/node_modules/*',
        '.git/*',
        '*/fixtures/*',
        'todoapi/wsgi.py',
        'todoapi/asgi.py',
        'todoapi/celery.py',
        'run_coverage.py',
    ])
    
    cov.start()
    
    try:
        # Ejecutar tests específicos que sabemos que existen
        from django.test.runner import DiscoverRunner
        test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
        
        # Lista de tests específicos que tienen contenido
        test_labels = [
            'dashboard.test_services',
            'dashboard.test_views', 
            'entities.test_viewsets',
            'inventory.test_filters',
            'services.test_filters',
            'services.test_performance',
        ]
        
        failures = test_runner.run_tests(test_labels)
        
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        failures = 1
    finally:
        cov.stop()
        cov.save()
        
        # Generar reportes
        print("\n" + "="*50)
        print("REPORTE DE COBERTURA")
        print("="*50)
        cov.report(show_missing=True)
        
        # Generar reporte HTML
        cov.html_report(directory='htmlcov')
        print(f"\nReporte HTML generado en: htmlcov/index.html")
        
        sys.exit(failures)