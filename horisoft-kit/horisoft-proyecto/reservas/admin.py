from django.contrib import admin

from .models import Reserva, ZonaComun


@admin.register(ZonaComun)
class ZonaComunAdmin(admin.ModelAdmin):
    list_display = ('id_zona', 'nombre', 'capacidad', 'costo_reserva', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'zona', 'residencia', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'zona')
    date_hierarchy = 'fecha'
