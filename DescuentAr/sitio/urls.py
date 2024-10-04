from django.contrib import admin
from django.urls import path
from sitio.views import *

urlpatterns = [
    path('', home, name = 'home'),
    path('crear_descuento/', crear_descuento, name='crear_descuento'),
    path('mis_publicaciones/', mis_publicaciones, name='mis_publicaciones'),
    path('api/guardar_voto/', guardar_voto, name='guardar_voto'),
    path('api/obtener_votos/<int:descuento_id>/', obtener_votos, name='obtener_votos'),
    path('detalle/<int:descuento_id>/', detalle_descuento, name='detalle_descuento'),
    path('guardados/', guardados, name='guardados'),
    path('api/obtener_guardado/<int:descuento_id>/', obtener_guardado, name='obtener_guardado'),
    path('api/guardar_descuento/', guardar_descuento, name='guardar_descuento'),
    path('suscripciones/', gestionar_suscripciones, name='gestionar_suscripciones'),
    path('api/suscribir_categoria/', suscribir_categoria, name='suscribir_categoria'),
    path('api/desuscribir_categoria/', desuscribir_categoria, name='desuscribir_categoria'),
]