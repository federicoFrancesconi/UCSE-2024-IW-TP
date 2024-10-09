from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

#dmin.site.register(CustomUser, UserAdmin)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "email_is_verified", "state")