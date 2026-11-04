from django.core.exceptions import ValidationError

from residentes.access import propiedades_accesibles
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from .models import Comunicado


def crear_comunicado(titulo, contenido, dirigido_a, autor, propiedad_horizontal):
    if not titulo or not titulo.strip():
        raise ValueError('El título es obligatorio.')
    if not contenido or not contenido.strip():
        raise ValueError('El contenido es obligatorio.')
    if not dirigido_a:
        raise ValueError('Debe indicar un destinatario válido.')
    if not autor:
        raise ValueError('Debe indicar el autor del comunicado.')

    comunicado = Comunicado(
        titulo=titulo.strip(),
        contenido=contenido.strip(),
        dirigido_a=dirigido_a,
        autor=autor,
        propiedad_horizontal=propiedad_horizontal,
    )
    try:
        comunicado.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    comunicado.save()
    return comunicado


def archivar_comunicado(comunicado):
    if comunicado.estado == Comunicado.ESTADO_ARCHIVADO:
        raise ValueError('El comunicado ya está archivado.')
    comunicado.estado = Comunicado.ESTADO_ARCHIVADO
    comunicado.save(update_fields=['estado', 'fecha_actualizacion'])
    return comunicado


def listar_comunicados_para_usuario(user):
    if not user or not user.is_authenticated:
        return Comunicado.objects.none()
    rol = obtener_rol(user)
    qs = Comunicado.objects.filter(
        estado=Comunicado.ESTADO_PUBLICADO,
        propiedad_horizontal__in=propiedades_accesibles(user),
    )
    if rol in {ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO}:
        return qs
    if rol == ROL_RESIDENTE:
        return qs.filter(dirigido_a__in=[Comunicado.DIRIGIDO_A_TODOS, Comunicado.DIRIGIDO_A_RESIDENTES])
    if rol == ROL_VIGILANTE:
        return qs.filter(dirigido_a__in=[Comunicado.DIRIGIDO_A_TODOS, Comunicado.DIRIGIDO_A_VIGILANTES])
    return qs.none()
