from .models import ROL_ADMINISTRADOR
from .permisos import (
    GESTION,
    GESTION_FINANCIERA,
    GESTION_SEGURIDAD,
    LECTURA_FINANCIERA,
    LECTURA_RESIDENTES,
    LECTURA_SEGURIDAD,
    USO_RESERVAS,
    obtener_rol,
)


def rol_actual(request):
    """Variables de plantilla para el menú: rol y qué secciones puede ver."""
    rol = obtener_rol(request.user)
    return {
        "rol_actual": rol,
        "ve_residentes": rol in LECTURA_RESIDENTES,
        "ve_reservas": rol in USO_RESERVAS,
        "puede_gestionar": rol in GESTION,
        "ve_financiera": rol in LECTURA_FINANCIERA,
        "puede_gestionar_financiera": rol in GESTION_FINANCIERA,
        "ve_seguridad": rol in LECTURA_SEGURIDAD,
        "puede_gestionar_seguridad": rol in GESTION_SEGURIDAD,
        "es_administrador": rol == ROL_ADMINISTRADOR,
    }
