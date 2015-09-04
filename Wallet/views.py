from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.shortcuts import render_to_response
from rest_framework import viewsets
from .models import Cuenta, Apunte, Etiqueta
from .serializers import CuentaSerializer, ApunteSerializer, EtiquetaSerializer
from django.core.context_processors import csrf
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from forms import ApunteForm
from django.http import HttpResponseRedirect
########################
#######API-REST#########
########################
class CuentaViewSet(viewsets.ModelViewSet):
    serializer_class = CuentaSerializer
    queryset = Cuenta.objects.all()
class ApunteViewSet(viewsets.ModelViewSet):
    serializer_class = ApunteSerializer
    queryset = Apunte.objects.all()
class EtiquetaViewSet(viewsets.ModelViewSet):
    serializer_class = EtiquetaSerializer
    queryset = Etiqueta.objects.all()

#########################
######USER FUNTIONS######
#########################
def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)
def auth_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/accounts/loggedin/')
    else:
        return HttpResponseRedirect('/accounts/invalid/')
@login_required
def loggedin(request):
    model = Cuenta.objects.filter(owner=request.user.id)
    return render_to_response('loggedin.html',
                              {'full_name': request.user.username, 'object_list': model})
def invalid_login(request):
    return render_to_response('invalid_login.html')
def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success/')
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    return render_to_response('login.html', args)
def register_success(request):
    return render_to_response('register_success.html')

#########################
#####CREATE FUNTIONS#####
#########################
@login_required
def ApunteCreate(request):
    c = {}
    c.update(csrf(request))

    descripcion = request.POST.get('descripcion','')
    dinero = request.POST.get('dinero','')
    cuentaOrigen = request.POST.get('cuentaOrigen','')
    cuentaDestino = request.POST.get('cuentaDestino','')
    ingresoGastoTransferencia = request.POST.get('ingresoGastoTransferencia','')
    fecha = request.POST.get('fecha','')
    etiquetas = request.POST.get('etiquetas','')
    return render_to_response('login.html', c)

@login_required
def CuentaCreate(request):
    c = {}
    c.update(csrf(request))

    nombre = c.POST.get('nombre','')
    saldoInicial = c.POST.get('saldoInicial','')
    return render_to_response('login.html', c)

@login_required
def EtiquetaCreate(request):
    c = {}
    c.update(csrf(request))

    titulo = c.POST.get('titulo','')
    return render_to_response('login.html', c)

#########################
#####UPDATE FUNTIONS#####
#########################
@login_required
class ApunteUpdate(UpdateView):
    model = Apunte
    fields = ['descripcion', 'dinero', 'cuentaOrigen', 'cuentaDestino', 'ingresoGastoTransferencia', 'fecha', 'etiquetas']
    template_name_suffix = '_update_form'
@login_required
class CuentaUpdate(UpdateView):
    model = Cuenta
    fields = ['owner', 'nombre', 'saldoInicial']
    template_name_suffix = '_update_form'
@login_required
class EtiquetaUpdate(UpdateView):
    model = Etiqueta
    fields = ['titulo']
    template_name_suffix = '_update_form'

#########################
#####DELETE FUNTIONS#####
#########################
@login_required
class ApunteDelete(DeleteView):
    model = Apunte
    success_url = reverse_lazy('apunte-list')
@login_required
class CuentaDelete(DeleteView):
    model = Cuenta
    success_url = reverse_lazy('cuenta-list')
@login_required
class EtiquetaDelete(DeleteView):
    model = Etiqueta
    success_url = reverse_lazy('etiqueta-list')