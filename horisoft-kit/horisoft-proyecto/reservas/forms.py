"""
Formularios de Zonas Comunes y Reservas.

Las reglas de negocio viven en ReservaForm.clean() (misma práctica que
ResidenciaForm en el módulo Residentes) y equivalen a las del prototipo Express:

  1. La zona común debe estar "Disponible".
  2. La fecha no puede ser anterior a hoy (hoy = fecha LOCAL de Colombia).
  3. La hora de fin debe ser posterior a la de inicio.
  4. No puede haber otra reserva activa de la misma zona con horario cruzado.
  5. (Nueva) Un Residente solo puede reservar a nombre de SUS residencias activas.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from residentes.models import Residencia
from usuarios.models import ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from .models import Reserva, ZonaComun


class ZonaComunForm(forms.ModelForm):
    class Meta:
        model = ZonaComun
        fields = ['nombre', 'descripcion', 'capacidad', 'costo_reserva', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'costo_reserva': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # El estado no se elige al crear: nace "Pendiente" y se cambia con las
        # acciones Confirmar / Cancelar de la lista.
        fields = ['zona', 'residencia', 'fecha', 'hora_inicio', 'hora_fin', 'observaciones']
        widgets = {
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'residencia': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        residencias = Residencia.objects.filter(activo=True).select_related('persona', 'unidad')
        if usuario is not None and obtener_rol(usuario) == ROL_RESIDENTE:
            perfil = getattr(usuario, 'perfil', None)
            persona = perfil.persona if perfil else None
            residencias = residencias.filter(persona=persona) if persona else residencias.none()
        self.fields['residencia'].queryset = residencias
        if not self.is_bound and not self.instance.pk and residencias.count() == 1:
            self.fields['residencia'].initial = residencias.first().pk
        self.fields['residencia'].label_from_instance = (
            lambda r: f'Unidad {r.unidad.numero_unidad} · {r.persona.nombre} ({r.rol})')

        # Se muestran todas las zonas con su estado: así el mensaje de la regla 1
        # es claro si alguien elige una que no está disponible.
        self.fields['zona'].label_from_instance = (
            lambda z: z.nombre if z.estado == ZonaComun.ESTADO_DISPONIBLE else f'{z.nombre} ({z.estado})')

    def clean(self):
        datos = super().clean()
        zona = datos.get('zona')
        fecha = datos.get('fecha')
        inicio = datos.get('hora_inicio')
        fin = datos.get('hora_fin')

        # Regla 1: zona disponible
        if zona and zona.estado != ZonaComun.ESTADO_DISPONIBLE:
            self.add_error(
                'zona', f'La zona "{zona.nombre}" no está disponible actualmente (estado: {zona.estado}).')

        # Regla 2: no reservar en el pasado. Se compara con la fecha LOCAL (Bogotá);
        # al editar una reserva antigua solo se exige si se cambió la fecha.
        if fecha and fecha < timezone.localdate() and (not self.instance.pk or 'fecha' in self.changed_data):
            self.add_error('fecha', 'No se pueden crear reservas en fechas pasadas.')

        # Regla 3: hora de fin posterior a la de inicio
        horas_validas = bool(inicio and fin and fin > inicio)
        if inicio and fin and not horas_validas:
            self.add_error('hora_fin', 'La hora de fin debe ser posterior a la hora de inicio.')

        # Regla 4: sin cruce de horario (solo si lo anterior está bien)
        if zona and fecha and horas_validas and not self.errors:
            if Reserva.hay_cruce(zona, fecha, inicio, fin, excluir_pk=self.instance.pk):
                raise ValidationError('Ya existe una reserva activa para esa zona en ese horario.')
        return datos
