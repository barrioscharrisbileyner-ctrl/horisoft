import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0002_parametroconfiguracion_propiedad_horizontal_and_more'),
        ('residentes', '0003_assign_existing_records_to_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametroconfiguracion',
            name='propiedad_horizontal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parametros_configuracion', to='residentes.propiedadhorizontal', verbose_name='Propiedad horizontal'),
        ),
    ]
