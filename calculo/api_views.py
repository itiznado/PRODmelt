from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from solucion import decidir
from .models import Registro
from .serializers import RegistroSerializer
from .permissions import PermisoDiferenciadoRegistro


class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.filter(eliminado=False).order_by("-fecha")
    serializer_class = RegistroSerializer
    permission_classes = [PermisoDiferenciadoRegistro]

    def _aplicar_regla(self, serializer):
        """Ejecuta decidir() con los datos nuevos y, si es PATCH, con los que ya tenía el registro."""
        datos = serializer.validated_data
        actual = serializer.instance

        def valor(campo):
            return datos[campo] if campo in datos else getattr(actual, campo)

        return decidir(valor("insumo"), valor("stock_actual"), valor("venta_proyectada"))

    def perform_create(self, serializer):
        r = self._aplicar_regla(serializer)
        serializer.save(estado=r["estado"], detalle=r["detalle"])

    def perform_update(self, serializer):
        r = self._aplicar_regla(serializer)
        serializer.save(estado=r["estado"], detalle=r["detalle"])

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def aceptados(self, request):
        """GET /api/registros/aceptados/ -> solo los que requieren producción."""
        qs = self.get_queryset().filter(estado__startswith="Aceptado")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)