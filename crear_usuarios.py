# crear_usuarios.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "produccion.settings")
django.setup()

from django.contrib.auth.models import User, Group

roles = ["admin", "normal", "viewer"]
for rol in roles:
    Group.objects.get_or_create(name=rol)

# Usuario de prueba con rol viewer, contraseña desde variable de entorno
pass_lector = os.environ.get("PASS_LECTOR", "ClaveSegura2026!")
user_lector, created = User.objects.get_or_create(username="lector")
if created:
    user_lector.set_password(pass_lector)
    user_lector.save()
    user_lector.groups.add(Group.objects.get(name="viewer"))
    print("Usuario lector configurado correctamente.")
else:
    print("El usuario lector ya existía.")

print("Grupos creados:", roles)