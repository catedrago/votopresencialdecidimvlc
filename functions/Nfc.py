#!/usr/bin/python3.5
import binascii
import Adafruit_PN532 as PN532
from itertools import zip_longest as zip
import sys, traceback, threading
import RPi.GPIO as GPIO
import time

"""
How to use this library:
First of all you MUST create an NFC object with the keys to use (6 bytes keys), one key for sector up to 16
nfc = Nfc([[0x07,0x07,0x07,0x07,0x07,0x07],[0x06,0x06,0x06,0x06,0x06,0x6]]) In this example we only use two keys for the first two sectors
Then if the card is virgin you should write the new keys to it
nfc.writeKeys();
Once this is done you can write/read the card normally with the functions explained down
nfc.write("hola");
print(nfc.read(all=True));
Finally if a key was used and you dont want to use that card until the next votation the default keys MUST be restored with:
nfc.cleanKeys();
"""
DEBUG_ = False
target_folder = "/tmp/evotebox/"


def handler():
    # Function triggered by the timeout, raises an exception
    Nfc.last_try = True


class Nfc:
    CS = 18
    MOSI = 23
    MISO = 24
    SCLK = 25

    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # permission keys to use in NFC card (PN532)
    ORIGINAL_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x07, 0x80, 0x69, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                    0xFF]  # Original key to write

    BLOCKS = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37,
              38, 40, 41, 42, 44, 45, 46, 48, 49, 50, 52, 53, 54, 56, 57, 58, 60, 61,
              62]  # Available information blocks

    AUTH_BLOCKS = [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]  # Blocks filled with keys

    def __init__(self, keysArray=[], debug=False):

        # PN532 initialization
        Nfc.debug = debug
        Nfc.keysArray = keysArray  # Store the new keys
        while (True):
            try:
                Nfc.pn532 = PN532.PN532(cs=Nfc.CS, sclk=Nfc.SCLK, mosi=Nfc.MOSI, miso=Nfc.MISO)
                Nfc.pn532.begin()
                Nfc.pn532.SAM_configuration()
                break
            except:
                if (Nfc.debug): print("Error creating Nfc object")

    @staticmethod
    def chuncks(hex, num):  # Auxiliar function
        for i in range(0, len(hex), num):
            yield hex[i:i + num]

    def card_available(self):
        """
        :return: True if there is a card available or False otherwise
        """
        exist = Nfc.pn532.read_passive_target()
        if exist is None:
            return False
        else:
            return True

    def read(self, start=0, end=47, all=False, timeout=15):
        """
        :param start: Starts the reading from this block
        :param end:  Ends the reading at this block
        :param all: If true read doesnt stop when it finds an empty block
        :param timeout: Sets a different timeout
        :return: String result if successful, 0 if an error occurs
        """
        try:
            Nfc.last_try = False
            t = threading.Timer(timeout, handler)
            t.start()

            if Nfc.debug:  print("Waiting for a Nfc compatible card to read...")

            while True:

                failed = False

                uid = Nfc.pn532.read_passive_target()
                while uid is None and not Nfc.last_try:
                    uid = Nfc.pn532.read_passive_target()

                data = ""

                for i in Nfc.BLOCKS[start:end]:

                    if i // 4 + 1 > len(Nfc.keysArray):
                        key = Nfc.CARD_KEY
                    else:
                        key = Nfc.keysArray[i // 4]

                    if Nfc.last_try or not Nfc.pn532.mifare_classic_authenticate_block(uid, i, PN532.MIFARE_CMD_AUTH_A,
                                                                                       key):
                        failed = True
                        break

                    chunck = Nfc.pn532.mifare_classic_read_block(i)
                    if chunck is None: failed = True; break

                    if chunck == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                        if all == True:
                            continue
                        else:
                            break;
                    chunck = binascii.unhexlify(chunck)
                    chunck = chunck.decode()
                    chunck = chunck.replace('\x00', '')
                    data += chunck

                if not failed:
                    break
                elif Nfc.last_try:
                    raise ValueError

        except ValueError:
            # traceback.print_exc()
            if Nfc.debug: print("Timeout")
            return 0

        except:
            t.cancel()
            if Nfc.debug: print("Card error")
            return 0

        t.cancel()
        return data

    def write(self, b, start=0, end=47, clean=False, timeout=15):
        """
        :param b: String to write on the Nfc card
        :param start: Starts the writing from this block
        :param end:  Ends the writing at this block
        :param clean: Sets to 0 all the rest of the blocks that are not used between the start and end block
        :param timeout: Sets a different timeout
        :return: 1 if success, 0 if there is an error
        """
        try:
            Nfc.last_try = False
            t = threading.Timer(timeout, handler)
            t.start()

            if Nfc.debug: print("Waiting for a Nfc compatible card to write...")

            while True:

                failed = False

                uid = Nfc.pn532.read_passive_target()
                while uid is None and not Nfc.last_try:
                    uid = Nfc.pn532.read_passive_target()
                hex = binascii.hexlify(b.encode())
                hexList = list(self.chuncks(hex, 16))
                blocksData = list(zip(Nfc.BLOCKS[start:end], hexList))

                for i in blocksData:
                    if i[0] // 4 + 1 > len(Nfc.keysArray):
                        key = Nfc.CARD_KEY
                    else:
                        key = Nfc.keysArray[i[0] // 4]

                    if Nfc.last_try or not Nfc.pn532.mifare_classic_authenticate_block(uid, i[0],
                                                                                       PN532.MIFARE_CMD_AUTH_A, key):
                        failed = True
                        break

                    value = i[1]
                    if value is None and clean:
                        value = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

                    elif value is None:
                        break;
                    while 16 > len(value):
                        value = value + b'0'

                    if not Nfc.pn532.mifare_classic_write_block(i[0], value):
                        failed = True
                        break

                if not failed:
                    break
                elif Nfc.last_try:
                    raise ValueError

        except ValueError:

            if Nfc.debug: print("Timeout")
            return 0

        except:

            if Nfc.debug: print("Card error")
            t.cancel()
            return 0

        t.cancel()
        return 1

    def writeKeys(self, timeout=15):
        """
        This function MUST be called before any read/write on a virgin card, it writes the keys that will be used to access the information
        :return: 0 if an error ocurred or 1 if all went good
        """
        try:
            Nfc.last_try = False
            t = threading.Timer(timeout, handler)
            t.start()

            if Nfc.debug: print("Waiting for a Nfc compatible card to write the keys...")
            while True:
                failed = False
                count = -1
                uid = Nfc.pn532.read_passive_target()
                while uid is None and not Nfc.last_try:
                    uid = Nfc.pn532.read_passive_target()

                for i in Nfc.keysArray:
                    count = count + 1
                    key = i[:]
                    key.extend([0xFF, 0x07, 0x80, 0x69])
                    key.extend(i)
                    if Nfc.last_try: failed = True; break
                    if Nfc.pn532.mifare_classic_authenticate_block(uid, Nfc.AUTH_BLOCKS[count], PN532.MIFARE_CMD_AUTH_A,
                                                                   i): continue
                    uid = Nfc.pn532.read_passive_target()
                    if not Nfc.pn532.mifare_classic_authenticate_block(uid, Nfc.AUTH_BLOCKS[count],
                                                                       PN532.MIFARE_CMD_AUTH_A,
                                                                       Nfc.CARD_KEY):
                        failed = True
                        break
                    Nfc.pn532.mifare_classic_write_block(Nfc.AUTH_BLOCKS[count], key)

                if not failed:
                    break
                elif Nfc.last_try:
                    raise ValueError

        except ValueError:

            if Nfc.debug: print("Timeout")
            return 0
        except:

            if Nfc.debug: print("Card Error")
            t.cancel()
            return 0

        t.cancel()
        return 1

    def cleanKeys(self, timeout=15):
        """
        This function removes the keys of the card and resets it to the default, MUST be called after the card will not be readed/written again
        :param timeout: Timeout that avoids infinite waiting
        :return: 0 if an error ocurred or 1 if all went good
        """
        try:
            Nfc.last_try = False
            t = threading.Timer(timeout, handler)
            t.start()

            if Nfc.debug: print("Waiting for a Nfc compatible card to clean the keys...")
            while True:
                failed = False
                count = -1
                uid = Nfc.pn532.read_passive_target()
                while uid is None and not Nfc.last_try:
                    uid = Nfc.pn532.read_passive_target()

                for i in Nfc.keysArray:
                    count = count + 1
                    if Nfc.last_try: failed = True; break
                    if Nfc.pn532.mifare_classic_authenticate_block(uid, Nfc.AUTH_BLOCKS[count], PN532.MIFARE_CMD_AUTH_A,
                                                                   Nfc.CARD_KEY): continue
                    uid = Nfc.pn532.read_passive_target()

                    if not Nfc.pn532.mifare_classic_authenticate_block(uid, Nfc.AUTH_BLOCKS[count],
                                                                       PN532.MIFARE_CMD_AUTH_A,
                                                                       i):
                        failed = True
                        break;

                    Nfc.pn532.mifare_classic_write_block(Nfc.AUTH_BLOCKS[count], Nfc.ORIGINAL_KEY)

                if not failed:
                    break;
                elif Nfc.last_try:
                    raise ValueError

        except ValueError:

            if Nfc.debug: print("Timeout")
            return 0
        except:

            if Nfc.debug: print("Card Error")
            t.cancel()
            return 0

        t.cancel()
        return 1

    def has_default_keys(self):

        uid = Nfc.pn532.read_passive_target()
        while uid is None:
            uid = Nfc.pn532.read_passive_target()
        if Nfc.pn532.mifare_classic_authenticate_block(uid, Nfc.AUTH_BLOCKS[0], PN532.MIFARE_CMD_AUTH_A, Nfc.CARD_KEY):
            return True
        else:
            return False


def escribir_votos(votos, dni=None):
    """
    Escribe en una tarjeta NFC los votos pasados por parametros
    :param votos: array de integers. [1,5,82,14]
    :return: True si va bien, False si no va bien
    """
    nfc = Nfc(get_keys())
    if (detect_module() == 1):
        if (nfc.writeKeys() == 0):
            return False
    if Nfc.debug: print("Escbribiendo votos {}".format(votos))
    if (votos == []):
        valores = "-"
    else:
        valores = "*".join(str(x) for x in votos)
    if (dni is not None): valores = valores + "_" + dni
    if Nfc.debug: print("Valores: {}".format(valores))
    if (nfc.write(valores, clean=True, end=15) == 1):
        return True
    else:
        return False


def tarjeta_interventor():
    """
    Escribe en la tarjeta un -1 para ser interventor
    :return: Resultado de escribir votos
    """
    return escribir_votos([-1])


def leer_votos():
    """
    Funcion que lee los votos de la tarjeta NFC
    :return: un array de integers (vacio si no hay votos), False si no se ha podido leer
    """
    dni = None
    nfc = Nfc(get_keys())
    if (nfc.writeKeys() == 0): return False
    votos = nfc.read()
    print("Votos desde read() :  {}".format(votos))
    try:
        votos = str(votos)
        pos = votos.find("_")
    except:
        pos = -1

    print("pos: {}".format(pos))
    if (pos != -1):
        dni = votos[(pos + 1):]
        votos = votos[0:(pos)]
    if (not votos): return False
    if (votos != '-'):
        try:
            votos = votos.split("*")
            votos = list(map(int, votos))
            if (dni is not None): votos.append(dni)
            return votos
        except:
            return False
    else:
        if (dni is not None): return [dni]
        return []


def default_keys():
    """
    :return True si tiene las claves por defecto, False si no
    """
    nfc = Nfc()
    return nfc.has_default_keys()


def detect_module():
    """
    Funcion que devuelve el numero del modulo
    :return: int. 1 2 o 3, dependiendo del modulo, 0 si no se ha conseguido detectar
    modulo 1 : tiene el pin GPIO06 conectado a 3.3 V
    modulo 2 : tiene el pin GPIO13 conectado a 3.3 V
    modulo 3 : tiene el pint GPIO19 conectado a 3.3V
    """

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


def get_keys():
    """
    Devuelve las claves para encriptar las tarjetas
    :return: Array con las claves
    """
    file_name = "keys_nfc"
    file = open(target_folder + file_name, "r")
    res = []
    for line in file:
        hexa = line.split(',')
        hexa = [int(str(x.rstrip()), 16) for x in hexa]
        res.append(hexa)
    return res


if __name__ == "__main__":
    # escribir_votos([1,2])
    print(leer_votos())
    # print(default_keys())
