"""
Pruebas del módulo Zonas Comunes y Reservas (CP-20 a CP-29).

Ejecutar:  python manage.py test reservas

Las fechas se calculan a partir de "hoy" (no se escriben fijas): una fecha fija
termina quedando en el pasado y hace fallar la prueba con el tiempo (ya pasó
con el prototipo Express: ver Bitácora de No Conformidad del plan de pruebas).
"""
from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE,
                             ROL_VIGILANTE)
from usuarios.testing import crear_usuario_con_rol

from .forms import ReservaForm
from .models import Reserva, ZonaComun


def hoy():
    return timezone.localdate()


def en_dias(n):
    return hoy() + timedelta(days=n)


class BaseReservasTest(TestCase):
    """Datos comunes: una copropiedad, dos residencias (de dos personas) y dos zonas."""

    def setUp(self):
        ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Prueba')
        u101 = UnidadResidencial.objects.create(numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        u202 = UnidadResidencial.objects.create(numero_unidad='202', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        self.ana = Persona.objects.create(numero_documento='111', nombre='Ana Pérez')
        self.luis = Persona.objects.create(numero_documento='222', nombre='Luis Gómez')
        self.res_ana = Residencia.objects.create(persona=self.ana, unidad=u101, rol=Residencia.ROL_PROPIETARIO)
        self.res_luis = Residencia.objects.create(persona=self.luis, unidad=u202, rol=Residencia.ROL_PROPIETARIO)

        self.salon = ZonaComun.objects.create(nombre='Salón Social', capacidad=50, costo_reserva=80000)
        self.cancha = ZonaComun.objects.create(
            nombre='Cancha Múltiple', capacidad=20, estado=ZonaComun.ESTADO_MANTENIMIENTO)

        self.admin = crear_usuario_con_rol('admin@horisoft.com', ROL_ADMINISTRADOR)
        self.u_ana = crear_usuario_con_rol('ana@horisoft.com', ROL_RESIDENTE, persona=self.ana)
        self.u_luis = crear_usuario_con_rol('luis@horisoft.com', ROL_RESIDENTE, persona=self.luis)

    def datos(self, **cambios):
        d = {'zona': self.salon.pk, 'residencia': self.res_ana.pk, 'fecha': en_dias(7).isoformat(),
             'hora_inicio': '14:00', 'hora_fin': '16:00', 'observaciones': ''}
        d.update(cambios)
        return d

    def reservar(self, zona=None, residencia=None, dias=7, inicio=time(14, 0), fin=time(16, 0),
                 estado=Reserva.ESTADO_PENDIENTE):
        return Reserva.objects.create(
            zona=zona or self.salon, residencia=residencia or self.res_ana, fecha=en_dias(dias),
            hora_inicio=inicio, hora_fin=fin, estado=estado)


class ReglasDeNegocioTest(BaseReservasTest):

    def form(self, **cambios):
        return ReservaForm(data=self.datos(**cambios), usuario=self.admin)

    def test_cp20_reserva_valida_nace_pendiente(self):
        """CP-20: una reserva válida se guarda en estado Pendiente."""
        f = self.form()
        self.assertTrue(f.is_valid(), f.errors)
        reserva = f.save()
        self.assertEqual(reserva.estado, Reserva.ESTADO_PENDIENTE)

    def test_cp21_zona_en_mantenimiento_rechazada(self):
        """CP-21: no se puede reservar una zona que no está Disponible."""
        f = self.form(zona=self.cancha.pk)
        self.assertFalse(f.is_valid())
        self.assertIn('no está disponible', str(f.errors['zona']))

    def test_cp22_fecha_pasada_rechazada_y_hoy_permitido(self):
        """CP-22: no se reserva en el pasado; hoy (fecha local) sí es válido."""
        ayer = self.form(fecha=en_dias(-1).isoformat())
        self.assertFalse(ayer.is_valid())
        self.assertIn('fechas pasadas', str(ayer.errors['fecha']))
        self.assertTrue(self.form(fecha=hoy().isoformat()).is_valid())

    def test_cp23_hora_fin_debe_ser_posterior(self):
        """CP-23: la hora de fin debe ser posterior a la de inicio."""
        for inicio, fin in (('16:00', '14:00'), ('14:00', '14:00')):
            f = self.form(hora_inicio=inicio, hora_fin=fin)
            self.assertFalse(f.is_valid(), (inicio, fin))
            self.assertIn('posterior', str(f.errors['hora_fin']))

    def test_cp24_cruce_de_horario(self):
        """CP-24: se rechaza un cruce; contiguas y canceladas no cuentan como cruce."""
        self.reservar(inicio=time(14, 0), fin=time(16, 0))

        cruce = self.form(hora_inicio='15:00', hora_fin='17:00')
        self.assertFalse(cruce.is_valid())
        self.assertIn('Ya existe una reserva activa', str(cruce.non_field_errors()))

        self.assertTrue(self.form(hora_inicio='16:00', hora_fin='18:00').is_valid())   # contigua después
        self.assertTrue(self.form(hora_inicio='12:00', hora_fin='14:00').is_valid())   # contigua antes
        otra_zona = ZonaComun.objects.create(nombre='Piscina', capacidad=30)
        self.assertTrue(self.form(zona=otra_zona.pk, hora_inicio='15:00', hora_fin='17:00').is_valid())

        Reserva.objects.update(estado=Reserva.ESTADO_CANCELADA)      # una cancelada libera el horario
        self.assertTrue(self.form(hora_inicio='15:00', hora_fin='17:00').is_valid())

    def test_cp25_un_residente_solo_reserva_a_nombre_de_sus_residencias(self):
        """CP-25: un Residente no puede reservar con la residencia de otra persona."""
        propio = ReservaForm(data=self.datos(residencia=self.res_ana.pk), usuario=self.u_ana)
        self.assertTrue(propio.is_valid(), propio.errors)
        ajeno = ReservaForm(data=self.datos(residencia=self.res_luis.pk), usuario=self.u_ana)
        self.assertFalse(ajeno.is_valid())
        self.assertIn('residencia', ajeno.errors)


class VistasYRolesTest(BaseReservasTest):

    def test_cp26_residente_ve_solo_sus_reservas(self):
        """CP-26: la lista de reservas de un Residente solo incluye las suyas."""
        mia = self.reservar(residencia=self.res_ana, dias=3)
        ajena = self.reservar(residencia=self.res_luis, dias=4)
        self.client.force_login(self.u_ana)
        r = self.client.get(reverse('reservas:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(list(r.context['reservas']), [mia])
        self.assertNotIn(ajena, r.context['reservas'])

        self.client.force_login(self.admin)   # el administrador ve todas
        self.assertEqual(len(self.client.get(reverse('reservas:lista')).context['reservas']), 2)

    def test_cp27_residente_crea_y_cancela_solo_las_suyas(self):
        """CP-27: un Residente crea su reserva y la cancela; no puede tocar la de otro."""
        self.client.force_login(self.u_ana)
        r = self.client.post(reverse('reservas:crear'), self.datos())
        self.assertRedirects(r, reverse('reservas:lista'))
        mia = Reserva.objects.get(residencia=self.res_ana)

        ajena = self.reservar(residencia=self.res_luis, dias=9)
        r = self.client.post(reverse('reservas:estado', args=[ajena.pk]), {'estado': 'Cancelada'})
        self.assertEqual(r.status_code, 404)
        ajena.refresh_from_db()
        self.assertEqual(ajena.estado, Reserva.ESTADO_PENDIENTE)

        # un Residente no confirma (eso es del personal administrativo)...
        r = self.client.post(reverse('reservas:estado', args=[mia.pk]), {'estado': 'Confirmada'})
        self.assertEqual(r.status_code, 403)
        # ...pero sí cancela la suya
        self.client.post(reverse('reservas:estado', args=[mia.pk]), {'estado': 'Cancelada'})
        mia.refresh_from_db()
        self.assertEqual(mia.estado, Reserva.ESTADO_CANCELADA)

    def test_cp28_matriz_de_roles_en_reservas_y_zonas(self):
        """CP-28: Administrativo confirma; Vigilante solo consulta; Residente no gestiona zonas."""
        reserva = self.reservar()

        administrativo = crear_usuario_con_rol('adm@horisoft.com', ROL_ADMINISTRATIVO)
        self.client.force_login(administrativo)
        self.client.post(reverse('reservas:estado', args=[reserva.pk]), {'estado': 'Confirmada'})
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.ESTADO_CONFIRMADA)
        self.assertEqual(self.client.get(reverse('reservas:zona_crear')).status_code, 200)
        self.assertEqual(self.client.get(reverse('reservas:editar', args=[reserva.pk])).status_code, 200)

        vigilante = crear_usuario_con_rol('vig@horisoft.com', ROL_VIGILANTE)
        self.client.force_login(vigilante)
        self.assertEqual(self.client.get(reverse('reservas:lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('reservas:zonas')).status_code, 200)
        self.assertEqual(self.client.get(reverse('reservas:crear')).status_code, 403)

        self.client.force_login(self.u_ana)   # Residente
        self.assertEqual(self.client.get(reverse('reservas:zona_crear')).status_code, 403)
        self.assertEqual(self.client.get(reverse('reservas:editar', args=[reserva.pk])).status_code, 403)

        self.client.logout()                  # sin sesión
        url = reverse('reservas:lista')
        self.assertRedirects(self.client.get(url), f"{reverse('usuarios:login')}?next={url}")

    def test_cp29_no_se_borra_lo_que_tiene_reservas(self):
        """CP-29: zonas y residencias con reservas quedan protegidas (mensaje, sin error 500)."""
        self.reservar()
        self.client.force_login(self.admin)

        r = self.client.post(reverse('reservas:zona_eliminar', args=[self.salon.pk]), follow=True)
        self.assertTrue(ZonaComun.objects.filter(pk=self.salon.pk).exists())
        self.assertContains(r, 'tiene reservas')

        r = self.client.post(reverse('residentes:persona_eliminar', args=[self.ana.pk]), follow=True)
        self.assertTrue(Persona.objects.filter(pk=self.ana.pk).exists())
        self.assertContains(r, 'tiene reservas asociadas')

        # Una zona sin reservas sí se puede eliminar
        self.client.post(reverse('reservas:zona_eliminar', args=[self.cancha.pk]))
        self.assertFalse(ZonaComun.objects.filter(pk=self.cancha.pk).exists())
