from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import CuentaCobro, Pago


def crear_cuenta(datos, *, residencia):
    concepto = (datos.get('concepto') or '').strip()
    valor = datos.get('valor')
    fecha_vencimiento = datos.get('fecha_vencimiento')
    if not concepto or valor is None or not fecha_vencimiento:
        raise ValidationError('concepto, valor y fecha_vencimiento son obligatorios.')
    valor_decimal = Decimal(str(valor))
    if valor_decimal <= 0:
        raise ValidationError('El valor de la cuenta debe ser mayor que cero.')
    cuenta = CuentaCobro.objects.create(
        residencia=residencia,
        concepto=concepto,
        valor=valor_decimal,
        fecha_vencimiento=fecha_vencimiento,
    )
    return cuenta


def registrar_pago(cuenta, valor_pagado, metodo_pago, *, usuario=None, referencia=''):
    valor = Decimal(str(valor_pagado))
    if valor <= 0:
        raise ValidationError('valor_pagado debe ser mayor que cero.')
    if metodo_pago not in dict(Pago.METODOS):
        raise ValidationError('Método de pago no válido.')

    with transaction.atomic():
        cuenta_lock = CuentaCobro.objects.select_for_update().get(pk=cuenta.pk)
        if cuenta_lock.estado == CuentaCobro.ESTADO_PAGADA:
            raise ValidationError('Esta cuenta ya se encuentra completamente pagada.')
        saldo = cuenta_lock.valor - cuenta_lock.valor_pagado
        if valor > saldo:
            raise ValidationError(f'El valor pagado excede el saldo pendiente ({saldo}).')
        pago = Pago.objects.create(
            cuenta=cuenta_lock,
            valor_pagado=valor,
            metodo_pago=metodo_pago,
            referencia=referencia,
            registrado_por=usuario,
        )
        return pago


def marcar_vencida(cuenta):
    with transaction.atomic():
        cuenta_lock = CuentaCobro.objects.select_for_update().get(pk=cuenta.pk)
        if cuenta_lock.estado == CuentaCobro.ESTADO_PAGADA:
            raise ValidationError('No se puede marcar como vencida una cuenta ya pagada.')
        cuenta_lock.estado = CuentaCobro.ESTADO_VENCIDA
        cuenta_lock.save(update_fields=['estado'])
        return cuenta_lock
