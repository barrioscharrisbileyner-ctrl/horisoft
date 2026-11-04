from .models import PropiedadHorizontal


def propiedades_accesibles(usuario):
    if not getattr(usuario, 'is_authenticated', False):
        return PropiedadHorizontal.objects.none()
    if usuario.is_superuser:
        return PropiedadHorizontal.objects.all()

    perfil = getattr(usuario, 'perfil', None)
    if perfil is None:
        return PropiedadHorizontal.objects.none()
    if perfil.rol == 'Residente':
        if perfil.persona_id is None:
            return PropiedadHorizontal.objects.none()
        return PropiedadHorizontal.objects.filter(
            unidades__residencias__persona_id=perfil.persona_id,
            unidades__residencias__activo=True,
        ).distinct()
    accesos = PropiedadHorizontal.objects.filter(
        accesos_usuario__usuario=usuario,
    ).distinct()
    if accesos.exists():
        return accesos
    if PropiedadHorizontal.objects.count() == 1:
        return PropiedadHorizontal.objects.all()
    return PropiedadHorizontal.objects.none()


def filtrar_por_propiedad(queryset, usuario, lookup='propiedad_horizontal'):
    return queryset.filter(**{f'{lookup}__in': propiedades_accesibles(usuario)})
