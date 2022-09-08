from machine import Pin, I2C
import ssd1306


i2c=I2C(-1,scl=Pin(22), sda=Pin(21))

address=0x3c
length=128
width=64

oled=ssd1306.SSD1306_I2C(length,width,i2c,address)


text_content_perc=""
num_items=0 #compute 
text_content_num="Number of Items: {}".format(num_items)

oled.text("Percentage Weight: {} \n {}".format(text_content_perc, text_content_num),5,5)

oled.show()


"""

# This Python code is meant for use with the Raspberry Pi and Adafruit's monochrome displays!

# This program is the simplest in the whole repo. All it does is print 3 'Hello!'s in various forms on the OLED display.
# It illustrates how to change the font size and positioning of text on the OLED... As well as showing how to do 
# basic text!

# This program was created by The Raspberry Pi Guy!

# Imports the necessary libraries... Gaugette 'talks' to the display ;-)
import gaugette.ssd1306
import time
import sys

# Setting some variables for our reset pin etc.
RESET_PIN = 15
DC_PIN    = 16

# Very important... This lets py-gaugette 'know' what pins to use in order to reset the display
led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
led.clear_display() # This clears the display but only when there is a led.display() as well!

# led.draw_text2(x-axis, y-axis, whatyouwanttoprint, size) < Understand?
# So led.drawtext2() prints simple text to the OLED display like so:

text = 'Hello!'
led.draw_text2(0,0,text,2)
text2 = 'Hello!'
led.draw_text2(0,16,text2,1)
text3 = 'Hello!'
led.draw_text2(32,25,text3,1)
led.display()
"""