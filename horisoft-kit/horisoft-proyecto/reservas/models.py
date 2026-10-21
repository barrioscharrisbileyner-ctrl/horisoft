"""
Modelos del módulo "Zonas Comunes y Reservas" (RQ03) de Horisoft.

Respetan las entidades ZONA_COMUN y RESERVA del MER (GA4-220501095-AA1-EV01).
La reserva se asocia a una Residencia del módulo Residentes (quién reserva y
desde qué unidad), no a un número suelto como en el prototipo Express.
"""
from django.core.validators import MinValueValidator
from django.db import models

from residentes.models import Residencia


class ZonaComun(models.Model):
    """Espacio compartido que se puede reservar: salón social, piscina, cancha..."""

    ESTADO_DISPONIBLE = 'Disponible'
    ESTADO_MANTENIMIENTO = 'Mantenimiento'
    ESTADO_INACTIVA = 'Inactiva'
    ESTADO_CHOICES = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_MANTENIMIENTO, 'En mantenimiento'),
        (ESTADO_INACTIVA, 'Inactiva'),
    ]

    id_zona = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)
    capacidad = models.PositiveIntegerField('Capacidad (personas)', validators=[MinValueValidator(1)])
    costo_reserva = models.PositiveIntegerField('Costo de la reserva (COP)', default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default=ESTADO_DISPONIBLE)

    class Meta:
        verbose_name = 'Zona común'
        verbose_name_plural = 'Zonas comunes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    """Uso de una zona común por una residencia, en una fecha y franja horaria."""

    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_CONFIRMADA = 'Confirmada'
    ESTADO_CANCELADA = 'Cancelada'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    id_reserva = models.AutoField(primary_key=True)
    # PROTECT: no se borra una zona ni una residencia que tengan reservas
    # (se conserva el historial; la zona se puede marcar "Inactiva").
    zona = models.ForeignKey(
        ZonaComun, on_delete=models.PROTECT,
        db_column='id_zona', related_name='reservas', verbose_name='Zona común',
    )
    residencia = models.ForeignKey(
        Residencia, on_delete=models.PROTECT,
        db_column='id_residencia', related_name='reservas', verbose_name='Residencia',
    )
    fecha = models.DateField('Fecha')
    hora_inicio = models.TimeField('Hora de inicio')
    hora_fin = models.TimeField('Hora de fin')
    observaciones = models.CharField('Observaciones', max_length=255, blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    creada = models.DateTimeField('Creada el', auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-hora_inicio']
        indexes = [models.Index(fields=['zona', 'fecha'], name='reserva_zona_fecha_idx')]

    def __str__(self):
        return f'{self.zona.nombre} · {self.fecha} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}'

    @property
    def esta_cancelada(self):
        return self.estado == self.ESTADO_CANCELADA

    @classmethod
    def hay_cruce(cls, zona, fecha, hora_inicio, hora_fin, excluir_pk=None):
        """
        ¿Existe otra reserva activa (no cancelada) de la misma zona y fecha cuyo
        horario se solape con [hora_inicio, hora_fin)? Dos reservas contiguas
        (una termina cuando la otra empieza) NO se consideran cruce.
        """
        cruces = cls.objects.filter(
            zona=zona, fecha=fecha,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio,
        ).exclude(estado=cls.ESTADO_CANCELADA)
        if excluir_pk:
            cruces = cruces.exclude(pk=excluir_pk)
        return cruces.exists()
