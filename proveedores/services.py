from django.core.exceptions import ValidationError

from .models import Proveedor


def crear_proveedor(
    nombre,
    nit,
    servicio,
    propiedad_horizontal,
    telefono='',
    estado=Proveedor.ESTADO_ACTIVO,
):
    if not nombre or not nombre.strip():
        raise ValueError('El nombre es obligatorio.')
    if not nit or not nit.strip():
        raise ValueError('El NIT es obligatorio.')
    if not servicio or not servicio.strip():
        raise ValueError('El servicio es obligatorio.')

    proveedor = Proveedor(
        nombre=nombre.strip(),
        nit=nit.strip(),
        servicio=servicio.strip(),
        propiedad_horizontal=propiedad_horizontal,
        telefono=telefono.strip() if telefono else '',
        estado=estado,
    )
    try:
        proveedor.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    proveedor.save()
    return proveedor


def actualizar_estado_proveedor(proveedor, estado):
    proveedor.estado = estado
    try:
        proveedor.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    proveedor.save(update_fields=['estado'])
    return proveedor
