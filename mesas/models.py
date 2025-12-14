from django.db import models

class Mesa(models.Model):
    ESTADOS = [
        ('LIBRE', 'Libre'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
    ]

    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='LIBRE')

    def __str__(self):
        return f"Mesa {self.numero} ({self.estado})"
