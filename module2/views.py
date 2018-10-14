from django.shortcuts import render
import time
DEBUG_ = False
from functions.reconocimiento import validoDNI
try:
    from functions.inicio_sistema import cerrar_proceso
    from functions.Nfc import tarjeta_interventor, escribir_votos, leer_votos
    from functions.propuestas import comprobar_distrito, get_presupuesto_distrito
    from functions.output_logging import print_output as print
except:
    DEBUG_ = True
    from functions.propuestas import comprobar_distrito, get_presupuesto_distrito
    print("No hay NFC, modo debug ON")

def comprobar_tarjeta(request):
    """
    Metodo auxiliar para comprobar la tarjeta.
    Salta a una pantalla de error si es necesario.
    False es que puede continuar con la ejecucion normal.
    dni_tarjeta la tarjeta ha sido usada
    interventor es tarj. interventor
    :param request:
    :return:
    """
    if DEBUG_:
        interventor = False
    else:
        # Comprobar si la tarjeta no tiene un voto con DNI ya

        votos = leer_votos()
        print("Comprobar tarjeta, Votos {}".format(votos))
        # Comprobar si la tarjeta no tiene un voto con DNI ya
        if votos :

            posible_dni = votos[-1]
            print("si votos, poible_dni {}".format(posible_dni))
            if validoDNI(posible_dni):
                print("DNI valido")
                return "dni_tarjeta"
        if votos is False:
            return "error_leer"
        interventor = votos == [-1]

    if interventor:
        print("Detectada tarjeta interventor")
        return "interventor"

    return False

def index(request):
    """
    Pagina de inicio que rlee la tarjeta y redirige a carrito de compra
    :param request:
    :return:
    """
    context = {}


    return render(request, 'module2/index.html', context)


def votar(request, votos):
    """
    Cuando se hace realidad la votación
    :param request:
    :return:
    """
    context = {}
    if votos:
        votos = votos.split(",")
        votos = [int(x) for x in votos]
    else:
        votos = []
    print(votos)
    if not DEBUG_:
        res = escribir_votos(votos)
        if not res:
            context = {
                "mensaje": "No se ha detectado tarjeta o la tarjeta no es válida",
                "mensaje2": "Pulse el botón ''Aceptar'' para volver al inicio y volver a intentarlo."
            }
            return render(request, 'module2/error.html', context)
    else:
        print("Modo DEBUG: los votos no se escriben")
    return render(request, 'module2/votando.html', context)


def votacion(request, distrito):
    """
    Pagina de carrito de compra, lees los votos de la tarjeta primero
    :param request:
    :param votos: array de integers
    :return:
    """
    resultado = comprobar_tarjeta(request)
    print("Resultado de comprobar_tarjeta: {}".format(resultado))
    if resultado == "error_leer":
        context = {
            "mensaje": "No se ha detectado tarjeta o la tarjeta no es válida",
            "mensaje2": "Pulse el botón ''Aceptar'' para volver al inicio y volver a intentarlo."
        }
        return render(request, 'module2/error.html', context)
    elif resultado == "dni_tarjeta":
        context = {
            "mensaje": "La tarjeta ya ha sido usada para votar.",
            "mensaje2": "Pulse el botón ''Aceptar'' para volver al inicio."
        }
        return render(request, 'module2/error.html', context)

    if not DEBUG_:
        print("Leyendo votos")
        votos = leer_votos()
        print("Leidos {}".format(votos))
        interventor = votos == [-1]
        if not interventor and votos:
            #Coger solo los votos de los distritos
            print("Comprobando distrito {} con el primer id de : {}".format(distrito, votos))
            if not comprobar_distrito(distrito, votos[0]):
                print("Resultado : False, votos vacios")
                # Si el distrito es diferente, no mostramos los votos.
                votos = []
    else:
        time.sleep(1)
        votos = []
        interventor = False

    if votos is not False:
        if interventor:
            print("Detectada tarjeta interventor")
            return render(request, 'module2/borrar.html', {})
        else:

            if distrito is None:
                distrito = -1

            presupuesto_distrito = get_presupuesto_distrito(distrito)
            if not presupuesto_distrito:
                context = {
                    "mensaje": "Error en el fichero de presupuestos por distrito.",
                    "mensaje2": "Pulse el botón ''Aceptar'' para volver al inicio y volver a intentarlo."
                }
                return render(request, 'module2/error.html', context)

            print("Seleccion de distrito: {}".format(distrito))
            context = {'votos': votos,
                       "presupuesto": presupuesto_distrito,
                       "distrito": distrito}
            return render(request, 'module2/votacion.html', context)
    else:
        context = {
            "mensaje": "Error leyendo la tarjeta",
            "mensaje2": "Pulse el botón ''Aceptar'' para volver al inicio y volver a intentarlo."
        }
        return render(request, 'module2/error.html', context)

def cerrar_sistema(request):
    """
    Vista para cerrar el sistema
    :param request:
    :return:
    """
    context = {}
    print("Cerrando el sistema!")
    print("Borrando toda la información")

    result = cerrar_proceso(2)

    if result == 'correct':
        return render(request, 'module2/apagar.html', context)
    else:
        return render(request, 'module2/error_apagar.html', context)

def distritos(request):
    """

    :param request:
    :return:
    """
    context = {}

    return render(request, 'module2/distritos.html', context)
