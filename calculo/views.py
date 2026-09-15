from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Registro
from solucion import decidir
from .decorators import requiere_rol


@login_required(login_url="login")
def lista(request):
    registros = Registro.objects.filter(eliminado=False)
    return render(request, "calculo/lista.html", {"registros": registros})


@requiere_rol("admin", "normal")
def crear(request):
    if request.method == "POST":
        insumo = request.POST.get("insumo", "").strip()
        try:
            stock_actual = float(request.POST.get("stock_actual"))
            venta_proyectada = float(request.POST.get("venta_proyectada"))
        except (TypeError, ValueError):
            messages.error(request, "Stock y venta proyectada deben ser números válidos.")
            return render(request, "calculo/crear.html")

        if not insumo:
            messages.error(request, "El nombre del insumo es obligatorio.")
            return render(request, "calculo/crear.html")

        resultado = decidir(insumo, stock_actual, venta_proyectada)

        Registro.objects.create(
            insumo=resultado["insumo"],
            estado=resultado["estado"],
            detalle=resultado["detalle"],
            stock_actual=stock_actual,
            venta_proyectada=venta_proyectada,
        )
        messages.success(request, f"Registro de '{insumo}' creado correctamente.")
        return redirect("lista")

    return render(request, "calculo/crear.html")


@requiere_rol("admin")
def editar(request, pk):
    registro = get_object_or_404(Registro, pk=pk, eliminado=False)

    if request.method == "POST":
        insumo = request.POST.get("insumo", "").strip()
        try:
            stock_actual = float(request.POST.get("stock_actual"))
            venta_proyectada = float(request.POST.get("venta_proyectada"))
        except (TypeError, ValueError):
            messages.error(request, "Stock y venta proyectada deben ser números válidos.")
            return render(request, "calculo/editar.html", {"registro": registro})

        # Regla crítica: recalcular siempre que cambien los datos de entrada
        resultado = decidir(insumo, stock_actual, venta_proyectada)

        registro.insumo = resultado["insumo"]
        registro.stock_actual = stock_actual
        registro.venta_proyectada = venta_proyectada
        registro.estado = resultado["estado"]
        registro.detalle = resultado["detalle"]
        registro.save()

        messages.success(request, f"Registro de '{insumo}' actualizado correctamente.")
        return redirect("lista")

    return render(request, "calculo/editar.html", {"registro": registro})

@requiere_rol("admin")
@require_POST
def eliminar(request, pk):
    registro = get_object_or_404(Registro, pk=pk, eliminado=False)
    registro.soft_delete()
    messages.success(request, f"Registro de '{registro.insumo}' eliminado.")
    return redirect("lista")