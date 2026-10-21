from django.contrib import admin

from .models import PropiedadHorizontal, Persona, UnidadResidencial, Residencia


@admin.register(PropiedadHorizontal)
class PropiedadHorizontalAdmin(admin.ModelAdmin):
    list_display = ('id_ph', 'nombre', 'nit')


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id_persona', 'numero_documento', 'nombre', 'telefono', 'email')
    search_fields = ('numero_documento', 'nombre')


@admin.register(UnidadResidencial)
class UnidadResidencialAdmin(admin.ModelAdmin):
    list_display = ('id_unidad', 'numero_unidad', 'tipo_unidad', 'propiedad_horizontal')
    list_filter = ('tipo_unidad',)


@admin.register(Residencia)
class ResidenciaAdmin(admin.ModelAdmin):
    list_display = ('id_residencia', 'persona', 'unidad', 'rol', 'fecha_inicio', 'activo')
    list_filter = ('rol', 'activo')
