from django.core.exceptions import ValidationError
from django.db import models

from residentes.models import PropiedadHorizontal


class ItemInventario(models.Model):
    ESTADO_BUENO = 'Bueno'
    ESTADO_REGULAR = 'Regular'
    ESTADO_MALO = 'Malo'
    ESTADO_FUERA_DE_SERVICIO = 'Fuera de servicio'
    ESTADOS = [
        (ESTADO_BUENO, 'Bueno'),
        (ESTADO_REGULAR, 'Regular'),
        (ESTADO_MALO, 'Malo'),
        (ESTADO_FUERA_DE_SERVICIO, 'Fuera de servicio'),
    ]

    id_item = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=150)
    categoria = models.CharField('Categoría', max_length=100)
    cantidad = models.PositiveIntegerField('Cantidad', default=0)
    cantidad_minima = models.PositiveIntegerField('Cantidad mínima', default=0)
    ubicacion = models.CharField('Ubicación', max_length=200, blank=True)
    estado = models.CharField('Estado', max_length=30, choices=ESTADOS, default=ESTADO_BUENO)
    fecha_creacion = models.DateTimeField('Fecha de registro', auto_now_add=True)
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='items_inventario',
        verbose_name='Propiedad horizontal',
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ítem de inventario'
        verbose_name_plural = 'Inventario'

    def __str__(self):
        return f'{self.nombre} ({self.cantidad})'

    def clean(self):
        super().clean()
        if not self.nombre or not self.nombre.strip():
            raise ValidationError({'nombre': 'El nombre es obligatorio.'})
        if not self.categoria or not self.categoria.strip():
            raise ValidationError({'categoria': 'La categoría es obligatoria.'})
        if self.cantidad < 0:
            raise ValidationError({'cantidad': 'La cantidad no puede ser negativa.'})
        if self.cantidad_minima < 0:
            raise ValidationError({'cantidad_minima': 'La cantidad mínima no puede ser negativa.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado no es válido.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
