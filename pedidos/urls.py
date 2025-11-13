from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PedidoViewSet, WebhookCocinaReady

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedidos')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/cocina/pedido-listo', WebhookCocinaReady.as_view()),
]
