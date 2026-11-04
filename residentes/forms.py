"""
Formularios del módulo Residentes y Unidades.

Igual que en la guía TallerExpress: usamos ModelForm para que el
formulario se arme a partir del modelo, con widgets de Bootstrap y una
regla de negocio en clean().
"""
from django import forms

from .access import propiedades_accesibles
from .models import Persona, UnidadResidencial, Residencia


class PropiedadScopedFormMixin:
    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
        if 'propiedad_horizontal' in self.fields:
            queryset = propiedades_accesibles(usuario) if usuario is not None else \
                self.fields['propiedad_horizontal'].queryset.model.objects.all()
            self.fields['propiedad_horizontal'].queryset = queryset
            self.fields['propiedad_horizontal'].required = False
            if not self.is_bound and not self.instance.pk and queryset.count() == 1:
                self.fields['propiedad_horizontal'].initial = queryset.first().pk

    def clean(self):
        cleaned_data = super().clean()
        if 'propiedad_horizontal' in self.fields and not cleaned_data.get('propiedad_horizontal'):
            propiedades = list(self.fields['propiedad_horizontal'].queryset[:2])
            if len(propiedades) == 1:
                cleaned_data['propiedad_horizontal'] = propiedades[0]
            else:
                self.add_error('propiedad_horizontal', 'Selecciona una copropiedad autorizada.')
        return cleaned_data


class PersonaForm(forms.ModelForm):
    numero_documento = forms.CharField(
        required=True,
        error_messages={'required': 'Este campo es obligatorio.'},
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Persona
        fields = ['numero_documento', 'nombre', 'telefono', 'email', 'propiedades']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'propiedades': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        propiedades = propiedades_accesibles(usuario) if usuario is not None else \
            self.fields['propiedades'].queryset.model.objects.all()
        self.fields['propiedades'].queryset = propiedades
        self.fields['propiedades'].required = False
        if not self.is_bound and not self.instance.pk and propiedades.count() == 1:
            self.fields['propiedades'].initial = [propiedades.first().pk]

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('propiedades'):
            propiedades = list(self.fields['propiedades'].queryset[:2])
            if len(propiedades) == 1:
                cleaned['propiedades'] = propiedades
            else:
                self.add_error('propiedades', 'Selecciona al menos una copropiedad autorizada.')
        return cleaned

    def save(self, commit=True):
        instance = self.instance
        retained = set()
        if instance.pk:
            allowed = self.fields['propiedades'].queryset.values_list('pk', flat=True)
            retained = set(instance.propiedades.exclude(pk__in=allowed).values_list('pk', flat=True))

        persona = super().save(commit=commit)
        if commit:
            if retained:
                persona.propiedades.add(*retained)
        else:
            save_m2m = self.save_m2m

            def save_m2m_with_retained():
                save_m2m()
                if retained:
                    persona.propiedades.add(*retained)

            self.save_m2m = save_m2m_with_retained
        return persona


class UnidadResidencialForm(PropiedadScopedFormMixin, forms.ModelForm):
    class Meta:
        model = UnidadResidencial
        fields = ['numero_unidad', 'tipo_unidad', 'propiedad_horizontal']
        widgets = {
            'numero_unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_unidad': forms.Select(attrs={'class': 'form-select'}),
            'propiedad_horizontal': forms.Select(attrs={'class': 'form-select'}),
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

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        propiedades = propiedades_accesibles(usuario) if usuario is not None else \
            self.fields['unidad'].queryset.model._meta.get_field('propiedad_horizontal').remote_field.model.objects.all()
        self.fields['unidad'].queryset = UnidadResidencial.objects.filter(
            propiedad_horizontal__in=propiedades,
        ).select_related('propiedad_horizontal')
        self.fields['persona'].queryset = Persona.objects.filter(
            propiedades__in=propiedades,
        ).distinct()

    def clean(self):
        cleaned = super().clean()
        persona = cleaned.get('persona')
        unidad = cleaned.get('unidad')
        rol = cleaned.get('rol')

        if persona and unidad and rol:
            if unidad.propiedad_horizontal_id not in persona.propiedades.values_list('pk', flat=True):
                raise forms.ValidationError('La persona no está asociada a esta copropiedad.')
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
