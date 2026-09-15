# calculo/decorators.py
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def tiene_rol(user, *roles):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=roles).exists() or user.is_superuser


def requiere_rol(*roles):
    def decorador(view_func):
        @wraps(view_func)
        @login_required(login_url="login")
        def wrapper(request, *args, **kwargs):
            if tiene_rol(request.user, *roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permisos suficientes para realizar esta acción.")
            return redirect("lista")
        return wrapper
    return decorador