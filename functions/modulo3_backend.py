"""
Archivo que recoge las funciones as importantes del modulo 3, tales omo usar Censo y NFC
Abstraccion para no tener que realizar ninguna logica en las vistas

"""

#Los diferentes imports son por si se usan desde Django o en pruebas locales, ya que cambian.
# try:
#     from .Nfc import leer_votos
#     from .censo import Censo
# except:
#     from Nfc import leer_votos
#     from censo import Censo


try:
    #raspby
    from . import censo
    from . import votacion
    from . import inicio_sistema

except:
    #local
    import censo
    import votacion
    import inicio_sistema


import ast
import pandas as pd

DEBUG_ = False


try:
    from . import Nfc
    from . import impresora
except:
    DEBUG_ = True
    print("No hay NFC, modo debug ON")

def preprocesado(dni):
    """
    Funcion que realiza el preprocesado del nombre de la persona
    :param dni:
    :param nombre:
    :return:
    """
    return dni

def puede_votar(dni_hash):
    """
    Metodo que verifica si el dni_hash puede o no votar.
    :param dni_hash: string
    :return: True si puede votar. "voted" si ya ha votado. "no" si no aparece en la lista de DNIs hasheado
    """
    if inicio_sistema.es_votacion_anonima():
        dni_hash = inicio_sistema.hash_one_dni(dni_hash)
    db = censo.Censo("{}/censo.db".format(inicio_sistema.censo_dir))

    if not inicio_sistema.decidimVlc:
        existe = db.check_census(dni_hash)
    else:
        existe = True

    if not existe:
        return "no"
    voted = db.check_voted(dni_hash)
    if voted:
        return "voted"
    print("puede votar")
    return True

def votar(dni):
    """
    Funcion que realiza las funciones de:
    - Verificar si el usuario dado puede votar
    - Leer la tarjeta NFC en caso de que se positivo y añadir el voto a la BD, asi como el tick de votado del usuario
    - Reescribe la tarjeta NFC con el dni, en la version no anonima
    :param dni: String
    :return: True si el usuario ha votado, False en caso de que no.
    """
    anon = inicio_sistema.es_votacion_anonima()
    print("Es anonima: {}".format(anon))
    if DEBUG_:
        # votos = [1004, 1453]
        votos = [1004]
    else:
        votos = Nfc.leer_votos()

    print("Votando con dni {} y votos {} en votacion anonima: {}".format( dni, votos, anon))
    db = censo.Censo("{}/censo.db".format(inicio_sistema.censo_dir), anonimo=anon)


    if anon:
        db_votos = votacion.Votacion("/tmp/evotebox/votacion.db")
        dni = inicio_sistema.hash_one_dni(dni)
        existe = db.check_census(dni)
        if not existe:
            return "no"
        voted = db.check_voted(dni)
        if voted:
            return "voted"



    if anon:
        for voto in votos:
            db_votos.votar(voto)

    if not DEBUG_ and inicio_sistema.hay_impresora():
        try:
            impresora.imprimir(votos)
        except:
            return "impresora"


    if not anon:
        print("Voto añadido. escribiendo  DNI en la tarjeta")
        try:
            Nfc.escribir_votos(votos, dni=dni)
        except:

            return "error_nfc"

    if inicio_sistema.decidimVlc:
        db.vote_decidimVlc(dni, votos=votos)
    else:
        db.vote(dni, votos=votos)

    print("fin del voto")

    return True


def recuento_votos():
    """
    Realiza un recuento de los votos
    """
    anon = inicio_sistema.es_votacion_anonima()


    def add_campo(proyecto):
        id_proyecto, n_votos = proyecto
        # anyade al diccionario
        votacion_dict["id_proyecto"].append(id_proyecto)
        votacion_dict["n_votos"].append(n_votos)

    def add_campo_no_anon(proyecto):
        dni, ha_votado, timestamp, votos = proyecto
        # anyade al diccionario
        ha_votado =  ha_votado == 1
        votacion_dict["dni"].append(dni)
        votacion_dict["ha_votado"].append(ha_votado)
        if ha_votado:
            votacion_dict["timestamp"].append(timestamp)
            votacion_dict["id_proyectos"].append(votos)
        else:
            votacion_dict["timestamp"].append(0)
            votacion_dict["id_proyectos"].append('-')

    if anon:
        votacion_db = votacion.Votacion("{}/votacion.db".format(inicio_sistema.censo_dir))
        votacion_dict = {
            "id_proyecto": [],
            "n_votos": [],
        }
        recuento = votacion_db.get_recuento()
        recuento = sorted(recuento, key=lambda tup: -tup[1])
        for proyecto in recuento:
            add_campo(proyecto)
        votacion_db.close_database()
    else:
        db = censo.Censo("{}/censo.db".format(inicio_sistema.censo_dir), anonimo=anon)
        votacion_dict = {
            "dni": [],
            "ha_votado": [],
            "timestamp": [],
            "id_proyectos": [],
        }
        recuento = db.get_votos()
        if not recuento:
            print("NO EXISTE VOTACION EN CENSO (version no anonima)")
            return
        for proyecto in recuento:
            add_campo_no_anon(proyecto)
        db.close_database()

    df = pd.DataFrame(data=votacion_dict)
    df.to_csv(inicio_sistema.path_usb + "/recuento_votos.csv", index=False)

def recuento_votos_ticket_final():
    """
    Realiza un recuento de los votos final
    Devuelve un diccionario con el id del proyecto y el numero de votos que ha obtenido
    """
    anon = inicio_sistema.es_votacion_anonima()


    def add_campo(proyecto):
        id_proyecto, n_votos = proyecto
        # anyade al diccionario
        votacion_dict["id_proyecto"].append(id_proyecto)
        votacion_dict["n_votos"].append(n_votos)

    def add_campo_no_anon(proyecto):
        dni, ha_votado, timestamp, votos = proyecto
        # anyade al diccionario
        ha_votado =  ha_votado == 1
        votacion_dict["dni"].append(dni)
        votacion_dict["ha_votado"].append(ha_votado)
        if ha_votado:
            votacion_dict["timestamp"].append(timestamp)
            votacion_dict["id_proyectos"].append(votos)
        else:
            votacion_dict["timestamp"].append(0)
            votacion_dict["id_proyectos"].append('-')

    if anon:
        votacion_db = votacion.Votacion("{}/votacion.db".format(inicio_sistema.censo_dir))
        votacion_dict = {
            "id_proyecto": [],
            "n_votos": [],
        }
        recuento = votacion_db.get_recuento()
        recuento = sorted(recuento, key=lambda tup: -tup[1])
        for proyecto in recuento:
            add_campo(proyecto)
        votacion_db.close_database()
    else:
        db = censo.Censo("{}/censo.db".format(inicio_sistema.censo_dir), anonimo=anon)
        votacion_dict = {
            "dni": [],
            "ha_votado": [],
            "timestamp": [],
            "id_proyectos": [],
        }
        recuento = db.get_votos()
        if not recuento:
            print("NO EXISTE VOTACION EN CENSO (version no anonima)")
            return
        for proyecto in recuento:
            add_campo_no_anon(proyecto)
        db.close_database()


    df = pd.DataFrame(data=votacion_dict)
    num_participantes = 0
    res = {}
    id_proyectos = df["id_proyectos"]
    for ids in id_proyectos:
        if ids == "-":
            continue
        num_participantes += 1
        ids = ast.literal_eval(ids)
        for id in ids:
            res[id] = res.get(id, 0) + 1
    if not DEBUG_:
        impresora.imprimir_ticket_final(res, num_participantes)
    else:
        print("DEBUG: imprimiendo: {} con {} participantes".format(res, num_participantes))

if __name__ == "__main__":
    recuento_votos_ticket_final()