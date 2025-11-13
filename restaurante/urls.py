from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path("", lambda r: HttpResponseRedirect("/api/")),
    path("admin/", admin.site.urls),
    path("api/", include("pedidos.urls")),
    path("mock/", include("mock.urls")),
]
