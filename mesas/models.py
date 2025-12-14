from django.db import models

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=20, choices=[('disponible', 'Disponible'), ('reservada', 'Reservada'), ('ocupada', 'Ocupada')])
    ubicacion = models.CharField(max_length=50)

    def __str__(self):
        return f"Mesa {self.numero} ({self.estado})"
