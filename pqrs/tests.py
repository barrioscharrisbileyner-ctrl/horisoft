from django.test import TestCase
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol

from .models import Pqr


class PqrTests(TestCase):
    def setUp(self):
        ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Copropiedad PQR')
        unidad = UnidadResidencial.objects.create(numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        self.persona = Persona.objects.create(numero_documento='1010', nombre='Ana PQR')
        self.residencia = Residencia.objects.create(persona=self.persona, unidad=unidad, rol=Residencia.ROL_PROPIETARIO)
        self.admin = crear_usuario_con_rol('admin-pqr@horisoft.com', ROL_ADMINISTRADOR)
        self.residente = crear_usuario_con_rol('residente-pqr@horisoft.com', ROL_RESIDENTE, persona=self.persona)

    def test_cp33_pqr_se_crea_y_aparece_para_residente(self):
        self.client.force_login(self.residente)
        response = self.client.post(
            reverse('pqrs:crear'),
            {
                'residencia': self.residencia.id_residencia,
                'tipo': 'Queja',
                'asunto': 'Ruido en la tarde',
                'descripcion': 'Hay ruido excesivo en el edificio.',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Pqr.objects.filter(asunto='Ruido en la tarde').exists())

    def test_cp34_admin_no_puede_responder_pqr_cerrada(self):
        pqr = Pqr.objects.create(
            residencia=self.residencia,
            tipo='Petición',
            asunto='Solicitud',
            descripcion='Necesito información',
            estado=Pqr.ESTADO_CERRADA,
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('pqrs:responder', args=[pqr.pk]), {'respuesta': 'Ya respondimos'}, follow=True)
        self.assertContains(response, 'ya cerrada')

    def test_cp35_admin_responde_pqr_y_la_cierra(self):
        pqr = Pqr.objects.create(
            residencia=self.residencia,
            tipo='Sugerencia',
            asunto='Mejoras',
            descripcion='Necesitamos más iluminación',
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('pqrs:responder', args=[pqr.pk]), {'respuesta': 'Gracias por la sugerencia.'}, follow=True)
        self.assertEqual(response.status_code, 200)
        pqr.refresh_from_db()
        self.assertEqual(pqr.estado, Pqr.ESTADO_CERRADA)
        self.assertIn('Gracias', pqr.respuesta)

    def test_detalle_pqr_muestra_accion_de_respuesta_a_administrador(self):
        pqr = Pqr.objects.create(
            residencia=self.residencia,
            tipo='Petición',
            asunto='Consulta administrativa',
            descripcion='Solicito información.',
        )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('pqrs:detalle', args=[pqr.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('pqrs:responder', args=[pqr.pk]))

    def test_cp36_residente_solo_ve_sus_pqrs(self):
        otra_persona = Persona.objects.create(numero_documento='2020', nombre='Luis Otro')
        otra_residencia = Residencia.objects.create(persona=otra_persona, unidad=self.residencia.unidad, rol=Residencia.ROL_PROPIETARIO)
        Pqr.objects.create(residencia=self.residencia, tipo='Queja', asunto='Mía', descripcion='Texto 1')
        Pqr.objects.create(residencia=otra_residencia, tipo='Queja', asunto='Ajena', descripcion='Texto 2')
        self.client.force_login(self.residente)
        response = self.client.get(reverse('pqrs:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mía')
        self.assertNotContains(response, 'Ajena')

    def test_residente_no_ve_pqrs_de_una_residencia_inactiva_en_otra_copropiedad(self):
        otra_ph = PropiedadHorizontal.objects.create(nombre='Otra copropiedad PQR')
        otra_unidad = UnidadResidencial.objects.create(
            numero_unidad='202', propiedad_horizontal=otra_ph,
        )
        residencia_anterior = Residencia.objects.create(
            persona=self.persona, unidad=otra_unidad, activo=False,
        )
        Pqr.objects.create(
            residencia=self.residencia,
            tipo=Pqr.TIPO_QUEJA,
            asunto='PQR actual',
            descripcion='Visible',
        )
        Pqr.objects.create(
            residencia=residencia_anterior,
            tipo=Pqr.TIPO_QUEJA,
            asunto='PQR de otra copropiedad',
            descripcion='No debe exponerse',
        )

        self.client.force_login(self.residente)
        response = self.client.get(reverse('pqrs:lista'))
        self.assertContains(response, 'PQR actual')
        self.assertNotContains(response, 'PQR de otra copropiedad')

    def test_lista_pqrs_paginada(self):
        Pqr.objects.bulk_create([
            Pqr(
                residencia=self.residencia,
                tipo='Queja',
                asunto=f'PQR {indice}',
                descripcion='Descripción de prueba',
            )
            for indice in range(21)
        ])
        self.client.force_login(self.admin)

        response = self.client.get(reverse('pqrs:lista'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pqrs']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
