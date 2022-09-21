from time import sleep
from umqtt.simple import MQTTClient
import sys
from emulated_hx711 import HX711
import numpy as np

import RPi.GPIO as gpio #only RPi4 downloads 

class Publisher: #full ESP32 publisher 

    def __init__(self, max_lim=10000): #init of data pts. 

        self.server="192.168.192.20" #MQTT server addr
        self.client_id="ESP32_LoadCell_Sensor"
        self.topic="weight"

        self.reference_unit = 1 #-441

        self.sample=0

        self.high=1 #constant high low for 5v and 0v, 
        self.low=0

        self.val=0

        self.dt =27
        self.sck=17

        self.time_quanta=0.006 #6

        self.hx=None
        self.client=None #objects

        self.max_limit=max_lim #g
        self.read_method=0 #0 or 1
        self.weight_ref_input=5 #1

        self.incline_deg=8.746 #degrees

    def compute_inclined_weight(self, w): #compute weight at angle 
    
        incline_rad=self.incline_deg*np.pi/180

        return w/np.sin(incline_rad) #weight component read by sensor at back of ramp 

    def readCount(self): #read from sensor after cal. 

        i=0
        count=0
        gpio.setup(self.dt, gpio.OUT)
        gpio.output(self.dt,1)
        gpio.output(self.sck,0)
        gpio.setup(self.dt, gpio.IN)

        while gpio.input(self.dt) == 1:
            i=0
            for i in range(24):
                gpio.output(self.sck,1)
                count=count<<1
                gpio.output(self.sck,0)

                sleep(self.time_quanta)

                if gpio.input(self.dt) == 0: 
                    count+=1
                
        gpio.output(self.sck,1)
        count=count^0x800000 #and operation for correct conversion
        gpio.output(self.sck,0)

        print("Data Count obtained from Load Cell.")

        return count 

    def cleanAndExit(self): #clean and exit if fail

        print("Cleaned and Exited ESP32.")
        gpio.cleanup()
        sys.exit()

        pass #sys exited by now, no pass case reaching 

    def calibrate(self): #one time calibration

        self.hx = HX711(5, 6)
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

                    msg="{}g".format(w)
                    self.client.publish(self.topic, msg)
                    print(msg)

                else:

                    print("Invalid sensor readings from Load Cell.")

            except (OSError, KeyboardInterrupt, SystemExit):
                print("Failed to read Load Cell sensor.")
                self.cleanAndExit()
            
            sleep(self.time_quanta)

        pass #doesnt reach pass case due to True always 

    def main(self): #main run

        self.initialize_mqtt()
        self.calibrate()

        self.process_read(self.weight_ref_input)

        pass #process read call

if __name__ == "__main__": #runs full class

    pub=Publisher()
    pub.main()

    #end
