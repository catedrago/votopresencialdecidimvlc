from django.shortcuts import render
from django.http import HttpResponse
import sys, time
sys.path.append("..")
DEBUG_ = False
try:
    from functions.inicio_sistema import cerrar_proceso
    from functions.Nfc import tarjeta_interventor, escribir_votos, leer_votos
except:
    print("MODO DEBUg ( no nfc)")
    DEBUG_ = True
from functions.inicio_sistema import get_configuracion, es_votacion_anonima
def index(request):
    """
    Pagina de inicio con boton para iniciar el sistema a escanear
    :param request:
    :return:
    """
    convocante, proces, correo = get_configuracion()
    context = {
        "anonimo": es_votacion_anonima(),
        "convocante": convocante,
        "proces": proces,
        "correo": correo
    }


    return render(request, 'module1/index.html', context)


def index_interventor(request):
    """
    Pagina de inicio con boton para iniciar el sistema a escanear e imprime la tarjeta interventor
    :param request:
    :return:
    """
    context = {}
    print("IMPRIMIENDO TARJETA INTERVENTOR")
    if not DEBUG_:
        no_error = tarjeta_interventor() # error
    else:
        print("DEBUG")
        time.sleep(3)
        no_error = True

    if no_error:
        return render(request, 'module1/tarjeta.html', context)
    else:
        print("ERROR escribiendo tarjeta interventor2")

        return render(request, 'module1/error_tarjeta_interventor.html', context)

def proceso_activo(request):
    """
    Para cuando detecta que hay una votacion pendiente.
    Verifica que estan las claves inicialziadas
    :param request:
    :return:
    """
    context = {}
    return render(request, 'module1/proceso_activo.html', context)


def borrar(request):
    """
    Borrar to do el sistema (claves..)
    :param request:
    :return:
    """
    context = {}
    return render(request, 'module1/borrar.html', context)

def index_tarjeta(request):
    """
    Pagina que muestra el boton ara imprimir tarjetas
    :param request:
    :return:
    """
    context = {}
    return render(request, 'module1/index_tarjeta.html', context)


def tarjeta(request):
    """
    Imprime la tarjeta
    :param request:
    :return:
    """
    context = {}
    if not DEBUG_:
        interventor = leer_votos() == [-1]

    else:
        time.sleep(3)
        interventor = False
        print("DEBUG: interventor {}".format(interventor))
    if interventor:
        print("Detectada tarjeta interventor")
        return render(request, 'module1/borrar.html', context)
    else:
        print("Escribiendo tarjeta")
        if not DEBUG_:
            correct = escribir_votos([])
        else:
            correct = True
            print("DEBUG correct al escribir votos: {}".format(correct))
        if correct:
            return render(request, 'module1/tarjeta.html', context)
        else:
            context = {
                "mensaje": "Error al escribir la tarjeta. Pruebe a cambiar de tarjeta, por favor.",
                "pantalla": "1"
            }
            return render(request, 'module1/error.html', context)

def cerrar_sistema(request):
    """
    Vista para cerrar el sistema
    :param request:
    :return:
    """
    context = {}
    print("Cerrando el sistema!")
    print("Borrando toda la información")

    if DEBUG_:
        time.sleep(3)
    result = cerrar_proceso(1)
    if result == 'correct':
        return render(request, 'module1/apagar.html', context)
    else:
        context = {
            "mensaje": "Error al cerrar el sistema"
        }
        return render(request, 'module1/error.html', context)
