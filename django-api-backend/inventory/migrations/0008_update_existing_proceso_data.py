# Generated manually to update existing proceso values
from django.db import migrations


def update_proceso_values(apps, schema_editor):
    """
    Update existing proceso values to match new choices:
    - disponible -> en_produccion
    - en_reparacion -> garantia
    """
    GPS = apps.get_model('inventory', 'GPS')
    
    # Update disponible to en_produccion
    GPS.objects.filter(proceso='disponible').update(proceso='en_produccion')
    
    # Update en_reparacion to garantia
    GPS.objects.filter(proceso='en_reparacion').update(proceso='garantia')


def reverse_proceso_values(apps, schema_editor):
    """
    Reverse the proceso value updates:
    - en_produccion -> disponible
    - garantia -> en_reparacion
    """
    GPS = apps.get_model('inventory', 'GPS')
    
    # Reverse en_produccion to disponible
    GPS.objects.filter(proceso='en_produccion').update(proceso='disponible')
    
    # Reverse garantia to en_reparacion
    GPS.objects.filter(proceso='garantia').update(proceso='en_reparacion')


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_update_proceso_values'),
    ]

    operations = [
        migrations.RunPython(
            update_proceso_values,
            reverse_proceso_values,
        ),
    ]