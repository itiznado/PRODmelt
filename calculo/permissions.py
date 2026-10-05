from rest_framework import permissions


class PermisoDiferenciadoRegistro(permissions.BasePermission):
    """
    Lectura y creación: cualquier usuario autenticado.
    Edición (PUT/PATCH) y borrado (DELETE): solo personal staff.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True

        return request.user.is_staff