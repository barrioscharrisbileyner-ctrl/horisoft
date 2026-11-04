from django.contrib.auth import get_user_model
from rest_framework import serializers

from comunicaciones.models import Comunicado
from pqrs.models import Pqr
from reservas.models import Reserva, ZonaComun
from reservas.forms import ReservaForm
from residentes.access import propiedades_accesibles
from residentes.models import Residencia
from usuarios.models import ROL_RESIDENTE
from usuarios.permisos import obtener_rol

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    id_residencia = serializers.SerializerMethodField()
    residencias = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'role',
            'id_residencia', 'residencias',
        ]

    def get_role(self, obj):
        perfil = getattr(obj, 'perfil', None)
        return perfil.rol if perfil else None

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    def get_residencias(self, obj):
        perfil = getattr(obj, 'perfil', None)
        if not perfil or perfil.rol != ROL_RESIDENTE or not perfil.persona_id:
            return []
        return [
            {
                'id_residencia': residencia.pk,
                'unidad': residencia.unidad.numero_unidad,
                'rol': residencia.rol,
            }
            for residencia in Residencia.objects.filter(
                persona_id=perfil.persona_id,
                activo=True,
                unidad__propiedad_horizontal__in=propiedades_accesibles(obj),
            ).select_related('unidad').order_by('unidad__numero_unidad')
        ]

    def get_id_residencia(self, obj):
        residencias = self.get_residencias(obj)
        return residencias[0]['id_residencia'] if residencias else None


class ReservaSerializer(serializers.ModelSerializer):
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    residencia_label = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id_reserva',
            'zona',
            'zona_nombre',
            'residencia',
            'residencia_label',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'observaciones',
            'estado',
        ]
        read_only_fields = ['id_reserva', 'estado', 'zona_nombre', 'residencia_label']

    def get_residencia_label(self, obj):
        return str(obj.residencia)

    def validate(self, attrs):
        request = self.context.get('request')
        if request is None:
            return attrs
        form_data = {
            field: self.initial_data.get(field)
            for field in ('zona', 'residencia', 'fecha', 'hora_inicio', 'hora_fin', 'observaciones')
            if field in self.initial_data
        }
        form = ReservaForm(data=form_data, usuario=request.user)
        if not form.is_valid():
            raise serializers.ValidationError({
                field: [str(error) for error in errors]
                for field, errors in form.errors.items()
            })
        return attrs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None:
            propiedades = propiedades_accesibles(request.user)
            self.fields['zona'].queryset = ZonaComun.objects.filter(
                propiedad_horizontal__in=propiedades,
            )
            self.fields['residencia'].queryset = Residencia.objects.filter(
                unidad__propiedad_horizontal__in=propiedades,
            )


class ZonaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaComun
        fields = ['id_zona', 'nombre', 'descripcion', 'capacidad', 'costo_reserva', 'estado']


class ComunicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicado
        fields = ['id_comunicado', 'titulo', 'contenido', 'dirigido_a', 'fecha_publicacion']


class PQRSerializer(serializers.ModelSerializer):
    residencia_label = serializers.SerializerMethodField()

    class Meta:
        model = Pqr
        fields = [
            'id_pqr',
            'residencia',
            'residencia_label',
            'tipo',
            'asunto',
            'descripcion',
            'respuesta',
            'estado',
            'fecha_creacion',
        ]
        read_only_fields = ['id_pqr', 'residencia_label', 'respuesta', 'estado', 'fecha_creacion']

    def get_residencia_label(self, obj):
        return str(obj.residencia)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None:
            self.fields['residencia'].queryset = Residencia.objects.filter(
                unidad__propiedad_horizontal__in=propiedades_accesibles(request.user),
            )
