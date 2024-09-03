from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DateTimeField
import datetime, time

# Create your models here.

STATES_DESCUENTO = [
    ('publicado', 'PUBLICADO'),
    ('revision', 'REVISION'),
    ('eliminado', 'ELIMINADO'),
    ('suspendido', 'SUSPENDIDO')
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=25, blank = False)
        
    def __str__(self):
        return self.nombre

class Descuento(models.Model):
    nombre = models.CharField(max_length=50, blank = False)
    descripcion = models.TextField(max_length=200, blank = False)
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank = True, null= True)
    fecha_hasta = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATES_DESCUENTO, verbose_name='Estado', null=True)

    def __str__(self):
        return self.nombre
    

class Voto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descuento = models.ForeignKey(Descuento, on_delete=models.CASCADE)
    voto_positivo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario} - {self.descuento} - {'Positivo' if self.voto_positivo else 'Negativo'}"