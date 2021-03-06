from audioop import reverse

from django.contrib.auth.models import User
from django.db import models


class Cuenta(models.Model):
    owner = models.ForeignKey('auth.User', related_name='user')
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    saldoInicial = models.FloatField(default=0)
    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.nombre})


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    createdBy = models.ForeignKey('auth.User', related_name='createdBy')
    titulo = models.CharField(max_length=200)


class Apunte(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    dinero = models.FloatField()
    cuentaOrigen = models.ForeignKey(Cuenta, related_name="cuentaOrigen")
    cuentaDestino = models.ForeignKey(Cuenta, related_name="cuentaDestino")
    ingresoGastoTransferencia = models.IntegerField()
    fecha = models.DateField()
    categoria = models.ForeignKey(Categoria, related_name="categoria")
    createdBy2 = models.ForeignKey('auth.User', related_name='createdBy2')

