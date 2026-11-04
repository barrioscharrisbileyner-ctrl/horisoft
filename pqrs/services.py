from django.core.exceptions import ValidationError

from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.permisos import obtener_rol

TIPOS_VALIDOS = ['Petición', 'Queja', 'Reclamo', 'Sugerencia']
ESTADOS_VALIDOS = ['Abierta', 'En proceso', 'Cerrada']


def validar_pqr_data(datos):
    campos = ['residencia', 'tipo', 'asunto', 'descripcion']
    for campo in campos:
        if not datos.get(campo):
            raise ValidationError(f'El campo {campo} es obligatorio.')
    if datos['tipo'] not in TIPOS_VALIDOS:
        raise ValidationError(f'Tipo inválido. Use uno de: {TIPOS_VALIDOS}.')
    return True


def responder_pqr(pqr, respuesta, usuario):
    if not respuesta or not respuesta.strip():
        raise ValidationError('La respuesta no puede estar vacía.')
    if obtener_rol(usuario) not in {ROL_ADMINISTRADOR}:
        raise PermissionError('Solo un administrador puede responder la PQR.')
    if pqr.estado == 'Cerrada':
        raise ValidationError('No se puede responder una PQR ya cerrada.')
    pqr.respuesta = respuesta.strip()
    pqr.estado = 'Cerrada'
    pqr.save(update_fields=['respuesta', 'estado'])
    return pqr
