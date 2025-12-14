from rest_framework.viewsets import ModelViewSet
from .models import Mesa
from .serializers import MesaSerializer

class MesaViewSet(ModelViewSet):
    queryset = Mesa.objects.all().order_by("numero")
    serializer_class = MesaSerializer
