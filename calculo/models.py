from django.db import models
from django.utils import timezone


class Registro(models.Model):
    ESTADO_CHOICES = [
        ("Aceptado: Produccion requerida", "Producción requerida"),
        ("Rechazado: Stock suficiente", "Stock suficiente"),
        ("Rechazado: Alerta de sobrestock", "Alerta de sobrestock"),
        ("Error: Valores no validos", "Valores no válidos"),
    ]

    # --- Entradas: lo que ingresa el usuario en el formulario ---
    insumo = models.CharField(max_length=100, verbose_name="Insumo")
    stock_actual = models.FloatField(null=True, blank=True, verbose_name="Stock actual")
    venta_proyectada = models.FloatField(null=True, blank=True, verbose_name="Venta proyectada (M$)")

    # --- Salidas: lo que calcula decidir(), nunca las llena el usuario a mano ---
    estado = models.CharField(max_length=40, choices=ESTADO_CHOICES, verbose_name="Estado")
    detalle = models.CharField(max_length=200, verbose_name="Detalle")

    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha de evaluación")

    # --- Borrado lógico ---
    eliminado = models.BooleanField(default=False, verbose_name="Eliminado")
    fecha_eliminacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f"{self.insumo} - {self.estado}"

    def soft_delete(self):
        """Marca el registro como inactivo registrando la marca de tiempo, sin borrar la fila."""
        self.eliminado = True
        self.fecha_eliminacion = timezone.now()
        self.save()