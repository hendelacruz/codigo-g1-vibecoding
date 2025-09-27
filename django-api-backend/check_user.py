import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings.development')
django.setup()

from authentication.models import CustomUser

# Verificar usuario
try:
    user = CustomUser.objects.get(username='Hdelacruz')
    print(f"Usuario encontrado: {user.username}")
    print(f"Email: {user.email}")
    print(f"Activo: {user.is_active}")
    print(f"Contraseña actual: {user.password}")
    print(f"Longitud: {len(user.password)}")
    
    # Verificar si está cifrada
    is_hashed = user.password.startswith(('pbkdf2_', 'bcrypt', 'argon2'))
    print(f"¿Cifrada?: {is_hashed}")
    
    if not is_hashed:
        print("CORRIGIENDO CONTRASEÑA...")
        user.set_password('Hygcompe')
        user.save()
        print("Contraseña corregida!")
        print(f"Nueva contraseña: {user.password}")
        
        # Verificar
        if user.check_password('Hygcompe'):
            print("✅ Verificación exitosa")
        else:
            print("❌ Error en verificación")
    
except CustomUser.DoesNotExist:
    print("Usuario no encontrado")
except Exception as e:
    print(f"Error: {e}")