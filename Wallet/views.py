from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.shortcuts import render_to_response
from rest_framework import viewsets
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from datetime import datetime, date
from .models import Cuenta, Apunte, Categoria
from .serializers import CuentaSerializer, ApunteSerializer, CategoriaSerializer, DatosTabla, CategoriaSerializerWithMoreData, ApuntesPorMes
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
    apuntes = apuntes.order_by('fecha')
    dinero = 0
    arrayDatos = []
    for cuenta in model:
        dinero = cuenta.saldoInicial + dinero

    for apunte in apuntes:
        if apunte.ingresoGastoTransferencia==1:
            dinero = dinero + apunte.dinero
            arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero, apunte.ingresoGastoTransferencia, apunte.dinero))

        elif apunte.ingresoGastoTransferencia==2:
            dinero = dinero - apunte.dinero
            arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero, apunte.ingresoGastoTransferencia, apunte.dinero))
    arrayFinal = []
    anterior = None
    for dato in arrayDatos:
        if(anterior is None):
            anterior = DatosTabla(dato.fecha.__str__(), dato.dinero, dato.i, dato.apunte)
            arrayFinal.append(anterior)
        else:
            if anterior.fecha==dato.fecha:
                if dato.i==1:
                    anterior.dinero= anterior.dinero + dato.apunte
                elif dato.i==2:
                    anterior.dinero = anterior.dinero - dato.apunte
            else:
                anterior = DatosTabla(dato.fecha.__str__(), dato.dinero, dato.i, dato.apunte)
                arrayFinal.append(anterior)

    apuntes = apuntes.order_by('-fecha')
    return render_to_response('loggedin.html',
                              {'full_name': request.user.username,
                               'object_list': model,
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'apuntes_list': apuntes,
                               'dinero': dinero,
                               'arrayDatos': arrayFinal,
                               'apuntesOrdenados': GetTendencias()})

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
def ApunteUpdate(request, id):
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
        apunte = Apunte.objects.get(id=int(id))
        apunte.fecha = fecha
        apunte.descripcion = descripcion
        apunte.dinero = dinero
        apunte.categoria = categoria
        apunte.ingresoGastoTransferencia = numero
        apunte.cuentaOrigen = cuentaOrigen
        apunte.cuentaDestino = cuentaDestino
        apunte.fecha = fechaProcesada
        apunte.save()
    return render_to_response('crearApunte.html',{'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})


@login_required
def CuentaUpdate(request, id):
    cuenta = Cuenta.objects.get(id=id)
    cuenta.nombre = request.POST.get('nombre', '')
    cuenta.saldoInicial = request.POST.get('dinero', '')
    cuenta.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def CategoriaUpdate(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.titulo = request.POST.get('titulo','')
    categoria.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

#########################
#####DELETE FUNTIONS#####
#########################
@login_required
def ApunteDelete(request, id):
    Apunte.objects.get(id=id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

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
@login_required()
def CuentaPanel(request, id):
    cuenta = Cuenta.objects.get(id=id)
    listaApuntes = Apunte.objects.filter(createdBy2=request.user.id)
    listaApuntes = listaApuntes.order_by('fecha')
    dinero2 = cuenta.saldoInicial
    dinero = cuenta.saldoInicial

    for apunte in listaApuntes:
        if apunte.cuentaOrigen==cuenta:
            if apunte.ingresoGastoTransferencia==1:
               dinero = dinero + apunte.dinero
            elif apunte.ingresoGastoTransferencia==2:
               dinero = dinero - apunte.dinero
            elif apunte.ingresoGastoTransferencia==3:
                dinero = dinero - apunte.dinero
        if apunte.cuentaDestino==cuenta:
            if apunte.ingresoGastoTransferencia==3:
                dinero = dinero + apunte.dinero
    arrayDatos = []
    for apunte in listaApuntes:
        if apunte.cuentaOrigen==cuenta:
            if apunte.ingresoGastoTransferencia==1:
                dinero2 = dinero2 + apunte.dinero
                arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero2, apunte.ingresoGastoTransferencia, apunte.dinero))
            elif apunte.ingresoGastoTransferencia==2:
                dinero2 = dinero2 - apunte.dinero
                arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero2, apunte.ingresoGastoTransferencia, apunte.dinero))
            elif apunte.ingresoGastoTransferencia==3:
                dinero2 = dinero2 - apunte.dinero
                arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero2, 3, apunte.dinero))
        if apunte.cuentaDestino==cuenta:
            if apunte.ingresoGastoTransferencia==3:
                dinero2 = dinero2 + apunte.dinero
                arrayDatos.append(DatosTabla(apunte.fecha.__str__(), dinero2, 4, apunte.dinero))

    arrayFinal = []
    anterior = None
    for dato in arrayDatos:
        if(anterior is None):
            anterior = DatosTabla(dato.fecha.__str__(), dato.dinero, dato.i, dato.apunte)
            arrayFinal.append(anterior)
        else:
            if anterior.fecha==dato.fecha:
                if dato.i==1:
                    anterior.dinero= anterior.dinero + dato.apunte
                elif dato.i==2:
                    anterior.dinero = anterior.dinero - dato.apunte
                elif dato.i==3:
                    anterior.dinero = anterior.dinero - dato.apunte
                elif dato.i==4:
                    anterior.dinero = anterior.dinero + dato.apunte
            else:
                anterior = DatosTabla(dato.fecha.__str__(), dato.dinero, dato.i, dato.apunte)
                arrayFinal.append(anterior)

    return render_to_response('cuentas.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'cuenta': cuenta,
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'apunte_list': Apunte.objects.all().filter(cuentaOrigen=cuenta).order_by('-fecha'),
                               'dinero': dinero,
                               'arrayDatos': arrayFinal})

def GetTendencias():
    apuntes = Apunte.objects.order_by("fecha")
    now = datetime.now()
    if now.month==2&now.day==29:
        lastYear = date(now.year-1, now.month, now.day-1)
    else:
        lastYear = date(now.year-1, now.month, now.day)
    apuntesOrdenados = []
    mesAnterior = 0

    i = 0
    for apunte  in apuntes:
        if apunte.fecha>lastYear:
            if mesAnterior!=0:
                if mesAnterior == apunte.fecha.month:
                    if apunte.ingresoGastoTransferencia==1:
                        apunteAnterior.ingresoTotal = apunteAnterior.ingresoTotal+apunte.dinero
                    elif apunte.ingresoGastoTransferencia==2:
                        apunteAnterior.gastoTotal = apunteAnterior.gastoTotal+apunte.dinero
                    mesAnterior = apunte.fecha.month
                else:
                    if apunte.ingresoGastoTransferencia==1:
                        apunteAnterior = ApuntesPorMes(apunte.fecha.month, {apunte}, 0, apunte.dinero, getMesStr(apunte.fecha.month) +" "+ apunte.fecha.year.__str__())
                        apuntesOrdenados.append(apunteAnterior)
                    elif apunte.ingresoGastoTransferencia==2:
                        apunteAnterior = ApuntesPorMes(apunte.fecha.month, {apunte}, apunte.dinero, 0, getMesStr(apunte.fecha.month) +" "+ apunte.fecha.year.__str__())
                        apuntesOrdenados.append(apunteAnterior)
                    mesAnterior = apunte.fecha.month
            else:
                if apunte.ingresoGastoTransferencia==1:
                    apunteAnterior = ApuntesPorMes(apunte.fecha.month, {apunte}, 0, apunte.dinero, getMesStr(apunte.fecha.month) +" "+ apunte.fecha.year.__str__())
                    apuntesOrdenados.append(apunteAnterior)

                elif apunte.ingresoGastoTransferencia==2:
                    apunteAnterior = ApuntesPorMes(apunte.fecha.month, {apunte}, apunte.dinero, 0, getMesStr(apunte.fecha.month) +" "+ apunte.fecha.year.__str__())
                    apuntesOrdenados.append(apunteAnterior)
                mesAnterior = apunte.fecha.month



    return apuntesOrdenados

def getMesStr(i):
    mes = ""
    if i == 1:
        mes = "Enero"
    elif i == 2:
        mes = "Febrero"
    elif i == 3:
        mes = "Marzo"
    elif i == 4:
        mes = "Abril"
    elif i == 5:
        mes = "Mayo"
    elif i == 6:
        mes = "Junio"
    elif i == 7:
        mes = "Julio"
    elif i == 8:
        mes = "Agosto"
    elif i == 9:
        mes = "Septiembre"
    elif i == 10:
        mes = "Octubre"
    elif i == 11:
        mes = "Noviembre"
    elif i == 12:
        mes = "Diciembre"
    return mes
@login_required()
def GetCategorias(request):
    todasCategoriasDesordenadas = Categoria.objects.filter(createdBy=request.user)
    categoriasIngresos = []
    categoriasGastos = []

    for categoria in todasCategoriasDesordenadas:
        apuntes = Apunte.objects.filter(categoria=categoria).filter(createdBy2=request.user.id)
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

@login_required()
def EditarCuentas(request):
    return render_to_response('editarCuentas.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})

@login_required()
def EditarCategorias(request):
    return render_to_response('editarCategorias.html',
                              {'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})
def ViewCreateApunte(request, id):
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
        apunte = Apunte(id=id, descripcion=descripcion, ingresoGastoTransferencia=numero, dinero=dinero, fecha=fechaProcesada, categoria=categoria, cuentaDestino=cuentaDestino, cuentaOrigen=cuentaOrigen )
        apunte.save()
    return render_to_response('crearApunte.html',{'full_name': request.user.username,
                               'object_list': Cuenta.objects.filter(owner=request.user.id),
                               'categoria_list': Categoria.objects.filter(createdBy=request.user.id),
                               'today': time.strftime("%Y-%m-%d")})
