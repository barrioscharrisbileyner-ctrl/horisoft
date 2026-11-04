from django.test import TestCase
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol

from .models import ItemInventario
from .services import actualizar_cantidad, actualizar_estado, crear_item


class InventarioTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-inventario@horisoft.com', ROL_ADMINISTRADOR)
        ph = PropiedadHorizontal.objects.get()
        persona = Persona.objects.create(numero_documento='INV-RES', nombre='Residente Inventario')
        unidad = UnidadResidencial.objects.create(numero_unidad='INV-1', propiedad_horizontal=ph)
        Residencia.objects.create(persona=persona, unidad=unidad)
        self.residente = crear_usuario_con_rol(
            'residente-inventario@horisoft.com', ROL_RESIDENTE, persona=persona,
        )

    def test_inv_01_crear_item_con_cantidad_valida(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('inventario:crear'),
            {
                'nombre': 'Mesa de reuniones',
                'categoria': 'Mobiliario',
                'cantidad': '4',
                'ubicacion': 'Sala principal',
                'estado': ItemInventario.ESTADO_BUENO,
            },
        )
        errores = response.context['form'].errors if response.context else ''
        self.assertEqual(response.status_code, 302, errores)
        item = ItemInventario.objects.get(nombre='Mesa de reuniones')
        self.assertEqual(item.cantidad_minima, 0)

    def test_inv_02_cantidad_negativa_rechazada(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('inventario:crear'),
            {
                'nombre': 'Escoba',
                'categoria': 'Limpieza',
                'cantidad': '-1',
                'ubicacion': 'Bodega',
                'estado': ItemInventario.ESTADO_BUENO,
            },
        )
        self.assertContains(response, 'cantidad')

    def test_inv_03_actualizar_cantidad_y_estado(self):
        item = crear_item(
            'Silla', 'Mobiliario', 10, PropiedadHorizontal.objects.get(),
            'Taller', ItemInventario.ESTADO_BUENO,
        )
        actualizar_cantidad(item, 12)
        actualizar_estado(item, ItemInventario.ESTADO_REGULAR)
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 12)
        self.assertEqual(item.estado, ItemInventario.ESTADO_REGULAR)

    def test_inv_04_residente_puede_ver_inventario(self):
        crear_item(
            'Extintor', 'Seguridad', 2, PropiedadHorizontal.objects.get(),
            'Recepción', ItemInventario.ESTADO_BUENO,
        )
        self.client.force_login(self.residente)
        response = self.client.get(reverse('inventario:inventario'))
        self.assertContains(response, 'Extintor')

    def test_lista_inventario_paginada(self):
        ph = PropiedadHorizontal.objects.get()
        for indice in range(21):
            crear_item(
                f'Artículo {indice}',
                'General',
                1,
                ph,
                'Bodega',
                ItemInventario.ESTADO_BUENO,
            )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('inventario:inventario'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['items']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
