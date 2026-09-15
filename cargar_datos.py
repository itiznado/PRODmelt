# cargar_datos.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "produccion.settings")
django.setup()

import json
from calculo.models import Registro

with open("datos.json", encoding="utf-8") as f:
    datos = json.load(f)

for r in datos:
    Registro.objects.create(
        insumo=r["insumo"],
        estado=r["estado"],
        detalle=r["detalle"],
        stock_actual=None,
        venta_proyectada=None,
    )

print(f"Cargados con éxito {len(datos)} registros.")