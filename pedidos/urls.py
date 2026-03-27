from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, cocina_estado, cocina_list

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path("cocina/estado/", cocina_estado, name="cocina-estado"),
    path("cocina/lista/", cocina_list, name="cocina-lista"),
]

urlpatterns += router.urls
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('solicitar/', views.formulario_publico, name='form_publico'),
    path('solicitar/<int:producto_pk>/', views.formulario_publico, name='form_publico_producto'),
    path('seguimiento/<str:token>/', views.seguimiento_pedido, name='seguimiento'),
]
