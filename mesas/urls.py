from rest_framework.routers import DefaultRouter
from .views import MesaViewSet

router = DefaultRouter()
router.register(r'', MesaViewSet, basename='mesa')

urlpatterns = router.urls
