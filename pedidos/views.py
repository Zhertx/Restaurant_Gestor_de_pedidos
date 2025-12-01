from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Pedido
from .serializers import PedidoSerializer


class PedidoViewSet(ModelViewSet):
    """
    API de Pedidos.

    Endpoints generados automáticamente por el router:
    - GET    /api/pedidos/           -> list
    - POST   /api/pedidos/           -> create
    - GET    /api/pedidos/{id}/      -> retrieve
    - PUT    /api/pedidos/{id}/      -> update
    - PATCH  /api/pedidos/{id}/      -> partial_update
    - DELETE /api/pedidos/{id}/      -> destroy

    Acciones personalizadas:
    - POST   /api/pedidos/{id}/confirmar/
    - POST   /api/pedidos/{id}/cancelar/
    - PATCH  /api/pedidos/{id}/listo/
    - PATCH  /api/pedidos/{id}/entregar/
    - PATCH  /api/pedidos/{id}/cerrar/
    """

    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """
        Confirma el pedido: valida stock (Módulo 1) y lo pasa a EN_PREPARACION.
        """
        pedido = self.get_object()
        try:
            pedido.confirmar()  # método del modelo
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """
        Cancela el pedido y libera el stock reservado.
        """
        pedido = self.get_object()
        try:
            pedido.cancelar()  # método del modelo
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def listo(self, request, pk=None):
        """
        Marca el pedido como LISTO desde la cocina.

        Este endpoint lo llama el webhook:
          POST /api/webhooks/cocina/pedido-listo/
        que internamente hace PATCH a:
          /api/pedidos/{id}/listo/
        """
        pedido = self.get_object()
        try:
            pedido.marcar_listo()  # método del modelo
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def entregar(self, request, pk=None):
        """
        Marca el pedido como ENTREGADO al cliente.
        """
        pedido = self.get_object()
        try:
            pedido.entregar()  # método del modelo
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def cerrar(self, request, pk=None):
        """
        Cierra el pedido (venta finalizada).
        """
        pedido = self.get_object()
        try:
            pedido.cerrar()  # método del modelo
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def cocina_estado(request):
    """
    Cambia el estado desde la 'pantalla de cocina'.
    body: { "pedido_id": "<uuid>", "estado": "EN_PREPARACION|LISTO|CANCELADO" }
    """
    pid = request.data.get("pedido_id")
    estado = request.data.get("estado")
    if not pid or not estado:
        return Response(
            {"detail": "pedido_id y estado son requeridos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        p = Pedido.objects.get(pk=pid)
        if estado == "EN_PREPARACION":
            if p.estado != Pedido.Estado.CREADO:
                return Response(
                    {"detail": "Solo desde CREADO."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            p.estado = Pedido.Estado.EN_PREPARACION
            p.full_clean()
            p.save(update_fields=["estado", "actualizado_en"])
        elif estado == "LISTO":
            p.marcar_listo()
        elif estado == "CANCELADO":
            p.cancelar()
        else:
            return Response({"detail": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoSerializer(p).data)
    except Pedido.DoesNotExist:
        return Response({"detail": "Pedido no existe."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def cocina_list(request):
    """
    Devuelve pedidos activos para visualizar en la cocina.
    (excluye CANCELADO y CERRADO)
    """
    activos = Pedido.objects.exclude(
        estado__in=[Pedido.Estado.CANCELADO, Pedido.Estado.CERRADO]
    ).order_by("creado_en")
    return Response(PedidoSerializer(activos, many=True).data)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import PedidoPublicoForm
from .models import Pedido, PedidoImagen
from django.views.decorators.http import require_http_methods
from django.contrib import messages

@require_http_methods(["GET", "POST"])
def formulario_publico(request, producto_pk=None):
    """
    Formulario público para crear un pedido desde la web.
    Si se envía POST: crea Pedido, guarda imágenes y redirige a seguimiento.
    """
    initial = {}
    if producto_pk:
        initial['producto'] = producto_pk

    if request.method == 'POST':
        form = PedidoPublicoForm(request.POST, request.FILES, initial=initial)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.plataforma = 'web'
            pedido.estado = 'solicitado'
            pedido.estado_pago = 'pendiente'
            pedido.save()

            archivos = request.FILES.getlist('imagenes')
            for f in archivos:
                PedidoImagen.objects.create(pedido=pedido, imagen=f)

            messages.success(request, 'Pedido creado correctamente.')
            return redirect('pedidos:seguimiento', token=pedido.token)
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = PedidoPublicoForm(initial=initial)

    return render(request, 'pedidos/form_publico.html', {'form': form})
    def seguimiento_pedido(request, token):
    pedido = get_object_or_404(Pedido, token=token)
    return render(request, 'pedidos/seguimiento.html', {'pedido': pedido})

