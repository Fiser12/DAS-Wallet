__author__ = 'Fiser'
from rest_framework import serializers
from Wallet.models import Cuenta, Apunte, Etiqueta


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = ('owner','id','nombre','saldoInicial',)
class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = ('id','titulo',)

class ApunteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apunte
        fields = ('id','descripcion', 'dinero', 'cuentaOrigen', 'cuentaDestino', 'ingresoGastoTransferencia', 'fecha', 'etiquetas')


