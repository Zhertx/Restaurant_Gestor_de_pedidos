from rest_framework import serializers
from .models import CategoriaMenu, Ingrediente, Plato, Receta

class CategoriaMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaMenu
        fields = "__all__"

class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = "__all__"

class RecetaSerializer(serializers.ModelSerializer):
    ingrediente = serializers.StringRelatedField()

    class Meta:
        model = Receta
        fields = ["ingrediente", "cantidad"]

class PlatoSerializer(serializers.ModelSerializer):
    categoria = CategoriaMenuSerializer(read_only=True)
    recetas = RecetaSerializer(many=True, read_only=True)

    class Meta:
        model = Plato
        fields = "__all__"
