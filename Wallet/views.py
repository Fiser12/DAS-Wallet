from rest_framework import viewsets
from .models import Cuenta, Apunte, Etiqueta
from .serializers import CuentaSerializer, ApunteSerializer, EtiquetaSerializer

class CuentaViewSet(viewsets.ModelViewSet):
    serializer_class = CuentaSerializer
    queryset = Cuenta.objects.all()

class ApunteViewSet(viewsets.ModelViewSet):
    serializer_class = ApunteSerializer
    queryset = Apunte.objects.all()

class EtiquetaViewSet(viewsets.ModelViewSet):
    serializer_class = EtiquetaSerializer
    queryset = Etiqueta.objects.all()


