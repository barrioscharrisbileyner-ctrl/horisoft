from django.db import migrations

from residentes.migration_helpers import assign_single_property


def assign_existing_records(apps, schema_editor):
    database = schema_editor.connection.alias
    Person = apps.get_model('residentes', 'Persona')
    Residence = apps.get_model('residentes', 'Residencia')
    Property = apps.get_model('residentes', 'PropiedadHorizontal')
    Access = apps.get_model('residentes', 'AccesoPropiedad')
    Profile = apps.get_model('usuarios', 'PerfilUsuario')

    for person_id, property_id in Residence.objects.using(database).values_list(
        'persona_id', 'unidad__propiedad_horizontal_id',
    ).distinct():
        Person.objects.using(database).get(pk=person_id).propiedades.add(property_id)

    property_ids = list(Property.objects.using(database).values_list('pk', flat=True))
    unassigned_people = Person.objects.using(database).filter(propiedades__isnull=True)
    if unassigned_people.exists():
        if len(property_ids) != 1:
            raise RuntimeError(
                'Cannot assign people without residences to a property: '
                f'expected exactly one property, found {len(property_ids)}. '
                'Assign each person explicitly and retry the migration.'
            )
        for person in unassigned_people.iterator():
            person.propiedades.add(property_ids[0])

    unassigned_profiles = Profile.objects.using(database).exclude(rol='Residente').filter(
        user__accesos_propiedad__isnull=True,
    )
    if unassigned_profiles.exists():
        if len(property_ids) != 1:
            raise RuntimeError(
                'Cannot assign existing non-resident users to a property: '
                f'expected exactly one property, found {len(property_ids)}. '
                'Add AccesoPropiedad rows for these users and retry the migration.'
            )
        Access.objects.using(database).bulk_create([
            Access(usuario_id=user_id, propiedad_horizontal_id=property_ids[0])
            for user_id in unassigned_profiles.values_list('user_id', flat=True)
        ], ignore_conflicts=True)

    for app_label, model_name in (
        ('reservas', 'ZonaComun'),
        ('comunicaciones', 'Comunicado'),
        ('documental', 'Documento'),
        ('seguridad', 'Vigilante'),
        ('inventario', 'ItemInventario'),
        ('proveedores', 'Proveedor'),
        ('configuracion', 'ParametroConfiguracion'),
    ):
        assign_single_property(apps, schema_editor, app_label, model_name)


class Migration(migrations.Migration):

    dependencies = [
        ('residentes', '0002_persona_propiedades_accesopropiedad'),
        ('usuarios', '0001_initial'),
        ('reservas', '0002_zonacomun_propiedad_horizontal_and_more'),
        ('comunicaciones', '0002_comunicado_propiedad_horizontal'),
        ('documental', '0003_documento_propiedad_horizontal'),
        ('seguridad', '0002_vigilante_propiedad_horizontal_and_more'),
        ('inventario', '0002_iteminventario_propiedad_horizontal'),
        ('proveedores', '0002_proveedor_propiedad_horizontal_alter_proveedor_nit_and_more'),
        ('configuracion', '0002_parametroconfiguracion_propiedad_horizontal_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_existing_records, migrations.RunPython.noop),
    ]
