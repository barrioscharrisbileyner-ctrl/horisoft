import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documental', '0003_documento_propiedad_horizontal'),
        ('residentes', '0003_assign_existing_records_to_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='propiedad_horizontal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documentos', to='residentes.propiedadhorizontal', verbose_name='Propiedad horizontal'),
        ),
    ]
