from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.shortcuts import render_to_response
from rest_framework import viewsets
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from datetime import datetime
from .models import Cuenta, Apunte, Categoria
from .serializers import CuentaSerializer, ApunteSerializer, CategoriaSerializer, CategoriaSerializerWithMoreData
import time

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
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/accounts/loggedin/')
    else:
        return HttpResponseRedirect('/accounts/invalid/')


@login_required
def loggedin(request):
    model = Cuenta.objects.filter(owner=request.user.id)
    apuntes = Apunte.objects.filter(createdBy2=request.user.id)
    apuntes = apuntes.order_by('-fecha')
    dinero = 0
    for cuenta in model:
        print(cuenta.nombre)
        dinero = cuenta.saldoInicial + dinero

    for apunte in apuntes:
        if apunte.ingresoGastoTransferencia==1:
            dinero = dinero + apunte.dinero
        elif apunte.ingresoGastoTransferencia==2:
            dinero = dinero - apunte.dinero

    return render_to_response('loggedin.html',
                              {'full_name': request.user.username,
                               'object_list': model,
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'apuntes_list': apuntes,
                               'dinero': dinero})

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

    descripcion = request.POST.get('descripcion', '')
    dinero = request.POST.get('dinero', '')
    cuentaOrigenNumero = request.POST.get('cuentaOrigen', '')
    cuentaOrigen = Cuenta.objects.get(id=int(cuentaOrigenNumero))
    cuentaDestinoNumero = request.POST.get('cuentaDestino', '')
    cuentaDestino = Cuenta.objects.get(id=int(cuentaDestinoNumero))
    ingresoGastoTransferencia = request.POST.get('ingresoGastoTransferencia', '')
    numero = 0
    continuar = True;
    if ingresoGastoTransferencia=="Ingreso":
        numero = 1
        cuentaDestino = cuentaOrigen

    elif ingresoGastoTransferencia=="Gasto":
        numero = 2
        cuentaDestino = cuentaOrigen

    elif ingresoGastoTransferencia=="Transferencia":
        numero = 3
        if cuentaOrigenNumero == cuentaDestinoNumero:
            continuar = False
    if continuar:
        fecha = request.POST.get('fecha', '')
        categoriaString = request.POST.get('categoria', '')
        categoria = Categoria.objects.get(id=int(categoriaString))
        fechaProcesada= datetime.strptime(fecha, '%m/%d/%Y')
        apunte = Apunte(descripcion=descripcion, dinero=dinero, cuentaDestino=cuentaDestino, cuentaOrigen=cuentaOrigen, ingresoGastoTransferencia=numero, fecha=fechaProcesada, categoria=categoria, createdBy2=request.user)
        apunte.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))



def CuentaCreate(request):
    nombre = request.POST.get('nombre', '')
    saldoInicial = request.POST.get('saldoInicial', '')
    idUser = request.user
    cuenta = Cuenta(nombre=nombre, owner=idUser, saldoInicial=saldoInicial)
    cuenta.save()
    return HttpResponseRedirect('/cuenta/editar/')


def CategoriaCreate(request):
    nombre = request.POST.get('titulo', '')
    eti = Categoria(titulo=nombre, createdBy=request.user)
    eti.save()
    return HttpResponseRedirect('/categoria/editar/')


#########################
#####UPDATE FUNTIONS#####
#########################
@login_required
class ApunteUpdate(UpdateView):
    model = Apunte
    fields = ['descripcion', 'dinero', 'cuentaOrigen', 'cuentaDestino', 'ingresoGastoTransferencia', 'fecha',
              'categoria']
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
def ApunteDelete(DeleteView, id):
    Apunte.objects.get(id=id).delete()
    return HttpResponseRedirect('/accounts/loggedin/')


@login_required
def CuentaDelete(request, id):
    Cuenta.objects.get(id=id).delete()
    return HttpResponseRedirect('/cuenta/editar/')


@login_required
def CategoriaDelete(request, id):
    Categoria.objects.get(id=id).delete()
    return HttpResponseRedirect('/categoria/editar/')


#########################
######GET FUNTIONS#######
#########################
def CuentaPanel(request, id):
    cuenta = Cuenta.objects.get(id=id)
    listaApuntes = Apunte.objects.filter(cuentaOrigen=cuenta)
    listaApuntes = listaApuntes.order_by('-fecha')
    dinero = cuenta.saldoInicial
    for apunte in listaApuntes:
        if apunte.ingresoGastoTransferencia==1:
            dinero = dinero +  apunte.dinero
        elif apunte.ingresoGastoTransferencia==2:
            dinero = dinero - apunte.dinero

    return render_to_response('cuentas.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'cuenta': cuenta,
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'apunte_list': listaApuntes,
                               'dinero': dinero})


def GetTendencias(request):
    return render_to_response('tendencias.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})


def GetPatrimonio(request):
    return render_to_response('patrimonioNeto.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})


def GetCategorias(request):
    todasCategoriasDesordenadas = Categoria.objects.filter(createdBy=request.user)
    categoriasIngresos = []
    categoriasGastos = []

    for categoria in todasCategoriasDesordenadas:
        apuntes = Apunte.objects.filter(categoria=categoria)
        apuntes.order_by('-fecha')

        dineroIngresos = 0
        dineroGastos = 0
        listaApuntesIngresos = []
        listaApuntesGastos = []
        for apunte in apuntes:
            if apunte.ingresoGastoTransferencia==1:
                dineroIngresos = dineroIngresos + apunte.dinero
                listaApuntesIngresos.append(apunte)
            elif apunte.ingresoGastoTransferencia==2:
                dineroGastos = dineroGastos + (apunte.dinero)
                listaApuntesGastos.append(apunte)


        categoriaIngresos = CategoriaSerializerWithMoreData(categoria=categoria, dinero=dineroIngresos, apuntes=listaApuntesIngresos)
        categoriaGastos = CategoriaSerializerWithMoreData(categoria=categoria, dinero=dineroGastos, apuntes=listaApuntesGastos)

        categoriasIngresos.append(categoriaIngresos)
        categoriasGastos.append(categoriaGastos)

    categoriasIngresos.sort(key=lambda x: x.dinero, reverse=True)
    categoriasGastos.sort(key=lambda x: x.dinero, reverse=True)

    return render_to_response('categoria.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d"),
                               'categoriasIngresos': categoriasIngresos,
                               'categoriasGastos': categoriasGastos})


def GetEstadisticas(request):
    return render_to_response('estadistica.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})


def EditarCuentas(request):
    return render_to_response('editarCuentas.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})


def EditarCategorias(request):
    return render_to_response('editarCategorias.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})
def ViewCreateApunte(request):
    return render_to_response('crearApunte.html',{'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})