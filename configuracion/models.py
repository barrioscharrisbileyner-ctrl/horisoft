from django.core.exceptions import ValidationError
from django.db import models

from residentes.models import PropiedadHorizontal


class ParametroConfiguracion(models.Model):
    clave = models.CharField('Clave', max_length=100)
    valor = models.TextField('Valor')
    descripcion = models.TextField('Descripción', blank=True)
    fecha_actualizacion = models.DateTimeField('Última actualización', auto_now=True)
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='parametros_configuracion',
        verbose_name='Propiedad horizontal',
    )

    class Meta:
        ordering = ['clave']
        verbose_name = 'Parámetro de configuración'
        verbose_name_plural = 'Parámetros de configuración'
        constraints = [
            models.UniqueConstraint(
                fields=['propiedad_horizontal', 'clave'],
                name='parametro_clave_por_propiedad_unico',
            ),
        ]

    def __str__(self):
        return self.clave

    def clean(self):
        super().clean()
        if not self.clave or not self.clave.strip():
            raise ValidationError({'clave': 'La clave es obligatoria.'})
        if self.valor is None or str(self.valor).strip() == '':
            raise ValidationError({'valor': 'El valor es obligatorio.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
