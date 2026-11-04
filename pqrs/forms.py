from django import forms

from residentes.access import propiedades_accesibles
from residentes.models import Residencia
from usuarios.models import ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from .models import Pqr


class PqrForm(forms.ModelForm):
    class Meta:
        model = Pqr
        fields = ['residencia', 'tipo', 'asunto', 'descripcion']
        widgets = {
            'residencia': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
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


class PqrRespuestaForm(forms.Form):
    respuesta = forms.CharField(
        label='Respuesta',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
    )
