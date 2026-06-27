"""
Pruebas automáticas del módulo Residentes y Unidades.

Complementan el plan de pruebas manual (ver README.md, sección "Entrega 3").
Se ejecutan con:

    python manage.py test residentes
"""
from django.test import TestCase
from django.urls import reverse

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
