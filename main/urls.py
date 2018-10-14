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

from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^iniciar/', views.iniciar, name='iniciar'),
    url(r'^error_usb/', views.error_usb, name='error_usb'), # m_1A No -> Si falla el usb se llama aqui
    url(r'^error_nfc/', views.error_nfc, name='error_nfc'),
    url(r'^error_db/', views.error_db, name='error_db'),
    url(r'^interventor/', views.interventor, name='interventor'),
    url(r'^module1/', include('module1.urls', namespace='module1')),
    url(r'^module2/', include('module2.urls', namespace='module2')),
    url(r'^module3/', include('module3.urls', namespace='module3')),
]
