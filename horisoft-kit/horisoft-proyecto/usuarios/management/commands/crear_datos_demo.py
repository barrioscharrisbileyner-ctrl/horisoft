"""
Carga datos de DEMOSTRACIÓN para recorrer el sistema y tomar las capturas del reporte.

    python manage.py crear_datos_demo                 # datos base
    python manage.py crear_datos_demo --paginacion    # además, 12 residentes (prueba de paginación, CP-07)

Es idempotente: se puede ejecutar varias veces sin duplicar nada.
Solo para entornos de prueba: crea usuarios con una contraseña conocida.
"""
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from reservas.models import Reserva, ZonaComun
from residentes.models import Persona, PropiedadHorizontal, Residencia, UnidadResidencial
from usuarios.models import (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE,
                             ROL_VIGILANTE, PerfilUsuario)

CLAVE_DEMO = 'Horisoft#2026'


class Command(BaseCommand):
    help = 'Carga datos de demostración (unidades, residentes, zonas, usuarios por rol y una reserva).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--paginacion', action='store_true',
            help='Crea además 12 residentes de relleno para probar la paginación (CP-07).')

    @transaction.atomic
    def handle(self, *args, **opciones):
        User = get_user_model()

        ph, _ = PropiedadHorizontal.objects.get_or_create(
            id_ph=1, defaults={'nombre': 'Conjunto Residencial Villa Serena'})

        unidades = {}
        for numero in ('101', '102', '201'):
            unidades[numero], _ = UnidadResidencial.objects.get_or_create(
                numero_unidad=numero, propiedad_horizontal=ph,
                defaults={'tipo_unidad': 'Apartamento'})

        ana, _ = Persona.objects.get_or_create(
            numero_documento='111',
            defaults={'nombre': 'Ana Pérez', 'telefono': '3001112233', 'email': 'ana@horisoft.com'})
        luis, _ = Persona.objects.get_or_create(
            numero_documento='222',
            defaults={'nombre': 'Luis Gómez', 'telefono': '3004445566', 'email': 'luis@horisoft.com'})

        res_ana, _ = Residencia.objects.get_or_create(
            persona=ana, unidad=unidades['101'], rol=Residencia.ROL_PROPIETARIO)
        res_luis, _ = Residencia.objects.get_or_create(
            persona=luis, unidad=unidades['201'], rol=Residencia.ROL_PROPIETARIO)

        salon, _ = ZonaComun.objects.get_or_create(
            nombre='Salón Social',
            defaults={'descripcion': 'Salón para eventos y reuniones', 'capacidad': 50,
                      'costo_reserva': 80000, 'estado': ZonaComun.ESTADO_DISPONIBLE})
        ZonaComun.objects.get_or_create(
            nombre='Piscina',
            defaults={'descripcion': 'Piscina para adultos y niños', 'capacidad': 30,
                      'costo_reserva': 0, 'estado': ZonaComun.ESTADO_DISPONIBLE})
        ZonaComun.objects.get_or_create(
            nombre='Cancha Múltiple',
            defaults={'descripcion': 'Cancha de fútbol y baloncesto', 'capacidad': 20,
                      'costo_reserva': 0, 'estado': ZonaComun.ESTADO_MANTENIMIENTO})

        usuarios = [
            ('admin@horisoft.com', 'Admin', 'Horisoft', ROL_ADMINISTRADOR, None),
            ('administrativo@horisoft.com', 'Ana María', 'Administrativa', ROL_ADMINISTRATIVO, None),
            ('vigilante@horisoft.com', 'Víctor', 'Vigilante', ROL_VIGILANTE, None),
            ('ana@horisoft.com', 'Ana', 'Pérez', ROL_RESIDENTE, ana),
            ('luis@horisoft.com', 'Luis', 'Gómez', ROL_RESIDENTE, luis),
        ]
        for correo, nombre, apellido, rol, persona in usuarios:
            if User.objects.filter(username=correo).exists():
                continue
            user = User.objects.create_user(
                username=correo, email=correo, password=CLAVE_DEMO,
                first_name=nombre, last_name=apellido, is_staff=(rol == ROL_ADMINISTRADOR))
            PerfilUsuario.objects.create(user=user, rol=rol, persona=persona)

        # Una reserva de Luis: sirve para comprobar que Ana NO la ve en su lista (CP-26).
        Reserva.objects.get_or_create(
            zona=salon, residencia=res_luis, fecha=timezone.localdate() + timedelta(days=3),
            hora_inicio=time(18, 0), hora_fin=time(20, 0),
            defaults={'estado': Reserva.ESTADO_CONFIRMADA, 'observaciones': 'Reunión familiar'})

        if opciones['paginacion']:
            for i in range(12):
                Persona.objects.get_or_create(
                    numero_documento=f'9{i:02d}', defaults={'nombre': f'Residente Demo {i:02d}'})

        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.'))
        self.stdout.write(f'\nUsuarios (contraseña de todos: {CLAVE_DEMO})')
        for correo, _n, _a, rol, _p in usuarios:
            self.stdout.write(f'  {rol:<15} {correo}')
        if opciones['paginacion']:
            self.stdout.write('\nSe crearon 12 residentes de relleno (documentos 900 a 911).')
