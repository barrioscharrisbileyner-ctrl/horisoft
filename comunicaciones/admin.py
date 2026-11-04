from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin, usuarios_visibles
from .models import Comunicado


@admin.register(Comunicado)
class ComunicadoAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['titulo', 'dirigido_a', 'estado', 'autor', 'fecha_publicacion']
    list_filter = ['dirigido_a', 'estado']
    search_fields = ['titulo', 'contenido']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'autor':
            formfield.queryset = usuarios_visibles(request.user)
        return formfield
