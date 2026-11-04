from django import forms

from residentes.forms import PropiedadScopedFormMixin

from .models import Documento


class DocumentoForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'tipo', 'archivo', 'url_archivo', 'descripcion', 'propiedad_horizontal']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,application/pdf'}),
            'url_archivo': forms.URLInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }
