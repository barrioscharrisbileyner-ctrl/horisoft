from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "persona", "creado")
    list_filter = ("rol",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
