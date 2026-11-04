import re

from django.core.exceptions import ValidationError
from django.db import models

from residentes.models import PropiedadHorizontal, Residencia


class Vigilante(models.Model):
    TURNO_DIURNO = 'Diurno'
    TURNO_NOCTURNO = 'Nocturno'
    TURNO_MIXTO = 'Mixto'
    TURNOS = [
        (TURNO_DIURNO, 'Diurno'),
        (TURNO_NOCTURNO, 'Nocturno'),
        (TURNO_MIXTO, 'Mixto'),
    ]

    ESTADO_ACTIVO = 'Activo'
    ESTADO_INACTIVO = 'Inactivo'
    ESTADOS = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    id_vigilante = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=150)
    documento = models.CharField('Documento', max_length=30)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    turno = models.CharField('Turno', max_length=20, choices=TURNOS, default=TURNO_DIURNO)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)
    fecha_creacion = models.DateTimeField('Fecha de registro', auto_now_add=True)
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal,
        on_delete=models.PROTECT,
        related_name='vigilantes',
        verbose_name='Propiedad horizontal',
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Vigilante'
        verbose_name_plural = 'Vigilantes'
        constraints = [
            models.UniqueConstraint(
                fields=['propiedad_horizontal', 'documento'],
                name='vigilante_documento_por_propiedad_unico',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.documento})'

    def clean(self):
        super().clean()
        if not self.nombre or not self.nombre.strip():
            raise ValidationError({'nombre': 'El nombre es obligatorio.'})
        if self.turno not in dict(self.TURNOS):
            raise ValidationError({'turno': 'El turno no es válido.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado no es válido.'})
        if self.propiedad_horizontal_id is None:
            raise ValidationError({'propiedad_horizontal': 'La copropiedad es obligatoria.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Visitante(models.Model):
    ESTADO_EN_INSTALACION = 'En instalación'
    ESTADO_FINALIZADA = 'Finalizada'
    ESTADOS = [
        (ESTADO_EN_INSTALACION, 'En instalación'),
        (ESTADO_FINALIZADA, 'Finalizada'),
    ]

    id_visita = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=150)
    documento = models.CharField('Documento', max_length=30)
    residencia = models.ForeignKey(Residencia, on_delete=models.PROTECT, related_name='visitas', verbose_name='Residencia')
    vigilante = models.ForeignKey(Vigilante, on_delete=models.PROTECT, related_name='visitas_autorizadas', verbose_name='Vigilante')
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    placa_vehiculo = models.CharField('Placa del vehículo', max_length=20, blank=True)
    fecha = models.DateField('Fecha', auto_now_add=True)
    hora_ingreso = models.DateTimeField('Hora de ingreso', auto_now_add=True)
    hora_salida = models.DateTimeField('Hora de salida', null=True, blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_EN_INSTALACION)

    class Meta:
        ordering = ['-hora_ingreso']
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'

    def __str__(self):
        return f'{self.nombre} ({self.documento})'

    def clean(self):
        super().clean()
        if not self.nombre or not self.nombre.strip():
            raise ValidationError({'nombre': 'El nombre es obligatorio.'})
        if not self.documento or not self.documento.strip():
            raise ValidationError({'documento': 'El documento es obligatorio.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado de la visita no es válido.'})
        if (
            self.residencia_id
            and self.vigilante_id
            and self.residencia.unidad.propiedad_horizontal_id != self.vigilante.propiedad_horizontal_id
        ):
            raise ValidationError('El vigilante y la residencia deben pertenecer a la misma copropiedad.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Camara(models.Model):
    ESTADO_ACTIVA = 'Activa'
    ESTADO_INACTIVA = 'Inactiva'
    ESTADO_MANTENIMIENTO = 'Mantenimiento'
    ESTADOS = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_INACTIVA, 'Inactiva'),
        (ESTADO_MANTENIMIENTO, 'En mantenimiento'),
    ]

    ubicacion = models.CharField('Ubicación', max_length=150)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_ACTIVA)
    zona = models.ForeignKey(
        'reservas.ZonaComun',
        on_delete=models.PROTECT,
        related_name='camaras',
        verbose_name='Zona común',
    )

    class Meta:
        ordering = ['ubicacion']
        verbose_name = 'Cámara'
        verbose_name_plural = 'Cámaras'

    def __str__(self):
        return f'Cámara en {self.ubicacion}'

    def clean(self):
        super().clean()
        if not self.ubicacion or not self.ubicacion.strip():
            raise ValidationError({'ubicacion': 'La ubicación de la cámara es obligatoria.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado de la cámara no es válido.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Vehiculo(models.Model):
    TIPO_AUTOMOVIL = 'Automóvil'
    TIPO_MOTOCICLETA = 'Motocicleta'
    TIPO_OTRO = 'Otro'
    TIPOS = [
        (TIPO_AUTOMOVIL, 'Automóvil'),
        (TIPO_MOTOCICLETA, 'Motocicleta'),
        (TIPO_OTRO, 'Otro'),
    ]

    placa = models.CharField('Placa', max_length=6, unique=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS)
    residencia = models.ForeignKey(
        Residencia,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name='Residencia',
    )

    class Meta:
        ordering = ['placa']
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f'{self.placa} ({self.tipo})'

    def clean(self):
        super().clean()
        if self.placa:
            self.placa = self.placa.replace(' ', '').upper()
            if not re.fullmatch(r'(?:[A-Z]{3}\d{3}|[A-Z]{3}\d{2}[A-Z])', self.placa):
                raise ValidationError({'placa': 'La placa debe tener un formato colombiano válido.'})
        if self.tipo not in dict(self.TIPOS):
            raise ValidationError({'tipo': 'El tipo de vehículo no es válido.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
