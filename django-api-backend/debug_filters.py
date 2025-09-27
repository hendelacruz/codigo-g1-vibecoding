#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

from inventory.models import Otros
from inventory.filters import OtrosFilter
from entities.models import Proveedor
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

print("=== RECREANDO DATOS DE TEST ===")

# Limpiar solo datos de Otros
Otros.objects.all().delete()

# Obtener o crear proveedor de prueba (igual que en el test)
proveedor, created = Proveedor.objects.get_or_create(
    ruc='12345678903',
    defaults={
        'nombre': 'Proveedor Otros',
        'correo': 'otros@proveedor.com',
        'celular': '123456789'
    }
)

# Crear items exactamente como en el test
item1 = Otros.objects.create(
    descripcion='Cable USB',
    categoria='Cables',
    cantidad=50,  # cantidad = stock_actual deseado (50)
    stock_actual=50,  # Debe estar en rango 20-60
    precio_unitario=Decimal('15.00'),
    numero_factura='O001',
    proveedor=proveedor,
    fecha_compra=timezone.now(),
    observaciones='Cables nuevos'
)

item2 = Otros.objects.create(
    descripcion='Antena GPS',
    categoria='Antenas',
    cantidad=3,  # cantidad = stock_actual deseado (3)
    stock_actual=3,  # Debe estar en bajo stock (<5)
    precio_unitario=Decimal('45.00'),
    numero_factura='O002',
    proveedor=proveedor,
    fecha_compra=timezone.now() - timedelta(days=20),
    observaciones='Antenas de repuesto'
)

print(f"Item1 creado: {item1.descripcion}, stock={item1.stock_actual}, id={item1.id}")
print(f"Item2 creado: {item2.descripcion}, stock={item2.stock_actual}, id={item2.id}")

print("\n=== TEST FILTRO RANGO DE STOCK (20-60) ===")
filter_data = {'stock_min': 20, 'stock_max': 60}
filterset = OtrosFilter(filter_data, queryset=Otros.objects.all())
print(f"Filtro válido: {filterset.is_valid()}")
print(f"Errores: {filterset.errors}")
print(f"Cantidad de resultados: {filterset.qs.count()}")
print("Resultados:")
for item in filterset.qs:
    print(f"  - {item.descripcion}: stock={item.stock_actual}, id={item.id}")

if filterset.qs.count() > 0:
    first_item = filterset.qs.first()
    print(f"Primer elemento: {first_item.descripcion} (id={first_item.id})")
    print(f"¿Es item1? {first_item == item1}")
    print(f"¿Es item2? {first_item == item2}")

print("\n=== TEST QUERY DIRECTA ===")
print("Items con stock >= 20 y <= 60:")
direct_query = Otros.objects.filter(stock_actual__gte=20, stock_actual__lte=60)
for item in direct_query:
    print(f"  - {item.descripcion}: stock={item.stock_actual}, id={item.id}")

print("\n=== TEST FILTRO BAJO STOCK ===")
filter_data = {'stock_bajo': True}
filterset = OtrosFilter(filter_data, queryset=Otros.objects.all())
print(f"Filtro válido: {filterset.is_valid()}")
print(f"Cantidad de resultados: {filterset.qs.count()}")
for item in filterset.qs:
    print(f"  - {item.descripcion}: stock={item.stock_actual}, id={item.id}")

print("\n=== VERIFICACIÓN FINAL ===")
print(f"Total items: {Otros.objects.count()}")
print("Todos los items:")
for item in Otros.objects.all().order_by('id'):
    print(f"  - ID {item.id}: {item.descripcion}, stock={item.stock_actual}")