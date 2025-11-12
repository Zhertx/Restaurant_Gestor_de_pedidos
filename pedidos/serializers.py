from rest_framework import serializers
from .models import Pedido

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ("id", "mesa", "cliente", "estado", "creado_en", "actualizado_en")

class PedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ("mesa", "cliente")
