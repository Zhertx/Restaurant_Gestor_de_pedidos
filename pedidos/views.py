from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Pedido
from .serializers import PedidoSerializer, PedidoCreateSerializer
from .adapters import StockClientM1, CocinaClientM4, build_signature

import hmac

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by("-creado_en")
    serializer_class = PedidoSerializer

    def get_serializer_class(self):
        # Usa tu serializer de creación cuando corresponda
        if getattr(self, "action", None) == "create":
            return PedidoCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        # Crea pedido con tu serializer de creación
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        pedido = Pedido.objects.create(**ser.validated_data)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """
        Paso 1: validar/reservar en M1
        Paso 2: enviar a M4
        Si falla M1 -> 400/502; si falla M4 -> liberar reserva y revertir a CREADO.
        """
        pedido = self.get_object()
        if pedido.estado != "CREADO":
            return Response({"detail": "Solo pedidos CREADO se pueden confirmar."}, status=400)

        if not pedido.items:
            return Response({"detail": "El pedido no tiene items."}, status=400)

        m1 = StockClientM1()
        m4 = CocinaClientM4()

        # 1) Validar/Reservar stock en M1
        try:
            resp = m1.validar_reservar(pedido.id, pedido.items)
        except Exception as e:
            return Response({"detail": f"Error contactando M1: {e}"}, status=502)

        if not resp.get("ok"):
            return Response({"detail": resp.get("error", "Sin stock disponible")}, status=400)

        pedido.reserva_id = resp.get("reserva_id")
        pedido.estado = "EN_PREPARACION"
        pedido.save()

        # 2) Enviar a cocina (M4)
        try:
            m4.enviar_pedido(pedido)
        except Exception as e:
            # liberar reserva si falla el envío a M4
            try:
                if pedido.reserva_id:
                    m1.liberar_reserva(pedido.reserva_id)
            except:
                pass
            pedido.reserva_id = None
            pedido.estado = "CREADO"
            pedido.save()
            return Response({"detail": f"Error enviando a M4: {e}"}, status=502)

        return Response(PedidoSerializer(pedido).data, status=200)

    @action(detail=True, methods=["patch"])
    def entregar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado != "LISTO":
            return Response({"detail": "Solo pedidos LISTO pueden pasar a ENTREGADO."}, status=400)
        pedido.estado = "ENTREGADO"
        pedido.save()
        return Response(PedidoSerializer(pedido).data)

    @action(detail=True, methods=["patch"])
    def cerrar(self, request, pk=None):
        """
        Confirma descuento definitivo en M1 y pasa a CERRADO.
        """
        pedido = self.get_object()
        if pedido.estado != "ENTREGADO":
            return Response({"detail": "Solo pedidos ENTREGADO pueden pasar a CERRADO."}, status=400)
        if not pedido.reserva_id:
            return Response({"detail": "No hay reserva asociada."}, status=400)

        m1 = StockClientM1()
        try:
            resp = m1.confirmar_descuento(pedido.reserva_id)
        except Exception as e:
            return Response({"detail": f"Error confirmando descuento en M1: {e}"}, status=502)

        if not resp.get("ok", True):
            return Response({"detail": resp.get("error", "No se pudo confirmar stock")}, status=400)

        pedido.estado = "CERRADO"
        pedido.save()
        return Response(PedidoSerializer(pedido).data)

    @action(detail=True, methods=["post", "patch"])
    def cancelar(self, request, pk=None):
        """
        Cancela el pedido y libera la reserva en M1 si existía.
        """
        pedido = self.get_object()
        if pedido.estado in ("CERRADO", "CANCELADO"):
            return Response({"detail": "Pedido ya finalizado."}, status=400)

        if pedido.reserva_id:
            m1 = StockClientM1()
            try:
                m1.liberar_reserva(pedido.reserva_id)
            except:
                # se registra en logs si quieres, pero no bloquea la cancelación
                pass

        pedido.estado = "CANCELADO"
        pedido.reserva_id = None
        pedido.save()
        return Response(PedidoSerializer(pedido).data, status=200)


class WebhookCocinaReady(APIView):
    """
    Webhook para que M4 notifique 'LISTO'
    POST /api/webhooks/cocina/pedido-listo
    Header: X-Signature: hmac_sha256(body, M3_WEBHOOK_SECRET)
    Body:   {"pedido_id":"<uuid>","estado":"LISTO"}
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        sig = request.headers.get("X-Signature")
        body_bytes = request.body or b""

        expected = build_signature(settings.M3_WEBHOOK_SECRET, body_bytes)
        if not sig or not hmac.compare_digest(sig, expected):
            return Response({"detail": "Firma inválida"}, status=401)

        pedido_id = request.data.get("pedido_id")
        estado = request.data.get("estado")

        if estado != "LISTO":
            return Response({"detail": "Estado no soportado"}, status=400)

        pedido = get_object_or_404(Pedido, pk=pedido_id)
        if pedido.estado != "EN_PREPARACION":
            return Response({"detail": "Pedido no está en preparación"}, status=400)

        pedido.estado = "LISTO"
        pedido.save()
        return Response({"ok": True})
