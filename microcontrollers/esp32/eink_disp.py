

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont
import epd7in5 #change to eink model of choice 


EPD_WIDTH=128 #px
EPD_HEIGHT=64 #px ##edit 

def disp_eink_img():

    epd = epd7in5.EPD()
    epd.init()


    # For simplicity, the arguments are explicit numerical coordinates
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 124)
    image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)    # 1: clear the frame
    draw = ImageDraw.Draw(image)
    image = Image.open('bmp/mrwhite2.bmp')
    draw.text((200, 10), 'e-Paper demo', font = font, fill = 255)
    epd.display_frame(epd.get_frame_buffer(image))

