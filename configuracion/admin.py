from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import ParametroConfiguracion


@admin.register(ParametroConfiguracion)
class ParametroConfiguracionAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['clave', 'valor', 'descripcion', 'fecha_actualizacion']
    search_fields = ['clave', 'descripcion']
