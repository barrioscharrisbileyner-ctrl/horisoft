from django.core.exceptions import ValidationError

from .models import Documento


def crear_documento(
    titulo,
    tipo,
    responsable,
    propiedad_horizontal,
    url_archivo='',
    descripcion='',
    archivo=None,
):
    if not titulo or not titulo.strip():
        raise ValueError('El título es obligatorio.')
    if not tipo:
        raise ValueError('Debe indicar el tipo del documento.')
    if not responsable:
        raise ValueError('Debe indicar el responsable.')
    if not url_archivo and not archivo:
        raise ValueError('Sube un PDF o indica una URL externa segura.')

    documento = Documento(
        titulo=titulo.strip(),
        tipo=tipo,
        responsable=responsable,
        propiedad_horizontal=propiedad_horizontal,
        url_archivo=url_archivo.strip() if url_archivo else '',
        archivo=archivo,
        descripcion=descripcion.strip() if descripcion else '',
    )
    try:
        documento.full_clean()
    except ValidationError as exc:
        raise ValueError('; '.join(msg for messages in exc.message_dict.values() for msg in messages)) from exc
    documento.save()
    return documento
