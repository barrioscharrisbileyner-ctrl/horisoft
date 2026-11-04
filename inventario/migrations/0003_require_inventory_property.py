import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_iteminventario_propiedad_horizontal'),
        ('residentes', '0003_assign_existing_records_to_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminventario',
            name='propiedad_horizontal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items_inventario', to='residentes.propiedadhorizontal', verbose_name='Propiedad horizontal'),
        ),
    ]
