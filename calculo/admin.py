from django.contrib import admin
from .models import Registro


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ("insumo", "estado", "stock_actual", "venta_proyectada", "detalle", "fecha", "eliminado")
    list_filter = ("estado", "eliminado")
    search_fields = ("insumo", "detalle")
    readonly_fields = ("fecha", "fecha_eliminacion")

    def get_queryset(self, request):
        # El admin debe poder auditar todo, incluidos los eliminados lógicamente
        return super().get_queryset(request)