__author__ = 'Fiser'
from rest_framework import serializers

from Wallet.models import Cuenta, Apunte, Categoria


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = ('owner', 'id', 'nombre', 'saldoInicial',)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'titulo',)


class ApunteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apunte
        fields = ('id', 'descripcion', 'dinero', 'cuentaOrigen', 'cuentaDestino', 'ingresoGastoTransferencia', 'fecha',
                  'categoria')

class CategoriaSerializerWithMoreData(object):
    categoria = Categoria
    apuntes = []
    dinero = 0
    def __init__(self, categoria, apuntes, dinero):
        self.dinero = dinero
        self.apuntes = apuntes
        self.categoria = categoria
    def __cmp__(self, other):
        return cmp(self.dinero, other.dinero)
