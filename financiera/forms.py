from django import forms

from residentes.access import propiedades_accesibles
from residentes.models import Residencia
from usuarios.models import ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from .models import ConvenioPago, CuentaCobro, Multa, Pago


class CuentaCobroForm(forms.ModelForm):
    class Meta:
        model = CuentaCobro
        fields = ['residencia', 'concepto', 'valor', 'fecha_vencimiento']
        widgets = {
            'residencia': forms.Select(attrs={'class': 'form-select'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        residencias = Residencia.objects.filter(activo=True).select_related('persona', 'unidad')
        if usuario is not None:
            residencias = residencias.filter(unidad__propiedad_horizontal__in=propiedades_accesibles(usuario))
        if usuario is not None and obtener_rol(usuario) == ROL_RESIDENTE:
            persona = getattr(getattr(usuario, 'perfil', None), 'persona', None)
            residencias = residencias.filter(persona=persona) if persona else residencias.none()
        self.fields['residencia'].queryset = residencias


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['cuenta', 'valor_pagado', 'metodo_pago']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'valor_pagado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        cuentas = CuentaCobro.objects.filter(activo=True).select_related('residencia__persona', 'residencia__unidad')
        if usuario is not None:
            cuentas = cuentas.filter(residencia__unidad__propiedad_horizontal__in=propiedades_accesibles(usuario))
        if usuario is not None and obtener_rol(usuario) == ROL_RESIDENTE:
            persona = getattr(getattr(usuario, 'perfil', None), 'persona', None)
            cuentas = cuentas.filter(residencia__persona=persona) if persona else cuentas.none()
        self.fields['cuenta'].queryset = cuentas


class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['residencia', 'concepto', 'valor', 'fecha', 'estado']
        widgets = {
            'residencia': forms.Select(attrs={'class': 'form-select'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        residencias = Residencia.objects.filter(activo=True).select_related('persona', 'unidad')
        if usuario is not None:
            residencias = residencias.filter(unidad__propiedad_horizontal__in=propiedades_accesibles(usuario))
            if obtener_rol(usuario) == ROL_RESIDENTE:
                persona = getattr(getattr(usuario, 'perfil', None), 'persona', None)
                residencias = residencias.filter(persona=persona) if persona else residencias.none()
        self.fields['residencia'].queryset = residencias


class ConvenioPagoForm(forms.ModelForm):
    class Meta:
        model = ConvenioPago
        fields = ['cuenta', 'cuotas', 'valor_cuota', 'estado']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'cuotas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'valor_cuota': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        cuentas = CuentaCobro.objects.filter(activo=True).select_related(
            'residencia__persona', 'residencia__unidad',
        )
        if usuario is not None:
            cuentas = cuentas.filter(residencia__unidad__propiedad_horizontal__in=propiedades_accesibles(usuario))
            if obtener_rol(usuario) == ROL_RESIDENTE:
                persona = getattr(getattr(usuario, 'perfil', None), 'persona', None)
                cuentas = cuentas.filter(residencia__persona=persona) if persona else cuentas.none()
        self.fields['cuenta'].queryset = cuentas
