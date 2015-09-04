"""WalletApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include, patterns
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from Wallet.views import CuentaViewSet, ApunteViewSet, EtiquetaViewSet, ApunteCreate, CuentaCreate

router = DefaultRouter()
router.register(r'cuenta', CuentaViewSet)
router.register(r'apunte', ApunteViewSet)
router.register(r'etiqueta', EtiquetaViewSet)

urlpatterns = patterns('',
url(r'^$', 'Wallet.views.login'),
url(r'^api/', include(router.urls)),
url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
url(r'^admin/', include(admin.site.urls)),

url(r'^accounts/login/$', 'Wallet.views.login'),
url(r'^accounts/auth/$', 'Wallet.views.auth_view'),
url(r'^accounts/logout/$', 'Wallet.views.logout'),
url(r'^accounts/loggedin/$', 'Wallet.views.loggedin'),
url(r'^accounts/invalid/$', 'Wallet.views.invalid_login'),
url(r'^accounts/register/$', 'Wallet.views.register_user'),
url(r'^accounts/register_success/$', 'Wallet.views.register_success'),
url(r'^createApunte/$', 'Wallet.views.ApunteCreate'),
url(r'^createEtiqueta/$', 'Wallet.views.CuentaCreate'),
url(r'^createCuenta/$', 'Wallet.views.EtiquetaCreate'),

)

