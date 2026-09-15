import json
import os
from tabulate import tabulate

ARCHIVO_DATOS = "datos.json"


def decidir(insumo, stock_actual, venta_proyectada, factor_uso=1.4, stock_maximo=8.0):
    # 1) Dato inválido: SIEMPRE va primero, o nunca se alcanza a revisar
    if stock_actual < 0 or venta_proyectada < 0:
        return {
            "insumo": insumo,
            "estado": "Error: Valores no validos",
            "detalle": "El stock y la venta proyectada no pueden ser negativos."
        }

    requerimiento_total = venta_proyectada * factor_uso

    # 2) Aceptado / Producir
    if stock_actual < requerimiento_total:
        faltante = requerimiento_total - stock_actual
        return {
            "insumo": insumo,
            "estado": "Aceptado: Produccion requerida",
            "detalle": f"Faltan {faltante:.2f} unidades por preparar."
        }

    # 3) Rechazo 1: stock suficiente
    if stock_actual <= stock_maximo:
        return {
            "insumo": insumo,
            "estado": "Rechazado: Stock suficiente",
            "detalle": "No es necesario producir mas por ahora."
        }

    # 4) Rechazo 2: sobrestock
    return {
        "insumo": insumo,
        "estado": "Rechazado: Alerta de sobrestock",
        "detalle": "El stock supera la capacidad maxima de almacenamiento."
    }


def cargar_registros():
    """Lee datos.json si existe; si no, devuelve lista vacía."""
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar_registro(registro, registros):
    """Agrega un registro nuevo a la lista y reescribe el archivo completo."""
    registros.append(registro)
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)
    return registros


if __name__ == "__main__":
    insumo = input("Insumo: ")
    stock_actual = float(input("Stock actual: "))
    venta_proyectada = float(input("Venta proyectada (millones $): "))

    resultado = decidir(insumo, stock_actual, venta_proyectada)
    print(f"\n{resultado['estado']}")
    print(resultado['detalle'])

    registros = cargar_registros()
    registros = guardar_registro(resultado, registros)

    print("\nHistorico de evaluaciones:")
    print(tabulate(registros, headers="keys"))