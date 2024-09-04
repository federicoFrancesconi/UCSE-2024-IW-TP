from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "id")
@admin.register(Descuento)
class DescuentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "id", "descripcion", "fecha_hasta", "categoria", "state")


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("descuento", "usuario", "voto_positivo")

