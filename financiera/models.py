from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.core.validators import MinValueValidator

from residentes.models import Residencia

User = get_user_model()


class CuentaCobro(models.Model):
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_PAGADA = 'Pagada'
    ESTADO_VENCIDA = 'Vencida'
    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PAGADA, 'Pagada'),
        (ESTADO_VENCIDA, 'Vencida'),
    ]

    id_cuenta = models.AutoField(primary_key=True)
    residencia = models.ForeignKey(
        Residencia,
        on_delete=models.PROTECT,
        related_name='cuentas_cobro',
        verbose_name='Residencia',
    )
    concepto = models.CharField('Concepto', max_length=200)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    valor_pagado = models.DecimalField('Valor pagado', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    fecha_vencimiento = models.DateField('Fecha de vencimiento')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    activo = models.BooleanField('Activa', default=True)
    fecha_creacion = models.DateTimeField('Creada el', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Actualizada el', auto_now=True)

    class Meta:
        ordering = ['-fecha_vencimiento']
        verbose_name = 'Cuenta de cobro'
        verbose_name_plural = 'Cuentas de cobro'

    def __str__(self):
        return f'{self.concepto} - {self.residencia}'

    @property
    def saldo_pendiente(self):
        return self.valor - self.valor_pagado

    def clean(self):
        super().clean()
        if self.valor <= 0:
            raise ValidationError('El valor de la cuenta debe ser mayor que cero.')
        if self.valor_pagado < 0:
            raise ValidationError('El valor pagado no puede ser negativo.')
        if self.valor_pagado > self.valor:
            raise ValidationError('El valor pagado no puede exceder el valor de la cuenta.')

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.valor_pagado >= self.valor:
            self.estado = self.ESTADO_PAGADA
        elif self.estado == self.ESTADO_PAGADA and self.valor_pagado < self.valor:
            self.estado = self.ESTADO_PENDIENTE
        super().save(*args, **kwargs)


class Pago(models.Model):
    METODO_EFECTIVO = 'Efectivo'
    METODO_TRANSFERENCIA = 'Transferencia'
    METODO_TARJETA = 'Tarjeta'
    METODO_PSE = 'PSE'
    METODOS = [
        (METODO_EFECTIVO, 'Efectivo'),
        (METODO_TRANSFERENCIA, 'Transferencia'),
        (METODO_TARJETA, 'Tarjeta'),
        (METODO_PSE, 'PSE'),
    ]

    id_pago = models.AutoField(primary_key=True)
    cuenta = models.ForeignKey(CuentaCobro, on_delete=models.PROTECT, related_name='pagos', verbose_name='Cuenta')
    valor_pagado = models.DecimalField('Valor pagado', max_digits=12, decimal_places=2)
    metodo_pago = models.CharField('Método de pago', max_length=20, choices=METODOS)
    referencia = models.CharField('Referencia', max_length=100, blank=True, default='')
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos_registrados', verbose_name='Registrado por')
    fecha_pago = models.DateTimeField('Fecha de pago', auto_now_add=True)

    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'{self.cuenta.concepto}: {self.valor_pagado}'

    def clean(self):
        super().clean()
        if self.valor_pagado <= 0:
            raise ValidationError('El valor pagado debe ser mayor que cero.')
        saldo = self.cuenta.saldo_pendiente
        if self.valor_pagado > saldo:
            raise ValidationError('El valor pagado excede el saldo pendiente de la cuenta.')

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('Los pagos son inmutables; no se pueden editar ni borrar.')
        self.full_clean()
        with transaction.atomic():
            cuenta = CuentaCobro.objects.select_for_update().get(pk=self.cuenta_id)
            saldo = cuenta.valor - cuenta.valor_pagado
            if self.valor_pagado > saldo:
                raise ValidationError('El valor pagado excede el saldo pendiente de la cuenta.')
            super().save(*args, **kwargs)
            cuenta.valor_pagado = cuenta.valor_pagado + self.valor_pagado
            if cuenta.valor_pagado >= cuenta.valor:
                cuenta.estado = cuenta.ESTADO_PAGADA
            elif cuenta.estado != cuenta.ESTADO_VENCIDA:
                cuenta.estado = cuenta.ESTADO_PENDIENTE
            cuenta.save(update_fields=['valor_pagado', 'estado'])
            if cuenta.estado == CuentaCobro.ESTADO_PAGADA:
                ConvenioPago.objects.filter(
                    cuenta=cuenta,
                    estado__in=[ConvenioPago.ESTADO_PENDIENTE, ConvenioPago.ESTADO_APROBADO],
                ).update(estado=ConvenioPago.ESTADO_CUMPLIDO)

    def delete(self, *args, **kwargs):
        raise ValidationError('Los pagos son inmutables; no se pueden editar ni borrar.')


class Multa(models.Model):
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_PAGADA = 'Pagada'
    ESTADO_ANULADA = 'Anulada'
    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PAGADA, 'Pagada'),
        (ESTADO_ANULADA, 'Anulada'),
    ]

    residencia = models.ForeignKey(
        Residencia,
        on_delete=models.PROTECT,
        related_name='multas',
        verbose_name='Residencia',
    )
    concepto = models.CharField('Concepto', max_length=200)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    fecha = models.DateField('Fecha')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)

    class Meta:
        ordering = ['-fecha', 'concepto']
        verbose_name = 'Multa'
        verbose_name_plural = 'Multas'

    def __str__(self):
        return f'{self.concepto} - {self.residencia}'

    def clean(self):
        super().clean()
        if self.valor is not None and self.valor <= 0:
            raise ValidationError({'valor': 'El valor de la multa debe ser mayor que cero.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado de la multa no es válido.'})
        if not self.concepto or not self.concepto.strip():
            raise ValidationError({'concepto': 'El concepto de la multa es obligatorio.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ConvenioPago(models.Model):
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_APROBADO = 'Aprobado'
    ESTADO_CUMPLIDO = 'Cumplido'
    ESTADO_CANCELADO = 'Cancelado'
    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADO, 'Aprobado'),
        (ESTADO_CUMPLIDO, 'Cumplido'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    cuenta = models.ForeignKey(
        CuentaCobro,
        on_delete=models.PROTECT,
        related_name='convenios',
        verbose_name='Cuenta de cobro',
    )
    cuotas = models.PositiveIntegerField(
        'Número de cuotas',
        validators=[MinValueValidator(1)],
    )
    valor_cuota = models.DecimalField(
        'Valor por cuota',
        max_digits=12,
        decimal_places=2,
    )
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)

    class Meta:
        ordering = ['cuenta', 'id']
        verbose_name = 'Convenio de pago'
        verbose_name_plural = 'Convenios de pago'

    def __str__(self):
        return f'{self.cuenta.concepto} · {self.cuotas} cuotas'

    @property
    def valor_total(self):
        return self.cuotas * self.valor_cuota

    def clean(self):
        super().clean()
        if self.cuotas is not None and self.cuotas < 1:
            raise ValidationError({'cuotas': 'El convenio debe tener al menos una cuota.'})
        if self.valor_cuota is not None and self.valor_cuota <= 0:
            raise ValidationError({'valor_cuota': 'El valor de cada cuota debe ser mayor que cero.'})
        if self.estado not in dict(self.ESTADOS):
            raise ValidationError({'estado': 'El estado del convenio no es válido.'})
        if not self.cuenta_id or self.valor_cuota is None or self.cuotas is None:
            return

        saldo = self.cuenta.saldo_pendiente
        total = self.cuotas * self.valor_cuota
        if self.estado == self.ESTADO_CUMPLIDO:
            if saldo > 0:
                raise ValidationError({'estado': 'El convenio solo puede cumplirse cuando la cuenta está pagada.'})
        elif self.estado != self.ESTADO_CANCELADO:
            if saldo <= 0:
                raise ValidationError({'estado': 'No se puede crear un convenio para una cuenta pagada.'})
            comprometido = sum(
                (
                    cuotas_existentes * valor_existente
                    for cuotas_existentes, valor_existente in ConvenioPago.objects.filter(
                        cuenta_id=self.cuenta_id,
                        estado__in=[self.ESTADO_PENDIENTE, self.ESTADO_APROBADO],
                    ).exclude(pk=self.pk).values_list('cuotas', 'valor_cuota')
                ),
                Decimal('0.00'),
            )
            if comprometido + total > saldo:
                raise ValidationError({'valor_cuota': 'El valor total de los convenios excede el saldo pendiente.'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            cuenta = CuentaCobro.objects.select_for_update().get(pk=self.cuenta_id)
            self.cuenta = cuenta
            self.full_clean()
            super().save(*args, **kwargs)
