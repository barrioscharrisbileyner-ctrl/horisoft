from django import forms

from residentes.forms import PropiedadScopedFormMixin

from .models import Comunicado


class ComunicadoForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'contenido', 'dirigido_a', 'propiedad_horizontal']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'dirigido_a': forms.Select(attrs={'class': 'form-select'}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }
