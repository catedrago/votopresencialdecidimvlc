"""
Archivo python donde se iran creando las funciones necesarias para la deteccion de los DNI o NIE a partir de imagenes
FICHERO spa.traineddata SUBSTITUIDO:
sudo cp functions/spa.traineddata /usr/share/tesseract-ocr/tessdata/spa.traineddata

"""

# import the necessary packages
import pytesseract
import re
from PIL import ImageFilter
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

import PIL.ImageOps
import time, os
import imutils
import numpy as np
import time
import cv2
DEBUG_ = False
try:
    # django
    from .camara import capturar
    #local
    # from camara import capturar
except:
    DEBUG_ = True
    print("Modo debug en reconocimiento")

nifRegEx = '[0-9]{8}[A-Za-z]';
nifRegEx2 = '[0-9]{9}';
nieRegEx = '[XYZxyz][0-9]{7}[A-Za-z]';

def recognize(letters):
    """:param letters: image array (PIL)"""



    # letters.show()
    # a = input(" ")
    # for angle in [0]:
    for angle in np.arange(0, -3, -0.5):
        letters = letters.rotate(angle)

        # letters.show()

        text = pytesseract.image_to_string(letters, lang="spa")
        # print("Rotated: {} Txt: {}".format(angle, text))
        text = text.upper()

        #### Evitar fallos en letras inexistentes
        ## Letras que no existen -> O , U , Ñ, I
        text = text.replace('O','0')
        text = text.replace('U','V')
        text = text.replace('Ñ','N')
        text = text.replace('I','1')

        ####

        text = re.sub(r'[\W_]+', '', text)

        print(text)
        matches = re.findall(nifRegEx, text)
        matches.extend(re.findall(nieRegEx, text))
        # print(matches)
        for match in matches:
            if validoDNI(match):
                return match.upper()
        # Q por 0
        matches = re.findall(nifRegEx2, text)
        for match in matches:
            if match and type(match) == str and len(match) > 0:
                match = list(match)

                ## Cambiamos ceros en la ultima posicion por Qs (no hay Os en los DNIs)
                if match[-1] == '0':
                    match[-1] = "Q"
                # Cambiamos 8 $ y 5 por S
                elif str(match[-1].upper()) == '8' or str(match[-1].upper()) == "$"\
                        or str(match[-1].upper()) == '5':
                    match[-1] = "S"
                # 4 -> A
                elif str(match[-1].upper()) == '4':
                    match[-1] = 'A'

                match = "".join(match)
                if validoDNI(match):
                    return match.upper()

    return False

def validoDNI(dni):
    """
    Comprueba si un DNI o NIE es valido.
    :param dni: String
    :return: boolean
    """
    try:
        dni = dni.upper()
        tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
        dig_ext = "XYZ"
        reemp_dig_ext = {'X':'0', 'Y':'1', 'Z':'2'}
        numeros = "1234567890"
        dni = dni.upper()
        if len(dni) == 9:
            dig_control = dni[8]
            dni = dni[:8]
            if dni[0] in dig_ext:
                dni = dni.replace(dni[0], reemp_dig_ext[dni[0]])
            return len(dni) == len([n for n in dni if n in numeros]) \
                and tabla[int(dni)%23] == dig_control
        return False
    except:
        return False

def get_dni(image):
    """
    Aplica tecnicas de OCR sobre el DNI.
    Lo primero que hace es realizar una cuadricula sobre la foto de un dni y saca varias partes recortadas, donde posiblemente
    se encuentre el DNI, despues se llama a la funcion de OCR recognize() para aplicar el OCR, la cual valida el dni TAMBIEN.

    Modificando las variables x_orig y y_orig variamos la zona de busqueda de DNIS.
    Con las variables window_{} controlamos el tamaño de la zona del DNI.
    Con la lista de variables de width_try y height_try realizamos las diferentes variaciones de movimiento de la ventana.

    Para testear, descomentar las linea de draw y y show y se observara la cuadricula de los DNIs

    :param image: pillow.
    :return String DNI o NIE valido o None en caso de no encontrar nada


    """
    dnis = []

    width_try = [-150]
    # width_try = [-20, -10, 0, 10, 20]
    # width_try = range(-40,40,20)
    height_try = [-150]
    # height_try = [-20, -10, 0, 10, 20]
    # height_try = range(-40,40,20)

    window_height = 300
    # window_height = 80
    window_width = 600
    # window_width = 300
    ################ Tipo 1

    x_orig, y_orig = 300, 370

    # draw = ImageDraw.Draw(image)

    for w in width_try:
        for h in height_try:
            x = x_orig + w
            y = y_orig + h
            # draw.rectangle(((x, y), (x + window_width, y + window_height)), fill=None, )
            letters = image.crop((x, y, x + window_width, y + window_height))

            dnis.append(letters)

    # image.show()

    print("A reconocer: {} dnis".format(len(dnis)))

    for dni in dnis:
        dni_str = recognize(dni)
        if validoDNI(dni_str):
            print("DNI valido : {} ".format(dni_str))
            return dni_str
    print("NO HAY DNI valido  ")


def ocr_id(im):
    """
    Funcion para detectar un numero de DNI o NIE en una imagen
    :param image: imagen cargada a partir de cv2
    :return DNI o NIE valido. En caso de no encontrar DNI/NIE valido devuelve None
    """
    im = im.convert('L')
    text = get_dni(im)

    return text

def ocr_dni_camera():
    """
    Funcion auxiliar que llama a ocr_id, cargando la imagen dada por la camara
    :param pathfile: string
    :return: String, dni valido
    """
    if DEBUG_:

        return "00000000A"
    cv2_image = capturar()
    cv2_im = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(cv2_im)
    dni = ocr_id(image)

    return dni

def ocr_dni_path(pathfile):
    """
    Funcion auxiliar que llama a ocr_id, cargando la imagen dada por parametro
    :param pathfile: string
    :return: String, dni valido
    """
    image = Image.open(pathfile)
    dni = ocr_id(image)

    return dni

if __name__ == "__main__":

    path = "~/Documentos/evotebox2/evotebox2"

    p = [["messigray.png"]]
    for files in p:
        for f in files:

            time1 = time.time()
            pathfile = "{}/{}".format(path, f)
            image = Image.open(pathfile)
            print(pathfile)
            dni = ocr_id(image)
            del image
            finish = time.time()
            print("Fichero {} dni {}".format(pathfile, dni))
            print("Ha tardado {}".format(finish-time1))
            print("-"*20, end="\n")

