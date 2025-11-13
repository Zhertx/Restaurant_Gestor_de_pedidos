# pedidos/admin.py
from django.contrib import admin
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "mesa", "cliente", "estado", "creado_en")
    search_fields = ("mesa", "cliente", "id")
    list_filter = ("estado", "creado_en")
