from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DateTimeField
import datetime, time
from django.conf import settings

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
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank = True, null= True)
    fecha_hasta = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATES_DESCUENTO, verbose_name='Estado', null=True)

    def __str__(self):
        return self.nombre
    
    def get_total_votos(self):
        return self.voto_set.count()
    
    def get_ratio_votos(self):
        total_votos = self.get_total_votos()
        positivos = self.voto_set.filter(voto_positivo=True).count()
        negativos = total_votos - positivos
        
        if total_votos == 0:
            return 0

        if negativos == 0:
            # Si no hay negativos, el ratio es infinito
            return float('inf')
        else:
            return positivos / negativos

class Voto(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    descuento = models.ForeignKey(Descuento, on_delete=models.CASCADE)
    voto_positivo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario} - {self.descuento} - {'Positivo' if self.voto_positivo else 'Negativo'}"
    
class DescuentoGuardado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    descuento = models.ForeignKey(Descuento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.descuento}"

class SuscripcionCategoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank = True, null= True)

    def __str__(self):
        return f"{self.usuario} - {self.categoria}"