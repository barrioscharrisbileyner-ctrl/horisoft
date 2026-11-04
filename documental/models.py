from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from residentes.models import PropiedadHorizontal

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024


def document_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'documents/{timezone.now():%Y/%m}/{uuid4().hex}{extension}'


class Documento(models.Model):
    TIPO_REGLAMENTO = 'Reglamento'
    TIPO_ACTA = 'Acta'
    TIPO_CIRCULAR = 'Circular'
    TIPO_OTRO = 'Otro'
    TIPOS = [
        (TIPO_REGLAMENTO, 'Reglamento'),
        (TIPO_ACTA, 'Acta'),
        (TIPO_CIRCULAR, 'Circular'),
        (TIPO_OTRO, 'Otro'),
    ]

    id_documento = models.AutoField(primary_key=True)
    titulo = models.CharField('Título', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, default=TIPO_REGLAMENTO)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='documentos_responsable', verbose_name='Responsable')
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='documentos',
        verbose_name='Propiedad horizontal',
    )
    url_archivo = models.URLField('URL externa del archivo', max_length=500, blank=True)
    archivo = models.FileField(
        'Archivo PDF',
        upload_to=document_upload_path,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    descripcion = models.TextField('Descripción', blank=True)
    fecha_subida = models.DateTimeField('Fecha de subida', auto_now_add=True)

    class Meta:
        ordering = ['-fecha_subida']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.titulo} ({self.tipo})'

    def clean(self):
        super().clean()
        if not self.titulo or not self.titulo.strip():
            raise ValidationError({'titulo': 'El título es obligatorio.'})
        if self.tipo not in dict(self.TIPOS):
            raise ValidationError({'tipo': 'El tipo del documento no es válido.'})
        if not self.url_archivo and not self.archivo:
            raise ValidationError({'archivo': 'Sube un PDF o indica una URL externa segura.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})
        if self.url_archivo and not self.url_archivo.lower().startswith('https://'):
            raise ValidationError({'url_archivo': 'La URL externa debe usar HTTPS.'})
        if self.archivo:
            if self.archivo.size > MAX_DOCUMENT_SIZE:
                raise ValidationError({'archivo': 'El archivo no puede superar 10 MB.'})
            if not getattr(self.archivo, '_committed', False):
                position = self.archivo.tell()
                self.archivo.seek(0)
                signature = self.archivo.read(5)
                self.archivo.seek(position)
                if signature != b'%PDF-':
                    raise ValidationError({'archivo': 'El contenido del archivo no corresponde a un PDF válido.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
