from django.shortcuts import render, redirect
from django.http import HttpResponse    

# Create your views here.
def home(request):
    return HttpResponse('<h1>PAGINA DE INICIO <h1>')
    # return render(request, 'home.html', {})