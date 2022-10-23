import time
import sys
import math
from hx711 import HX711
import network
import time
import random
from custom_libs.simple import MQTTClient
from machine import Pin
import esp
import gc

class BinProtocol: #full ESP32 load measurer only

    def __init__(self, caltime=30, tq=0.006, max_lim=10000): #init of data pts. 

        self.dt =27 #pin number d"number" and not GPIO number 
        self.sck=35

        self.red_pin=12
        self.green_pin=14
        self.on_pin=5
        
        self.r=None
        self.g=None
        self.o=None
        
        self.pw=-1 #percent by weight value
        
        self.dtp=None
        self.sckp=None
        
        self.hx=None

        self.time_quanta=tq #3 #1 #6 #0.006

        self.max_limit=max_lim #g #max wt as is as per load cell 100% capacity, mutable but hardset

        self.incline_deg=8.746 #degrees
        
        self.flip=False #binary
                
        self.max_limit_over_ang=self.max_limit*math.sin(self.incline_deg)
        
        self.iter_val_num=10 #avg over no. of samples
        self.check_calibration_ww=caltime #for w
        
        self.factor_w=1.8 #change-able
        
        self.wifi_ssid = "Bellaire Dojo"  # Enter Wifi SSID
        self.wifi_pass = "Z2wCAXMB" #"v7KTGKbe"  # Enter Wifi Pasword

        self.server = "mqtt3.thingspeak.com" # Enter Mqtt Broker Name

        self.port = 1883
        self.channel_id = "1899502" #Enter Channel Id here
        self.user = "LzUbDCQNGyYsCi07ICoCPRk"  # Enter User Id here
        self.client_id = "LzUbDCQNGyYsCi07ICoCPRk" #Enter Client Id here
        self.password = "OFtbgUKZyCTgbjpFTPYzqMqs" #Enter Password here
        
        self.topic_out = "channels/" + self.channel_id + "/publish"
        
        self.client=None #class
        
        self.preset=False
        
    def callback(self, topic, msg): #set callbackk mqtt
        
        print(topic)
        print(msg)
        
        pass
        
    def init_pins(self): #initializes pins to avoid re-init
        
        esp.osdebug(None)
        gc.collect() #OS clean to start
        
        self.r=Pin(self.red_pin, Pin.OUT)
        self.g=Pin(self.green_pin, Pin.OUT)
        self.o=Pin(self.on_pin, Pin.OUT)
            
        self.dtp=Pin(self.dt, Pin.OUT)
        self.sckp=Pin(self.sck, Pin.IN)
        
        self.hx=HX711(self.sck, self.dt)
        self.hx.set_scale(self.max_limit)
        
        if self.flip==False:
        
            temp=self.dtp
            self.dtp=self.sckp
            self.sckp=temp #flipping
                
        print("\nMachine Pins Set. \n")
        
        pass
    
    def init_connection(self):
        
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(self.wifi_ssid, self.wifi_pass)

        while station.isconnected() == False:
            pass

        print('\nConnection to WLAN successful. \n')
        time.sleep(10)
        
        self.client = MQTTClient(self.client_id, self.server, self.port, self.user, self.password,60) 
        self.client.set_callback(self.callback)

        self.client.connect()
        
        print("\nMQTT Publisher Client Connected to the Cloud.\n")
        
        pass

    def set_rgb(self, r_v, g_v): #set rgb values 
        
        self.r.value(r_v)
        self.g.value(g_v)
        
        pass

    def clean_and_exit(self): #clean and exit if fail

        print("\nCleaned and Exited ESP32. \n")
        sys.exit() #shouldnt get here anyways, hopefully 

        pass #sys exited by now, no pass case reaching

    def decide_color(self): #color scaler, conditional

        if 0<=self.pw<=5:
            
            self.set_rgb(1,0) #red

        elif 5<self.pw<=10:
            
            self.set_rgb(1,1) #yellow

        elif 10<self.pw<=100:
            
            self.set_rgb(0,1) #green

        pass
    
    def calibration_estimate(self, w): #math calc. ##edit function
        
        known_dv=-444000
        known_wt=39.689 #g
        known_wt_ang=self.factor_w*known_wt*math.sin(self.incline_deg)
        
        ratio=known_dv/known_wt_ang
        
        bin_dv=-433000
        
        ratio=(known_dv-bin_dv)/known_wt
        new_w=(w-bin_dv)/ratio
            
        if new_w<0: #known weight: 1.4 oz=39.6893g #417314.7 -- digital
            new_w=0 #assumed at 0
                
        if new_w>self.max_limit:
            new_w=self.max_limit
                    
        return new_w

    def process_read(self): #full true run of the read and data process
        
        print("\nBeginning Reading...\n")
        self.hx.tare()
        
        iter=0
        sum_w=0
        
        while True:
            
            print("\nIteration {}\n".format(iter))
    
            try:
                
                average=self.hx.read_average() #one method is fine, no need for raw and avg. reads 
                
                w=average
                                
                w_cal=self.calibration_estimate(w) #formula for DAC within physical domain
                                
                if isinstance(w_cal,float) or isinstance(w_cal, int): #extra measure  for int values 
                    
                    print("\nComputed Weight: {}g\n".format(w_cal))
                    
                    if iter%self.check_calibration_ww==0 and iter!=0 and self.preset==False:
                    
                        print("\nNew 100% weight reference set, from {}g, to {}g\n".format(self.max_limit, w_cal))
                                            
                        if w_cal==0:
                            w_cal=1 #min gram set
                                                
                        self.max_limit=w_cal
                        self.preset=True
                    
                    if iter%self.iter_val_num==0 and iter!=0: #can be done by time difference, but simpler this way
                        
                        self.client.check_msg()
                        
                        avg_w_cal=sum_w/self.iter_val_num #avg of 10 sent over
                        self.pw=(avg_w_cal/self.max_limit)*100 #same as if avg of each of 10 points weight -> percent is taken
                        sum_w=0
                        
                        msg_mqtt="field1="+str(self.pw)+"&field2="+str(avg_w_cal) #field1 = % and field2 = wt. (g)             
                        self.client.publish(self.topic_out, msg_mqtt)
                        
                        print("\nAverage of 10 samples (SENT VIA MQTT)--> {}% : {}g\n".format(self.pw, avg_w_cal))
                    
                    perc_w=(w_cal/self.max_limit)*100
                    self.pw=perc_w
                    print("\n{}% : {}g\n".format(w_cal, self.pw))
                    
                    sum_w+=w_cal
                                        
                    self.decide_color()
                        
                    print("\nLED Color set for corresponding Weight.\n")
                
                else:

                    print("\nInvalid sensor readings from Load Cell. Trying again...\n")
                    
                self.o.value(1)

            except (OSError, KeyboardInterrupt, SystemExit):
                
                self.o.value(0)
                self.set_rgb(0,0) #for full measure

                print("\nFailed to read Load Cell sensor. Shutting Down...\n")
                self.clean_and_exit()
                
            time.sleep(self.time_quanta)
            print("\n")
                
            iter+=1

        pass #doesnt reach pass case due to True always
    
    def main(self): #main run
        
        self.init_pins()
        self.init_connection()
        self.process_read() #esp32 oled is too expensive per bin to add as a esp32 embedded display, or wired too, scrapped , ssd 1680 incompatible for eink 2.13

        pass #process read call
    
#"""

if __name__ == "__main__": #runs full class #here for now, in boot originally 
    
    id_no=0
    
    if id_no==0: #unique id
        
        time.sleep(30) #default time for system calibration on firmware level
    
        tqt=1 #s
        ml_m=5000 #g
        ct=30 #s

        bp=BinProtocol(tq=tqt, caltime=ct, max_lim=ml_m)
        bp.main()
        
#"""
