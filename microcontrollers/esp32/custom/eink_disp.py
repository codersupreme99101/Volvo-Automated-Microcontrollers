from adafruit_magtag.magtag import MagTag
from PIL import Image 
import displayio

import board
import time 

magtag = MagTag()

RED = 0x880000
GREEN = 0x008800
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0x888888

def light_up(color):
    magtag.peripherals.neopixel_disable = False
    magtag.peripherals.neopixels.fill(color)

name="" #get with some clever method

image_file="barcode_imgs/{}.png".format(name)

max_limit=10000 #g #5000 #g

weight_data=500 #get weight data from sensor 

#weight dispayer for neopixels 

def light_condition(weight_data, max_limit):

    if 0<=weight_data<max_limit/7:
        light_up(RED)

    elif max_limit/7<=weight_data<(2*max_limit)/7:
        light_up(YELLOW)

    elif (2*max_limit)/7<=weight_data<(3*max_limit)/7:
        light_up(GREEN)

    elif (3*max_limit)/7<=weight_data<(4*max_limit)/7:
        light_up(CYAN)

    elif (4*max_limit)/7<=weight_data<(5*max_limit)/7:
        light_up(BLUE)

    elif (5*max_limit)/7<=weight_data<(6*max_limit)/7:
        light_up(MAGENTA)

    elif (6*max_limit)/7<=weight_data<=(max_limit):
        light_up(WHITE) #simple, all same color, level indicator 

    pass


def png_to_bmp(filename): #png to bitmap conversion

    file_in=filename+".png"
    img=Image.open(file_in)

    file_out="{}.bmp".format(filename)
    img.save("barcode_bitmap/{}".format(file_out))

    pass

def load_image(img_name):

    board.DISPLAY.brightness = 0
    splash = displayio.Group()
    board.DISPLAY.show(splash)

    odb = displayio.OnDiskBitmap('barcode_bitmap/{}.bmp'.format(img_name))
    face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
    splash.append(face)
    
    board.DISPLAY.refresh(target_frames_per_second=60)

    board.DISPLAY.brightness = 0.5 #0-1
    time.sleep(0.05) #minor refresh

    pass


