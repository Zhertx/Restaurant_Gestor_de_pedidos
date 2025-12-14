from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaMenuViewSet,
    IngredienteViewSet,
    PlatoViewSet,
    StockViewSet,
)

router = DefaultRouter()
router.register(r"categorias", CategoriaMenuViewSet)
router.register(r"ingredientes", IngredienteViewSet)
router.register(r"platos", PlatoViewSet)
router.register(r"stock", StockViewSet, basename="stock")

urlpatterns = router.urls
