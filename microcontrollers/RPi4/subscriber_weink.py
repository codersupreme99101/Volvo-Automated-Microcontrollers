import json
from time import sleep
import datetime
from PIL import Image 
import numpy as np

import paho.mqtt.client as mqtt #only Rpi4 Downloads
import board #ESP32 specific imports 
import displayio
import adafruit_ssd1680

class Subscriber: #subs class for Rpi4

    def __init__(self, fn): #init of data pts

        self.reception_delay=180 #s

        self.delay=3 #s
        self.filename=fn #load from input
        self.max_limit=10000 #preset from esp32

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

        displayio.release_displays()
        spi = board.SPI()  # Uses SCK and MOSI
        epd_cs = board.D9
        epd_dc = board.D10
        epd_reset = board.D8
        epd_busy = board.D7

        display_bus = displayio.FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
        sleep(self.delay)

        display = adafruit_ssd1680.SSD1680(display_bus,width=250,height=122,busy_pin=epd_busy,highlight_color=0xFF0000,rotation=270)
        g = displayio.Group()

        self.png_to_bmp(self.filename)

        with open("barcode_bitmaps/{}.bmp".format(self.filename), "rb") as f: #issue with board values on esp32, only works on rpi4 for this eink display as ssd_1680 dirver is compatible with rpi4 only, and magtag doesnt turn on
            pic = displayio.OnDiskBitmap(f)

            t = displayio.TileGrid(pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter()))
            
            g.append(t)
            display.show(g)
            display.refresh()

            print("2.13 E-Ink Refreshed.")
            sleep(self.delay)

        pass

if __name__ == "__main__": #runs full class

    fn1="barcode_prod1_test" #fill input 

    sub=Subscriber(fn1)
    sub.main()

    #end #decoder run after main run from here, in separate manual script 

    #python /home/pi/subscriber_weink.py & python /home/pi/datasave.py 
    # if needed, or ignore anything with and apst & symbol 
