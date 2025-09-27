#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings')
django.setup()

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

# Test URLs that should exist
test_urls = [
    'entities:cliente-list',
    'entities:proveedor-list', 
    'entities:unidad-list',
    'cliente-list',
    'proveedor-list',
    'unidad-list'
]

print("Testing URL patterns:")
for url_name in test_urls:
    try:
        url = reverse(url_name)
        print(f"✓ {url_name} -> {url}")
    except NoReverseMatch as e:
        print(f"✗ {url_name} -> {e}")

# Also check the router URLs
from entities.urls import router
print("\nRouter registered URLs:")
for prefix, viewset, basename in router.registry:
    print(f"  {prefix} -> {basename}")
    print(f"    List: {basename}-list")
    print(f"    Detail: {basename}-detail")