import uuid
from django.db import models

class Pedido(models.Model):
    class Estado(models.TextChoices):
        CREADO = "CREADO", "Creado"
        EN_PREPARACION = "EN_PREPARACION", "En preparación"
        LISTO = "LISTO", "Listo"
        ENTREGADO = "ENTREGADO", "Entregado"
        CERRADO = "CERRADO", "Cerrado"
        CANCELADO = "CANCELADO", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mesa = models.CharField(max_length=20, null=True, blank=True)
    cliente = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.CREADO)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def puede_modificarse(self):
        return self.estado == Pedido.Estado.CREADO

    def __str__(self):
        return f"Pedido {self.id} (mesa={self.mesa or '-'}, estado={self.estado})"
