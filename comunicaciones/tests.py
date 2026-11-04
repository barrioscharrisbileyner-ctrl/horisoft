from django.test import TestCase
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol

from .models import Comunicado
from .services import archivar_comunicado, crear_comunicado


class ComunicacionesTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-comunicaciones@horisoft.com', ROL_ADMINISTRADOR)
        ph = PropiedadHorizontal.objects.get()
        persona = Persona.objects.create(numero_documento='COM-RES', nombre='Residente Comunicaciones')
        unidad = UnidadResidencial.objects.create(numero_unidad='COM-1', propiedad_horizontal=ph)
        Residencia.objects.create(persona=persona, unidad=unidad)
        self.residente = crear_usuario_con_rol(
            'residente-comunicaciones@horisoft.com', ROL_RESIDENTE, persona=persona,
        )

    def test_com_01_crear_comunicado_con_destinatario_valido(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('comunicaciones:crear'),
            {
                'titulo': 'Aviso de mantenimiento',
                'contenido': 'Se realizará mantenimiento del ascensor a las 10:00.',
                'dirigido_a': Comunicado.DIRIGIDO_A_RESIDENTES,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comunicado.objects.filter(titulo='Aviso de mantenimiento').exists())

    def test_com_02_destinatario_invalido_rechazado(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('comunicaciones:crear'),
            {
                'titulo': 'Comunicado inválido',
                'contenido': 'Esto no debe guardarse.',
                'dirigido_a': 'Clientes',
            },
        )
        self.assertContains(response, 'dirigido_a')

    def test_com_03_archivar_duplicado_rechaza(self):
        comunicado = crear_comunicado(
            titulo='Publicación de prueba',
            contenido='Texto de prueba',
            dirigido_a=Comunicado.DIRIGIDO_A_TODOS,
            autor=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
        )
        archivar_comunicado(comunicado)
        with self.assertRaisesMessage(ValueError, 'ya está archivado'):
            archivar_comunicado(comunicado)

    def test_com_04_residente_ve_solo_comunicados_permitidos(self):
        Comunicado.objects.create(
            titulo='Para todos',
            contenido='Mensaje de todos',
            dirigido_a=Comunicado.DIRIGIDO_A_TODOS,
            autor=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
        )
        Comunicado.objects.create(
            titulo='Solo residentes',
            contenido='Mensaje para residentes',
            dirigido_a=Comunicado.DIRIGIDO_A_RESIDENTES,
            autor=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
        )
        Comunicado.objects.create(
            titulo='Solo vigilantes',
            contenido='Mensaje para vigilantes',
            dirigido_a=Comunicado.DIRIGIDO_A_VIGILANTES,
            autor=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
        )

        self.client.force_login(self.residente)
        response = self.client.get(reverse('comunicaciones:comunicados'))
        self.assertContains(response, 'Para todos')
        self.assertContains(response, 'Solo residentes')
        self.assertNotContains(response, 'Solo vigilantes')

    def test_lista_comunicados_paginada(self):
        ph = PropiedadHorizontal.objects.get()
        for indice in range(21):
            crear_comunicado(
                titulo=f'Comunicado {indice}',
                contenido='Mensaje de prueba',
                dirigido_a=Comunicado.DIRIGIDO_A_TODOS,
                autor=self.admin,
                propiedad_horizontal=ph,
            )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('comunicaciones:comunicados'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['comunicados']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
