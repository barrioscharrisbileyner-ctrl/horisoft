from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.testing import crear_usuario_con_rol

from .models import Documento
from .services import crear_documento


class DocumentalTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-documental@horisoft.com', ROL_ADMINISTRADOR)
        ph = PropiedadHorizontal.objects.get()
        persona = Persona.objects.create(numero_documento='DOC-RES', nombre='Residente Documental')
        unidad = UnidadResidencial.objects.create(numero_unidad='DOC-1', propiedad_horizontal=ph)
        Residencia.objects.create(persona=persona, unidad=unidad)
        self.residente = crear_usuario_con_rol(
            'residente-documental@horisoft.com', ROL_RESIDENTE, persona=persona,
        )

    def test_doc_01_crear_documento_con_tipo_valido(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('documental:crear'),
            {
                'titulo': 'Reglamento interno',
                'tipo': Documento.TIPO_REGLAMENTO,
                'url_archivo': 'https://example.com/reglamento.pdf',
                'descripcion': 'Normas internas vigentes.',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Documento.objects.filter(titulo='Reglamento interno').exists())

    def test_doc_02_tipo_invalido_rechazado(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('documental:crear'),
            {
                'titulo': 'Documento inválido',
                'tipo': 'Contrato',
                'url_archivo': 'https://example.com/invalido.pdf',
                'descripcion': 'Este tipo no existe.',
            },
        )
        self.assertContains(response, 'tipo')

    def test_doc_03_documento_puede_eliminarse(self):
        documento = crear_documento(
            titulo='Acta de reunión',
            tipo=Documento.TIPO_ACTA,
            responsable=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
            url_archivo='https://example.com/acta.pdf',
            descripcion='Acta entregada.',
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('documental:eliminar', args=[documento.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Documento.objects.filter(pk=documento.pk).exists())

    def test_doc_04_residente_puede_ver_documentos(self):
        Documento.objects.create(
            titulo='Circular de pagos',
            tipo=Documento.TIPO_CIRCULAR,
            responsable=self.admin,
            propiedad_horizontal=PropiedadHorizontal.objects.get(),
            url_archivo='https://example.com/circular.pdf',
            descripcion='Pago de administración.',
        )
        self.client.force_login(self.residente)
        response = self.client.get(reverse('documental:documentos'))
        self.assertContains(response, 'Circular de pagos')

    def test_doc_05_solo_usuarios_con_rol_pueden_descargar_pdf(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                documento = Documento.objects.create(
                    titulo='Reglamento PDF',
                    tipo=Documento.TIPO_REGLAMENTO,
                    responsable=self.admin,
                    propiedad_horizontal=PropiedadHorizontal.objects.get(),
                    archivo=SimpleUploadedFile('reglamento.pdf', b'%PDF-1.7 contenido', content_type='application/pdf'),
                )
                self.client.force_login(self.residente)
                response = self.client.get(reverse('documental:descargar', args=[documento.pk]))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Disposition'], f'attachment; filename="documento-{documento.pk}.pdf"')
                self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
                self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.7 contenido')

    def test_doc_06_archivo_no_pdf_rechazado(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('documental:crear'),
            {
                'titulo': 'No es PDF',
                'tipo': Documento.TIPO_OTRO,
                'archivo': SimpleUploadedFile('archivo.pdf', b'contenido ejecutable', content_type='application/pdf'),
            },
        )
        self.assertContains(response, 'no corresponde a un PDF válido')
        self.assertFalse(Documento.objects.filter(titulo='No es PDF').exists())

    def test_lista_documentos_paginada(self):
        ph = PropiedadHorizontal.objects.get()
        for indice in range(21):
            crear_documento(
                titulo=f'Documento {indice}',
                tipo=Documento.TIPO_OTRO,
                responsable=self.admin,
                propiedad_horizontal=ph,
                url_archivo=f'https://example.com/documento-{indice}.pdf',
            )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('documental:documentos'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['documentos']), 20)
        self.assertTrue(response.context['pagina'].has_next())
        self.assertContains(response, '?page=2')
