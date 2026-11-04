from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import Pqr


@admin.register(Pqr)
class PqrAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'residencia__unidad__propiedad_horizontal'
    list_display = ('id_pqr', 'residencia', 'tipo', 'estado', 'fecha_creacion')
    list_filter = ('tipo', 'estado')
    search_fields = ('asunto', 'descripcion', 'respuesta')
