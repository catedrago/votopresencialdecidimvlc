from django.shortcuts import render
import sys
from functions.inicio_sistema import cerrar_proceso, hay_impresora

DEBUG_ = False
sys.path.append("..")
# from functions import Nfc
from functions import modulo3_backend as m3
from functions.reconocimiento import ocr_dni_path, validoDNI, ocr_dni_camera


try:
    from functions.Nfc import leer_votos
except:
    DEBUG_ = True
    print("No hay NFC, modo debug ON en views del modulo 3")

    path_img = "path a imagen de prueba"

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
    Pagina de inicio con boton para iniciar el sistema, se muestra antes de reconocer la tarjeta y DNI
    :param request:
    :return:
    """
    context = {}
    print("index module3")

    return render(request, 'module3/index.html', context)

def reconocimiento(request):
    """
    Pagina que muestra los datos de la persona leidos por la camara
    :param request:
    :return:
    """

    resultado = comprobar_tarjeta(request)
    print("Resultado de comprobar_tarjeta: {}".format(resultado))
    if resultado == "error_leer":
        context = {
            "mensaje": "No se ha detectado tarjeta o la tarjeta no es válida"
        }
        return render(request, 'module3/error.html', context)

    if resultado == "dni_tarjeta":
        context = {
            "mensaje": "La tarjeta ya ha sido usada para votar."
        }
        return render(request, 'module3/error.html', context)
    elif resultado == "interventor":
        if hay_impresora():
            return render(request, 'module3/imprimir.html', {})
        else:
            return render(request, 'module3/borrar.html', {})
    else:
        if DEBUG_:
            dni = ocr_dni_path(path_img)
        else:
            dni = ocr_dni_camera()

        if not dni or not validoDNI(dni):
            context = {
                "mensaje": "El sistema no ha podido obtener el número de DNI. Pulse el botón 'Aceptar' para intentarlo de nuevo o introducirlo de manera manual."
                           ""
            }
            return render(request, 'module3/error.html', context)
        else:
            context = {"dni": dni}
            return render(request, 'module3/reconocimiento.html', context)

def reconocimiento_manual(request, dni):
    """
    Funcion que muestra los datos pero se le pasan de forma manual a la funcion
    :param request:
    :param dni:
    :param nombre:
    :return:
    """
    dni = dni.upper()
    print("Reconocimiento manual: {}".format(dni))
    if dni == "00000000A":
        context = {
            "mensaje": "El DNI o NIE introducido es incorrecto."
        }
        return render(request, 'module3/error.html', context)
    context = {"dni": dni}
    print("Todo bien, pasamos a reconocimiento.html")
    return render(request, 'module3/reconocimiento.html', context)

def recoger(request):
    """
    Pantalla para recoger
    :param request:
    :return:
    """

    context = {}
    return render(request, 'module3/recoger.html', context)

def cerrar_sistema(request):
    """
    Vista para cerrar el sistema
    :param request:
    :return:
    """
    context = {}
    print("Cerrando el sistema!")
    print("Borrando toda la información")
    result = cerrar_proceso(3)

    if result == 'correct':
        return render(request, 'module3/apagar.html', context)
    else:
        return render(request, 'module3/error_apagar.html', context)

def manual(request):
    """
    Vista que devuelve a vista con el teclado en pantalla
    :param request:
    :return:
    """

    resultado = comprobar_tarjeta(request)
    if resultado == "error_leer":
        context = {
            "mensaje": "No se ha detectado tarjeta o la tarjeta no es válida"
        }
        return render(request, 'module3/error.html', context)


    if resultado == "dni_tarjeta":
        context = {
            "mensaje": "La tarjeta ya ha sido usada para votar."
        }
        return render(request, 'module3/error.html', context)
    elif resultado == "interventor":
        if hay_impresora():
            return render(request, 'module3/imprimir.html', {})
        else:
            return render(request, 'module3/borrar.html', {})
    else:
        return render(request, 'module3/manual.html', {})

def get_manual(request, dni):
    """
    Vista que recoge el dni y verifica que puedan votar
    FUNCION IMPORTANTE: guarda en la vista el dni de la persona en caso de que puedan votar
    Devuelve a una pagina de error o pide que inserte el voto quitando su DNI.
    :param request:
    :return:
    """
    dni = dni.upper()
    votar = m3.puede_votar(dni)
    if not validoDNI(dni):
        print("ValidoDNI() devuelve False. DNI incorrecto")
        context = {
            "dni": dni,
            "mensaje": "El DNI o NIE que ha introducido no es correcto.",
            "pantalla": "4"
        }
        return render(request, 'module3/insertar_voto.html', context)
    elif votar == True: #puede votar y vamos a recoger su voto
        print("ok: puede votar")
        context = {
            "dni" : dni,
            "mensaje": "El sistema va a proceder a escribir el número de identificación en la tarjeta de votación. No retire la tarjeta y pulse el botón 'Aceptar' para inciar el proceso.",
            "pantalla": "1"
        }
        return render(request, 'module3/insertar_voto.html', context)
    elif votar == "voted":
        print("Ya ha votado")
        context = {
            "dni": dni,
            "mensaje": "El DNI {} ya ha votado.".format(dni),
            "pantalla": "2"
        }
        #usted ya ha votado
        return render(request, 'module3/insertar_voto.html', context)
    elif votar == "no":
        print("No puede votar")
        context = {
            "dni": dni,
            "mensaje": "El DNI {} no puede votar.".format(dni),
            "pantalla": "3"
        }
        #no aparece en el censo
        return render(request, 'module3/insertar_voto.html', context)

def votar(request, dni):
    """
    Funcion que vota definitivamente, lee los votos y guarda en el censo la persona
    :param request:
    :param dni:
    :param nombre:
    :return:
    """

    dni = dni.upper()
    resultado = comprobar_tarjeta(request)
    if resultado == "error_leer":
        context = {
            "mensaje": "No se ha detectado tarjeta o la tarjeta no es válida"
        }
        return render(request, 'module3/error.html', context)

    if resultado == "dni_tarjeta":
        context = {
            "mensaje": "La tarjeta ya ha sido usada para votar."
        }
        return render(request, 'module3/error.html', context)
    elif resultado == "interventor":
        if hay_impresora():
            return render(request, 'module3/imprimir.html', {})
        else:
            return render(request, 'module3/borrar.html', {})

    if DEBUG_:
        result = False
    else:
        result = m3.votar(dni)
    context = {}
    if result == "impresora":
        context = {
            "mensaje": "Error en la impresora"
        }
        return render(request, 'module3/error.html', context)

    elif result == "voted": #no puede pasar
        print("Ya ha votado")
        context = {
            "dni": dni,
            "mensaje": "El DNI {} ya ha votado.".format(dni),
            "pantalla": "2"
        }
        #usted ya ha votado
        return render(request, 'module3/insertar_voto.html', context)
    elif result == "no": #no puede pasar
        print("No puede votar")
        context = {
            "dni": dni,
            "mensaje": "El DNI {} no puede votar.".format(dni),
            "pantalla": "3"
        }
    elif result == "error_nfc":
        print("Error en el NFC")
        context = {
            "dni": dni,
            "mensaje": "El DNI {} no se ha podido escribir en la tarjeta.".format(dni),
            "pantalla": "5"
        }
        #no aparece en el censo
        return render(request, 'module3/insertar_voto.html', context)
    return render(request, 'module3/recoger.html', context)

def borrar(request):
    """
    Pantalla de aviso de borrado
    :param request:
    :return:
    """

    return render(request, 'module3/borrar.html', {})

def imprimir(request):
    """
    Logica para la impresion y redirigir a cerrado
    :param request:
    :return:
    """
    try:
        m3.recuento_votos_ticket_final()
    except:
        context = {
            "mensaje": "Error en la impresora"
        }
        return render(request, 'module3/error.html', context)
    return render(request, 'module3/borrar.html', {})