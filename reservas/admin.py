from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import Reserva, ZonaComun


@admin.register(ZonaComun)
class ZonaComunAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ('id_zona', 'nombre', 'capacidad', 'costo_reserva', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'zona__propiedad_horizontal'
    list_display = ('id_reserva', 'zona', 'residencia', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'zona')
    date_hierarchy = 'fecha'
