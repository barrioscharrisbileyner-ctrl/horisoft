from django.core.exceptions import ObjectDoesNotExist

from .models import ROL_ADMINISTRADOR


def obtener_rol(user):
    """
    Rol del usuario, o None si no tiene sesión o perfil.
    Un superusuario creado con createsuperuser (sin perfil) cuenta como Administrador.
    """
    if not user.is_authenticated:
        return None
    try:
        return user.perfil.rol
    except ObjectDoesNotExist:
        return ROL_ADMINISTRADOR if user.is_superuser else None


# ---- Matriz de permisos por rol (un solo lugar para ajustarla) ----
from .models import (ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)  # noqa: E402

# Gestión completa (crear / editar / eliminar) de Residentes, Unidades y Zonas Comunes.
GESTION = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
# Consultar Residentes, Unidades y Residencias.
LECTURA_RESIDENTES = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE)
# Consultar zonas comunes y reservas (cada Residente solo ve las suyas).
USO_RESERVAS = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
# Crear reservas y cancelarlas.
ESCRIBIR_RESERVAS = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
