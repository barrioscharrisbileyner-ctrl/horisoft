from django.core.exceptions import FieldDoesNotExist
from django.contrib.auth import get_user_model
from django.db.models import Q

from .access import propiedades_accesibles
from .models import PropiedadHorizontal


PROPERTY_LOOKUPS = (
    'propiedad_horizontal',
    'unidad__propiedad_horizontal',
    'residencia__unidad__propiedad_horizontal',
    'zona__propiedad_horizontal',
    'cuenta__residencia__unidad__propiedad_horizontal',
)


def has_model_path(model, path):
    current = model
    for part in path.split('__'):
        try:
            field = current._meta.get_field(part)
        except FieldDoesNotExist:
            return False
        if field.related_model is None:
            return False
        current = field.related_model
    return True


def property_lookup(model):
    return next((path for path in PROPERTY_LOOKUPS if has_model_path(model, path)), None)


def usuarios_visibles(usuario):
    User = get_user_model()
    if usuario.is_superuser:
        return User.objects.all()
    propiedades = propiedades_accesibles(usuario)
    return User.objects.filter(
        Q(accesos_propiedad__propiedad_horizontal__in=propiedades)
        | Q(perfil__persona__propiedades__in=propiedades),
    ).distinct()


class PropiedadScopedAdminMixin:
    property_lookup = 'propiedad_horizontal'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(
            **{f'{self.property_lookup}__in': propiedades_accesibles(request.user)},
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        propiedades = propiedades_accesibles(request.user)
        for field in form.base_fields.values():
            queryset = getattr(field, 'queryset', None)
            if queryset is None:
                continue
            model = queryset.model
            if model is PropiedadHorizontal:
                field.queryset = propiedades
                continue
            lookup = property_lookup(model)
            if lookup:
                field.queryset = queryset.filter(**{f'{lookup}__in': propiedades})
        return form
