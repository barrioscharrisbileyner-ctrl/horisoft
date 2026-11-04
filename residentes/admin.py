from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q

from .access import propiedades_accesibles
from .admin_scope import PropiedadScopedAdminMixin
from .models import AccesoPropiedad, PropiedadHorizontal, Persona, UnidadResidencial, Residencia


@admin.register(PropiedadHorizontal)
class PropiedadHorizontalAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'pk'
    list_display = ('id_ph', 'nombre', 'nit')

    def has_add_permission(self, request):
        return request.user.is_superuser


@admin.register(AccesoPropiedad)
class AccesoPropiedadAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ('usuario', 'propiedad_horizontal', 'creado')
    list_filter = ('propiedad_horizontal',)
    search_fields = ('usuario__email', 'usuario__username', 'propiedad_horizontal__nombre')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'usuario' and not request.user.is_superuser:
            User = get_user_model()
            propiedades = propiedades_accesibles(request.user)
            kwargs['queryset'] = User.objects.filter(
                Q(accesos_propiedad__propiedad_horizontal__in=propiedades)
                | Q(perfil__persona__propiedades__in=propiedades),
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Persona)
class PersonaAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'propiedades'
    list_display = ('id_persona', 'numero_documento', 'nombre', 'telefono', 'email')
    search_fields = ('numero_documento', 'nombre')
    filter_horizontal = ('propiedades',)


@admin.register(UnidadResidencial)
class UnidadResidencialAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ('id_unidad', 'numero_unidad', 'tipo_unidad', 'propiedad_horizontal')
    list_filter = ('tipo_unidad',)


@admin.register(Residencia)
class ResidenciaAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'unidad__propiedad_horizontal'
    list_display = ('id_residencia', 'persona', 'unidad', 'rol', 'fecha_inicio', 'activo')
    list_filter = ('rol', 'activo')
