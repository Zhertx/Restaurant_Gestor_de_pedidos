from django.db import models

class CategoriaMenu(models.Model):
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    plato = models.ForeignKey(Plato, related_name="recetas", on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
