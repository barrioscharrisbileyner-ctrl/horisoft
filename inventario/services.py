from django.core.exceptions import ValidationError

from .models import ItemInventario


def crear_item(
    nombre,
    categoria,
    cantidad,
    propiedad_horizontal,
    ubicacion='',
    estado=ItemInventario.ESTADO_BUENO,
    cantidad_minima=0,
):
    if not nombre or not nombre.strip():
        raise ValueError('El nombre es obligatorio.')
    if not categoria or not categoria.strip():
        raise ValueError('La categoría es obligatoria.')
    if cantidad is None or cantidad < 0:
        raise ValueError('La cantidad debe ser un número mayor o igual a cero.')

    item = ItemInventario(
        nombre=nombre.strip(),
        categoria=categoria.strip(),
        cantidad=int(cantidad),
        cantidad_minima=int(cantidad_minima),
        propiedad_horizontal=propiedad_horizontal,
        ubicacion=ubicacion.strip() if ubicacion else '',
        estado=estado,
    )
    try:
        item.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    item.save()
    return item


def actualizar_cantidad(item, cantidad):
    if cantidad is None or cantidad < 0:
        raise ValueError('La cantidad debe ser un número mayor o igual a cero.')
    item.cantidad = int(cantidad)
    item.save(update_fields=['cantidad'])
    return item


def actualizar_estado(item, estado):
    item.estado = estado
    try:
        item.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    item.save(update_fields=['estado'])
    return item
