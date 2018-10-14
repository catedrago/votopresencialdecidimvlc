"""
Archivo para sobrescribir print y escribir en un fichero
importar print_output con import as print
"""
import os

FILE_NAME_OUTPUT = "/home/dietpi/log"

def print_output(text):
    try:
        try:
            if type(text) == list:
                text = ' '.join(text)
        except:
            if type(text) == list:
                text = ' '.join(str(text))
        with open(FILE_NAME_OUTPUT, "a") as myfile:
            myfile.write(text+"\n")
    except:
        myfile.write("Fallo grabando algo :)" + "\n")

def borrar_log():
    try:
        os.remove(FILE_NAME_OUTPUT)
    except OSError:
        pass