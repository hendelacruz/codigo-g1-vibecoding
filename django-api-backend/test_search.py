#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.testing')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from entities.models import Cliente
from entities.filters import ClienteFilter
from django.db.models import Q

User = get_user_model()

# Simular el entorno de test
print("=== SIMULANDO ENTORNO DE TEST ===")

# Crear datos de prueba como en el test
print("Creando datos de prueba...")
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'password': 'testpass123', 'email': 'test@test.com'}
)

# Crear clientes de prueba
cliente1 = Cliente.objects.create(
    nombre='Cliente Test 1',
    ruc='12345678901',
    direccion='Calle 123',
    correo='cliente1@test.com',
    celular='987654321',
    contacto='Contacto 1'
)

cliente2 = Cliente.objects.create(
    nombre='Cliente Test 2',
    ruc='12345678902',
    direccion='Avenida 456',
    correo='cliente2@test.com',
    celular='987654322',
    contacto='Contacto 2'
)

cliente3 = Cliente.objects.create(
    nombre='Cliente Test 3',
    ruc='12345678903',
    direccion='Carrera 789',
    correo='cliente3@test.com',
    celular='987654323',
    contacto='Contacto 3'
)

print("=== CLIENTES DE PRUEBA CREADOS ===")
for cliente in Cliente.objects.filter(nombre__startswith='Cliente Test'):
    print(f"Cliente: {cliente.nombre}: {cliente.direccion}")

# Probar filtro con 'Av'
print("\n=== FILTRO CON 'Av' ===")
filtro = ClienteFilter({'search': 'Av'})
resultados = filtro.qs
print(f"Resultados encontrados: {resultados.count()}")
for resultado in resultados:
    print(f"- {resultado.nombre}: {resultado.direccion}")

# Probar filtro con 'Calle'
print("\n=== FILTRO CON 'Calle' ===")
filtro = ClienteFilter({'search': 'Calle'})
resultados = filtro.qs
print(f"Resultados encontrados: {resultados.count()}")
for resultado in resultados:
    print(f"- {resultado.nombre}: {resultado.direccion}")

# Limpiar datos de prueba
print("\n=== LIMPIANDO DATOS DE PRUEBA ===")
Cliente.objects.filter(nombre__startswith='Cliente Test').delete()
User.objects.filter(username='testuser').delete()
print("Datos de prueba eliminados.")