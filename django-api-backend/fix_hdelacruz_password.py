#!/usr/bin/env python
"""
Script para diagnosticar y solucionar el problema de autenticación del usuario Hdelacruz
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

from authentication.models import CustomUser, Role
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction


def diagnose_user():
    """
    Diagnostica el estado actual del usuario Hdelacruz
    """
    try:
        user = CustomUser.objects.get(username='Hdelacruz')
        
        print("=== DIAGNÓSTICO DEL USUARIO HDELACRUZ ===")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Nombre completo: {user.first_name} {user.last_name}")
        print(f"Es activo: {user.is_active}")
        print(f"Es staff: {user.is_staff}")
        print(f"Es superuser: {user.is_superuser}")
        print(f"Último login: {user.last_login}")
        print(f"Fecha de creación: {user.date_joined}")
        print(f"Contraseña actual: {user.password}")
        print(f"Longitud del hash: {len(user.password)}")
        
        # Verificar si la contraseña está cifrada
        is_hashed = user.password.startswith(('pbkdf2_', 'bcrypt', 'argon2'))
        print(f"¿Contraseña cifrada?: {is_hashed}")
        
        # Verificar rol
        try:
            if hasattr(user, 'rol') and user.rol:
                print(f"Rol asignado: {user.rol.nombre} - {user.rol.get_nombre_display()}")
                print(f"Rol activo: {user.rol.is_active}")
            else:
                print("❌ Sin rol asignado")
        except Exception as e:
            print(f"❌ Error al verificar rol: {e}")
        
        print()
        
        # Verificar si puede autenticarse con la contraseña actual
        if not is_hashed:
            print("🔍 PROBLEMA IDENTIFICADO:")
            print("La contraseña NO está cifrada. Esto impide la autenticación.")
            print("Contraseña actual (texto plano):", user.password)
            return user, False
        else:
            print("✅ La contraseña está correctamente cifrada.")
            return user, True
            
    except CustomUser.DoesNotExist:
        print("❌ Usuario 'Hdelacruz' no encontrado")
        return None, False
    except Exception as e:
        print(f"❌ Error al diagnosticar usuario: {e}")
        return None, False


def fix_password(user, new_password="Hygcompe"):
    """
    Cifra correctamente la contraseña del usuario
    """
    print(f"\n=== SOLUCIONANDO PROBLEMA DE CONTRASEÑA ===")
    print(f"Cifrando contraseña: {new_password}")
    
    try:
        with transaction.atomic():
            # Cifrar la contraseña
            user.set_password(new_password)
            user.save()
            
            print("✅ Contraseña cifrada y guardada exitosamente")
            print(f"Nuevo hash: {user.password}")
            
            # Verificar que la contraseña funciona
            if user.check_password(new_password):
                print("✅ Verificación exitosa: La contraseña funciona correctamente")
                return True
            else:
                print("❌ Error: La contraseña no se verificó correctamente")
                return False
                
    except Exception as e:
        print(f"❌ Error al cifrar contraseña: {e}")
        return False


def ensure_role():
    """
    Asegura que el usuario tenga un rol asignado
    """
    try:
        user = CustomUser.objects.get(username='Hdelacruz')
        
        if not hasattr(user, 'rol') or not user.rol:
            print("\n=== ASIGNANDO ROL AL USUARIO ===")
            
            # Buscar un rol apropiado (preferiblemente administrador)
            try:
                admin_role = Role.objects.filter(nombre__in=['ADMIN', 'administrador']).first()
                if admin_role:
                    user.rol = admin_role
                    user.save()
                    print(f"✅ Rol asignado: {admin_role.nombre}")
                else:
                    print("❌ No se encontró un rol de administrador")
                    # Mostrar roles disponibles
                    roles = Role.objects.all()
                    print("Roles disponibles:")
                    for role in roles:
                        print(f"  - {role.nombre}: {role.get_nombre_display()}")
                        
            except Exception as e:
                print(f"❌ Error al asignar rol: {e}")
        else:
            print(f"\n✅ Usuario ya tiene rol asignado: {user.rol.nombre}")
            
    except Exception as e:
        print(f"❌ Error al verificar/asignar rol: {e}")


def test_authentication():
    """
    Prueba la autenticación del usuario
    """
    print("\n=== PROBANDO AUTENTICACIÓN ===")
    
    try:
        from django.contrib.auth import authenticate
        
        user = authenticate(username='Hdelacruz', password='Hygcompe')
        
        if user:
            print("✅ Autenticación exitosa!")
            print(f"Usuario autenticado: {user.username}")
            print(f"Es activo: {user.is_active}")
            return True
        else:
            print("❌ Autenticación falló")
            
            # Verificar posibles causas
            try:
                db_user = CustomUser.objects.get(username='Hdelacruz')
                if not db_user.is_active:
                    print("Causa: Usuario no está activo")
                elif not db_user.check_password('Hygcompe'):
                    print("Causa: Contraseña incorrecta")
                else:
                    print("Causa: Problema desconocido en autenticación")
            except:
                print("Causa: Usuario no existe")
                
            return False
            
    except Exception as e:
        print(f"❌ Error al probar autenticación: {e}")
        return False


def main():
    """
    Función principal que ejecuta el diagnóstico y solución
    """
    print("🔧 INICIANDO DIAGNÓSTICO Y REPARACIÓN DEL USUARIO HDELACRUZ")
    print("=" * 60)
    
    # Paso 1: Diagnosticar
    user, password_ok = diagnose_user()
    
    if not user:
        print("❌ No se puede continuar sin el usuario")
        return
    
    # Paso 2: Solucionar contraseña si es necesario
    if not password_ok:
        success = fix_password(user)
        if not success:
            print("❌ No se pudo solucionar el problema de contraseña")
            return
    
    # Paso 3: Verificar/asignar rol
    ensure_role()
    
    # Paso 4: Probar autenticación
    auth_success = test_authentication()
    
    print("\n" + "=" * 60)
    if auth_success:
        print("🎉 PROBLEMA SOLUCIONADO: El usuario puede autenticarse correctamente")
        print("Credenciales para el frontend:")
        print("  Username: Hdelacruz")
        print("  Password: Hygcompe")
    else:
        print("❌ PROBLEMA PERSISTE: Revisar logs anteriores para más detalles")


if __name__ == "__main__":
    main()