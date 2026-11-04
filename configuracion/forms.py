from django import forms

from residentes.forms import PropiedadScopedFormMixin

from .models import ParametroConfiguracion


class ParametroConfiguracionForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = ParametroConfiguracion
        fields = ['clave', 'valor', 'descripcion', 'propiedad_horizontal']
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }


class ParametroConfiguracionValorForm(forms.ModelForm):
    class Meta:
        model = ParametroConfiguracion
        fields = ['valor', 'descripcion']
        widgets = {
            'valor': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
