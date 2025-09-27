#!/usr/bin/env python
"""
Script de depuración para entender el problema con el filtro de ventas.
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

User = get_user_model()

def debug_sales_filter():
    """Depura el filtro de ventas para entender el problema"""
    
    print("=== DEPURACIÓN DEL FILTRO DE VENTAS ===\n")
    
    # Verificar datos existentes
    print("1. Verificando datos existentes...")
    print(f"   Ventas existentes: {Ventas.objects.count()}")
    print(f"   Clientes existentes: {Cliente.objects.count()}")
    print(f"   Usuarios existentes: {User.objects.count()}")
    print(f"   Roles existentes: {Role.objects.count()}")
    print()
    
    # Crear datos de prueba únicos
    print("2. Creando datos de prueba únicos...")
    
    # Usar o crear role
    role, created = Role.objects.get_or_create(
        nombre='DebugAdmin',
        defaults={
            'descripcion': 'Debug Administrator role',
            'permisos': ['view_ventas', 'add_ventas', 'change_ventas', 'delete_ventas']
        }
    )
    
    # Usar o crear usuario
    user, created = User.objects.get_or_create(
        username='debuguser',
        defaults={
            'email': 'debug@example.com',
            'rol': role
        }
    )
    if created:
        user.set_password('debugpass123')
        user.save()
    
    # Crear cliente único
    cliente, created = Cliente.objects.get_or_create(
        ruc='99999999999',
        defaults={
            'nombre': 'Debug Cliente',
            'direccion': 'Debug Address',
            'contacto': 'Debug Contact',
            'celular': '999999999',
            'correo': 'debug@cliente.com'
        }
    )
    
    # Crear unidad única
    unidad, created = Unidad.objects.get_or_create(
        placa='DEBUG-123',
        defaults={
            'tipo': 'camion',
            'marca': 'Debug Marca',
            'modelo': 'Debug Modelo',
            'serie': 'DEBUG123456',
            'cliente': cliente
        }
    )
    
    # Eliminar ventas de debug existentes
    Ventas.objects.filter(numero_factura__startswith='DEBUG-').delete()
    
    # Crear ventas de debug
    venta1 = Ventas.objects.create(
        mes=date(2024, 1, 1),
        fecha_pago=time(14, 30),
        numero_operacion='DEBUG001',
        tipo_pago='efectivo',
        banco='BCP',
        numero_factura='DEBUG-001',
        fecha_generacion_factura=timezone.now(),
        cliente=cliente,
        descripcion='Debug venta 1',
        unidad=unidad,
        precio=Decimal('1180.00'),
        estado='pendiente'
    )
    
    venta2 = Ventas.objects.create(
        mes=date(2024, 1, 2),
        fecha_pago=time(15, 30),
        numero_operacion='DEBUG002',
        tipo_pago='transferencia',
        banco='BBVA',
        numero_factura='DEBUG-002',
        fecha_generacion_factura=timezone.now(),
        cliente=cliente,
        descripcion='Debug venta 2',
        unidad=unidad,
        precio=Decimal('2360.00'),
        estado='pagado'
    )
    
    print("   ✓ Datos de prueba creados\n")
    
    # Verificar datos creados
    print("3. Verificando datos de debug creados...")
    debug_ventas = Ventas.objects.filter(numero_factura__startswith='DEBUG-')
    print(f"   Total de ventas de debug: {debug_ventas.count()}")
    
    for venta in debug_ventas:
        print(f"   - Venta {venta.numero_factura}: estado='{venta.estado}', tipo_pago='{venta.tipo_pago}', cliente_id={venta.cliente.id}")
    
    print()
    
    # Probar filtros solo en ventas de debug
    print("4. Probando filtros en ventas de debug...")
    
    # Filtro por estado pendiente
    pendientes = debug_ventas.filter(estado='pendiente')
    print(f"   Ventas DEBUG con estado 'pendiente': {pendientes.count()}")
    for venta in pendientes:
        print(f"     - {venta.numero_factura}: {venta.estado}")
    
    # Filtro por estado pagado
    pagadas = debug_ventas.filter(estado='pagado')
    print(f"   Ventas DEBUG con estado 'pagado': {pagadas.count()}")
    for venta in pagadas:
        print(f"     - {venta.numero_factura}: {venta.estado}")
    
    # Filtro por tipo_pago transferencia
    transferencias = debug_ventas.filter(tipo_pago='transferencia')
    print(f"   Ventas DEBUG con tipo_pago 'transferencia': {transferencias.count()}")
    for venta in transferencias:
        print(f"     - {venta.numero_factura}: {venta.tipo_pago}")
    
    # Filtro por cliente
    ventas_cliente = debug_ventas.filter(cliente=cliente)
    print(f"   Ventas DEBUG del cliente {cliente.id}: {ventas_cliente.count()}")
    for venta in ventas_cliente:
        print(f"     - {venta.numero_factura}: cliente_id={venta.cliente.id}")
    
    # Probar filtros en todas las ventas para comparar
    print("\n5. Comparando con filtros en TODAS las ventas...")
    
    # Filtro por estado pendiente en todas las ventas
    all_pendientes = Ventas.objects.filter(estado='pendiente')
    print(f"   TODAS las ventas con estado 'pendiente': {all_pendientes.count()}")
    
    # Filtro por estado pagado en todas las ventas
    all_pagadas = Ventas.objects.filter(estado='pagado')
    print(f"   TODAS las ventas con estado 'pagado': {all_pagadas.count()}")
    
    # Filtro por tipo_pago transferencia en todas las ventas
    all_transferencias = Ventas.objects.filter(tipo_pago='transferencia')
    print(f"   TODAS las ventas con tipo_pago 'transferencia': {all_transferencias.count()}")
    
    # Filtro por cliente en todas las ventas
    all_ventas_cliente = Ventas.objects.filter(cliente=cliente)
    print(f"   TODAS las ventas del cliente {cliente.id}: {all_ventas_cliente.count()}")
    
    print("\n=== FIN DE LA DEPURACIÓN ===")

if __name__ == '__main__':
    debug_sales_filter()