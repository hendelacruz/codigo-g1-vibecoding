#!/usr/bin/env python3
"""
Script para ejecutar el servidor Django en modo red local.
Permite acceso desde otras computadoras en la misma red.
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

def get_local_ip():
    """Obtiene la IP local de la máquina."""
    try:
        # Conecta a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.100"  # IP por defecto

def main():
    """Función principal para ejecutar el servidor."""
    # Obtener la IP local
    local_ip = get_local_ip()
    
    print("🚀 INICIANDO SERVIDOR DJANGO PARA RED LOCAL")
    print("=" * 50)
    print(f"🌐 IP Local detectada: {local_ip}")
    print(f"🔗 Acceso desde red local: http://{local_ip}:8000")
    print(f"🔗 Acceso local: http://localhost:8000")
    print("=" * 50)
    print()
    
    # Configurar variables de entorno
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
    
    # Ejecutar el servidor en todas las interfaces (0.0.0.0)
    try:
        print("📡 Ejecutando servidor en 0.0.0.0:8000...")
        print("💡 Presiona Ctrl+C para detener el servidor")
        print()
        
        # Ejecutar manage.py runserver
        subprocess.run([
            sys.executable, 
            'manage.py', 
            'runserver', 
            '0.0.0.0:8000'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())