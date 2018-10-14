"""
Archivo que contiene las funciones para iniciar el sistema

Este archivo ha sido modificado para la versión de votación de DecidimVlc2018
Algunas partes del código en la vwrsión anonima podrian estar modificadas y necesitan revision

"""
from __future__ import print_function
import os, binascii, shutil
from os.path import isfile, join
from subprocess import call
import json
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import time

DEBUG_ = False
decidimVlc = True # -> no se verifica el censo

try:
    from . import censo
    from . import votacion
    from . import modulo3_backend as m3
    from . import output_logging
except:
    import censo
    import votacion
    import modulo3_backend as m3
    import output_logging

nombre_archivo_prop_distr = "presupuestos_distrito.csv"
nombre_bd_censo = "bd_censo.csv"
dir_temp_evotebox = "/tmp/evotebox"
path_usb = "/tmp/usb"
home_dir = "/home/dietpi"

try:
    import RPi.GPIO as GPIO

    output_logging.borrar_log()
    from . import output_logging as print
    print = print.print_output
except:
    print("MODO DEBUg ( no nfc)")
    home_dir = "~/Documentos/evotebox2"
    DEBUG_ = True

configuration_file = "{}/evotebox2/functions/configuracion.json".format(home_dir)
censo_dir = "{}".format(home_dir)

def init_module(mod):
    """
    Funcion que inicia to_do el sistema
    :param mod: Numero del modulo
    :return: String, 
    correct -> tdo correcto
    error_usb -> se ha producido un error en el usb
    error_nfc -> se ha producido un error al importar las claves nfc
    error_db -> se ha producido un error al realizar operaciones en la base de datos
    """

    # Comprobar si se encuentra el usb con los ficheros
    usb = check_usb()
    # Comprobar la variable de entorno evotebox
    env = 'apertura_siempre'
    # env = obtener_estado()

    if usb != 'error_usb':

        #TODO no hay estados
        # Obtener en que modulo se ejecuta
        if env == 'voting':
            result = continuar_proceso(mod)
        elif env == 'cierre':
            result = cerrar_proceso(mod)
        else:
            result = cargar_proceso(mod)
    else: #error de usb
        return 'error_usb'
    return result

def cargar_proceso(var_module):
    """
    ENV == apertura, carga el proceso de arranque de cada modulo
    :param var_module: variable de entorno de estado (String)
    :return: variable de estado, True si correcto, False si falla
    """
    print("Cargar proceso")

    #Crea carpeta temporal
    try:
        call("mkdir {}".format(dir_temp_evotebox), shell=True)
    except Exception as e:
        print("La carpeta {} ya existe".format(dir_temp_evotebox))
        
    copy_conf()
    print("modulo {}".format(var_module))
    if var_module == 1:

        #Comprobar si se encuentran las claves en el usb
        if check_NFC_keys():

            #Guardar las claves NFC en tmp
            copy_tmp_NFC_keys()
        else:
            print("Creando claves NFC")
            #Crear claves NFC y guardarlas en el USB
            create_save_NFC_keys()

            #Guardar las claves NFC en tmp
            copy_tmp_NFC_keys()

            #Hash de los dni's de los votantes
        if es_votacion_anonima():
            hash_dni()

        #Pasa a estado voting
        cambiar_estado('voting')
        umount_pendrive()
        return 'correct'

    elif var_module == 2:

        #Comprobar si se encuentran las claves en el usb
        if check_NFC_keys():
            #Guardar las claves NFC en tmp
            copy_tmp_NFC_keys()
        else:
            #No existen las claves NFC
            return 'error_nfc'

        #bd propuestas
        copy_bd_propuestas_mod2()

        # Set ENV variable a voting
        cambiar_estado('voting')

        return 'correct'

    elif var_module == 3:
        #Comprobar si se encuentran las claves en el usb
        if check_NFC_keys():
            if not exists_keys_NFC():
                #Guardar las claves NFC en tmp
                copy_tmp_NFC_keys()
        else:
            #No existen las claves NFC
            print("No existen las claves NFC en el USB")
            return 'error_nfc'


        if hay_impresora():
            #Configurar impresora
            configurar_impresora()

        #Importar la base de datos
        crear_censo()

        #propuestas db
        copy_bd_propuestas_mod3()

        if es_votacion_anonima():
            print("--------- VOTACION ANONIMA -----------")
            #Creamos la BD de votos
            create_db_votos()

            # Crear las claves del cifrado de la base de datos
            create_certs()

            # Cifrar la base de datos
            cifrado_db()

            # Descifrar la base de datos
            descifrar_db()
        else:
            print("--------- VOTACION NO ANONIMA -----------")


        #Pasa a estado voting
        cambiar_estado('voting')
        umount_pendrive()
        return True

    else:
        print("Error de modulo")
        return False

def umount_pendrive():
    """
    Funcion que desmonta el prndrive
    :return:
    """
    if not DEBUG_:
        print("Desmontando pendrive")
        call("sudo umount /dev/sda1", shell=True)

def create_db_votos():
    """
    Crea la base de datos y la tabla de votacion vacia
    :return:
    """
    db = votacion.Votacion("{}/votacion.db".format(dir_temp_evotebox))
    db.create_table()
    db.close_database()

def continuar_proceso(var_module):
    """
    ENV = voting, continuar la apertura del modulo
    :param var_module: variable de entorno de estado (String)
    :return: variable de estado, True si correcto, False si falla
    """
    print("Continuando el proceso")
    #Si se encuentra en el modulo 3 descifrar la base de datos y continuar
    if var_module == 3:
        #Descifrar la base de datos
        if check_certs():
            descifrar_db()
        else:
            #No se encuentra la base de datos ni los archivos de descifrado
            return "error_db_continuar"

    elif var_module == 1:
        #Comprobar si se encuentran las claves en el usb
        if check_NFC_keys():
            #Guardar las claves NFC en tmp
            copy_tmp_NFC_keys()
        else:
            return 'error_nfc'

    elif var_module == 2:
        #Comprobar si se encuentran las claves en el usb
        if check_NFC_keys():
            #Guardar las claves NFC en tmp
            copy_tmp_NFC_keys()
        else:
            return 'error_usb'

def cerrar_proceso(var_module):
    """
    ENV = cierre, cerrar el modulo
    :param var_module: variable de entorno de estado (String)
    :return: variable de estado, True si correcto, False si falla
    """
    print("Cerrado del proceso, borrando los archivos temporales del sistema")
    # Set ENV variable a cierre
    cambiar_estado('cierre')
    if var_module == 1 or var_module == 2:
        return 'correct'

    if check_usb() == "error_usb":
        print("Falta algo en el usb")
        return 'error_usb'

    # Si se encuentra en el modulo 3 cerrar la base de datos y cifrarla
    if var_module == 3:

        m3.recuento_votos()
        if cifrado_db():
            # copy_db_to_usb()
            copy = copy_on_home()
            if not copy:
                return "error_db_cerrar"
        else:
            return 'error_db_cerrar'

    ## En decidimVlc la base de datos no se borra, se guarda de forma incremental dia a dia
    if not decidimVlc:
        # Limpiar carpeta temporal
        try:
            call("rm -rf " + dir_temp_evotebox + "*", shell=True)
            call(censo_dir + "/censo.db", shell=True)
            # os.remove(censo_dir + "/censo.db")
        except Exception as e:
            print("Fallo al borrar la carpeta temporal: {}".format(dir_temp_evotebox))
            return False

    # Desmontamos el pendrive para que se guarden los datos
    umount_pendrive()

    return 'correct'

"""
FUNCIONES DE APOYO
"""

def copy_on_home():
    """
    Copia los datos en una carpeta en home
    Copia censo_cifrado.db.enc y recuento_votos.csv
    :return:
    """
    print("copy_on_home")
    date = datetime.now() + timedelta(hours=2)
    copy_dir_name = "copia_{}".format(date.strftime("%Y_%m_%d_%H_%M_%S"))
    if not os.path.exists("{}/{}".format(home_dir, copy_dir_name)):
        os.makedirs("{}/{}".format(home_dir, copy_dir_name))
    try:
        if not es_votacion_anonima():
            print("Copiando fichero censo {}/censo.db en {}/{}/censo.db".format(censo_dir, home_dir, copy_dir_name))
            shutil.copyfile("{}/censo.db".format(censo_dir), "{}/{}/censo.db".format(home_dir, copy_dir_name))
            print("Copiando fichero recuento de votos de {}/recuento_votos.csv en {}/{}/recuento_votos.csv".format(path_usb, home_dir, copy_dir_name))
            shutil.copyfile("{}/recuento_votos.csv".format(path_usb), "{}/{}/recuento_votos.csv".format(home_dir, copy_dir_name))
            return True
        else:
            pass
            #TODO que hay que copiar?
    except Exception as e:
        print("Fallo al copiar: {}".format(e))
        return False

def obtener_estado():
    """
    Comprueba si existe archivo estado devuelve el string de estado, sino crea el fichero y pone estado apertura
    :return: String del estado, False si error
    """
    try:
        if os.path.isfile("{}/estado".format(dir_temp_evotebox)):
            file = open("{}/estado".format(dir_temp_evotebox),"r")
            line = file.readline()[:-1]
            print(len(line))
            if line == 'cierre':
                res = 'cierre'
            elif line == 'voting':
                res = 'voting'
            else:
                res = 'apertura'
            file.close()
            return res
        else:
            file = open("{}/estado".format(dir_temp_evotebox),"w")
            file.write('apertura')
            file.close
    except Exception as e:
        return False

def cambiar_estado(estado):
    """
    Cambia el estado en el archivo temporal
    :param estado: Estado a modificar (String)
    :return: Estado (Boolean) False no error, True error
    """
    try:
        if os.path.isfile("{}/estado".format(dir_temp_evotebox)):
            with open('{}/estado'.format(dir_temp_evotebox), 'r+') as f:
                f.read()
                f.seek(0, 0)
                f.write(estado + "\n")
                f.close()
            return True
        else:
            return False
    except Exception as e:
        raise

def check_usb():
    """
    Comprobar que se encuentran los ficheros necesarios para el modulo 1, configuracion.json

    :return: String con el path del usb path_usb o False si hay error
    """
    try:
        if not os.path.isdir(path_usb):
            print("No hay carpeta usb :{}".format(os.path.isdir(path_usb)))
            return 'error_usb'


        usb_files = [f for f in os.listdir(path_usb) if isfile(join(path_usb, f))]
        exists_conf = "configuracion.json" in usb_files
        exists_bd = "bd_propuestas.csv" in usb_files
        exists_censo_db = nombre_bd_censo in usb_files


        if decidimVlc:
            exists_pres_distr = nombre_archivo_prop_distr in usb_files

        if exists_conf and exists_bd and exists_censo_db:
            if decidimVlc:
                if exists_pres_distr:
                    return path_usb
                else:
                    print("Falta el fichero {}".format(nombre_archivo_prop_distr))
                    return 'error_usb'
            else:
                return path_usb
        else:
            print("Error! No se encuentran los ficheros necesarios en el usb. Existe configuracion.json: {} \n y bd_propuestas.csv {} y {} {}".format(
                exists_conf, exists_bd, nombre_bd_censo,exists_censo_db
            ))
            return 'error_usb'
    except:
        return 'error_usb'

def check_certs():
    """
    Comprueba si hay archivos de cifrado y descifrado
    :return: Estado (Boolean) False no error, True error
    """
    print("check_certs")
    try:
        return os.path.isfile(path_usb+"/private.pem") and os.path.isfile(path_usb+"/keyfile.enc") and os.path.isfile("{}/censo.db.enc".format(dir_temp_evotebox))
    except Exception as e:
        return False

def check_NFC_keys():
    """
    Comprueba si hay archivo de claves en el USB
    :return: Estado (Boolean) False no error, True error
    """
    print("check_usb")
    try:
        return os.path.isfile(path_usb+"/keys_nfc")
    except Exception as e:
        return False

def create_save_NFC_keys():
    """
    Crea las claves NFC y las guarda en el USB
    :return: Estado (Boolean) False no error, True error
    """
    print("create_save_NFC_keys")
    keys = []
    file = open(path_usb+"/keys_nfc","w")
    for i in range(0,16):
        key = ""
        for k in range(0,6):
            key += binascii.b2a_hex(os.urandom(1)).decode('ascii')
            if k < 5:
                key += ","
        keys.append(key)
        file.write(key+'\n')
    file.close()
    #Verificar que hay 
    result = False
    test = open(path_usb+"/keys_nfc","r")
    i = 0
    for k in test:
        if k[:-1] == keys[i]:
            result = True
        i = i+1
    return result


def hay_impresora():
    """
    Hay impresora o no
    :return: True si, False no hay
    """

    conectada = json.loads(open(configuration_file, encoding="utf-8").read())['impresora']

    return conectada.lower() == "si"

def configurar_impresora():
    """
    Si se va a utilizar una impresora se crea el archivo impresora en  dir_temp_evotebox
    :return: Boolean
    """
    print("configurar_impresora")

    file = open(dir_temp_evotebox + "/impresora", "w")
    file.close()
    return True

def copy_conf():
    """
    Copia la configuracion en la carpeta functions
    :return: True, o False si va mal
    """
    path_to_copy = "{}/evotebox2/functions/configuracion.json".format(home_dir)

    print("copy archivo de configuracion propuestas en {}".format(path_to_copy))
    try:
        shutil.copyfile("{}/configuracion.json".format(path_usb), path_to_copy)
        return True
    except Exception as e:
        print("Error en la copia del archivo de configuracion")
        return False

def copy_bd_propuestas_mod3():
    """
    Copia la bd de ropuestas en el directorio functions/propuestas.
    En la version decidimVlc tambien se copia la relacion del presupuesto por distrito.
    :return: True, o False si va mal
    """

    if not os.path.exists("{}/evotebox2/functions/propuestas".format(home_dir)):
        os.makedirs("{}/evotebox2/functions/propuestas".format(home_dir))

    path_to_copy = "{}/evotebox2/functions/propuestas/bd_propuestas.csv".format(home_dir)

    print("copy bd propuestas en {}".format(path_to_copy))
    try:
        shutil.copyfile("{}/bd_propuestas.csv".format(path_usb), path_to_copy)

    except Exception as e:
        print("Error en la copia de las propuestas del modulo (origen: {} destino: {}".format(
            "{}/bd_propuestas.csv".format(path_usb),
            path_to_copy
        ))
        return False

    ### Copia de los presupuestos por distrito
    path_to_copy = "{}/evotebox2/functions/propuestas/{}".format(home_dir, nombre_archivo_prop_distr)
    print("copy presupuestos por distrito en {}".format(path_to_copy))
    try:
        shutil.copyfile("{}/{}".format(path_usb, nombre_archivo_prop_distr), path_to_copy)

    except Exception as e:
        print("Error en la copia de los presupuestos por distrito del modulo 3 (origen: {} destino: {}".format(
            "{}/{}".format(path_usb, nombre_archivo_prop_distr),
            path_to_copy
        ))
        return False

    return True

def copy_bd_propuestas_mod2():
    """
    Copia la bd de ropuestas en el directorio templates del modulo 2
    En la version decidimVlc tambien se copia la relacion del presupuesto por distrito.
    :return: True, o False si va mal
    """
    copy_bd_propuestas_mod3()
    path_to_copy = "{}/evotebox2/module2/static/module2/bd_propuestas.csv".format(home_dir)

    print("copy bd propuestas en {}".format(path_to_copy))
    try:
        shutil.copyfile("{}/bd_propuestas.csv".format(path_usb), path_to_copy)

    except Exception as e:
        print("Error en la copia de las propuestas del modulo 2")
        return False


    ### Copia de los presupuestos por distrito
    path_to_copy = "{}/evotebox2/functions/propuestas/{}".format(home_dir, nombre_archivo_prop_distr)
    print("copy presupuestos por distrito en {}".format(path_to_copy))
    try:
        shutil.copyfile("{}/{}".format(path_usb, nombre_archivo_prop_distr), path_to_copy)

    except Exception as e:
        print("Error en la copia de los presupuestos por distrito del modulo 2(origen: {} destino: {}".format(
            "{}/{}".format(path_usb, nombre_archivo_prop_distr),
            path_to_copy
        ))
        return False

    return True

def exists_keys_NFC():
    """
    Verifica si en este modulo existen las llaves NFC o no
    :return: True si extsien, False si no
    """
    try:
        os.path.isfile("{}/keys_nfc".format(dir_temp_evotebox))
    except:
        return False
def copy_tmp_NFC_keys():
    """
    Copiar claves a tmp
    :return: Estado (Boolean) False no error, True error
    """
    print("copy_tmp_NFC_keys")
    try:
        shutil.copyfile(path_usb+"/keys_nfc", "{}/keys_nfc".format(dir_temp_evotebox))
        return True
    except Exception as e:
        print("Error en la copia de las claves NFC")
        return False

def copy_db_to_usb():
    """
    Copiar claves a tmp
    :return: Estado (Boolean) False no error, True error
    """
    print("copy_db_to_usb")
    try:
        shutil.copyfile("{}/censo.db.enc".format(dir_temp_evotebox),path_usb+"/censo_cifrado.db.enc")
        return True
    except Exception as e:
        return False

def crear_censo():
    '''
    Importar censo al sistema en dir_temp_evotebox
     Main de importar censo y guardar en la base de datos en la carpeta dir_temp_evotebox/{censo.db}
    :return: boolean. True si no hay error, String, error_db_censo si se produce un error
    '''
    print("crear censo")
    try:
        usb_files = [f for f in os.listdir(path_usb) if isfile(join(path_usb, f))]

        if nombre_bd_censo not in usb_files:
            print("No se puede importar censo desde el USB. Falta el archivo censo con los DNIs hasheados")
            return "No se puede importar censo desde el USB. Falta el archivo censo con los DNIs hasheados"

        dnis_hash = obtener_dni()
        db = censo.Censo("{}/censo.db".format(censo_dir))
        db.create_table()
        if not decidimVlc:
            for dni_hash in dnis_hash:
                db.add_DNI(dni_hash)
                # print("hash añadido {}".format(dni_hash))
        else:
            print("No se ñaden DNIs al censo, version DecidimVlc")
        db.close_database()
        return True
    except Exception as e:
        print("error_db_censo")
        return 'error_db_censo'


"""
    Funciones de cifrado y descifrado de la base de datos
"""
def cifrado_db():
    """
    Cifrado de la base de datos
    :return: boolean. True si no hay error
    """
    print("cifrado_db")
    try:
        result = call("openssl enc -aes-256-cbc -a -kfile " + path_usb +"/keyfile -in " + dir_temp_evotebox + "/censo.db -out " + dir_temp_evotebox + "/censo.db.enc", shell=True)
        if es_votacion_anonima():
            os.remove(censo_dir + "/censo.db")
        return True
    except Exception as e:
        print("Fallo en cifrado db")
        return False

def descifrar_db():
    """
    Descifrar la base de datos
    :return: boolean. True si no hay error
    """
    print("descifrar_db")
    try:
        call("openssl rsautl -decrypt -inkey " + path_usb + "/private.pem -in "+path_usb+"/keyfile.enc -out "+path_usb+"/keyfile.dec", shell=True )
        call("openssl enc -d -aes-256-cbc -a -kfile " + path_usb +"/keyfile.dec -in " + dir_temp_evotebox + "/censo.db.enc -out " + dir_temp_evotebox + "/censo.db", shell=True)
        os.remove(dir_temp_evotebox + "/censo.db.enc")
        return True     
    except Exception as e:
        raise

def create_certs():
    """
    Crear los certificados de cifrado en el usb
    :return: boolean. True si no hay error
    """
    print("create_certs")
    try:
        call("openssl rand -base64 128 > "+path_usb+"/keyfile",shell=True)
        call("openssl genrsa -out " +path_usb+"/private.pem 2048",shell=True)
        call("openssl rsa -in "+path_usb+"/private.pem -out "+path_usb+"/public.pem -outform PEM -pubout",shell=True)
        call("openssl rsautl -encrypt -pubin -inkey "+path_usb+"/public.pem -in "+path_usb+"/keyfile -out "+path_usb+"/keyfile.enc",shell=True)
        return True
    except Exception as e:
        raise


def detect_module():
    """
    Funcion que devuelve el numero del modulo
    :return: int. 1 2 o 3, dependiendo del modulo
    modulo 1 : tiene el pin GPIO06 conectado a 3.3 V
    modulo 2 : tiene el pin GPIO13 conectado a 3.3 V
    modulo 3 : else

    @ Adrian
    """
    if DEBUG_:
        return 2


    GPIO.setmode(GPIO.BCM)
    GPIO.setup(19, GPIO.IN)
    GPIO.setup(13, GPIO.IN)
    GPIO.setup(6, GPIO.IN)


    time.sleep(2)


    while (True):
        res1 = 0
        res2 = 0
        for x in range(10):
            res1 = res1 + GPIO.input(6)
        if (res1 > 0 and res1 < 9):
            continue
        elif (res1 > 0):
            res1 = 1
        for x in range(10):
            res2 = res2 + GPIO.input(13)
        if (res2 > 0 and res2 < 9):
            continue
        elif (res2 > 0):
            res2 = 1




        if (res1 == 1 and res2 == 0):
            res = 1
            break
        elif (res1 == 0 and res2 == 1):
            res = 2
            break
        elif (res1 == 0 and res2 == 0):
            res = 3
            break

    print("Modulo {} detectado".format(res))

    return res


def hash_dni():
    """
    Hashea los dni del archivo de configuración y crea el censo que necesita el modulo3
    :param path_module: String
    :return: Boolean, True si se han creado los archivos
    """

    df = pd.read_csv("{}/{}".format(path_usb, nombre_bd_censo))
    df = df['dni'].apply(lambda x: hashlib.sha512(x.encode('utf-8')).hexdigest())

    df = df.to_frame()
    df.to_csv("{}/{}".format(path_usb, nombre_bd_censo), index=False, columns=["dni"])


def hash_one_dni(dni):
    """
    Hashea un dni
    :param dni: String
    :return: Boolean, True si se han creado los archivos
    """
    # Hashea el dni
    hs = hashlib.sha512(dni.encode('utf-8')).hexdigest()
    # print("DNI hasheado: {}".format(hs))
    return hs

def obtener_dni():
    """
    Obtiene los dni's del archivo censo
    :return: Array String
    """
    df = pd.read_csv("{}/{}".format(path_usb, nombre_bd_censo))

    return df['dni'].tolist()


def es_votacion_anonima():
    """
    Devuelve el tipo de la votación.
    :return: True si es anonima, False si es no anonima
    """
    anonimo = json.loads(open("{}".format(configuration_file), encoding="utf-8").read())['anonimo']

    return anonimo.lower() == "si"

def get_configuracion():
    """
    Devuelve el Nombre del convocante, nombre del proceso y direccion de correo para la connfiguracion.
    :return: String, String, String
    """

    json_file = json.loads(open("{}".format(configuration_file), encoding="utf-8").read())
    conf = json_file['configuracion']
    return conf['convocante'], conf['proces'], conf['correo']

def get_presupuesto():
    """
    Devuelve presupueto maximo.
    :return: int
    """

    json_file = json.loads(open("{}".format(configuration_file), encoding="utf-8").read())
    conf = json_file['configuracion']
    return conf['presupuesto']

if __name__ == "__main__":
    print(hash_dni())
