from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from comunicaciones.models import Comunicado
from reservas.models import Reserva, ZonaComun
from pqrs.models import Pqr
from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol


class ApiAuthTests(APITestCase):
    def setUp(self):
        self.user = crear_usuario_con_rol('api@horisoft.com', ROL_ADMINISTRADOR)
        self.user.set_password('Horisoft#2026')
        self.user.save()

    def test_api_login_returns_tokens_and_user(self):
        response = self.client.post(
            reverse('auth-login'),
            {'username': 'api@horisoft.com', 'password': 'Horisoft#2026'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'api@horisoft.com')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        me = self.client.get(reverse('auth-me'))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data['role'], ROL_ADMINISTRADOR)

    def test_api_schema_is_available_without_authentication(self):
        response = self.client.get(reverse('api-schema'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('openapi', response.data)

    def test_login_is_rate_limited(self):
        cache.clear()
        for _ in range(5):
            self.client.post(
                reverse('auth-login'),
                {'username': 'api@horisoft.com', 'password': 'incorrecta'},
                format='json',
            )

        response = self.client.post(
            reverse('auth-login'),
            {'username': 'api@horisoft.com', 'password': 'incorrecta'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        cache.clear()


class ApiReservasTests(APITestCase):
    def setUp(self):
        ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto API')
        unidad = UnidadResidencial.objects.create(numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        self.ana = Persona.objects.create(numero_documento='111', nombre='Ana API')
        self.luis = Persona.objects.create(numero_documento='222', nombre='Luis API')
        self.res_ana = Residencia.objects.create(persona=self.ana, unidad=unidad, rol=Residencia.ROL_PROPIETARIO)
        self.zona = ZonaComun.objects.create(
            nombre='Sala API', capacidad=10, propiedad_horizontal=ph,
        )
        self.reserva_ana = Reserva.objects.create(
            zona=self.zona,
            residencia=self.res_ana,
            fecha=timezone.localdate() + timedelta(days=2),
            hora_inicio='09:00',
            hora_fin='10:00',
        )
        self.residente = crear_usuario_con_rol('ana-api@horisoft.com', ROL_RESIDENTE, persona=self.ana)
        self.residente.set_password('Horisoft#2026')
        self.residente.save()

    def test_residente_only_sees_his_reservas(self):
        self.client.force_authenticate(user=self.residente)
        response = self.client.get(reverse('reservas-list-create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id_reserva'], self.reserva_ana.id_reserva)

    def test_api_reservas_reutiliza_validaciones_de_formulario(self):
        self.client.force_authenticate(user=self.residente)
        response = self.client.post(
            reverse('reservas-list-create'),
            {
                'zona': self.zona.pk,
                'residencia': self.res_ana.pk,
                'fecha': (timezone.localdate() + timedelta(days=5)).isoformat(),
                'hora_inicio': '13:00',
                'hora_fin': '14:00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        self.zona.estado = ZonaComun.ESTADO_MANTENIMIENTO
        self.zona.save()
        rechazada = self.client.post(
            reverse('reservas-list-create'),
            {
                'zona': self.zona.pk,
                'residencia': self.res_ana.pk,
                'fecha': (timezone.localdate() + timedelta(days=6)).isoformat(),
                'hora_inicio': '13:00',
                'hora_fin': '14:00',
            },
            format='json',
        )
        self.assertEqual(rechazada.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no está disponible', str(rechazada.data))

    def test_api_reservas_detalle_cancelacion_y_zonas(self):
        self.client.force_authenticate(user=self.residente)

        zonas = self.client.get(reverse('zonas-comunes-list'))
        self.assertEqual(zonas.status_code, status.HTTP_200_OK)
        self.assertEqual(zonas.data['results'][0]['id_zona'], self.zona.pk)

        detalle = self.client.get(
            reverse('reservas-detail', args=[self.reserva_ana.pk]),
        )
        self.assertEqual(detalle.status_code, status.HTTP_200_OK)

        cancelada = self.client.post(
            reverse('reservas-cancel', args=[self.reserva_ana.pk]),
        )
        self.assertEqual(cancelada.status_code, status.HTTP_200_OK)
        self.assertEqual(cancelada.data['estado'], Reserva.ESTADO_CANCELADA)

        repetida = self.client.post(
            reverse('reservas-cancel', args=[self.reserva_ana.pk]),
        )
        self.assertEqual(repetida.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_residente_no_accede_a_detalle_de_reserva_ajena(self):
        otra_residencia = Residencia.objects.create(
            persona=self.luis,
            unidad=self.res_ana.unidad,
        )
        ajena = Reserva.objects.create(
            zona=self.zona,
            residencia=otra_residencia,
            fecha=timezone.localdate() + timedelta(days=7),
            hora_inicio='15:00',
            hora_fin='16:00',
        )
        self.client.force_authenticate(user=self.residente)
        response = self.client.get(reverse('reservas-detail', args=[ajena.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_datos_basicos_del_residente_y_auth_requerida(self):
        anonimo = self.client.get(reverse('resident-me'))
        self.assertEqual(anonimo.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.residente)
        response = self.client.get(reverse('resident-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id_residencia'], self.res_ana.pk)
        self.assertEqual(response.data['residencias'][0]['unidad'], '101')

    def test_usuario_no_lista_ni_crea_reservas_de_otra_copropiedad(self):
        otra_ph = PropiedadHorizontal.objects.create(nombre='Conjunto API B')
        otra_unidad = UnidadResidencial.objects.create(
            numero_unidad='B-101', propiedad_horizontal=otra_ph,
        )
        otra_persona = Persona.objects.create(numero_documento='API-B', nombre='Otra persona')
        otra_residencia = Residencia.objects.create(persona=otra_persona, unidad=otra_unidad)
        otra_zona = ZonaComun.objects.create(
            nombre='Sala B', capacidad=10, propiedad_horizontal=otra_ph,
        )
        otra_reserva = Reserva.objects.create(
            zona=otra_zona,
            residencia=otra_residencia,
            fecha=timezone.localdate() + timedelta(days=4),
            hora_inicio='11:00',
            hora_fin='12:00',
        )

        admin_a = crear_usuario_con_rol('admin-api-a@horisoft.com', ROL_ADMINISTRADOR)
        self.client.force_authenticate(user=admin_a)
        response = self.client.get(reverse('reservas-list-create'))
        self.assertEqual(response.status_code, 200)
        ids = {row['id_reserva'] for row in response.data['results']}
        self.assertIn(self.reserva_ana.id_reserva, ids)
        self.assertNotIn(otra_reserva.id_reserva, ids)

        denied = self.client.post(
            reverse('reservas-list-create'),
            {
                'zona': otra_zona.pk,
                'residencia': otra_residencia.pk,
                'fecha': (timezone.localdate() + timedelta(days=5)).isoformat(),
                'hora_inicio': '13:00',
                'hora_fin': '14:00',
            },
            format='json',
        )
        self.assertEqual(denied.status_code, 400)


class ApiPqrTests(APITestCase):
    def setUp(self):
        property = PropiedadHorizontal.objects.create(nombre='Conjunto PQR API')
        unit = UnidadResidencial.objects.create(numero_unidad='201', propiedad_horizontal=property)
        self.person = Persona.objects.create(numero_documento='333', nombre='Residente API')
        self.residence = Residencia.objects.create(persona=self.person, unidad=unit)
        other_person = Persona.objects.create(numero_documento='444', nombre='Otro API')
        self.other_residence = Residencia.objects.create(persona=other_person, unidad=unit)
        self.resident = crear_usuario_con_rol('pqr-api@horisoft.com', ROL_RESIDENTE, persona=self.person)
        self.client.force_authenticate(user=self.resident)

    def test_resident_cannot_assign_pqr_to_another_resident_or_set_admin_fields(self):
        denied = self.client.post(
            reverse('pqrs-list-create'),
            {
                'residencia': self.other_residence.pk,
                'tipo': Pqr.TIPO_QUEJA,
                'asunto': 'PQR ajena',
                'descripcion': 'No debe registrarse.',
            },
            format='json',
        )
        self.assertEqual(denied.status_code, 403)

        created = self.client.post(
            reverse('pqrs-list-create'),
            {
                'residencia': self.residence.pk,
                'tipo': Pqr.TIPO_QUEJA,
                'asunto': 'PQR propia',
                'descripcion': 'Solicitud permitida.',
                'respuesta': 'No autorizada',
                'estado': Pqr.ESTADO_CERRADA,
            },
            format='json',
        )
        self.assertEqual(created.status_code, 201)
        pqr = Pqr.objects.get(asunto='PQR propia')
        self.assertEqual(pqr.estado, Pqr.ESTADO_ABIERTA)
        self.assertEqual(pqr.respuesta, '')

    def test_comunicados_publicados_se_filtran_por_rol_y_copropiedad(self):
        Comunicado.objects.create(
            titulo='Aviso residentes',
            contenido='Contenido informativo.',
            dirigido_a=Comunicado.DIRIGIDO_A_RESIDENTES,
            autor=self.resident,
            propiedad_horizontal=self.residence.unidad.propiedad_horizontal,
        )
        Comunicado.objects.create(
            titulo='Aviso vigilantes',
            contenido='Información operativa.',
            dirigido_a=Comunicado.DIRIGIDO_A_VIGILANTES,
            autor=self.resident,
            propiedad_horizontal=self.residence.unidad.propiedad_horizontal,
        )
        response = self.client.get(reverse('comunicados-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['titulo'], 'Aviso residentes')
