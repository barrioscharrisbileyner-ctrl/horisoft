"""
Formularios del módulo Residentes y Unidades.

Igual que en la guía TallerExpress: usamos ModelForm para que el
formulario se arme a partir del modelo, con widgets de Bootstrap y una
regla de negocio en clean().
"""
from django import forms

from .models import Persona, UnidadResidencial, Residencia


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['numero_documento', 'nombre', 'telefono', 'email']
        widgets = {
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UnidadResidencialForm(forms.ModelForm):
    class Meta:
        model = UnidadResidencial
        # propiedad_horizontal NO va en el formulario: la asigna la vista
        # automáticamente (ver views.py -> obtener_ph_default), porque en
        # esta instancia de Horisoft solo existe una copropiedad.
        fields = ['numero_unidad', 'tipo_unidad']
        widgets = {
            'numero_unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_unidad': forms.Select(attrs={'class': 'form-select'}),
        }


class ResidenciaForm(forms.ModelForm):
    class Meta:
        model = Residencia
        # fecha_inicio NO va: es automática (auto_now_add)
        fields = ['persona', 'unidad', 'rol', 'activo']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-select'}),
            'unidad': forms.Select(attrs={'class': 'form-select'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'activo': 'Residencia activa',
        }

    def clean(self):
        cleaned = super().clean()
        persona = cleaned.get('persona')
        unidad = cleaned.get('unidad')
        rol = cleaned.get('rol')

        if persona and unidad and rol:
            # Regla de negocio 1: no se puede asociar a la misma persona dos
            # veces, activa, con el mismo rol, a la misma unidad.
            duplicados = Residencia.objects.filter(
                persona=persona, unidad=unidad, rol=rol, activo=True,
            )
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                raise forms.ValidationError(
                    'Esta persona ya está asociada a esta unidad con ese mismo rol.'
                )

            # Regla de negocio 2: una unidad no puede tener más de un
            # Propietario activo al mismo tiempo.
            if rol == Residencia.ROL_PROPIETARIO:
                otros_propietarios = Residencia.objects.filter(
                    unidad=unidad, rol=Residencia.ROL_PROPIETARIO, activo=True,
                ).exclude(persona=persona)
                if self.instance.pk:
                    otros_propietarios = otros_propietarios.exclude(pk=self.instance.pk)
                if otros_propietarios.exists():
                    raise forms.ValidationError(
                        'Esta unidad ya tiene un propietario activo registrado.'
                    )
        return cleaned
