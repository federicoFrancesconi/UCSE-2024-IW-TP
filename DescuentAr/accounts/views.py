from django.contrib.auth.forms import UserCreationForm
#Note that we use reverse_lazy to redirect users to the login page upon successful registration rather than reverse,
# because for all generic class-based views, the URLs are not loaded when the file is imported,
# so we have to use the lazy form of reverse to load them later when we are sure they're available.
from django.urls import reverse_lazy
from django.views.generic import CreateView


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"