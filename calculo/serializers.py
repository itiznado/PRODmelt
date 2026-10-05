from rest_framework import serializers
from .models import Registro


class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ["id", "insumo", "stock_actual", "venta_proyectada", "estado", "detalle", "fecha"]
        read_only_fields = ["estado", "detalle", "fecha"]
        extra_kwargs = {
            "stock_actual": {"required": True, "allow_null": False},
            "venta_proyectada": {"required": True, "allow_null": False},
        }

    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock actual no puede ser negativo.")
        return value

    def validate_venta_proyectada(self, value):
        if value < 0:
            raise serializers.ValidationError("La venta proyectada no puede ser negativa.")
        return value