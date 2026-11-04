import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0002_proveedor_propiedad_horizontal_alter_proveedor_nit_and_more'),
        ('residentes', '0003_assign_existing_records_to_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='propiedad_horizontal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='proveedores', to='residentes.propiedadhorizontal', verbose_name='Propiedad horizontal'),
        ),
    ]
