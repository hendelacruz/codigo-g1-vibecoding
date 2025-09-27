#!/usr/bin/env python3
"""
Tests para verificar la configuración de acceso desde red local.
"""

import os
import sys
import requests
import socket
import time
import subprocess
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')

import django
django.setup()

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.management import call_command
from rest_framework.test import APITestCase
from authentication.models import User

class NetworkConfigurationTest(TestCase):
    """Tests para verificar la configuración de red local."""
    
    def test_allowed_hosts_configuration(self):
        """Verifica que ALLOWED_HOSTS esté configurado para red local."""
        allowed_hosts = settings.ALLOWED_HOSTS
        
        # Debe incluir configuraciones para red local
        self.assertIn('*', allowed_hosts, "ALLOWED_HOSTS debe incluir '*' para desarrollo")
        self.assertIn('0.0.0.0', allowed_hosts, "ALLOWED_HOSTS debe incluir '0.0.0.0'")
        
        print("✅ ALLOWED_HOSTS configurado correctamente")
    
    def test_cors_configuration(self):
        """Verifica que CORS esté configurado para permitir acceso desde red local."""
        # Verificar que CORS_ALLOW_ALL_ORIGINS esté habilitado
        cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        self.assertTrue(cors_allow_all, "CORS_ALLOW_ALL_ORIGINS debe estar en True para desarrollo")
        
        # Verificar que CORS_ALLOW_CREDENTIALS esté habilitado
        cors_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', False)
        self.assertTrue(cors_credentials, "CORS_ALLOW_CREDENTIALS debe estar en True")
        
        print("✅ CORS configurado correctamente")
    
    def test_debug_mode_enabled(self):
        """Verifica que DEBUG esté habilitado en desarrollo."""
        self.assertTrue(settings.DEBUG, "DEBUG debe estar habilitado en desarrollo")
        print("✅ DEBUG mode habilitado")

class NetworkAccessTest(APITestCase):
    """Tests para verificar el acceso a la API desde red local."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_api_endpoints_accessible(self):
        """Verifica que los endpoints principales sean accesibles."""
        # Test endpoint de documentación
        response = self.client.get('/api/docs/')
        self.assertIn(response.status_code, [200, 301, 302], 
                     "Endpoint de documentación debe ser accesible")
        
        # Test endpoint de login
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200, 
                        "Endpoint de login debe funcionar correctamente")
        
        print("✅ Endpoints principales accesibles")
    
    def test_cors_headers_present(self):
        """Verifica que las cabeceras CORS estén presentes."""
        response = self.client.options('/api/auth/login/')
        
        # Verificar cabeceras CORS
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        for header in cors_headers:
            self.assertIn(header, response.headers, 
                         f"Cabecera CORS {header} debe estar presente")
        
        print("✅ Cabeceras CORS presentes")

def get_local_ip():
    """Obtiene la IP local de la máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.100"

def test_network_connectivity():
    """Test manual para verificar conectividad de red."""
    print("\n🌐 TESTING NETWORK CONNECTIVITY")
    print("=" * 50)
    
    local_ip = get_local_ip()
    print(f"🔍 IP Local detectada: {local_ip}")
    
    # Test de conectividad básica
    try:
        # Verificar que el puerto 8000 esté disponible
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Puerto 8000 está disponible")
        else:
            print("❌ Puerto 8000 no está disponible")
            print("💡 Ejecuta: python run_server_network.py")
            
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
    
    print("\n📋 URLs de acceso:")
    print(f"🏠 Local: http://localhost:8000")
    print(f"🌐 Red local: http://{local_ip}:8000")
    print(f"📚 Documentación: http://{local_ip}:8000/api/docs/")
    print(f"🔐 Login: http://{local_ip}:8000/api/auth/login/")

def main():
    """Función principal para ejecutar todos los tests."""
    print("🧪 EJECUTANDO TESTS DE CONFIGURACIÓN DE RED")
    print("=" * 60)
    
    # Ejecutar tests de Django
    try:
        call_command('test', 'test_network_config', verbosity=2)
        print("✅ Tests de configuración completados")
    except Exception as e:
        print(f"❌ Error en tests: {e}")
    
    # Test manual de conectividad
    test_network_connectivity()
    
    print("\n🎉 TESTS COMPLETADOS")
    print("💡 Si todos los tests pasan, tu configuración está lista para red local")

if __name__ == "__main__":
    main()