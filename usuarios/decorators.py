from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .permisos import obtener_rol


def rol_requerido(*roles):
    """
    Protege una vista por rol.

        from usuarios.decorators import rol_requerido
        from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO

        @rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
        def lista_residentes(request): ...

    - Sin sesión: redirige al login (LOGIN_URL).
    - Con sesión pero rol no permitido: responde 403.
    """

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if obtener_rol(request.user) not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)

        return login_required(envoltura)

    return decorador
