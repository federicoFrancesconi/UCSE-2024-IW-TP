from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse    
from django.contrib.auth.decorators import login_required
from .forms import DescuentoForm
from sitio.models import *

# Create your views here.
def home(request):
    descuentos = Descuento.objects.all()

    return render(request, 'home.html', {'lista_descuentos': descuentos})

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