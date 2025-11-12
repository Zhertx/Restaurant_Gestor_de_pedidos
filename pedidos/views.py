from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Pedido
from .serializers import PedidoSerializer, PedidoCreateSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by("-creado_en")
    serializer_class = PedidoSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return PedidoCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        pedido = Pedido.objects.create(**ser.validated_data)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)
