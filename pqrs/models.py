from django.db import models

from residentes.models import Residencia


class Pqr(models.Model):
    TIPO_PETICION = 'Petición'
    TIPO_QUEJA = 'Queja'
    TIPO_RECLAMO = 'Reclamo'
    TIPO_SUGERENCIA = 'Sugerencia'
    TIPOS = [
        (TIPO_PETICION, 'Petición'),
        (TIPO_QUEJA, 'Queja'),
        (TIPO_RECLAMO, 'Reclamo'),
        (TIPO_SUGERENCIA, 'Sugerencia'),
    ]

    ESTADO_ABIERTA = 'Abierta'
    ESTADO_EN_PROCESO = 'En proceso'
    ESTADO_CERRADA = 'Cerrada'
    ESTADOS = [
        (ESTADO_ABIERTA, 'Abierta'),
        (ESTADO_EN_PROCESO, 'En proceso'),
        (ESTADO_CERRADA, 'Cerrada'),
    ]

    id_pqr = models.AutoField(primary_key=True)
    residencia = models.ForeignKey(
        Residencia,
        on_delete=models.PROTECT,
        related_name='pqrs',
        verbose_name='Residencia',
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, default=TIPO_PETICION)
    asunto = models.CharField('Asunto', max_length=160)
    descripcion = models.TextField('Descripción')
    respuesta = models.TextField('Respuesta', blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_ABIERTA)
    fecha_creacion = models.DateTimeField('Creada el', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Actualizada el', auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'PQR'
        verbose_name_plural = 'PQRs'

    def __str__(self):
        return f'{self.tipo} - {self.asunto}'
