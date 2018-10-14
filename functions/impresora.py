# encoding: utf-8
from __future__ import unicode_literals, print_function
from escpos.printer import Usb
import traceback
from datetime import datetime, timedelta
from escpos import *
try:
    #raspby
    from . import propuestas
except:
    import propuestas

path_proyecto = "/home/dietpi/evotebox2/"

#formatea a euro, poniendo puntos
def format_price(price):
    price = str(price)
    res = ''
    count = 0
    for p in reversed(price):
        count += 1
        res += p
        if count%3 == 0:
            res += '.'

    res = res[::-1]

    if res[0] == '.':
        res = res[1:]
    return res


def imprimir(data=[]):
    try:
        impr(data)
    except Exception as e:
        print("Error en la impresora: \n {}".format(traceback.format_exc()))

def impr(data = []):
    """
    Data = id de proyectos votados
    :param data:
    :return:
    """
    p = Usb(0x04b8, 0x0e15, 0, )
    # f = open("to_save", 'r+')
    # lines = f.readlines()[0]
    # data = ast.literal_eval(lines)
    p.image("{}functions/cabecera.jpg".format(path_proyecto))
    p.set(font='a', height=1, align='center')
    p.codepage = 'cp850'
    # p.charcode("MULTILINGUAL")
    # print(p.codepage)
    try:
        p.text('Presupuestos Participativos de Inversiones 2018\n')
        p.text('- Recibo informativo - \n')

        p.text('----------------------------------- \n')
        p.set(font='a', height=2, align='center')
        # date = datetime.now()
        date = datetime.now() + timedelta(hours=2)
        p.text('Votación realizada: \n {} \n \n'.format(date.strftime("%Y-%m-%d %H:%M:%S")))
        p.set(font='a', height=2, align='center')
        p.text('Proyectos elegidos: \n \n')
        p.set(font='a', height=1, align='center')
        #propuestas
        contMax = 0
        for i in data:
            e = propuestas.search_name_by_id(i)
            if e is None:
                print("Id de proyecto {} no valido".format(i))

            else:
                title, price = e
                contMax = contMax + int(price)
                price = format_price(price)
                p.text('{} - {} e \n\n'.format(title, price))

        p.set(font='a', height=2, align='center')
        p.text('\n Inversión total votada: ')
        p.text('{} e \n'.format(format_price(contMax)))
        p.set(font='a', height=1, align='center')
        p.text('\n \n Gracias por su participación \n')
        p.text('----------------------------------- \n')
        p.set(font='a', height=1, align='center')
        p.text(
            'Sistema presencial de votación electrónica \n')
        p.text("Evotebox \n")
        p.image("{}functions/gente.png".format(path_proyecto))
        p.cut()
        p.close()
    except:
        # print(traceback.format_exc())
        p.cut()
        p.close()


def imprimir_ticket_final(data = {}, num_participantes=0):
    """
    Data = diccionario {id:num}
    :param data:
    :return:
    """
    p = Usb(0x04b8, 0x0e15, 0, )

    p.image("{}functions/cabecera.jpg".format(path_proyecto))
    p.set(font='a', height=1, align='center')
    p.codepage = 'cp850'
    try:
        p.text('Presupuestos Participativos de Inversiones 2018\n')
        p.text('- Acta de recuento - \n')

        p.text('----------------------------------- \n')
        p.set(font='a', height=2, align='center')
        # date = datetime.now()
        date = datetime.now() + timedelta(hours=2)
        p.text('Recuento realizado: \n {} \n \n'.format(date.strftime("%Y-%m-%d %H:%M:%S")))
        p.set(font='a', height=2, align='center')
        p.text('Participantes: {} personas\n \n'.format(num_participantes))
        p.text('Total de proyectos votados: {} proyectos \n \n'.format(len(data)))
        p.text('Proyectos votados: \n \n')
        p.set(font='a', height=1, align='center')
        if len(data) == 0:
            p.text("Lista vacia")
        #propuestas
        for i in data:
            e = propuestas.search_name_by_id(i)
            if e is None:
                print("Id de proyecto {} no valido".format(i))

            else:
                title, price = e
                votos = data[i]
                if votos == 1:
                    p.text('{} - {} voto \n\n'.format(title, votos))
                else:
                    p.text('{} - {} votos \n\n'.format(title, votos))

        p.set(font='a', height=1, align='center')
        p.text('----------------------------------- \n')
        p.set(font='a', height=1, align='center')
        p.text(
            'Sistema presencial de votación electrónica \n')
        p.text("Evotebox \n")
        p.image("{}functions/gente.png".format(path_proyecto))
        p.cut()
        p.close()
    except:
        # print(traceback.format_exc())
        p.cut()
        p.close()


def init():
    impr([1004, 1453, 1])


if __name__ == '__main__':
    # for i in [1004, 1453]:
    #     title, price = propuestas.search_name_by_id(i)
    #     print(title, price)
    init()
