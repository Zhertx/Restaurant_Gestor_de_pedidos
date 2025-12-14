from rest_framework.routers import DefaultRouter
from .views import CategoriaMenuViewSet, IngredienteViewSet, PlatoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaMenuViewSet)
router.register(r'ingredientes', IngredienteViewSet)
router.register(r'platos', PlatoViewSet)

urlpatterns = router.urls
