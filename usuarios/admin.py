from django.contrib import admin
from django.db.models import Q

from residentes.access import propiedades_accesibles
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "persona", "creado")
    list_filter = ("rol",)
    search_fields = ("user__email", "user__first_name", "user__last_name")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        propiedades = propiedades_accesibles(request.user)
        return queryset.filter(
            Q(persona__propiedades__in=propiedades)
            | Q(user__accesos_propiedad__propiedad_horizontal__in=propiedades),
        ).distinct()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'persona' and not request.user.is_superuser:
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(
                propiedades__in=propiedades_accesibles(request.user),
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
