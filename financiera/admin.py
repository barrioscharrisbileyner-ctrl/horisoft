from django.contrib import admin

from residentes.admin_scope import PropiedadScopedAdminMixin
from .models import ConvenioPago, CuentaCobro, Multa, Pago


@admin.register(CuentaCobro)
class CuentaCobroAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'residencia__unidad__propiedad_horizontal'
    list_display = ('id_cuenta', 'residencia', 'concepto', 'valor', 'valor_pagado', 'estado', 'fecha_vencimiento')
    list_filter = ('estado', 'fecha_vencimiento')
    search_fields = ('concepto', 'residencia__persona__nombre', 'residencia__unidad__numero_unidad')


@admin.register(Pago)
class PagoAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'cuenta__residencia__unidad__propiedad_horizontal'
    list_display = ('id_pago', 'cuenta', 'valor_pagado', 'metodo_pago', 'referencia', 'registrado_por', 'fecha_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
    search_fields = ('cuenta__concepto', 'referencia', 'registrado_por__email')
    readonly_fields = ('cuenta', 'valor_pagado', 'metodo_pago', 'referencia', 'registrado_por', 'fecha_pago')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Multa)
class MultaAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'residencia__unidad__propiedad_horizontal'
    list_display = ('id', 'residencia', 'concepto', 'valor', 'fecha', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('concepto', 'residencia__persona__nombre', 'residencia__unidad__numero_unidad')


@admin.register(ConvenioPago)
class ConvenioPagoAdmin(PropiedadScopedAdminMixin, admin.ModelAdmin):
    property_lookup = 'cuenta__residencia__unidad__propiedad_horizontal'
    list_display = ('id', 'cuenta', 'cuotas', 'valor_cuota', 'estado')
    list_filter = ('estado',)
    search_fields = ('cuenta__concepto', 'cuenta__residencia__persona__nombre')
