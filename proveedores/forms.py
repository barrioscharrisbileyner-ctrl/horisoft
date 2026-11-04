from django import forms

from residentes.forms import PropiedadScopedFormMixin

from .models import Proveedor


class ProveedorForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'nit', 'servicio', 'telefono', 'estado', 'propiedad_horizontal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }


class ProveedorEstadoForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
