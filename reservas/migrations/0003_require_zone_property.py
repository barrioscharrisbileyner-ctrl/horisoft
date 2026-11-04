import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0002_zonacomun_propiedad_horizontal_and_more'),
        ('residentes', '0003_assign_existing_records_to_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zonacomun',
            name='propiedad_horizontal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='zonas_comunes', to='residentes.propiedadhorizontal', verbose_name='Propiedad horizontal'),
        ),
    ]
