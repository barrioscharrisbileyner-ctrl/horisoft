"""
Modelos del módulo "Residentes y Unidades" de Horisoft.

Estos modelos respetan las entidades y llaves definidas en el Modelo
Entidad-Relación (MER) de Horisoft (evidencia GA4-220501095-AA1-EV01):
PROPIEDAD_HORIZONTAL, PERSONA, UNIDAD_RESIDENCIAL y RESIDENCIA.

Nota: a Persona se le agregaron 'telefono' y 'email' (no estaban en el MER
original) porque el caso de uso RQ05 "Gestionar Información de Residentes y
Unidades" exige capturar datos de contacto del residente. A Residencia se
le agregaron 'fecha_inicio' y 'activo' para poder controlar el historial de
asociaciones.
"""
from django.db import models


class PropiedadHorizontal(models.Model):
    """La copropiedad administrada por Horisoft. Normalmente existe un solo
    registro (la copropiedad donde corre esta instancia del sistema)."""
    id_ph = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre de la copropiedad', max_length=150)
    nit = models.CharField('NIT', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Propiedad Horizontal'
        verbose_name_plural = 'Propiedades Horizontales'

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    """Cualquier persona natural relacionada con la copropiedad: residente,
    propietario, arrendatario, etc. (entidad PERSONA del MER)."""
    id_persona = models.AutoField(primary_key=True)
    numero_documento = models.CharField('Número de documento', max_length=20, unique=True)
    nombre = models.CharField('Nombre completo', max_length=150)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Correo electrónico', blank=True)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.numero_documento})'


class UnidadResidencial(models.Model):
    """Una unidad de propiedad: apartamento, casa o local
    (entidad UNIDAD_RESIDENCIAL del MER)."""

    TIPO_APARTAMENTO = 'Apartamento'
    TIPO_CASA = 'Casa'
    TIPO_LOCAL = 'Local'
    TIPO_CHOICES = [
        (TIPO_APARTAMENTO, 'Apartamento'),
        (TIPO_CASA, 'Casa'),
        (TIPO_LOCAL, 'Local'),
    ]

    id_unidad = models.AutoField(primary_key=True)
    numero_unidad = models.CharField('Número de unidad (Apto/Casa)', max_length=20)
    tipo_unidad = models.CharField('Tipo de unidad', max_length=20, choices=TIPO_CHOICES, default=TIPO_APARTAMENTO)
    propiedad_horizontal = models.ForeignKey(
        PropiedadHorizontal, on_delete=models.CASCADE,
        db_column='id_ph', related_name='unidades', verbose_name='Propiedad horizontal',
    )

    class Meta:
        verbose_name = 'Unidad Residencial'
        verbose_name_plural = 'Unidades Residenciales'
        ordering = ['numero_unidad']
        unique_together = [('numero_unidad', 'propiedad_horizontal')]

    def __str__(self):
        return f'{self.numero_unidad} ({self.tipo_unidad})'


class Residencia(models.Model):
    """Asocia una Persona con una Unidad Residencial bajo un rol determinado
    (entidad RESIDENCIA del MER). Es el "módulo central" de esta entrega,
    equivalente a OrdenServicio en el ejemplo TallerExpress: relaciona dos
    catálogos (Persona y UnidadResidencial) y aplica una regla de negocio."""

    ROL_PROPIETARIO = 'Propietario'
    ROL_ARRENDATARIO = 'Arrendatario'
    ROL_FAMILIAR = 'Familiar'
    ROL_CHOICES = [
        (ROL_PROPIETARIO, 'Propietario'),
        (ROL_ARRENDATARIO, 'Arrendatario / Inquilino'),
        (ROL_FAMILIAR, 'Familiar / Conviviente'),
    ]

    id_residencia = models.AutoField(primary_key=True)
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE,
        db_column='id_persona', related_name='residencias', verbose_name='Persona',
    )
    unidad = models.ForeignKey(
        UnidadResidencial, on_delete=models.CASCADE,
        db_column='id_unidad', related_name='residencias', verbose_name='Unidad residencial',
    )
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default=ROL_ARRENDATARIO)
    fecha_inicio = models.DateField('Fecha de inicio', auto_now_add=True)
    activo = models.BooleanField('Residencia activa', default=True)

    class Meta:
        verbose_name = 'Residencia'
        verbose_name_plural = 'Residencias'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.persona.nombre} -> {self.unidad.numero_unidad} ({self.rol})'
