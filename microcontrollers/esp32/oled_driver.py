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