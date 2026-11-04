from django.core.exceptions import ValidationError
from django.db import models

from residentes.models import PropiedadHorizontal


class Proveedor(models.Model):
    ESTADO_ACTIVO = 'Activo'
    ESTADO_INACTIVO = 'Inactivo'
    ESTADOS = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=150)
    nit = models.CharField('NIT', max_length=30)
    servicio = models.CharField('Servicio', max_length=150)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)
    fecha_creacion = models.DateTimeField('Fecha de registro', auto_now_add=True)
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='proveedores',
        verbose_name='Propiedad horizontal',
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        constraints = [
            models.UniqueConstraint(
                fields=['propiedad_horizontal', 'nit'],
                name='proveedor_nit_por_propiedad_unico',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.nit})'

    def clean(self):
        super().clean()
        if not self.nombre or not self.nombre.strip():
            raise ValidationError({'nombre': 'El nombre es obligatorio.'})
        if not self.nit or not self.nit.strip():
            raise ValidationError({'nit': 'El NIT es obligatorio.'})
        if not self.servicio or not self.servicio.strip():
            raise ValidationError({'servicio': 'El servicio es obligatorio.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado no es válido.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
