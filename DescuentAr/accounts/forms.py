from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# Form personalizado para login que usa email en lugar de username
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", required=True)

# Form personalizado para registration, que incluye email
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # Anulamos la seccion de habilitar autenticación basada en contraseñas
    usable_password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            # No modifico el campo email_is_verified porque por default es False
            user.save()
        return user