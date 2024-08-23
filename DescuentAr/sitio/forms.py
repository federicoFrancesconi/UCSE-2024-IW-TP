from django import forms
from .models import Descuento

class DescuentoForm(forms.ModelForm):
    class Meta:
        model = Descuento
        fields = ['nombre', 'fecha_hasta', 'descripcion']