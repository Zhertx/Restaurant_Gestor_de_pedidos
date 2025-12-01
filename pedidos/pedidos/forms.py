from django import forms
from .models import Pedido

class PedidoPublicoForm(forms.ModelForm):
    imagenes = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label='Imágenes de referencia'
    )

    class Meta:
        model = Pedido
        fields = ['cliente_nombre', 'email', 'telefono', 'descripcion', 'producto', 'fecha_entrega']
