from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse    
from django.contrib.auth.decorators import login_required
from .forms import DescuentoForm
from sitio.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, BooleanField, ExpressionWrapper
from datetime import datetime
from django.http import JsonResponse
from haystack.query import SearchQuerySet

ordenamiento = [
    ('1', 'fecha'),
    ('2', 'cantidad de votos')
]

def home(request):

    id_categoria = request.GET.get('id_categoria')
    fecha_hasta = request.GET.get('fecha_hasta')
    fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date() if fecha_hasta else None
    estado_descuento = request.GET.get('estado_descuento')
    ordenamiento_seleccionado = request.GET.get('ordenamiento_seleccionado')

    categorias = Categoria.objects.all()

    descuentos = Descuento.objects.all().annotate(
        votos_positivos=Count('voto', filter=Q(voto__voto_positivo=True)),
        votos_negativos=Count('voto', filter=Q(voto__voto_positivo=False)),
        diferencia_votos=Count('voto', filter=Q(voto__voto_positivo=True)) - Count('voto', filter=Q(voto__voto_positivo=False))
    )

    # Si el usuario no está loggeado le mostramos solo los descuentos publicados
    if not request.user.is_authenticated:
        descuentos = descuentos.filter(state='publicado')
    # Si el usuario está loggeado le mostramos los descuentos publicados y en revision
    else:
        descuentos = descuentos.filter(Q(state='publicado') | Q(state='revision'))
        if estado_descuento:
            descuentos = descuentos.filter(state=estado_descuento)

    if id_categoria:
        descuentos = descuentos.filter(categoria_id = id_categoria)
    
    #si trae el filtro lo hace, sino busca los vigentes 
    descuentos = descuentos.filter(fecha_hasta__lt=fecha) if fecha is not None else descuentos.filter(fecha_hasta__gte=datetime.today().date())


    descuentos = descuentos.order_by('-id')
    if ordenamiento_seleccionado is not None:
        if ordenamiento_seleccionado == 1:
            descuentos = descuentos.order_by('-fecha_hasta')
        else:
            descuentos = descuentos.order_by('-diferencia_votos')

    return render(request, 'home.html', {
        'lista_descuentos': descuentos,
        'categorias': categorias,
        'ordenamiento': ordenamiento,
        'ordenamienot_seleccionado' : ordenamiento_seleccionado,
        'categoria_seleccionada': id_categoria,
        'fecha_hasta_seleccionada': fecha_hasta,
        'estado_seleccionado': estado_descuento,
        'estados': ['publicado', 'revision'],
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

            notificar_suscriptores(request, descuento.id, descuento.categoria)

            return redirect('home')
    else:
        form = DescuentoForm()
    return render(request, 'crear_descuento.html', {'form': form})

from django.core import mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def notificar_suscriptores(request, descuentoId, categoria):
    connection = mail.get_connection()
    current_site = get_current_site(request)
    suscripciones_a_categoria = SuscripcionCategoria.objects.filter(categoria=categoria)

    suscriptores = [sc.usuario for sc in suscripciones_a_categoria]

    mails = []
    for suscriptor in suscriptores:
        email_recipiente = suscriptor.email
        
        # Armamos el mensaje de correo
        subject = "Nuevo Descuento!"
        mensaje = render_to_string('notificacion_nuevo_descuento.html', {
            'request': request,
            'user': suscriptor,
            'domain': current_site.domain,
            'id_descuento': descuentoId,
            'categoria':categoria
        })

        email = mail.EmailMessage(
            subject, mensaje, to=[email_recipiente]
        )
        email.content_subtype = 'html'

        mails.append(email)

    connection.send_messages(mails)

@login_required
def mis_publicaciones(request):

    descuentos = Descuento.objects.filter(usuario_creador=request.user).annotate(
        votos_positivos=Count('voto', filter=Q(voto__voto_positivo=True)),
        votos_negativos=Count('voto', filter=Q(voto__voto_positivo=False))
    )
    
    return render(request, 'mis_publicaciones.html', {'lista_descuentos': descuentos,})

@login_required
def guardados(request):
    descuentos_guardados = DescuentoGuardado.objects.filter(usuario=request.user).select_related('descuento')

    descuentos_ids = [dg.descuento.id for dg in descuentos_guardados]
    descuentos = Descuento.objects.filter(id__in=descuentos_ids).annotate(
        votos_positivos=Count('voto', filter=Q(voto__voto_positivo=True)),
        votos_negativos=Count('voto', filter=Q(voto__voto_positivo=False))
    )

    return render(request, 'guardados.html', {'lista_descuentos': descuentos,})

@login_required
def gestionar_suscripciones(request):
    categorias = Categoria.objects.all()
    categorias_suscritas = SuscripcionCategoria.objects.filter(usuario=request.user).values_list('categoria', flat=True)

    return render(request, 'gestionar_suscripciones.html', {
        'categorias': categorias,
        'categorias_suscritas': categorias_suscritas,
    })


##################################### apis ###############################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def eliminar_descuento(request, descuento_id):
    try:
        descuento = Descuento.objects.get(pk=descuento_id)

        if descuento.usuario_creador != request.user:
            return Response({"error": "No tienes permiso para eliminar este descuento"}, status=status.HTTP_403_FORBIDDEN)
        
        descuento.state = 'eliminado'
        descuento.save()

        return Response({"message": "Descuento marcado como eliminado correctamente"}, status=status.HTTP_200_OK)

    except Descuento.DoesNotExist:
        return Response({"error": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_votos(request, descuento_id):
    try:
        descuento = Descuento.objects.get(pk=descuento_id)
        votos_positivos = Voto.objects.filter(descuento=descuento, voto_positivo=True).count()
        votos_negativos = Voto.objects.filter(descuento=descuento, voto_positivo=False).count()
        
        # Inicializa variables para el estado del voto
        ya_votado = False
        voto_positivo = None
        
        if request.user.is_authenticated:
            # Comprueba si el usuario ha votado en este descuento
            voto = Voto.objects.filter(descuento=descuento, usuario=request.user).first()
            if voto:
                ya_votado = True
                voto_positivo = voto.voto_positivo
        
        data = {
            'votos_positivos': votos_positivos,
            'votos_negativos': votos_negativos,
            'ya_votado': ya_votado,
            'voto_positivo': voto_positivo,
        }    
        return Response(data)
    
    except Descuento.DoesNotExist:
        return Response({'error': 'Descuento no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_voto(request):
    descuento_id = request.data.get('descuento_id')
    voto_positivo = request.data.get('voto_positivo') == 'true'  # True por defecto si no se envía

    try:
        descuento = Descuento.objects.get(pk=descuento_id)
        # Verificar si el usuario ya ha votado por este descuento
        voto_existente = Voto.objects.filter(usuario=request.user, descuento=descuento).first()
        if voto_existente is not None:
            if voto_existente != voto_positivo:
                voto_existente.voto_positivo = voto_positivo
                voto_existente.save()

                validarEstadoDescuento(descuento, voto_existente)

                return Response({"message": "Voto actualizado correctamente", "estado_descuento": descuento.state}, status=status.HTTP_200_OK)
            else:
                print("ya has votado antes")
                return Response({"error": "Ya has votado por este descuento"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            nuevo_voto = Voto.objects.create(
                usuario=request.user,
                descuento=descuento,
                voto_positivo=voto_positivo
            )

            validarEstadoDescuento(descuento, nuevo_voto)

            return Response({"message": "Voto registrado correctamente", "estado_descuento": descuento.state}, status=status.HTTP_201_CREATED)

    except Descuento.DoesNotExist:
        return Response({"error": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def retirar_voto(request):
    try:
        descuento_id = request.data.get('descuento_id')
        usuario = request.user

        # Verifica que el usuario esté autenticado
        if not usuario.is_authenticated:
            return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

        # Obtiene el voto del usuario
        voto = Voto.objects.get(descuento_id=descuento_id, usuario=usuario)
        voto.delete()  # Elimina el voto

        return Response({'message': 'Voto retirado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    except Voto.DoesNotExist:
        return Response({'error': 'Voto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validarEstadoDescuento(descuento, voto):
    if voto.voto_positivo:
        if descuento.state == 'revision':
            if descuento.get_total_votos() >= 2 and descuento.get_ratio_votos() >= 2:
                descuento.state = 'publicado'
                descuento.save()
    else:
        if descuento.state == 'publicado':
            if descuento.get_ratio_votos() <= 1.5:
                descuento.state = 'suspendido'
                descuento.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_guardado(request, descuento_id):
    usuario = request.user

    try:
        descuento = Descuento.objects.get(pk=descuento_id)

        descuento_existente = DescuentoGuardado.objects.filter(descuento=descuento, usuario=usuario).first()

        guardado = descuento_existente is not None
        
        data = {
            'guardado': guardado
        }    
        return Response(data)
    
    except Descuento.DoesNotExist:
        return Response({'error': 'Descuento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# Usamos una lógica de tipo "toggle": si estaba guardado, lo borramos, si no, lo guardamos
# Si bien los principios HTTP dicen que esto se separa
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_descuento(request):
    usuario = request.user
    descuento_id = request.data.get('descuento_id')

    try:
        descuento = Descuento.objects.get(pk=descuento_id)

        # Verificar si el usuario ya guardo este descuento
        descuento_existente = DescuentoGuardado.objects.filter(descuento=descuento, usuario=usuario).first()

        if descuento_existente is not None:
            descuento_existente.delete()
            return Response({"message": "Descuento quitado de guardados"}, status=status.HTTP_200_OK)
        else:
            DescuentoGuardado.objects.create(
                usuario=usuario,
                descuento=descuento
            )
    
            return Response({"message": "Descuento guardado correctamente"}, status=status.HTTP_201_CREATED)

    except Descuento.DoesNotExist:
        return Response({"error": "Descuento no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@login_required
def suscribir_categoria(request):
    categoria_id = request.POST.get('categoria_id')
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    # Crear la suscripción
    SuscripcionCategoria.objects.create(usuario=request.user, categoria=categoria)
    return JsonResponse({'message': 'Suscripción exitosa'}, status=201)

@api_view(['POST'])
@login_required
def desuscribir_categoria(request):
    categoria_id = request.POST.get('categoria_id')
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    # Eliminar la suscripción
    SuscripcionCategoria.objects.filter(usuario=request.user, categoria=categoria).delete()
    return JsonResponse({'message': 'Desuscripción exitosa'}, status=200)

# ----------------------------------------------------
# View proporcionada por la cátedra para poder reconstruir el índice de whoosh de la búsqueda interna

def rebuild_index(request):
    from django.core.management import call_command
    from django.http import JsonResponse
    try:
        call_command("rebuild_index", noinput=False)
        result = "Index rebuilt"
    except Exception as err:
        result = f"Error: {err}"

    return JsonResponse({"result": result})


def search_descuento(request):
    query = request.GET.get('buscar')

    if query:
        results = SearchQuerySet().filter(nombre__icontains = query)
    else:
        results = []

    return render(request, 'search/search.html', {'resultados': results})