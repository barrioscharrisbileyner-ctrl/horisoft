from rest_framework.permissions import BasePermission

from usuarios.permisos import obtener_rol


class RoleRequired(BasePermission):
    """Permite acceder a una vista solo si el usuario tiene uno de los roles permitidos."""

    allowed_roles = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed_roles = getattr(view, 'allowed_roles', getattr(self, 'allowed_roles', ()))
        return obtener_rol(request.user) in allowed_roles
