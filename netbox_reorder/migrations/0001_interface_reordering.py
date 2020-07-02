from cacheops import invalidate_model
from django.db import migrations

import netbox_reorder.ordering


def _update_model_names(model):
    # Update each unique field value in bulk
    for name in model.objects.values_list('name', flat=True).order_by('name').distinct():
        model.objects.filter(name=name).update(_name=netbox_reorder.ordering.naturalize_interface(name, max_length=100))

    invalidate_model(model)


def naturalize_interfacetemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'InterfaceTemplate'))


def naturalize_interfaces(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'Interface'))


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0096_interface_ordering'),
    ]

    operations = [
        migrations.RunPython(
            code=naturalize_interfacetemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_interfaces,
            reverse_code=migrations.RunPython.noop
        ),
    ]
