from django.contrib import admin
from django.urls import path
from sitio.views import *

urlpatterns = [
    path('', home, name = 'home'),
    path('crear_descuento/', crear_descuento, name='crear_descuento'),
    path('api/guardar_voto/', guardar_voto, name='guardar_voto'),
    path('api/obtener_votos/<int:descuento_id>/', obtener_votos, name='obtener_votos'),
    path('detalle/<int:descuento_id>/', detalle_descuento, name='detalle_descuento'),
]