from django.shortcuts import render, redirect
import os
import sys
sys.path.append("..")
# from functions import Nfc
from functions.inicio_sistema import init_module, detect_module

def index(request):
    """
    Pagina de inicio con boton para iniciar el sistema
    :param request:
    :return:
    """
    context = {}

    return render(request, 'main/index.html', context)

def error_usb(request):
    context = {}
    return render(request, 'main/error_usb.html', context)

def error_nfc(request):
    context = {}
    return render(request, 'main/error_nfc.html', context)

def error_db(request):
    context = {}
    return render(request, 'main/error_db.html', context)

def error_proceso(request):
    context = {}
    return render(request, 'main/error_proceso.html', context)

def sis_activado(request):
    context = {}
    return render(request, 'main/sis_activado.html', context)


def iniciar(request):
    context = {}
    ## Detectar el modulo (por hardware), copiar claves, inicializacion comun...
    mod = detect_module()

    res_correcto = init_module(mod)
    if res_correcto == 'error_usb':
        print("Main views: Error en el USB")
        return render(request, 'main/error_usb.html', context)
    elif res_correcto == 'error_nfc':
        print("Main views Error en el NFC")
        return render(request, 'main/error_usb.html', context)
    print("modulo {}".format(mod))
    if mod == 1:
        context = {
            "modulo": 1
        }
        # Recordar que antes de iniciar el modulo 1 hay que imprimir las tarjetas de interventor <--- Aplicacion 1, hace set de las claves.
        return render(request, 'main/sis_activado.html', context)
    elif mod == 2:
        context = {
            "modulo": 2
        }
        return render(request, 'main/sis_activado.html', context)
    elif mod == 3:
        context = {
            "modulo": 3
        }
        return render(request, 'main/sis_activado.html', context)

def interventor(request):
    """
    Metodo que saca las tarjetas de interventor
    :param request:
    :return:
    """
    context = {}
    print("Imprimiendo tarjeta de interventor - debug")
    return render(request, 'main/interventor.html', context)

