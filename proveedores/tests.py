from django.test import TestCase
from django.urls import reverse

from residentes.models import PropiedadHorizontal
from usuarios.models import ROL_ADMINISTRADOR, ROL_PROVEEDOR
from usuarios.testing import crear_usuario_con_rol

from .models import Proveedor
from .services import crear_proveedor


class ProveedoresTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-proveedor@horisoft.com', ROL_ADMINISTRADOR)
        self.proveedor_user = crear_usuario_con_rol('proveedor-user@horisoft.com', ROL_PROVEEDOR)

    def test_prov_01_crear_proveedor_con_nit_unico(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('proveedores:crear'),
            {
                'nombre': 'Servicios Eléctricos S.A.S.',
                'nit': '900123456-1',
                'servicio': 'Mantenimiento eléctrico',
                'telefono': '3201234567',
                'estado': Proveedor.ESTADO_ACTIVO,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Proveedor.objects.filter(nit='900123456-1').exists())

    def test_prov_02_nit_duplicado_rechazado(self):
        crear_proveedor(
            'Limpieza Domiciliaria', '800987654-2', 'Aseo general',
            PropiedadHorizontal.objects.get(),
        )
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('proveedores:crear'),
            {
                'nombre': 'Limpieza Domiciliaria 2',
                'nit': '800987654-2',
                'servicio': 'Aseo general',
                'telefono': '3002223333',
                'estado': Proveedor.ESTADO_ACTIVO,
            },
        )
        self.assertContains(response, 'nit')

    def test_prov_03_proveedor_puede_ver_listado(self):
        crear_proveedor(
            'Jardinería Verde', '901234567-9', 'Jardinería',
            PropiedadHorizontal.objects.get(),
        )
        self.client.force_login(self.proveedor_user)
        response = self.client.get(reverse('proveedores:proveedores'))
        self.assertContains(response, 'Jardinería Verde')

    def test_prov_04_estado_invalido_rechazado(self):
        proveedor = crear_proveedor(
            'Gas y Servicios', '903456789-2', 'Gas', PropiedadHorizontal.objects.get(),
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('proveedores:estado', args=[proveedor.pk]), {'estado': 'Suspendido'})
        self.assertContains(response, 'estado')

    def test_lista_proveedores_paginada(self):
        ph = PropiedadHorizontal.objects.get()
        for indice in range(21):
            crear_proveedor(
                f'Proveedor {indice}',
                f'900000{indice:04d}-1',
                'Servicio de prueba',
                ph,
            )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('proveedores:proveedores'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['proveedores']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
