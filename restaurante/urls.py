from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("ui.urls","ui"), namespace="ui")),
    path("mock/", include("mock.urls")),     # ← para cargar /mock/menu/ y /mock/stock/estado/
    path("api/", include("pedidos.urls")),   # ← tu API real DRF
    path("api/webhooks/", include(("mock.urls","mock"), namespace="mock")),
]
