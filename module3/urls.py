"""evotebox2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^reconocimiento/', views.reconocimiento, name='reconocimiento'),
    url(r'^borrar/', views.borrar, name='borrar'),
    url(r'^imprimir/', views.imprimir, name='imprimir'),
    url(r'^manual/', views.manual, name='manual'),
    url(r'^recoger/', views.recoger, name='recoger'),
    url(r'^cerrar_sistema/', views.cerrar_sistema, name='cerrar_sistema'),
    url(r'^get_manual/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/', views.get_manual, name='get_manual'),
    # url(r'^get_manual/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/(?P<nombre>[a-zA-ZçñÇÑ ]+)?$', views.get_manual, name='get_manual'),
    url(r'^reconocimiento_manual/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/', views.reconocimiento_manual, name='reconocimiento_manual'),
    # url(r'^reconocimiento_manual/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/(?P<nombre>[a-zA-ZçñÇÑ ]+)?$', views.reconocimiento_manual, name='reconocimiento_manual'),
    # url(r'^votar/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/(?P<nombre>[a-zA-ZçñÇÑ ]+)?$', views.votar, name='votar'),
    url(r'^votar/(?P<dni>[a-zA-Z0-9çñÇÑ]+)/', views.votar, name='votar'),

]