from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    unidad = models.CharField(max_length=50)  # gramos, ml, unidades, etc.

    def __str__(self):
        return self.nombre


class Stock(models.Model):
    ingrediente = models.OneToOneField(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.FloatField()

    def __str__(self):
        return f"{self.ingrediente.nombre} - {self.cantidad}"


class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.FloatField()

    class Meta:
        unique_together = ('plato', 'ingrediente')
