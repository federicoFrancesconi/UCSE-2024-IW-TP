from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

STATES= [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('eliminado', 'Eliminado')
    ]

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    email_is_verified = models.BooleanField(default=False)
    state = models.CharField(choices=STATES, max_length=15,name='state', null=True, default='activo')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']  # El campo usuario no es el identificador, pero es requerido

    objects = CustomUserManager()

    def __str__(self):
        return self.email