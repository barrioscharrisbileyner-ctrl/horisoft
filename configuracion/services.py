from django.core.exceptions import ValidationError

from .models import ParametroConfiguracion


def crear_parametro(clave, valor, propiedad_horizontal, descripcion=''):
    if not clave or not clave.strip():
        raise ValueError('La clave es obligatoria.')
    if valor is None or str(valor).strip() == '':
        raise ValueError('El valor es obligatorio.')

    parametro = ParametroConfiguracion(
        clave=clave.strip(),
        valor=str(valor).strip(),
        propiedad_horizontal=propiedad_horizontal,
        descripcion=descripcion.strip() if descripcion else '',
    )
    try:
        parametro.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for values in exc.message_dict.values() for msg in values)) from exc
    parametro.save()
    return parametro


def actualizar_valor_parametro(parametro, valor, descripcion=None):
    if valor is None or str(valor).strip() == '':
        raise ValueError('El valor es obligatorio.')
    parametro.valor = str(valor).strip()
    if descripcion is not None:
        parametro.descripcion = descripcion.strip() if descripcion else ''
    try:
        parametro.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for values in exc.message_dict.values() for msg in values)) from exc
    parametro.save(update_fields=['valor', 'descripcion', 'fecha_actualizacion'])
    return parametro
