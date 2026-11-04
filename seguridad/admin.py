from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import Camara, Vehiculo, Vigilante, Visitante


@admin.register(Vigilante)
class VigilanteAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'documento', 'turno', 'estado']
    list_filter = ['turno', 'estado']
    search_fields = ['nombre', 'documento']


@admin.register(Visitante)
class VisitanteAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'residencia__unidad__propiedad_horizontal'
    list_display = ['nombre', 'documento', 'residencia', 'vigilante', 'estado', 'hora_ingreso']
    list_filter = ['estado', 'vigilante']
    search_fields = ['nombre', 'documento']


@admin.register(Camara)
class CamaraAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'zona__propiedad_horizontal'
    list_display = ['ubicacion', 'zona', 'estado']
    list_filter = ['estado']
    search_fields = ['ubicacion', 'zona__nombre']


@admin.register(Vehiculo)
class VehiculoAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'residencia__unidad__propiedad_horizontal'
    list_display = ['placa', 'tipo', 'residencia']
    search_fields = ['placa', 'residencia__persona__nombre', 'residencia__unidad__numero_unidad']
