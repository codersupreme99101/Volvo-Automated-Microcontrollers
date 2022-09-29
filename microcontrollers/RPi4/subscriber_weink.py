import json
from time import sleep
import datetime
from PIL import Image 
import numpy as np

import paho.mqtt.client as mqtt #only Rpi4 imports
import board 
import busio
import digitalio
from adafruit_epd.ssd1680 import Adafruit_SSD1680 #only RPi4 compatible driver, and 2.13 eink display compatible itself by design
from adafruit_epd.epd import Adafruit_EPD #for color fills , maybe remove ??? ##check

class Subscriber: #subs class for Rpi4

    def __init__(self, fn): #init of data pts

        self.reception_delay=180 #s

        self.delay=3 #s
        self.filename=fn #load from input
        self.max_limit=10000 #preset from esp32
        self.display=None #init fill
        self.bitmap_enable=True #binary 
        self.centering_p=False #binary #in image displ fn 
        self.enable_refresh=False #binary 

    def png_to_bmp(self, filename): #png or jpg or jpeg to bitmap conversion

        file_in="barcode_imgs/"+filename+".png"
        img=Image.open(file_in)

        file_out="{}.bmp".format(filename)
        img.save("barcode_bitmaps/{}".format(file_out))

        print("Image converted to Bitmap on E-Ink 2.13.")

        pass

    def on_connect(self, client, userdata, flags, rc): #mqtt broker connection fire

        print("Connected with RPi4 with result code: {}".format(rc))
        client.subscribe("weight")

        pass

    def make_json(self, weight_data): #makes json tfrom sensor read weight data 

        date_now=datetime.datetime.now()

        data={"weight":weight_data,"capacity":np.round((weight_data/self.max_limit)*100,3),"timestamp":date_now}

        fname="json_wdata_{}".format(date_now)
        with open("datasave/{}.json".format(fname),"w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        ffname="{}.json".format(fname)
        print("JSON file made and stored in RPi4 datasave folder: {}".format(ffname))

        pass 

    def on_message(self, client, user_data, msg): #published message received fired 

        w=[float(x) for x in msg.payload.decode("utf-8").split(",")]
        print("{}g {}%".format(w,np.round((w/self.max_limit)*100,3)))
        print("Weight data received to RPi4")
        self.make_json(w)
        sleep(self.reception_delay) #3 min min. screen delay

        pass

    def main(self): #main run

        client=mqtt.Client()
        client.on_connect=self.on_connect
        client.on_message=self.on_message
        client.connect("localhost",1883,60) ##check for host ports 

        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        ecs = digitalio.DigitalInOut(board.CE0)
        dc = digitalio.DigitalInOut(board.D22)
        rst = digitalio.DigitalInOut(board.D27)
        busy = digitalio.DigitalInOut(board.D17)
        srcs = None

        self.display = Adafruit_SSD1680(122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=srcs, rst_pin=rst, busy_pin=busy)
        self.display.fill(Adafruit_EPD.WHITE)

        self.png_to_bmp(self.filename)

        self.display_img(self.filename)

        print("2.13 E-Ink Refreshed.")
        sleep(self.delay)

        pass

    def display_img(self, filename): #displays bmp bitwise

        if self.bitmap_enable==True:

            image=Image.open("barcode_bitmaps/"+filename+".bmp")

        else:

            image=Image.open("barcode_bitmaps/"+filename+".png")

        image_ratio = image.width / image.height
        screen_ratio = self.display.width / self.display.height

        if screen_ratio < image_ratio:
            scaled_width = image.width * self.display.height // image.height
            scaled_height = self.display.height
        else:
            scaled_width = self.display.width
            scaled_height = image.height * self.display.width // image.width

        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        if self.centering_p==True:

            x = scaled_width // 2 - self.display.width // 2
            y = scaled_height // 2 - self.display.height // 2
            image = image.crop((x, y, x + self.display.width, y + self.display.height))

        if self.bitmap_enable==False:

            image = image.convert("1").convert("L") #remove the L part???? ##decide after trials

        self.display.image(image)
        self.display.display()

        print("Image displayed.")

        if self.enable_refresh==True: #optional

            self.display.refresh()

        pass

if __name__ == "__main__": #runs full class

    fn1="barcode_prod1_test" #fill input 

    sub=Subscriber(fn1)
    sub.main()

    #end #decoder run after main run from here, in separate manual script 

    #python /home/pi/subscriber_weink.py & python /home/pi/datasave.py 
    # if needed, or ignore anything with and apst & symbol 

    #~mosquitto_sub -d -t "ESP32_LoadCell_Sensor" for preliminary data test of reception via terminal
    #~~needed for above: sudo apt-get install mosquitto mosquitto-clients


