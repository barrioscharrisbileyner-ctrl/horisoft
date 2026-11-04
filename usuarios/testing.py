"""Utilidades para las pruebas de otras apps (no es un módulo de pruebas)."""
from django.contrib.auth import get_user_model

from residentes.models import AccesoPropiedad, PropiedadHorizontal
from .models import PerfilUsuario

CLAVE_PRUEBAS = "Horisoft#2026"


def crear_usuario_con_rol(correo, rol, persona=None, activo=True):
    User = get_user_model()
    propiedad = PropiedadHorizontal.objects.first()
    if propiedad is None:
        propiedad = PropiedadHorizontal.objects.create(nombre='Conjunto de pruebas')
    user = User.objects.create_user(
        username=correo, email=correo, password=CLAVE_PRUEBAS,
        first_name="Nombre", last_name="Apellido", is_active=activo)
    PerfilUsuario.objects.create(user=user, rol=rol, persona=persona)
    if rol != "Residente":
        AccesoPropiedad.objects.create(usuario=user, propiedad_horizontal=propiedad)
    return user
