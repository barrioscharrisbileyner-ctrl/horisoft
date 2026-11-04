from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from residentes.models import PropiedadHorizontal


class Comunicado(models.Model):
    DIRIGIDO_A_TODOS = 'Todos'
    DIRIGIDO_A_ADMINISTRADORES = 'Administradores'
    DIRIGIDO_A_RESIDENTES = 'Residentes'
    DIRIGIDO_A_VIGILANTES = 'Vigilantes'

    DESTINATARIOS = [
        (DIRIGIDO_A_TODOS, 'Todos'),
        (DIRIGIDO_A_ADMINISTRADORES, 'Administradores'),
        (DIRIGIDO_A_RESIDENTES, 'Residentes'),
        (DIRIGIDO_A_VIGILANTES, 'Vigilantes'),
    ]

    ESTADO_PUBLICADO = 'Publicado'
    ESTADO_ARCHIVADO = 'Archivado'
    ESTADOS = [
        (ESTADO_PUBLICADO, 'Publicado'),
        (ESTADO_ARCHIVADO, 'Archivado'),
    ]

    id_comunicado = models.AutoField(primary_key=True)
    titulo = models.CharField('Título', max_length=200)
    contenido = models.TextField('Contenido')
    dirigido_a = models.CharField('Dirigido a', max_length=20, choices=DESTINATARIOS, default=DIRIGIDO_A_TODOS)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comunicados', verbose_name='Autor')
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='comunicados',
        verbose_name='Propiedad horizontal',
    )
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_PUBLICADO)
    fecha_publicacion = models.DateTimeField('Publicación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Actualización', auto_now=True)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'

    def __str__(self):
        return f'{self.titulo} ({self.dirigido_a})'

    def clean(self):
        super().clean()
        if not self.titulo or not self.titulo.strip():
            raise ValidationError({'titulo': 'El título es obligatorio.'})
        if not self.contenido or not self.contenido.strip():
            raise ValidationError({'contenido': 'El contenido es obligatorio.'})
        if self.dirigido_a not in dict(self.DESTINATARIOS):
            raise ValidationError({'dirigido_a': 'El destinatario no es válido.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
