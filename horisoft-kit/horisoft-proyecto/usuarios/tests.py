"""
Pruebas del módulo Autenticación y Roles (CP-10 a CP-19).

Ejecutar:  python manage.py test usuarios

Dependen del modelo residentes.Persona solo a través de crear_persona().
"""
from io import StringIO

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import (PERSONA_MODEL, ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE,
                     PerfilUsuario)

User = get_user_model()
CLAVE = "Horisoft#2026"


def crear_persona(documento="1001"):
    """Crea una Persona del módulo Residentes (campos de residentes.Persona)."""
    Persona = apps.get_model(PERSONA_MODEL)
    return Persona.objects.create(numero_documento=documento, nombre="Ana Gómez")


def crear_usuario(correo, rol, persona=None, activo=True):
    user = User.objects.create_user(
        username=correo, email=correo, password=CLAVE,
        first_name="Nombre", last_name="Apellido", is_active=activo)
    PerfilUsuario.objects.create(user=user, rol=rol, persona=persona)
    return user


def datos_registro(**cambios):
    datos = {
        "nombre": "Carlos", "apellido": "Ramírez", "correo": "carlos@horisoft.com",
        "rol": ROL_VIGILANTE, "persona": "", "password1": CLAVE, "password2": CLAVE,
    }
    datos.update(cambios)
    return datos


class AutenticacionYRolesTests(TestCase):

    def setUp(self):
        self.admin = crear_usuario("admin@horisoft.com", ROL_ADMINISTRADOR)

    def entrar_como_admin(self):
        self.client.force_login(self.admin)

    # ---------------- Registro de usuarios ----------------

    def test_cp10_admin_crea_usuario_valido(self):
        """CP-10: un Administrador crea un usuario válido (User + PerfilUsuario)."""
        self.entrar_como_admin()
        r = self.client.post(reverse("usuarios:crear"), datos_registro())
        self.assertRedirects(r, reverse("usuarios:lista"))
        user = User.objects.get(username="carlos@horisoft.com")
        self.assertEqual(user.perfil.rol, ROL_VIGILANTE)
        self.assertTrue(user.check_password(CLAVE))  # contraseña guardada con hash

    def test_cp11_correo_duplicado_rechazado(self):
        """CP-11: no se permite un correo ya registrado (sin distinguir mayúsculas)."""
        self.entrar_como_admin()
        r = self.client.post(reverse("usuarios:crear"), datos_registro(correo="ADMIN@horisoft.com"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ya existe un usuario registrado con ese correo")
        self.assertEqual(User.objects.count(), 1)

    def test_cp12_contrasenas_distintas_rechazadas(self):
        """CP-12: las dos contraseñas deben coincidir."""
        self.entrar_como_admin()
        r = self.client.post(reverse("usuarios:crear"), datos_registro(password2="OtraClave#2026"))
        self.assertContains(r, "Las contraseñas no coinciden")
        self.assertFalse(User.objects.filter(username="carlos@horisoft.com").exists())

    def test_cp13_residente_requiere_persona(self):
        """CP-13: un Residente exige una Persona; con ella se crea y queda vinculada."""
        self.entrar_como_admin()
        r = self.client.post(reverse("usuarios:crear"), datos_registro(rol=ROL_RESIDENTE))
        self.assertContains(r, "Un residente debe estar vinculado a una persona")
        self.assertFalse(User.objects.filter(username="carlos@horisoft.com").exists())

        persona = crear_persona()
        r = self.client.post(reverse("usuarios:crear"),
                             datos_registro(rol=ROL_RESIDENTE, persona=persona.pk))
        self.assertRedirects(r, reverse("usuarios:lista"))
        self.assertEqual(User.objects.get(username="carlos@horisoft.com").perfil.persona, persona)

    # ---------------- Login ----------------

    def test_cp14_login_correcto(self):
        """CP-14: login con correo y contraseña correctos (el correo no distingue mayúsculas)."""
        r = self.client.post(reverse("usuarios:login"),
                             {"username": "ADMIN@Horisoft.com", "password": CLAVE})
        self.assertRedirects(r, reverse("usuarios:inicio"), fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)

    def test_cp15_login_incorrecto_o_cuenta_inactiva(self):
        """CP-15: contraseña incorrecta y cuenta inactiva no inician sesión."""
        r = self.client.post(reverse("usuarios:login"),
                             {"username": "admin@horisoft.com", "password": "mala"})
        self.assertContains(r, "Correo o contraseña incorrectos")
        self.assertNotIn("_auth_user_id", self.client.session)

        crear_usuario("inactivo@horisoft.com", ROL_VIGILANTE, activo=False)
        r = self.client.post(reverse("usuarios:login"),
                             {"username": "inactivo@horisoft.com", "password": CLAVE})
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(r.status_code, 200)

    # ---------------- Protección por sesión y por rol ----------------

    def test_cp16_vistas_protegidas_sin_sesion_redirigen_al_login(self):
        """CP-16: sin sesión, las vistas protegidas redirigen al login."""
        for nombre in ("usuarios:lista", "usuarios:crear", "usuarios:perfil"):
            url = reverse(nombre)
            r = self.client.get(url)
            self.assertRedirects(r, f"{reverse('usuarios:login')}?next={url}")

    def test_cp17_rol_requerido_permite_y_niega(self):
        """CP-17: @rol_requerido deja pasar al Administrador y responde 403 a otros roles."""
        self.entrar_como_admin()
        self.assertEqual(self.client.get(reverse("usuarios:lista")).status_code, 200)

        residente = crear_usuario("res@horisoft.com", ROL_RESIDENTE, persona=crear_persona("2002"))
        self.client.force_login(residente)
        self.assertEqual(self.client.get(reverse("usuarios:lista")).status_code, 403)
        self.assertEqual(self.client.get(reverse("usuarios:crear")).status_code, 403)
        self.assertEqual(self.client.get(reverse("usuarios:perfil")).status_code, 200)

    # ---------------- Reglas adicionales ----------------

    def test_cp18_admin_no_puede_bloquearse_a_si_mismo(self):
        """CP-18: un Administrador no puede desactivarse ni quitarse su rol."""
        self.entrar_como_admin()
        url = reverse("usuarios:editar", args=[self.admin.perfil.pk])
        r = self.client.post(url, {"rol": ROL_VIGILANTE, "persona": ""})  # is_active ausente = False
        self.assertContains(r, "No puedes desactivar tu propia cuenta")
        self.assertContains(r, "No puedes quitarte el rol de Administrador")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertEqual(self.admin.perfil.rol, ROL_ADMINISTRADOR)

    def test_cp19_comando_crear_administrador(self):
        """CP-19: el comando crear_administrador deja un usuario que puede entrar."""
        call_command("crear_administrador", correo="Jefe@Horisoft.com", password=CLAVE,
                     stdout=StringIO())
        user = User.objects.get(username="jefe@horisoft.com")
        self.assertEqual(user.perfil.rol, ROL_ADMINISTRADOR)
        r = self.client.post(reverse("usuarios:login"),
                             {"username": "jefe@horisoft.com", "password": CLAVE})
        self.assertRedirects(r, reverse("usuarios:inicio"), fetch_redirect_response=False)

    def test_cp32_inicio_lleva_a_cada_rol_a_su_seccion(self):
        """CP-32: tras el login, cada rol llega a su sección principal."""
        destinos = {
            ROL_ADMINISTRADOR: "residentes:inicio",
            ROL_VIGILANTE: "residentes:inicio",
            ROL_RESIDENTE: "reservas:lista",
            "Proveedor": "usuarios:perfil",
        }
        for i, (rol, destino) in enumerate(destinos.items()):
            usuario = crear_usuario(f"rol{i}@horisoft.com", rol,
                                    persona=crear_persona(f"90{i}") if rol == ROL_RESIDENTE else None)
            self.client.force_login(usuario)
            r = self.client.get(reverse("usuarios:inicio"))
            self.assertRedirects(r, reverse(destino), fetch_redirect_response=False, msg_prefix=rol)
