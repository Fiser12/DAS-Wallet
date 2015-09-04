from Wallet.models import Apunte, Cuenta, Etiqueta

__author__ = 'Fiser'
from django import forms

class ApunteForm(forms.ModelForm):
    class Meta:
        model = Apunte
        fields = "__all__"
