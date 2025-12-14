from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    CategoriaMenu,
    Ingrediente,
    Plato,
    Receta,
)
from .serializers import (
    CategoriaMenuSerializer,
    IngredienteSerializer,
    PlatoSerializer,
)


class CategoriaMenuViewSet(viewsets.ModelViewSet):
    queryset = CategoriaMenu.objects.all()
    serializer_class = CategoriaMenuSerializer


class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer


class PlatoViewSet(viewsets.ModelViewSet):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer


class StockViewSet(viewsets.ViewSet):
    """
    Endpoint para validar y reservar stock
    """

    @action(detail=False, methods=["post"])
    def validar_reservar(self, request):
        """
        Body esperado:
        {
          "platos": [
            {"plato_id": 1, "cantidad": 2}
          ]
        }
        """

        platos = request.data.get("platos", [])

        if not platos:
            return Response(
                {"error": "No se enviaron platos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        faltantes = []

        # Validar stock
        for item in platos:
            plato_id = item["plato_id"]
            cantidad_pedida = item["cantidad"]

            recetas = Receta.objects.filter(plato_id=plato_id)

            for receta in recetas:
                requerido = receta.cantidad * cantidad_pedida
                if receta.ingrediente.cantidad_disponible < requerido:
                    faltantes.append({
                        "ingrediente": receta.ingrediente.nombre,
                        "disponible": receta.ingrediente.cantidad_disponible,
                        "requerido": requerido,
                    })

        if faltantes:
            return Response(
                {
                    "ok": False,
                    "faltantes": faltantes,
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Reservar stock (descontar)
        for item in platos:
            plato_id = item["plato_id"]
            cantidad_pedida = item["cantidad"]

            recetas = Receta.objects.filter(plato_id=plato_id)

            for receta in recetas:
                receta.ingrediente.cantidad_disponible -= (
                    receta.cantidad * cantidad_pedida
                )
                receta.ingrediente.save()

        return Response(
            {"ok": True, "mensaje": "Stock reservado"},
            status=status.HTTP_200_OK,
        )
