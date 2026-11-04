from django import forms

from reservas.models import ZonaComun
from residentes.access import propiedades_accesibles
from residentes.models import Residencia
from residentes.forms import PropiedadScopedFormMixin
from usuarios.models import ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from .models import Camara, Vehiculo, Vigilante, Visitante


class VigilanteForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Vigilante
        fields = ['nombre', 'documento', 'telefono', 'turno', 'estado', 'propiedad_horizontal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
        }


class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombre', 'documento', 'residencia', 'vigilante', 'motivo', 'placa_vehiculo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'residencia': forms.Select(attrs={'class': 'form-select'}),
            'vigilante': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        propiedades = propiedades_accesibles(usuario) if usuario is not None else None
        residencias = Residencia.objects.filter(activo=True).select_related('persona', 'unidad')
        vigilantes = Vigilante.objects.filter(estado=Vigilante.ESTADO_ACTIVO)
        if propiedades is not None:
            residencias = residencias.filter(unidad__propiedad_horizontal__in=propiedades)
            vigilantes = vigilantes.filter(propiedad_horizontal__in=propiedades)
        self.fields['residencia'].queryset = residencias
        self.fields['vigilante'].queryset = vigilantes

    def clean(self):
        cleaned = super().clean()
        residencia = cleaned.get('residencia')
        vigilante = cleaned.get('vigilante')
        if (
            residencia
            and vigilante
            and residencia.unidad.propiedad_horizontal_id != vigilante.propiedad_horizontal_id
        ):
            raise forms.ValidationError('El vigilante y la residencia deben pertenecer a la misma copropiedad.')
        return cleaned


class CamaraForm(forms.ModelForm):
    class Meta:
        model = Camara
        fields = ['ubicacion', 'estado', 'zona']
        widgets = {
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        zonas = ZonaComun.objects.all()
        if usuario is not None:
            zonas = zonas.filter(propiedad_horizontal__in=propiedades_accesibles(usuario))
        self.fields['zona'].queryset = zonas


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'tipo', 'residencia']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 6}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'residencia': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        residencias = Residencia.objects.filter(activo=True).select_related('persona', 'unidad')
        if usuario is not None:
            residencias = residencias.filter(unidad__propiedad_horizontal__in=propiedades_accesibles(usuario))
            if obtener_rol(usuario) == ROL_RESIDENTE:
                perfil = getattr(usuario, 'perfil', None)
                persona = perfil.persona if perfil else None
                residencias = residencias.filter(persona=persona) if persona else residencias.none()
        self.fields['residencia'].queryset = residencias
