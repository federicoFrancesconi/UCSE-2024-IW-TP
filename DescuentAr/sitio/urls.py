from django.contrib import admin
from django.urls import path
from sitio.views import *

urlpatterns = [
    path('', home, name = 'home'),
]