from time import sleep
from custom_libs.simple import MQTTClient
import sys
from custom_libs.emulated_hx711 import HX711
import numpy as np

from machine import Pin, deepsleep #for ESP32

class Publisher: #full ESP32 publisher 

    def __init__(self, ru=1, max_lim=10000): #init of data pts. 

        self.server="192.168.192.20" #MQTT server addr
        self.client_id="ESP32_LoadCell_Sensor"
        self.topic="weight"

        self.reference_unit = ru

        self.sample=0

        self.high=1 #constant high low for 5v and 0v, 
        self.low=0

        self.val=0

        self.dt =27
        self.sck=17

        self.red_pin=11
        self.green_pin=13
        self.blue_pin=15

        self.time_quanta=1 #6 #0.006

        self.hx=None
        self.client=None #objects

        self.max_limit=max_lim #g
        self.read_method=0 #0 or 1

        self.incline_deg=8.746 #degrees

    def compute_inclined_weight(self, w): #compute weight at angle 
    
        incline_rad=self.incline_deg*np.pi/180

        return w/np.sin(incline_rad) #weight component read by sensor at back of ramp 

    def blink(self, pin): #blink module for basic func

        p_blink=Pin(pin, Pin.OUT)
        p_blink.on()

        pass

    def turn_off_blink(self, pin): #turn off

        p_blink=Pin(pin, Pin.OUT)
        p_blink.off()

        pass

    def red_on(self): #red pin on

        self.blink(self.red_pin)

        pass

    def blue_on(self): #blue pin on

        self.blink(self.blue_pin)

        pass

    def green_on(self): #blue pin on

        self.blink(self.green_pin)

        pass

    def yellow_on(self): #yellow custom

        self.blink(self.red_pin)
        self.blink(self.green_pin)

        pass
        
    def cyan_on(self): #cyan custom

        self.blink(self.green_pin)
        self.blink(self.blue_pin)

        pass

    def magenta_on(self): #magenta custom

        self.blink(self.red_pin)
        self.blink(self.blue_pin)

        pass

    def white_on(self): #white custom, all

        self.blink(self.red_pin)
        self.blink(self.blue_pin)
        self.blink(self.green_pin)

        pass

    def readCount(self): #read from sensor after cal. 

        i=0
        count=0
        p_dt=Pin(self.dt, Pin.OUT)
        p_dt.on()
        p_sck=Pin(self.sck, Pin.IN)
        p_sck.off()

        while p_dt.value() == 1:
            i=0
            for i in range(24):
                p_sck.on()
                count=count<<1
                p_sck.off()

                sleep(self.time_quanta)

                if p_dt.value() == 0: 
                    count+=1
                
        p_sck.on()
        count=count^0x800000 #and operation for correct conversion
        p_sck.off()

        print("Data Count obtained from Load Cell.")

        return count 

    def cleanAndExit(self): #clean and exit if fail

        print("Cleaned and Exited ESP32.")
        deepsleep(10000) #low power nap
        sys.exit()

        pass #sys exited by now, no pass case reaching 

    def calibrate(self): #one time calibration

        self.hx = HX711(self.dt, self.sck)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.reference_unit)
        self.hx.reset()
        self.hx.tare()

        print("HX711 Calibration Performed.")

        pass

    def initialize_mqtt(self): #start mqtt process

        self.client=MQTTClient(self.client_id, self.server)
        self.client.connect() #mosquitto_sub -d -t "weight"

        print("ESP32 Publisher established. ")

        pass

    def decide_color(self, weight_val): #color scaler, conditional

        if 0<=weight_val<=self.max_limit/7:
            self.red_on()

        elif self.max_limit/7<weight_val<=2*(self.max_limit/7):
            self.yellow_on

        elif 2*(self.max_limit/7)<weight_val<=3*(self.max_limit/7):
            self.magenta_on()

        elif 3*(self.max_limit/7)<weight_val<=4*(self.max_limit/7):
            self.cyan_on()

        elif 4*(self.max_limit/7)<weight_val<=5*(self.max_limit/7):
            self.blue_on()

        elif 5*(self.max_limit/7)<weight_val<=6*(self.max_limit/7):
            self.green_on()

        elif 6*(self.max_limit/7)<weight_val<=7*(self.max_limit/7):
            self.white_on()

        pass

    def process_read(self): #full true run of the read and data process

        while True:
    
            try:

                if self.read_method==0: #method 1

                    w = max(0, float(self.hx.get_weight(self.dt)))
                    self.hx.power_down()
                    self.hx.power_up()

                elif self.read_method==1:#method 2

                    count= self.readCount() 
                    w=(count-self.sample)/106

                w=self.compute_inclined_weight(w)

                self.decide_color(w)

                if isinstance(w,float):

                    msg="{}g".format(w)
                    self.client.publish(self.topic, msg)
                    print(msg+" {}%".format(np.round((w/self.max_limit)*100,3)))

                else:

                    print("Invalid sensor readings from Load Cell.")

            except (OSError, KeyboardInterrupt, SystemExit):
                print("Failed to read Load Cell sensor.")
                self.cleanAndExit()
            
            sleep(self.time_quanta)
            self.turn_off_blink(self.red_pin)
            self.turn_off_blink(self.blue_pin)
            self.turn_off_blink(self.green_pin) #state reset

        pass #doesnt reach pass case due to True always 

    def main(self): #main run

        self.calibrate()

        self.initialize_mqtt()

        self.process_read()

        pass #process read call

if __name__ == "__main__": #runs full class

    nru=1 ##edit ru based on initial weight readings for known weight value to load cell value ratio (inverse: load cell val / known weight = ru)

    pub=Publisher(ru=nru)
    pub.main()

    #end
