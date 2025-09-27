#!/usr/bin/env python
"""
Script para limpiar usuarios del sistema
Mantiene solo los usuarios especificados y elimina el resto permanentemente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

from authentication.models import CustomUser
from django.db import transaction


def cleanup_users():
    """
    Elimina todos los usuarios excepto admin y Hdelacruz
    """
    # Usuarios que deben mantenerse
    KEEP_USERNAMES = ['admin', 'Hdelacruz']
    
    print("=== SCRIPT DE LIMPIEZA DE USUARIOS ===")
    print(f"Usuarios a mantener: {', '.join(KEEP_USERNAMES)}")
    print()
    
    # Obtener todos los usuarios
    all_users = CustomUser.objects.all()
    users_to_keep = CustomUser.objects.filter(username__in=KEEP_USERNAMES)
    users_to_delete = CustomUser.objects.exclude(username__in=KEEP_USERNAMES)
    
    print(f"Total usuarios en sistema: {all_users.count()}")
    print(f"Usuarios a mantener: {users_to_keep.count()}")
    print(f"Usuarios a eliminar: {users_to_delete.count()}")
    print()
    
    # Mostrar usuarios que se mantendrán
    print("=== USUARIOS QUE SE MANTENDRÁN ===")
    for user in users_to_keep:
        print(f"✅ ID: {user.id} | Username: {user.username} | Nombre: {user.first_name} {user.last_name}")
    print()
    
    # Mostrar usuarios que se eliminarán
    print("=== USUARIOS QUE SE ELIMINARÁN ===")
    for user in users_to_delete:
        print(f"❌ ID: {user.id} | Username: {user.username} | Nombre: {user.first_name} {user.last_name}")
    print()
    
    # Confirmación de seguridad
    if users_to_delete.count() == 0:
        print("No hay usuarios para eliminar.")
        return
    
    confirmation = input(f"¿Estás seguro de que quieres eliminar {users_to_delete.count()} usuarios? (escriba 'CONFIRMAR' para proceder): ")
    
    if confirmation != 'CONFIRMAR':
        print("Operación cancelada.")
        return
    
    # Realizar eliminación en transacción
    try:
        with transaction.atomic():
            deleted_count = 0
            for user in users_to_delete:
                username = user.username
                user_id = user.id
                user.delete()
                deleted_count += 1
                print(f"✅ Eliminado: ID {user_id} - {username}")
            
            print(f"\n🎉 Eliminación completada exitosamente!")
            print(f"Total usuarios eliminados: {deleted_count}")
            
    except Exception as e:
        print(f"❌ Error durante la eliminación: {str(e)}")
        return
    
    # Verificar resultado final
    print("\n=== VERIFICACIÓN FINAL ===")
    remaining_users = CustomUser.objects.all()
    print(f"Usuarios restantes en el sistema: {remaining_users.count()}")
    
    for user in remaining_users:
        print(f"✅ ID: {user.id} | Username: {user.username} | Nombre: {user.first_name} {user.last_name}")


def show_current_users():
    """
    Muestra todos los usuarios actuales sin eliminar nada
    """
    print("=== USUARIOS ACTUALES EN EL SISTEMA ===")
    users = CustomUser.objects.all()
    
    for user in users:
        print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Nombre: {user.first_name} {user.last_name} | Activo: {user.is_active}")
    
    print(f"\nTotal usuarios: {users.count()}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        show_current_users()
    else:
        cleanup_users()