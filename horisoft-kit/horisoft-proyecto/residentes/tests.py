"""
Pruebas automáticas del módulo Residentes y Unidades.

Complementan el plan de pruebas manual (ver README.md, sección "Entrega 3").
Se ejecutan con:

    python manage.py test residentes
"""
from django.test import TestCase
from django.urls import reverse

from usuarios.models import (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_PROVEEDOR,
                             ROL_RESIDENTE, ROL_VIGILANTE)
from usuarios.testing import crear_usuario_con_rol

from .models import Persona, UnidadResidencial, Residencia, PropiedadHorizontal


class ResidenciaReglasDeNegocioTest(TestCase):
    def setUp(self):
        self.ph = PropiedadHorizontal.objects.create(nombre='Conjunto Prueba', nit='900111222-1')
        self.unidad = UnidadResidencial.objects.create(
            numero_unidad='101', tipo_unidad=UnidadResidencial.TIPO_APARTAMENTO,
            propiedad_horizontal=self.ph,
        )
        self.persona1 = Persona.objects.create(numero_documento='111', nombre='Ana Pérez')
        self.persona2 = Persona.objects.create(numero_documento='222', nombre='Luis Gómez')

    def test_crear_residencia_valida(self):
        residencia = Residencia.objects.create(
            persona=self.persona1, unidad=self.unidad, rol=Residencia.ROL_PROPIETARIO,
        )
        self.assertTrue(residencia.activo)

    def test_no_permite_dos_propietarios_activos(self):
        Residencia.objects.create(
            persona=self.persona1, unidad=self.unidad, rol=Residencia.ROL_PROPIETARIO,
        )
        from .forms import ResidenciaForm
        form = ResidenciaForm(data={
            'persona': self.persona2.pk, 'unidad': self.unidad.pk,
            'rol': Residencia.ROL_PROPIETARIO, 'activo': True,
        })
        self.assertFalse(form.is_valid())

    def test_no_permite_residencia_duplicada(self):
        Residencia.objects.create(
            persona=self.persona1, unidad=self.unidad, rol=Residencia.ROL_ARRENDATARIO,
        )
        from .forms import ResidenciaForm
        form = ResidenciaForm(data={
            'persona': self.persona1.pk, 'unidad': self.unidad.pk,
            'rol': Residencia.ROL_ARRENDATARIO, 'activo': True,
        })
        self.assertFalse(form.is_valid())


class VistasCRUDTest(TestCase):
    def setUp(self):
        self.ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Prueba')
        # Las vistas ahora exigen sesión: se entra como Administrador.
        self.client.force_login(crear_usuario_con_rol('admin@horisoft.com', ROL_ADMINISTRADOR))

    def test_lista_personas_responde_200(self):
        response = self.client.get(reverse('residentes:personas'))
        self.assertEqual(response.status_code, 200)

    def test_crear_persona_por_post(self):
        url = reverse('residentes:persona_crear')
        response = self.client.post(url, {
            'numero_documento': '999', 'nombre': 'Residente de Prueba',
            'telefono': '', 'email': '',
        })
        self.assertEqual(response.status_code, 302)  # redirige tras guardar
        self.assertTrue(Persona.objects.filter(numero_documento='999').exists())

    def test_crear_persona_sin_documento_no_guarda(self):
        url = reverse('residentes:persona_crear')
        response = self.client.post(url, {'numero_documento': '', 'nombre': 'Sin Documento'})
        self.assertEqual(response.status_code, 200)  # vuelve a mostrar el formulario con error
        self.assertFalse(Persona.objects.filter(nombre='Sin Documento').exists())

    def test_crear_unidad_por_post(self):
        url = reverse('residentes:unidad_crear')
        response = self.client.post(url, {'numero_unidad': '202', 'tipo_unidad': 'Apartamento'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UnidadResidencial.objects.filter(numero_unidad='202').exists())

    def test_eliminar_unidad_requiere_post(self):
        unidad = UnidadResidencial.objects.create(
            numero_unidad='303', tipo_unidad='Casa', propiedad_horizontal=self.ph,
        )
        url = reverse('residentes:unidad_eliminar', args=[unidad.pk])
        # Un GET no debe eliminar (eliminar siempre exige POST)
        self.client.get(url)
        self.assertTrue(UnidadResidencial.objects.filter(pk=unidad.pk).exists())
        # Un POST sí elimina
        self.client.post(url)
        self.assertFalse(UnidadResidencial.objects.filter(pk=unidad.pk).exists())


class ProteccionPorRolTest(TestCase):
    """CP-30 y CP-31: las vistas de Residentes exigen sesión y rol (usuarios.@rol_requerido)."""

    def setUp(self):
        self.ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Prueba')
        self.unidad = UnidadResidencial.objects.create(
            numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=self.ph)

    def test_cp30_sin_sesion_redirige_al_login(self):
        """CP-30: sin sesión, las vistas de Residentes redirigen al login y no ejecutan nada."""
        for nombre in ('residentes:inicio', 'residentes:personas', 'residentes:unidades',
                       'residentes:residencias', 'residentes:persona_crear'):
            url = reverse(nombre)
            r = self.client.get(url)
            self.assertRedirects(r, f"{reverse('usuarios:login')}?next={url}", msg_prefix=nombre)
        # y un POST anónimo de eliminación no borra nada
        self.client.post(reverse('residentes:unidad_eliminar', args=[self.unidad.pk]))
        self.assertTrue(UnidadResidencial.objects.filter(pk=self.unidad.pk).exists())

    def test_cp31_matriz_de_roles_en_residentes(self):
        """CP-31: Admin/Administrativo gestionan; Vigilante solo consulta; Residente y Proveedor no entran."""
        lista, crear = reverse('residentes:personas'), reverse('residentes:persona_crear')
        eliminar = reverse('residentes:unidad_eliminar', args=[self.unidad.pk])

        for rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO):
            self.client.force_login(crear_usuario_con_rol(f'{rol}@h.com', rol))
            self.assertEqual(self.client.get(lista).status_code, 200, rol)
            self.assertEqual(self.client.get(crear).status_code, 200, rol)

        self.client.force_login(crear_usuario_con_rol('vigilante@h.com', ROL_VIGILANTE))
        self.assertEqual(self.client.get(lista).status_code, 200)       # consulta: sí
        self.assertEqual(self.client.get(crear).status_code, 403)       # crear: no
        self.client.post(eliminar)                                      # eliminar: no
        self.assertTrue(UnidadResidencial.objects.filter(pk=self.unidad.pk).exists())

        for rol in (ROL_RESIDENTE, ROL_PROVEEDOR):
            self.client.force_login(crear_usuario_con_rol(f'{rol}@h.com', rol))
            self.assertEqual(self.client.get(lista).status_code, 403, rol)


class PlanManualResidentesTest(TestCase):
    """
    Automatización del plan de pruebas manual CP-01 a CP-09 (README, sección 4.2):
    cada prueba repite, a través de las vistas, los pasos del caso manual.
    """

    def setUp(self):
        self.ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Prueba')
        self.client.force_login(crear_usuario_con_rol('admin@horisoft.com', ROL_ADMINISTRADOR))
        self.unidad = UnidadResidencial.objects.create(
            numero_unidad='101', tipo_unidad='Apartamento', propiedad_horizontal=self.ph)
        self.ana = Persona.objects.create(numero_documento='111', nombre='Ana Pérez')
        self.luis = Persona.objects.create(numero_documento='222', nombre='Luis Gómez')

    def _asociar(self, persona, rol):
        return self.client.post(reverse('residentes:residencia_crear'), {
            'persona': persona.pk, 'unidad': self.unidad.pk, 'rol': rol, 'activo': 'on'})

    def test_cp01_crear_residente_valido(self):
        """CP-01: el residente se guarda y aparece en la lista."""
        r = self.client.post(reverse('residentes:persona_crear'), {
            'numero_documento': '333', 'nombre': 'Marta Ríos', 'telefono': '3001112233', 'email': 'marta@correo.com'})
        self.assertRedirects(r, reverse('residentes:personas'))
        self.assertContains(self.client.get(reverse('residentes:personas')), 'Marta Ríos')

    def test_cp02_crear_residente_sin_documento(self):
        """CP-02: no guarda y muestra "Este campo es obligatorio."."""
        r = self.client.post(reverse('residentes:persona_crear'), {'numero_documento': '', 'nombre': 'Sin Documento'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Este campo es obligatorio')
        self.assertFalse(Persona.objects.filter(nombre='Sin Documento').exists())

    def test_cp03_crear_unidad_valida(self):
        """CP-03: la unidad se guarda y aparece en la lista."""
        r = self.client.post(reverse('residentes:unidad_crear'), {'numero_unidad': '305', 'tipo_unidad': 'Casa'})
        self.assertRedirects(r, reverse('residentes:unidades'))
        self.assertContains(self.client.get(reverse('residentes:unidades')), '305')

    def test_cp04_asociar_residente_a_unidad(self):
        """CP-04: se crea la residencia y aparece en la lista."""
        r = self._asociar(self.ana, Residencia.ROL_ARRENDATARIO)
        self.assertRedirects(r, reverse('residentes:residencias'))
        self.assertContains(self.client.get(reverse('residentes:residencias')), 'Ana Pérez')

    def test_cp05_dos_propietarios_en_la_misma_unidad(self):
        """CP-05: muestra el error de validación y no guarda."""
        self._asociar(self.ana, Residencia.ROL_PROPIETARIO)
        r = self._asociar(self.luis, Residencia.ROL_PROPIETARIO)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'ya tiene un propietario activo')
        self.assertEqual(Residencia.objects.filter(unidad=self.unidad).count(), 1)

    def test_cp06_residencia_duplicada(self):
        """CP-06: muestra el error de validación y no guarda."""
        self._asociar(self.ana, Residencia.ROL_ARRENDATARIO)
        r = self._asociar(self.ana, Residencia.ROL_ARRENDATARIO)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'ya está asociada')
        self.assertEqual(Residencia.objects.filter(persona=self.ana).count(), 1)

    def test_cp07_listar_con_paginacion(self):
        """CP-07: 10 por página y controles de paginación (12 residentes -> 2 páginas)."""
        for i in range(10):  # con Ana y Luis (setUp) suman 12
            Persona.objects.create(numero_documento=f'9{i:02d}', nombre=f'Residente {i:02d}')
        pagina1 = self.client.get(reverse('residentes:personas'))
        self.assertEqual(len(pagina1.context['personas']), 10)
        self.assertContains(pagina1, 'Página 1 de 2')
        pagina2 = self.client.get(reverse('residentes:personas') + '?page=2')
        self.assertEqual(len(pagina2.context['personas']), 2)

    def test_cp08_editar_residente(self):
        """CP-08: el cambio de teléfono queda reflejado en la lista."""
        r = self.client.post(reverse('residentes:persona_editar', args=[self.ana.pk]), {
            'numero_documento': '111', 'nombre': 'Ana Pérez', 'telefono': '3159998877', 'email': ''})
        self.assertRedirects(r, reverse('residentes:personas'))
        self.assertContains(self.client.get(reverse('residentes:personas')), '3159998877')

    def test_cp09_eliminar_con_confirmacion(self):
        """CP-09: el botón pide confirmación (JS) y solo un POST elimina."""
        lista = self.client.get(reverse('residentes:personas'))
        self.assertContains(lista, 'confirm(')                       # confirmación en la interfaz
        url = reverse('residentes:persona_eliminar', args=[self.luis.pk])
        self.client.get(url)                                         # GET no elimina
        self.assertTrue(Persona.objects.filter(pk=self.luis.pk).exists())
        self.client.post(url)                                        # POST elimina
        self.assertFalse(Persona.objects.filter(pk=self.luis.pk).exists())
