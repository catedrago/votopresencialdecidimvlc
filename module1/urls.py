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
    ## index con y sin tarjeta interventor
    url(r'^$', views.index, name='index'),
    url(r'^index_tarjeta', views.index_tarjeta, name='index_tarjeta'),
    url(r'^index_interventor', views.index_interventor, name='index_interventor'),
    ##fin index

    url(r'^proceso_activo/', views.proceso_activo, name='proceso_activo'),
    url(r'^tarjeta/', views.tarjeta, name='tarjeta'),

    url(r'^borrar/', views.borrar, name='borrar'),
    url(r'^cerrar_sistema/', views.cerrar_sistema, name='cerrar_sistema'),
]
