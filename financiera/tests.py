from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import ConvenioPago, CuentaCobro, Multa, Pago
from .services import registrar_pago
from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol


class FinancieraTests(TestCase):
    def setUp(self):
        ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Financiero')
        unidad = UnidadResidencial.objects.create(numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        self.persona = Persona.objects.create(numero_documento='123', nombre='María Finanzas')
        self.residencia = Residencia.objects.create(persona=self.persona, unidad=unidad, rol=Residencia.ROL_PROPIETARIO)
        self.admin = crear_usuario_con_rol('admin-financiera@horisoft.com', ROL_ADMINISTRADOR)
        self.administrativo = crear_usuario_con_rol('adm-financiera@horisoft.com', ROL_ADMINISTRATIVO)
        self.residente = crear_usuario_con_rol('residente-financiera@horisoft.com', ROL_RESIDENTE, persona=self.persona)

    def test_fin_01_cuenta_se_crea_con_valor_positivo(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('financiera:cuenta_crear'),
            {
                'residencia': self.residencia.pk,
                'concepto': 'Cuota de administración',
                'valor': '250000',
                'fecha_vencimiento': (date.today() + timedelta(days=15)).isoformat(),
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CuentaCobro.objects.filter(concepto='Cuota de administración').exists())

    def test_fin_02_valor_negativo_rechazado(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('financiera:cuenta_crear'),
            {
                'residencia': self.residencia.pk,
                'concepto': 'Cuenta inválida',
                'valor': '-100',
                'fecha_vencimiento': (date.today() + timedelta(days=10)).isoformat(),
            },
        )
        self.assertContains(response, 'valor')

    def test_fin_03_pago_no_puede_exceder_saldo(self):
        cuenta = CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Mantenimiento',
            valor='100000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )
        self.client.force_login(self.administrativo)
        response = self.client.post(
            reverse('financiera:pago_crear'),
            {
                'cuenta': cuenta.pk,
                'valor_pagado': '250000',
                'metodo_pago': Pago.METODO_TRANSFERENCIA,
            },
        )
        self.assertContains(response, 'saldo')

    def test_fin_04_pago_registra_y_marcan_cuenta_pagada(self):
        cuenta = CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Mantenimiento',
            valor='100000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )
        self.client.force_login(self.administrativo)
        response = self.client.post(
            reverse('financiera:pago_crear'),
            {
                'cuenta': cuenta.pk,
                'valor_pagado': '100000',
                'metodo_pago': Pago.METODO_TRANSFERENCIA,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.estado, CuentaCobro.ESTADO_PAGADA)
        self.assertEqual(cuenta.valor_pagado, cuenta.valor)
        self.assertTrue(Pago.objects.filter(cuenta=cuenta).exists())

    def test_fin_06_pagos_parciales_actualizan_el_saldo_solo_una_vez(self):
        cuenta = CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Cuota parcial',
            valor='100000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )
        self.client.force_login(self.administrativo)
        for valor in ('40000', '60000'):
            response = self.client.post(
                reverse('financiera:pago_crear'),
                {
                    'cuenta': cuenta.pk,
                    'valor_pagado': valor,
                    'metodo_pago': Pago.METODO_TRANSFERENCIA,
                },
                follow=True,
            )
            self.assertEqual(response.status_code, 200)

        cuenta.refresh_from_db()
        self.assertEqual(cuenta.valor_pagado, cuenta.valor)
        self.assertEqual(cuenta.estado, CuentaCobro.ESTADO_PAGADA)
        self.assertEqual(Pago.objects.filter(cuenta=cuenta).count(), 2)

    def test_fin_05_residente_solo_ve_sus_cuentas(self):
        otra_persona = Persona.objects.create(numero_documento='456', nombre='Pedro Otro')
        otra_residencia = Residencia.objects.create(persona=otra_persona, unidad=self.residencia.unidad, rol=Residencia.ROL_PROPIETARIO)
        CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Mía',
            valor='50000',
            fecha_vencimiento=date.today() + timedelta(days=1),
        )
        CuentaCobro.objects.create(
            residencia=otra_residencia,
            concepto='Ajena',
            valor='90000',
            fecha_vencimiento=date.today() + timedelta(days=2),
        )
        self.client.force_login(self.residente)
        response = self.client.get(reverse('financiera:cuentas'))
        self.assertContains(response, 'Mía')
        self.assertNotContains(response, 'Ajena')

    def test_residente_no_ve_cuentas_de_otra_copropiedad_sin_residencia_activa(self):
        otra_ph = PropiedadHorizontal.objects.create(nombre='Otra copropiedad financiera')
        otra_unidad = UnidadResidencial.objects.create(
            numero_unidad='202', propiedad_horizontal=otra_ph,
        )
        residencia_anterior = Residencia.objects.create(
            persona=self.persona, unidad=otra_unidad, activo=False,
        )
        CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Cuenta actual',
            valor='10000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )
        CuentaCobro.objects.create(
            residencia=residencia_anterior,
            concepto='Cuenta de otra copropiedad',
            valor='20000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )

        self.client.force_login(self.residente)
        response = self.client.get(reverse('financiera:cuentas'))
        self.assertContains(response, 'Cuenta actual')
        self.assertNotContains(response, 'Cuenta de otra copropiedad')

    def test_convenio_no_puede_superar_el_saldo_y_cumple_al_pagar_cuenta(self):
        cuenta = CuentaCobro.objects.create(
            residencia=self.residencia,
            concepto='Saldo convenio',
            valor='100000',
            valor_pagado='20000',
            fecha_vencimiento=date.today() + timedelta(days=5),
        )
        convenio = ConvenioPago.objects.create(
            cuenta=cuenta,
            cuotas=4,
            valor_cuota='20000',
            estado=ConvenioPago.ESTADO_APROBADO,
        )
        self.assertEqual(convenio.valor_total, 80000)

        with self.assertRaisesMessage(ValidationError, 'excede el saldo pendiente'):
            ConvenioPago.objects.create(
                cuenta=cuenta,
                cuotas=5,
                valor_cuota='20000',
                estado=ConvenioPago.ESTADO_PENDIENTE,
            )
        with self.assertRaisesMessage(ValidationError, 'valor total de los convenios'):
            ConvenioPago.objects.create(
                cuenta=cuenta,
                cuotas=1,
                valor_cuota='1000',
                estado=ConvenioPago.ESTADO_PENDIENTE,
            )

        registrar_pago(cuenta, '80000', Pago.METODO_TRANSFERENCIA)
        convenio.refresh_from_db()
        self.assertEqual(convenio.estado, ConvenioPago.ESTADO_CUMPLIDO)

    def test_multa_rechaza_valores_no_positivos(self):
        with self.assertRaisesMessage(ValidationError, 'mayor que cero'):
            Multa.objects.create(
                residencia=self.residencia,
                concepto='Uso indebido',
                valor='0',
                fecha=date.today(),
            )

    def test_multa_se_registra_y_residente_solo_ve_las_propias(self):
        otra_persona = Persona.objects.create(numero_documento='789', nombre='Otra residente')
        otra_residencia = Residencia.objects.create(
            persona=otra_persona,
            unidad=self.residencia.unidad,
        )
        Multa.objects.create(
            residencia=self.residencia,
            concepto='Parqueadero',
            valor='50000',
            fecha=date.today(),
        )
        Multa.objects.create(
            residencia=otra_residencia,
            concepto='Ruido',
            valor='25000',
            fecha=date.today(),
        )
        self.client.force_login(self.residente)
        response = self.client.get(reverse('financiera:multas'))
        self.assertContains(response, 'Parqueadero')
        self.assertNotContains(response, 'Ruido')
