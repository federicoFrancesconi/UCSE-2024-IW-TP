# Importamos los formularios personalizados que creamos en forms.py
from .forms import CustomUserCreationForm, CustomAuthenticationForm
# Usamos reverse_lazy porque la URL todavía no está cargada cuando importamos el archivo
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"