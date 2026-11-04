from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin, usuarios_visibles
from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'responsable', 'fecha_subida']
    list_filter = ['tipo']
    search_fields = ['titulo', 'descripcion']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'responsable':
            formfield.queryset = usuarios_visibles(request.user)
        return formfield
