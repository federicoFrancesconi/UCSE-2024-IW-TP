from django import forms
from .models import Descuento


class DateInput(forms.DateInput):
    input_type = 'date'

class DescuentoForm(forms.ModelForm):
    class Meta:
        model = Descuento
        fields = ['nombre', 'categoria', 'fecha_hasta', 'descripcion']
        widgets = {
            'fecha_hasta': DateInput(),
        }