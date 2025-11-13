from django.urls import path
from .views import mock_validar_reservar, mock_liberar, mock_confirmar, mock_cocina_pedidos

urlpatterns = [
    path("stock/validar-reservar", mock_validar_reservar),
    path("stock/liberar", mock_liberar),
    path("stock/confirmar", mock_confirmar),
    path("cocina/pedidos", mock_cocina_pedidos),
]
