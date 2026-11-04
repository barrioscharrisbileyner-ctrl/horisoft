from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'servicio', 'estado']
    list_filter = ['estado']
    search_fields = ['nombre', 'nit', 'servicio']
