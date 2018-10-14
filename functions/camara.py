import io
import time
import picamera
import smbus
import cv2
import numpy as np
import random


# Create an in-memory stream

def capturar():
    """ 
    function that captures an image from the camera
    :return cv2 image object
    """
    my_stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        # camera.start_preview()
        # Camera warm-up sou    time
        flash(4)
        time.sleep(1)
        # time.sleep(600)
        camera.capture(my_stream, 'jpeg')
        buff = np.fromstring(my_stream.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(buff, 1)
        flash(0)
        return img


def flash(num_leds=4):
    bus = smbus.SMBus(1)
    if (num_leds == 0):
        bus.write_byte_data(0x70, 0x00, 0x00)
    elif (num_leds == 1):
        bus.write_byte_data(0x70, 0x00, 0x2)
    elif (num_leds == 2):
        bus.write_byte_data(0x70, 0x00, 0xA)
    elif (num_leds == 3):
        bus.write_byte_data(0x70, 0x00, 0x1A)
    else:
        bus.write_byte_data(0x70, 0x00, 0x5A)


def capturar_to_jpg(filename, path):
    """
    function that captures an image from the camera
    :return cv2 image object
    """
    my_stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # Camera warm-up time
        flash(4)
        time.sleep(4)
        filepath = '{}/{}.jpg'.format(path, filename)
        camera.capture(filepath)
        camera.stop_preview()
        flash(0)
        print("Nueva captura en {}".format(filepath))
        # camera.capture(my_stream, 'jpeg')
        # buff = np.fromstring(my_stream.getvalue(), dtype=np.uint8)
        # img=cv2.imdecode(buff,1)


if __name__ == "__main__":
    # capturar()
    a = ""
    while a != "fin":
        # filename = "dni_{}".format(random.randint(0,100000000))
        capturar_to_jpg(filename="dni_nuevo", path="./data/DNIS")

        a = input("escribe fin para finalizar\n")
