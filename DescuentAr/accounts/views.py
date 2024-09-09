# Importamos los formularios personalizados que creamos en forms.py
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Usamos reverse_lazy porque la URL todavía no está cargada cuando importamos el archivo
from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        # Extrae el usuario y contraseña del formulario
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Autenticamos el usuario para conocer el campo email_is_verified
        user = authenticate(request=self.request, username=username, password=password)

        if user is not None:
            # Loggeamos manualmente el usuario para que podamos acceder a sus datos de necesitar verificar el mail
            login(self.request, user)

            if user.email_is_verified:
                return redirect('home')
            else:
                # Si el email no fue verificado, redireccionamos a la vista de verificación
                messages.error(self.request, 'Debe verificar el email antes de iniciar sesión.')
                return redirect('verify-email')
        else:
            # Si la autenticación falla, dejamos que lo maneje el LoginView
            return self.form_invalid(form)

from django.contrib.auth import login

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("verify-email")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save()
        # Loggeamos manualmente el usuario para que podamos acceder a sus datos al verificar el email
        login(self.request, user)
        # Hacemos un redirect a la url de verificación del email
        return redirect(self.success_url)

from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages

User = get_user_model()

# Si el usuario no tiene email verificado, se genera un token y se le envía un mail de verificación
def verify_email(request):
    # Si me hace un post es porque le dió submit en el formulario
    if request.method == "POST":
        if request.user.email_is_verified != True:
            current_site = get_current_site(request)
            user = request.user
            email = request.user.email

            # Cerramos la sesion del usuario porque solo lo habiamos loggeado para conocer sus atributos
            logout(request)

            # Armamos el mensaje de correo
            subject = "Verificá tu correo"
            message = render_to_string('registration/verify_email_message.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })

            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()

            return redirect('verify-email-done')
        else:
            return redirect('signup')
    return render(request, 'registration/verify_email.html')

# Alerta al usuario cuando se le envió el mail de verificación
def verify_email_done(request):
    return render(request, 'registration/verify_email_done.html')

# Verifica el link de verificación del email
# Para eso revisa si el token es valido y "activa" el usuario
def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Tu correo fue verificado.')
        return redirect('verify-email-complete')   
    else:
        messages.warning(request, 'El link de verificación es inválido.')
    return render(request, 'registration/verify_email_confirm.html')

def verify_email_complete(request):
    return render(request, 'registration/verify_email_complete.html')