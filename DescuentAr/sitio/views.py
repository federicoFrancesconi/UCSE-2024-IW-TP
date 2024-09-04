from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse    
from django.contrib.auth.decorators import login_required
from .forms import DescuentoForm
from sitio.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from datetime import datetime

# Create your views here.
def home(request):

    categoria_id = request.GET.get('categoria_id')
    fecha_hasta = request.GET.get('fecha_hasta')
    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date() if fecha_hasta else None
    cant_votos = request.GET.get('cant_votos')

    categorias = Categoria.objects.all()

    descuentos = Descuento.objects.all().annotate(
        votos_positivos=Count('voto', filter=Q(voto__voto_positivo=True)),
        votos_negativos=Count('voto', filter=Q(voto__voto_positivo=False)),
        diferencia_votos=Count('voto', filter=Q(voto__voto_positivo=True)) - Count('voto', filter=Q(voto__voto_positivo=False))
    )

    if categoria_id:
        descuentos = descuentos.filter(categoria_id = categoria_id)
    

    #si trae el filtro lo hace, sino busca los vigentes 
    descuentos = descuentos.filter(fecha_hasta__lt=fecha) if fecha is not None else descuentos.filter(fecha_hasta__gte=datetime.today().date())

    if cant_votos:
        descuentos = descuentos.filter(diferencia_votos__gte=int(cant_votos))

    return render(request, 'home.html', {
        'lista_descuentos': descuentos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'cant_votos_seleccionada': cant_votos,
    })

def detalle_descuento(request, descuento_id):
    descuento = get_object_or_404(Descuento, pk=descuento_id)
    return render(request, 'detalle.html', {'descuento': descuento})


@login_required
def crear_descuento(request):
    if request.method == 'POST':
        form = DescuentoForm(request.POST)
        if form.is_valid():
            descuento = form.save(commit=False)
            descuento.usuario_creador = request.user
            descuento.save()
            return redirect('home.html')  # Redirige a una página de éxito
    else:
        form = DescuentoForm()
    return render(request, 'crear_descuento.html', {'form': form})