from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import ItemInventario


@admin.register(ItemInventario)
class ItemInventarioAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'cantidad', 'cantidad_minima', 'estado', 'ubicacion']
    list_filter = ['categoria', 'estado']
    search_fields = ['nombre', 'categoria']
