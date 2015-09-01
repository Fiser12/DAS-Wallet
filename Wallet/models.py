from django.db import models

class Cuenta(models.Model):
    owner = models.ForeignKey('auth.User', related_name='user')
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    saldoInicial = models.FloatField()
class Etiqueta(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
class Apunte(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    dinero = models.FloatField()
    cuentaOrigen = models.ForeignKey(Cuenta, related_name="cuentaOrigen")
    cuentaDestino = models.ForeignKey(Cuenta, related_name="cuentaDestino")
    ingresoGastoTransferencia = models.IntegerField()
    fecha = models.DateTimeField()
    etiquetas = models.ManyToManyField(Etiqueta, related_name="etiquetas")