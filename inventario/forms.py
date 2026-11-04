from django import forms

from residentes.forms import PropiedadScopedFormMixin

from .models import ItemInventario


class ItemInventarioForm(PropiedadScopedFormMixin, forms.ModelForm):
    cantidad_minima = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
    )

    class Meta:
        model = ItemInventario
        fields = ['nombre', 'categoria', 'cantidad', 'cantidad_minima', 'ubicacion', 'estado', 'propiedad_horizontal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cantidad_minima(self):
        return self.cleaned_data.get('cantidad_minima') or 0
