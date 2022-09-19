from time import sleep
from umqtt.simple import MQTTClient
import sys
from emulated_hx711 import HX711
from PIL import Image 
import numpy as np

import displayio #only rpi4 downloads
from adafruit_magtag.magtag import MagTag
import board
import RPi.GPIO as gpio

class Publisher: #full ESP32 publisher 

    def __init__(self, img_nn, max_lim=10000): #init of data pts. 

        self.server="192.168.192.20" #MQTT server addr
        self.client_id="ESP32_LoadCell_Sensor"
        self.topic="weight"

        self.referenceUnit = 1 #-441

        self.rs =18
        self.en =23
        self.d4 =24
        self.d5=25
        self.d6 =8
        self.d7 =7

        self.sample=0

        self.high=1

        self.low=0

        self.val=0

        self.dt =27
        self.sck=17

        self.time_quanta=0.006 #6

        self.hx=None
        self.client=None #objects
        self.magtag=None

        self.red = 0x880000
        self.green = 0x008800
        self.blue = 0x000088
        self.yellow = 0x884400
        self.cyan = 0x0088BB
        self.magenta = 0x9900BB
        self.white = 0x888888

        self.brightness_mgtg=0.5
        self.max_limit=max_lim #g
        self.image_name=img_nn
        self.read_method=0 #0 or 1
        self.weight_ref_input=5 #1

        self.incline_deg=8.746 #degrees

    def compute_inclined_weight(self, w):
    
        incline_rad=self.incline_deg*np.pi/180

        return w/np.sin(incline_rad) #weight component read by sensor at back of ramp 

    def readCount(self): #read from sensor after cal. 

        i=0
        Count=0
        gpio.setup(self.dt, gpio.OUT)
        gpio.output(self.dt,1)
        gpio.output(self.sck,0)
        gpio.setup(self.dt, gpio.IN)

        while gpio.input(self.dt) == 1:
            i=0
        for i in range(24):
            gpio.output(self.sck,1)
            Count=Count<<1
            gpio.output(self.sck,0)
            sleep(0.001)
            if gpio.input(self.dt) == 0: 
                Count=Count+1
                
        gpio.output(self.sck,1)
        Count=Count^0x800000
        gpio.output(self.sck,0)

        return Count 

    def cleanAndExit(self): #clean and exit if fail

        print("Cleaned and Exited.")
        gpio.cleanup()
        sys.exit()

        pass #sys exited by now, no pass case reaching 

    def calibrate(self): #one time calibration

        self.hx = HX711(5, 6)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.referenceUnit)
        self.hx.reset()
        self.hx.tare()

        pass

    def initialize_mqtt(self): #start mqtt process

        self.client=MQTTClient(self.client_id, self.server)
        self.client.connect() #mosquitto_sub -d -t "weight"
        self.magtag=MagTag()

        pass

    def light_up(self, color): #light all 4 neopixels to color

        self.magtag.peripherals.neopixel_disable = False
        self.magtag.peripherals.neopixels.fill(color)

        pass

    def png_to_bmp(self, filename): #png or jpg or jpeg to bitmap conversion

        file_in="barcode_imgs/"+filename+".png"
        img=Image.open(file_in)

        file_out="{}.bmp".format(filename)
        img.save("barcode_bitmaps/{}".format(file_out))

        pass

    def load_image(self, img_name): #loadimage to magtag
    
        board.DISPLAY.brightness = 0
        splash = displayio.Group()
        board.DISPLAY.show(splash)

        odb = displayio.OnDiskBitmap('barcode_bitmaps/{}.bmp'.format(img_name))
        face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
        splash.append(face)
        
        board.DISPLAY.refresh(target_frames_per_second=60)

        board.DISPLAY.brightness = self.brightness_mgtg
        sleep(self.time_quanta*10000)

        pass

    def light_condition(self, weight_data):
    
        if 0<=weight_data<self.max_limit/7:
            self.light_up(self.red)

        elif self.max_limit/7<=weight_data<(2*self.max_limit)/7:
            self.light_up(self.yellow)

        elif (2*self.max_limit)/7<=weight_data<(3*self.max_limit)/7:
            self.light_up(self.green)

        elif (3*self.max_limit)/7<=weight_data<(4*self.max_limit)/7:
            self.light_up(self.cyan)

        elif (4*self.max_limit)/7<=weight_data<(5*self.max_limit)/7:
            self.light_up(self.blue)

        elif (5*self.max_limit)/7<=weight_data<(6*self.max_limit)/7:
            self.light_up(self.magenta)

        elif (6*self.max_limit)/7<=weight_data<=(self.max_limit):
            self.light_up(self.white) #simple, all same color, level indicator 

        pass

    def process_read(self, input_val): #full true run of the read and data process

        while True:
    
            try:

                if self.read_method==0: #method 1

                    w = max(0, float(self.hx.get_weight(input_val)))
                    self.hx.power_down()
                    self.hx.power_up()

                elif self.read_method==1:#method 2

                    count= self.readCount() 
                    w=(count-self.sample)/106

                w=self.compute_inclined_weight(w)

                if isinstance(w,float):

                    self.light_condition(w)

                    msg="{}g".format(w)
                    self.client.publish(self.topic, msg)
                    print(msg)

                else:

                    print("Invalid sensor readings.")

            except (OSError, KeyboardInterrupt, SystemExit):
                print("Failed to read sensor.")
                self.cleanAndExit()
            
            sleep(self.time_quanta)

        pass #doesnt reach pass case due to True always 

    def main(self): #main run

        self.initialize_mqtt()
        self.calibrate()
        self.png_to_bmp(self.image_name)

        self.load_image(self.image_name)
        self.process_read(self.weight_ref_input)

        pass #process read call

if __name__ == "__main__": #runs full class

    image_inst="barcode_prod1_test" #add image name here (no file suffix or filepath, only name)
    pub=Publisher(image_inst)
    pub.main()

    #end
