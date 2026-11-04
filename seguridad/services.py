from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from residentes.models import PropiedadHorizontal
from .models import Vigilante, Visitante


def crear_vigilante(
    nombre,
    documento,
    propiedad_horizontal,
    telefono='',
    turno=None,
    estado=Vigilante.ESTADO_ACTIVO,
):
    if not nombre or not nombre.strip():
        raise ValueError('El nombre es obligatorio.')
    if not documento or not documento.strip():
        raise ValueError('El documento es obligatorio.')
    if turno is None:
        raise ValueError('El turno es obligatorio.')

    vigilante = Vigilante(
        nombre=nombre.strip(),
        documento=documento.strip(),
        propiedad_horizontal=propiedad_horizontal,
        telefono=telefono.strip() if telefono else '',
        turno=turno,
        estado=estado,
    )
    try:
        vigilante.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    vigilante.save()
    return vigilante


def actualizar_estado_vigilante(vigilante, estado):
    vigilante.estado = estado
    try:
        vigilante.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    vigilante.save(update_fields=['estado'])
    return vigilante


def registrar_ingreso(nombre, documento, residencia, vigilante, motivo='', placa_vehiculo=''):
    if not nombre or not nombre.strip():
        raise ValueError('El nombre del visitante es obligatorio.')
    if not documento or not documento.strip():
        raise ValueError('El documento del visitante es obligatorio.')
    if not residencia:
        raise ValueError('Debe indicar la residencia.')
    if not vigilante:
        raise ValueError('Debe indicar el vigilante que autoriza la visita.')

    if vigilante.estado != Vigilante.ESTADO_ACTIVO:
        raise ValueError(f'El vigilante "{vigilante.nombre}" no está activo en este turno.')

    propiedad_id = residencia.unidad.propiedad_horizontal_id
    with transaction.atomic():
        PropiedadHorizontal.objects.select_for_update().get(pk=propiedad_id)
        if Visitante.objects.filter(
            documento=documento.strip(),
            estado=Visitante.ESTADO_EN_INSTALACION,
            residencia__unidad__propiedad_horizontal_id=propiedad_id,
        ).exists():
            raise ValueError('Este visitante ya tiene un ingreso activo sin salida registrada en esta copropiedad.')

        visita = Visitante(
            nombre=nombre.strip(),
            documento=documento.strip(),
            residencia=residencia,
            vigilante=vigilante,
            motivo=motivo.strip() if motivo else '',
            placa_vehiculo=placa_vehiculo.strip() if placa_vehiculo else '',
        )
        try:
            visita.full_clean()
        except ValidationError as exc:
            raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
        visita.save()
        return visita


def registrar_salida(visita):
    if visita.estado != Visitante.ESTADO_EN_INSTALACION:
        raise ValueError('Esta visita ya tiene una salida registrada.')
    visita.hora_salida = timezone.now()
    visita.estado = Visitante.ESTADO_FINALIZADA
    visita.save(update_fields=['estado', 'hora_salida'])
    return visita
