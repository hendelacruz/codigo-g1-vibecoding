# Generated manually for data migration
from django.db import migrations


def migrate_estado_to_proceso(apps, schema_editor):
    """
    Migrates existing estado values to the new estado + proceso structure.
    
    Old estado values are mapped as follows:
    - 'disponible' -> estado='no_asignado', proceso='disponible'
    - 'asignado' -> estado='asignado', proceso='disponible'
    - 'dañado' -> estado='no_asignado', proceso='dañado'
    - 'en_reparacion' -> estado='no_asignado', proceso='en_reparacion'
    - 'en_mantenimiento' -> estado='no_asignado', proceso='en_mantenimiento'
    - 'dado_de_baja' -> estado='no_asignado', proceso='dado_de_baja'
    - 'activo' -> estado='asignado', proceso='disponible'
    - 'suspendido' -> estado='asignado', proceso='en_mantenimiento'
    - 'perdido' -> estado='no_asignado', proceso='dado_de_baja'
    """
    GPS = apps.get_model('inventory', 'GPS')
    
    # Mapping from old estado to new (estado, proceso)
    estado_mapping = {
        'disponible': ('no_asignado', 'disponible'),
        'asignado': ('asignado', 'disponible'),
        'dañado': ('no_asignado', 'dañado'),
        'en_reparacion': ('no_asignado', 'en_reparacion'),
        'en_mantenimiento': ('no_asignado', 'en_mantenimiento'),
        'dado_de_baja': ('no_asignado', 'dado_de_baja'),
        'activo': ('asignado', 'disponible'),
        'suspendido': ('asignado', 'en_mantenimiento'),
        'perdido': ('no_asignado', 'dado_de_baja'),
    }
    
    for gps in GPS.objects.all():
        old_estado = gps.estado
        
        if old_estado in estado_mapping:
            new_estado, new_proceso = estado_mapping[old_estado]
            gps.estado = new_estado
            gps.proceso = new_proceso
        else:
            # Default fallback for unknown states
            if gps.cliente:
                gps.estado = 'asignado'
                gps.proceso = 'disponible'
            else:
                gps.estado = 'no_asignado'
                gps.proceso = 'disponible'
        
        gps.save()


def reverse_migrate_estado_to_proceso(apps, schema_editor):
    """
    Reverses the estado/proceso migration.
    
    Maps new (estado, proceso) combinations back to old estado values.
    """
    GPS = apps.get_model('inventory', 'GPS')
    
    # Reverse mapping from (estado, proceso) to old estado
    reverse_mapping = {
        ('no_asignado', 'disponible'): 'disponible',
        ('asignado', 'disponible'): 'asignado',
        ('no_asignado', 'dañado'): 'dañado',
        ('no_asignado', 'en_reparacion'): 'en_reparacion',
        ('no_asignado', 'en_mantenimiento'): 'en_mantenimiento',
        ('no_asignado', 'dado_de_baja'): 'dado_de_baja',
        ('asignado', 'en_mantenimiento'): 'suspendido',
        ('no_asignado', 'en_transito'): 'disponible',  # Map to closest equivalent
        ('asignado', 'en_transito'): 'asignado',  # Map to closest equivalent
    }
    
    for gps in GPS.objects.all():
        key = (gps.estado, gps.proceso)
        
        if key in reverse_mapping:
            gps.estado = reverse_mapping[key]
        else:
            # Default fallback
            if gps.cliente:
                gps.estado = 'asignado'
            else:
                gps.estado = 'disponible'
        
        gps.save()


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_separate_estado_proceso'),
    ]

    operations = [
        migrations.RunPython(
            migrate_estado_to_proceso,
            reverse_migrate_estado_to_proceso,
        ),
    ]