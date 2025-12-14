from rest_framework import viewsets
from .models import CategoriaMenu, Ingrediente, Plato
from .serializers import CategoriaMenuSerializer, IngredienteSerializer, PlatoSerializer

class CategoriaMenuViewSet(viewsets.ModelViewSet):
    queryset = CategoriaMenu.objects.all()
    serializer_class = CategoriaMenuSerializer

class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer

class PlatoViewSet(viewsets.ModelViewSet):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer
