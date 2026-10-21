from .models import ROL_ADMINISTRADOR
from .permisos import LECTURA_RESIDENTES, USO_RESERVAS, GESTION, obtener_rol


def rol_actual(request):
    """Variables de plantilla para el menú: rol y qué secciones puede ver."""
    rol = obtener_rol(request.user)
    return {
        "rol_actual": rol,
        "ve_residentes": rol in LECTURA_RESIDENTES,
        "ve_reservas": rol in USO_RESERVAS,
        "puede_gestionar": rol in GESTION,
        "es_administrador": rol == ROL_ADMINISTRADOR,
    }
