from django.conf import settings
from django.db import models

# Roles del sistema (alineados al mapa de navegación y al backend Express).
ROL_ADMINISTRADOR = "Administrador"
ROL_RESIDENTE = "Residente"
ROL_VIGILANTE = "Vigilante"
ROL_ADMINISTRATIVO = "Administrativo"
ROL_PROVEEDOR = "Proveedor"

ROLES = [
    (ROL_ADMINISTRADOR, "Administrador"),
    (ROL_RESIDENTE, "Residente"),
    (ROL_VIGILANTE, "Vigilante"),
    (ROL_ADMINISTRATIVO, "Administrativo"),
    (ROL_PROVEEDOR, "Proveedor"),
]

# Modelo de Persona del módulo Residentes. Si en tu proyecto se llama distinto,
# cámbialo aquí o define USUARIOS_PERSONA_MODEL en settings.py ("app.Modelo").
PERSONA_MODEL = getattr(settings, "USUARIOS_PERSONA_MODEL", "residentes.Persona")


class PerfilUsuario(models.Model):
    """
    Extiende al User de Django con el rol del sistema y, opcionalmente, la
    Persona del módulo Residentes a la que corresponde (entidad
    "PerfilUsuario" del MER).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(max_length=20, choices=ROLES, default=ROL_RESIDENTE)
    persona = models.OneToOneField(
        PERSONA_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfil_usuario",
        help_text="Obligatoria para los residentes.",
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.rol})"
