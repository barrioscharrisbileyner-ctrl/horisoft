from django.test import TestCase
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol

from .models import ParametroConfiguracion
from .services import actualizar_valor_parametro, crear_parametro


class ConfiguracionTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-config@horisoft.com', ROL_ADMINISTRADOR)
        ph = PropiedadHorizontal.objects.get()
        persona = Persona.objects.create(numero_documento='CFG-RES', nombre='Residente Configuración')
        unidad = UnidadResidencial.objects.create(numero_unidad='CFG-1', propiedad_horizontal=ph)
        Residencia.objects.create(persona=persona, unidad=unidad)
        self.residente = crear_usuario_con_rol(
            'residente-config@horisoft.com', ROL_RESIDENTE, persona=persona,
        )

    def test_cfg_01_crear_parametro_con_clave_unica(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('configuracion:crear'),
            {
                'clave': 'horario_mantenimiento',
                'valor': '18:00',
                'descripcion': 'Horario del mantenimiento general.',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ParametroConfiguracion.objects.filter(clave='horario_mantenimiento').exists())

    def test_cfg_02_clave_duplicada_rechazada(self):
        crear_parametro(
            'tarifa_admin', '25000', PropiedadHorizontal.objects.get(), 'Tarifa estándar',
        )
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('configuracion:crear'),
            {
                'clave': 'tarifa_admin',
                'valor': '30000',
                'descripcion': 'Intento duplicado',
            },
        )
        self.assertContains(response, 'clave')

    def test_cfg_03_actualizar_valor_parametro(self):
        parametro = crear_parametro(
            'valor_residente', '5000', PropiedadHorizontal.objects.get(), 'Cuota base',
        )
        actualizar_valor_parametro(parametro, '6000', 'Cuota actualizada')
        parametro.refresh_from_db()
        self.assertEqual(parametro.valor, '6000')
        self.assertEqual(parametro.descripcion, 'Cuota actualizada')

    def test_cfg_04_residente_puede_ver_parametros(self):
        crear_parametro(
            'aforo_maximo', '120', PropiedadHorizontal.objects.get(), 'Capacidad máxima',
        )
        self.client.force_login(self.residente)
        response = self.client.get(reverse('configuracion:parametros'))
        self.assertContains(response, 'aforo_maximo')

    def test_lista_parametros_paginada(self):
        ph = PropiedadHorizontal.objects.get()
        for indice in range(21):
            crear_parametro(f'parametro_{indice}', str(indice), ph, 'Prueba')
        self.client.force_login(self.admin)

        response = self.client.get(reverse('configuracion:parametros'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['parametros']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
