#!/usr/bin/env python
"""
Script de depuración específico para simular el test que está fallando.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

from sales.models import Ventas
from entities.models import Cliente, Unidad
from authentication.models import Role
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, time
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def debug_specific_test():
    """Simula exactamente el test que está fallando"""
    
    print("=== DEPURACIÓN ESPECÍFICA DEL TEST ===\n")
    
    # Limpiar datos de ventas
    print("1. Limpiando datos de ventas...")
    Ventas.objects.all().delete()
    print("   ✓ Ventas eliminadas\n")
    
    # Crear datos exactamente como en el test
    print("2. Creando datos exactamente como en el test...")
    
    # Crear role y usuario
    role, created = Role.objects.get_or_create(
        nombre='TestAdmin',
        defaults={
            'descripcion': 'Test Administrator role',
            'permisos': ['view_ventas', 'add_ventas', 'change_ventas', 'delete_ventas']
        }
    )
    
    user, created = User.objects.get_or_create(
        dni='99999999',
        defaults={
            'username': 'testuser_debug',
            'email': 'test_debug@example.com',
            'celular': '+51987654321',
            'rol': role
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Crear cliente
    cliente, created = Cliente.objects.get_or_create(
        ruc='12345678901',
        defaults={
            'nombre': 'Test Cliente',
            'direccion': 'Test Address',
            'contacto': 'Test Contact',
            'celular': '987654321',
            'correo': 'test@example.com'
        }
    )
    
    # Crear unidad
    unidad, created = Unidad.objects.get_or_create(
        placa='DEBUG-999',
        defaults={
            'tipo': 'camion',
            'marca': 'Test Marca',
            'modelo': 'Test Modelo',
            'serie': 'DEBUG999',
            'cliente': cliente
        }
    )
    
    print("   ✓ Datos creados\n")
    
    # Verificar relación cliente-unidad
    print("3. Verificando relación cliente-unidad...")
    print(f"   Cliente ID: {cliente.id}")
    print(f"   Unidad ID: {unidad.id}")
    print(f"   Unidad.cliente ID: {unidad.cliente.id}")
    print(f"   ¿Unidad pertenece al cliente?: {unidad.cliente == cliente}")
    print()
    
    # Crear ventas exactamente como en el test
    print("4. Creando ventas...")
    try:
        # Nota: Solo proporcionamos precio, los demás campos se calculan automáticamente
        venta1 = Ventas.objects.create(
            mes=date(2024, 1, 1),
            fecha_pago=time(14, 30),
            numero_operacion='1234567890',
            tipo_pago='efectivo',
            banco='BCP',
            numero_factura='F001-001',
            fecha_generacion_factura=timezone.now(),
            cliente=cliente,
            descripcion='Venta de prueba 1',
            unidad=unidad,
            precio=Decimal('1180.00'),
            importe=Decimal('1000.00'),  # 1180/1.18
            igv=Decimal('180.00'),       # 1000*0.18
            total=Decimal('1180.00'),    # 1000+180
            estado='pendiente'
        )
        print("   ✓ Venta 1 creada")
        
        venta2 = Ventas.objects.create(
            mes=date(2024, 1, 2),
            fecha_pago=time(15, 30),
            numero_operacion='0987654321',
            tipo_pago='transferencia',
            banco='BBVA',
            numero_factura='F001-002',
            fecha_generacion_factura=timezone.now(),
            cliente=cliente,
            descripcion='Venta de prueba 2',
            unidad=unidad,
            precio=Decimal('2360.00'),
            importe=Decimal('2000.00'),  # 2360/1.18
            igv=Decimal('360.00'),       # 2000*0.18
            total=Decimal('2360.00'),    # 2000+360
            estado='pagado'
        )
        print("   ✓ Venta 2 creada")
    except Exception as e:
        print(f"   ❌ Error creando ventas: {e}")
        return
    
    # Verificar datos creados
    print("\n5. Verificando datos creados...")
    all_ventas = Ventas.objects.all()
    print(f"   Total de ventas: {all_ventas.count()}")
    
    for venta in all_ventas:
        print(f"   - {venta.numero_factura}: estado='{venta.estado}', tipo_pago='{venta.tipo_pago}'")
    
    print()
    
    # Configurar cliente API
    print("6. Configurando cliente API...")
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    base_url = '/api/sales/ventas/'
    print("   ✓ Cliente API configurado\n")
    
    # Probar filtros exactamente como en el test
    print("7. Probando filtros como en el test...")
    
    # Filter by estado
    print("   Filtro por estado=pendiente:")
    response = client.get(f'{base_url}?estado=pendiente')
    print(f"     Status: {response.status_code}")
    if response.status_code == 200:
        results = response.data.get('results', [])
        print(f"     Resultados: {len(results)}")
        for result in results:
            print(f"       - {result['numero_factura']}: {result['estado']}")
    else:
        print(f"     Error: Status {response.status_code}")
        if hasattr(response, 'data'):
            print(f"     Data: {response.data}")
        else:
            print(f"     Content: {response.content.decode()}")
    
    print()
    
    # Filter by tipo_pago
    print("   Filtro por tipo_pago=transferencia:")
    response = client.get(f'{base_url}?tipo_pago=transferencia')
    print(f"     Status: {response.status_code}")
    if response.status_code == 200:
        results = response.data.get('results', [])
        print(f"     Resultados: {len(results)}")
        for result in results:
            print(f"       - {result['numero_factura']}: {result['tipo_pago']}")
    else:
        print(f"     Error: Status {response.status_code}")
        if hasattr(response, 'data'):
            print(f"     Data: {response.data}")
        else:
            print(f"     Content: {response.content.decode()}")
    
    print()
    
    # Filter by cliente
    print(f"   Filtro por cliente={cliente.id}:")
    response = client.get(f'{base_url}?cliente={cliente.id}')
    print(f"     Status: {response.status_code}")
    if response.status_code == 200:
        results = response.data.get('results', [])
        print(f"     Resultados: {len(results)}")
        for result in results:
            print(f"       - {result['numero_factura']}: cliente_id={result.get('cliente', 'N/A')}")
    else:
        print(f"     Error: Status {response.status_code}")
        if hasattr(response, 'data'):
            print(f"     Data: {response.data}")
        else:
            print(f"     Content: {response.content.decode()}")
    
    print("\n=== FIN DE LA DEPURACIÓN ESPECÍFICA ===")

if __name__ == '__main__':
    debug_specific_test()