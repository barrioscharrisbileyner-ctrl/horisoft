from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.testing import crear_usuario_con_rol

from .models import Camara, Vehiculo, Vigilante, Visitante
from .services import crear_vigilante, registrar_ingreso


class SeguridadTests(TestCase):
    def setUp(self):
        ph = PropiedadHorizontal.objects.create(id_ph=1, nombre='Conjunto Seguridad')
        self.admin = crear_usuario_con_rol('admin-seguridad@horisoft.com', ROL_ADMINISTRADOR)
        self.vigilante_user = crear_usuario_con_rol('vigilante-seguridad@horisoft.com', ROL_VIGILANTE)

        unidad = UnidadResidencial.objects.create(numero_unidad='202', tipo_unidad='Apartamento', propiedad_horizontal=ph)
        persona = Persona.objects.create(numero_documento='998877', nombre='Ana Seguridad')
        self.residencia = Residencia.objects.create(persona=persona, unidad=unidad, rol=Residencia.ROL_PROPIETARIO)
        self.residente_user = crear_usuario_con_rol(
            'residente-seguridad@horisoft.com', ROL_RESIDENTE, persona=persona,
        )

    def test_seg_01_crear_vigilante_con_turno_valido(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('seguridad:vigilante_crear'),
            {
                'nombre': 'Carlos Torres',
                'documento': '1122334455',
                'telefono': '3001234567',
                'turno': Vigilante.TURNO_DIURNO,
                'estado': Vigilante.ESTADO_ACTIVO,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vigilante.objects.filter(documento='1122334455').exists())

    def test_seg_02_documento_duplicado_rechazado(self):
        crear_vigilante(
            'Luis Vigilante', '123456', self.residencia.unidad.propiedad_horizontal,
            telefono='3000000000', turno=Vigilante.TURNO_NOCTURNO,
        )
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('seguridad:vigilante_crear'),
            {
                'nombre': 'Luis Segundo',
                'documento': '123456',
                'telefono': '3001111111',
                'turno': Vigilante.TURNO_DIURNO,
                'estado': Vigilante.ESTADO_ACTIVO,
            },
        )
        self.assertContains(response, 'documento')

    def test_seg_03_no_permite_doble_ingreso_activo_mismo_documento(self):
        vigilante = crear_vigilante(
            'Pedro Vigilante', '654321', self.residencia.unidad.propiedad_horizontal,
            turno=Vigilante.TURNO_MIXTO,
        )
        registrar_ingreso(
            nombre='Visitante Uno',
            documento='557788',
            residencia=self.residencia,
            vigilante=vigilante,
            motivo='Visita familiar',
        )
        with self.assertRaisesMessage(ValueError, 'ingreso activo'):
            registrar_ingreso(
                nombre='Visitante Dos',
                documento='557788',
                residencia=self.residencia,
                vigilante=vigilante,
                motivo='Otra visita',
            )

    def test_seg_04_registrar_salida_cierra_visita(self):
        vigilante = crear_vigilante(
            'Sara Vigilante', '887766', self.residencia.unidad.propiedad_horizontal,
            turno=Vigilante.TURNO_DIURNO,
        )
        visita = registrar_ingreso(
            nombre='Visitante Final',
            documento='9988771',
            residencia=self.residencia,
            vigilante=vigilante,
            motivo='Entrega de paquete',
        )
        self.client.force_login(self.vigilante_user)
        response = self.client.post(reverse('seguridad:salida', args=[visita.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        visita.refresh_from_db()
        self.assertEqual(visita.estado, Visitante.ESTADO_FINALIZADA)

    def test_camara_se_asocia_a_una_zona_y_rechaza_ubicacion_vacia(self):
        from reservas.models import ZonaComun

        zona = ZonaComun.objects.create(
            nombre='Entrada principal',
            capacidad=1,
            propiedad_horizontal=self.residencia.unidad.propiedad_horizontal,
        )
        camara = Camara.objects.create(ubicacion='Portería', zona=zona)
        self.assertEqual(camara.estado, Camara.ESTADO_ACTIVA)
        with self.assertRaisesMessage(ValidationError, 'ubicación'):
            Camara.objects.create(ubicacion=' ', zona=zona)

    def test_vehiculo_valida_placas_colombianas_y_unicidad(self):
        carro = Vehiculo.objects.create(
            placa='abc123',
            tipo=Vehiculo.TIPO_AUTOMOVIL,
            residencia=self.residencia,
        )
        moto = Vehiculo.objects.create(
            placa='def45g',
            tipo=Vehiculo.TIPO_MOTOCICLETA,
            residencia=self.residencia,
        )
        self.assertEqual(carro.placa, 'ABC123')
        self.assertEqual(moto.placa, 'DEF45G')

        with self.assertRaisesMessage(ValidationError, 'formato colombiano'):
            Vehiculo.objects.create(
                placa='A1B23C',
                tipo=Vehiculo.TIPO_AUTOMOVIL,
                residencia=self.residencia,
            )
        with self.assertRaises(ValidationError):
            Vehiculo.objects.create(
                placa='ABC123',
                tipo=Vehiculo.TIPO_AUTOMOVIL,
                residencia=self.residencia,
            )

    def test_residente_registra_vehiculo_solo_en_su_residencia(self):
        self.client.force_login(self.residente_user)
        response = self.client.post(
            reverse('seguridad:vehiculo_crear'),
            {
                'placa': 'ABC123',
                'tipo': Vehiculo.TIPO_AUTOMOVIL,
                'residencia': self.residencia.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vehiculo.objects.filter(placa='ABC123').exists())

        otra_propiedad = PropiedadHorizontal.objects.create(nombre='Otra seguridad')
        otra_unidad = UnidadResidencial.objects.create(numero_unidad='303', propiedad_horizontal=otra_propiedad)
        otra_persona = Persona.objects.create(numero_documento='998878', nombre='Otra persona')
        otra_residencia = Residencia.objects.create(persona=otra_persona, unidad=otra_unidad)
        respuesta_ajena = self.client.post(
            reverse('seguridad:vehiculo_crear'),
            {
                'placa': 'DEF456',
                'tipo': Vehiculo.TIPO_AUTOMOVIL,
                'residencia': otra_residencia.pk,
            },
        )
        self.assertContains(respuesta_ajena, 'residencia')
        self.assertFalse(Vehiculo.objects.filter(placa='DEF456').exists())

    def test_vigilante_no_puede_administrar_vehiculos(self):
        self.client.force_login(self.vigilante_user)
        response = self.client.get(reverse('seguridad:vehiculo_crear'))
        self.assertEqual(response.status_code, 403)
