from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.shortcuts import render_to_response
from rest_framework import viewsets
from .models import Cuenta, Apunte, Categoria
from .serializers import CuentaSerializer, ApunteSerializer, CategoriaSerializer
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.template import RequestContext

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
class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()

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
    categoria = request.POST.get('categoria','')

    return render_to_response('loggedin.html', c)

def CuentaCreate(request):
    nombre = request.POST.get('nombre','')
    saldoInicial = request.POST.get('saldoInicial','')
    idUser = request.user
    cuenta = Cuenta(nombre=nombre, owner=idUser, saldoInicial=saldoInicial)
    cuenta.save()
    return HttpResponseRedirect('/accounts/loggedin/')

def CategoriaCreate(request):
    nombre = request.POST.get('titulo','')
    eti = Categoria(titulo=nombre)
    eti.save()
    return HttpResponseRedirect('/accounts/loggedin/')

#########################
#####UPDATE FUNTIONS#####
#########################
@login_required
class ApunteUpdate(UpdateView):
    model = Apunte
    fields = ['descripcion', 'dinero', 'cuentaOrigen', 'cuentaDestino', 'ingresoGastoTransferencia', 'fecha', 'categoria']
    template_name_suffix = '_update_form'
@login_required
class CuentaUpdate(UpdateView):
    model = Cuenta
    fields = ['owner', 'nombre', 'saldoInicial']
    template_name_suffix = '_update_form'
@login_required
class CategoriaUpdate(UpdateView):
    model = Categoria
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
class CategoriaDelete(DeleteView):
    model = Categoria
    success_url = reverse_lazy('categoria-list')
#########################
######GET FUNTIONS#######
#########################
def CuentaPanel(request, id):
    cuenta = Cuenta.objects.get(id=id)
    listaApuntes = Apunte.objects.filter(cuentaOrigen=cuenta)
    return render_to_response('categoria.html',
                              {'full_name': request.user.username, 'object_list': Cuenta.objects.filter(owner=request.user.id)})
