def assign_single_property(apps, schema_editor, app_label, model_name):
    property_model = apps.get_model('residentes', 'PropiedadHorizontal')
    model = apps.get_model(app_label, model_name)
    database = schema_editor.connection.alias
    unassigned = model.objects.using(database).filter(propiedad_horizontal__isnull=True)
    if not unassigned.exists():
        return

    properties = property_model.objects.using(database).order_by('pk')
    count = properties.count()
    if count != 1:
        raise RuntimeError(
            f'Cannot assign {app_label}.{model_name} rows with no property: '
            f'expected exactly one property, found {count}. Assign these rows manually '
            'before retrying the migration.'
        )
    unassigned.update(propiedad_horizontal_id=properties.values_list('pk', flat=True).get())
