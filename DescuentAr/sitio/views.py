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
            descuento.state = 'revision'
            descuento.save()
            return redirect('home.html')  # Redirige a una página de éxito
    else:
        form = DescuentoForm()
    return render(request, 'crear_descuento.html', {'form': form})




##################################### apis ###############################

@api_view(['GET'])
def obtener_votos(request, descuento_id):
    try:
        descuento = Descuento.objects.get(pk=descuento_id)
        votos_positivos = Voto.objects.filter(descuento=descuento, voto_positivo=True).count()
        votos_negativos = Voto.objects.filter(descuento=descuento, voto_positivo=False).count()
        
        data = {
            'votos_positivos': votos_positivos,
            'votos_negativos': votos_negativos,
        }    
        return Response(data)
    
    except Descuento.DoesNotExist:
        return Response({'error': 'Descuento no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_voto(request):
    descuento_id = request.data.get('descuento_id')
    voto_positivo = request.data.get('voto_positivo')  # True por defecto si no se envía

    try:
        descuento = Descuento.objects.get(pk=descuento_id)
        # Verificar si el usuario ya ha votado por este descuento
        voto_existente = Voto.objects.filter(usuario=request.user, descuento=descuento).first()
        if voto_existente is not None:
            if voto_existente != voto_positivo:
                voto_existente.voto_positivo = voto_positivo
                voto_existente.save()
                return Response({"message": "Voto actualizado correctamente"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Ya has votado por este descuento"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            nuevo_voto = Voto.objects.create(
                usuario=request.user,
                descuento=descuento,
                voto_positivo=voto_positivo
            )
    
            return Response({"message": "Voto registrado correctamente"}, status=status.HTTP_201_CREATED)

    except Descuento.DoesNotExist:
        return Response({"error": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)