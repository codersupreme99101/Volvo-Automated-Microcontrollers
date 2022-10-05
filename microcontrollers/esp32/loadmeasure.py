from time import sleep
import sys
#from custom_libs.emulated_hx711 import HX711
import math
from hx711 import HX711

from machine import Pin, deepsleep #for ESP32

class LoadMeasure: #full ESP32 load measurer only

    def __init__(self, ll, func_opt=0, tq=0.006, max_lim=10000): #init of data pts. 

        self.dt =27 #pin number d"number" and not GPIO number 
        self.sck=35

        self.red_pin=12
        self.green_pin=13
        self.blue_pin=14
        
        self.r=None
        self.g=None
        self.b=None
        self.a=None
        
        self.dtp=None
        self.sckp=None
        
        self.hx=None

        self.last_pin=18

        self.time_quanta=tq #3 #1 #6 #0.006

        self.max_limit=max_lim #g #max wt as is as per load cell 100% capacity, mutable but hardset

        self.lit_level=ll #method #0, 1 

        self.incline_deg=8.746 #degrees
        
        self.flip=False #binary
        
        self.function_ch=func_opt
        
        self.max_limit_over_ang=self.max_limit*math.sin(self.incline_deg)
        
    def init_pins(self): #initializes pins to avoid re-init
        
        self.r=Pin(self.red_pin, Pin.OUT)
        self.g=Pin(self.green_pin, Pin.OUT)
        self.b=Pin(self.blue_pin, Pin.OUT)
        
        if self.lit_level==1:
            self.a=Pin(self.last_pin, Pin.OUT)
            
        self.dtp=Pin(self.dt, Pin.OUT)
        self.sckp=Pin(self.sck, Pin.IN)
        
        self.hx=HX711(self.sck, self.dt)
        self.hx.set_scale(self.max_limit)
        
        if self.flip==False:
        
            temp=self.dtp
            self.dtp=self.sckp
            self.sckp=temp #flipping
                
        print("All Pins Set!")
        
        pass

    def set_rgb(self, r_v, g_v, b_v): #set rgb values 
        
        self.r.value(r_v)
        self.g.value(g_v)
        self.b.value(b_v)
        
        pass

    def cleanAndExit(self): #clean and exit if fail

        print("Cleaned and Exited ESP32.")
        deepsleep(10000) #low power nap
        sys.exit() #shouldnt get here anyways, hopefully 

        pass #sys exited by now, no pass case reaching
    
    def set_level4(self, v1, v2, v3, v4): #set 4 level
        
        self.r.value(v1)
        self.g.value(v2)
        self.b.value(v3)
        self.a.value(v4)
        
        pass

    def decide_color(self, weight_val): #color scaler, conditional

        if 0<=weight_val<=self.max_limit*0.01:
            
            self.set_rgb(1,0,0) #red

        elif 0.01*(self.max_limit)<weight_val<=0.05*(self.max_limit):
            
            self.set_rgb(1,1,1) #white

        elif 0.05*(self.max_limit/7)<weight_val<=0.15*(self.max_limit):
            
            self.set_rgb(0,0,1) #blue

        elif 0.15*(self.max_limit)<weight_val<=(self.max_limit):
            
            self.set_rgb(0,1,0) #green

        pass

    def decide_level(self, weight): #4 levle blue led conditional

        #12,13,14,18 lowest to highest led point

        if 0<=weight<=0.01*self.max_limit:
            
            self.set_level4(1,0,0,0) #lvl 1

        elif 0.01*self.max_limit<weight<=0.05*self.max_limit:
            
            self.set_level4(1,1,0,0) #lvl 2

        elif 0.05*self.max_limit<weight<=0.15*self.max_limit:
            
            self.set_level4(1,1,1,0) #lvl 3

        elif 0.15*self.max_limit<weight<=self.max_limit:
            
            self.set_level4(1,1,1,1) #Lvl 4

        pass
    
    def calibration_estimate(self, w): #math calc. ##edit function
        
        known_dv=-389177 #417314.7 
        known_wt=39.689 #g
        known_wt_ang=known_wt*math.sin(self.incline_deg)
        
        ratio=known_dv/known_wt_ang
        
        bin_wt=300 #g
        bin_dv=bin_wt*ratio
        
        if self.function_ch==0: ##multiple methods for functions, see which is best by trial and error 
            new_w=ratio*w
        elif self.function_ch==1:
            new_w=ratio*w*math.sin(self.incline_deg)
        elif self.function_ch==2:
            new_w=ratio*w-bin_dv
        elif self.function_ch==3:
            new_w=ratio*w*math.sin(self.incline_deg)-bin_dv
        elif self.function_ch==4:
            new_w=ratio*w+bin_dv
        elif self.function_ch==5:
            new_w=ratio*w*math.sin(self.incline_deg)+bin_dv
        elif self.function_ch==6:
            new_w=ratio*w/math.sin(self.incline_deg)
        elif self.function_ch==7:
            new_w=(ratio*w/math.sin(self.incline_deg))-bin_dv
        elif self.function_ch==8:
            new_w=(ratio*w/math.sin(self.incline_deg))+bin_dv
            
        elif self.function_ch==9:
            ratio=(423200-421350)/175
            new_w=(w-421350)/ratio
            
            if new_w<0:
                new_w=0
                
            if new_w>self.max_limit:
                new_w=self.max_limit
                    
        return new_w

    def process_read(self): #full true run of the read and data process
        
        print("Reading...")
        self.hx.tare()
        
        iter=0

        while True:
            
            print("Iteration {}".format(iter))
    
            try:
                
                average=self.hx.read_average()
                print("Avg. Read (Digital): {}".format(average))
                
                w=average
                
                #w_cal=w #for now 
                
                w_cal=self.calibration_estimate(w) #formula for DAC within physical domain
                
                print("Computed Weight: {}g".format(w_cal))
                                

                if self.lit_level=="rgb": #method of light up
                    
                    self.decide_color(w_cal)
                    
                    print("LED RGB System Set for Weight.")
                    
                elif self.lit_level=="4-level": #other id
                    self.decide_level(w_cal)
                    
                    print("LED 4 Level System Set for Weight.")
                    
                else:
                    
                    print("Incorrect LED System Chosen.")

                if isinstance(w,float):

                    msg="{}g".format(w_cal)
                    
                    perc_w=(w_cal/self.max_limit)*100
                    print(msg+" {}%".format(perc_w))

                else:

                    print("Invalid sensor readings from Load Cell.")

            except (OSError, KeyboardInterrupt, SystemExit):

                print("Failed to read Load Cell sensor.")
                self.cleanAndExit()
                
            sleep(self.time_quanta)
            print("\n")
                
            iter+=1

        pass #doesnt reach pass case due to True always 

    def main(self): #main run
        
        self.init_pins()
        self.process_read() #esp32 oled is too expensive per bin to add as a esp32 embedded display, or wired too, scrapped , ssd 1680 incompatible for eink 2.13

        pass #process read call

if __name__ == "__main__": #runs full class
    
    ll_test="rgb" #"4-level"
    tqt=3 #0.006 #0.006 #1 #5
    
    ml_m=5000 #g
    
    fn_o=9 #0,1,2,3,...,8 incl. --> special =9

    loma=LoadMeasure(tq=tqt, func_opt=fn_o, ll=ll_test, max_lim=ml_m)
    loma.main()
    
    #known weight: 1.4 oz=39.6893g #417314.7 -- digital
    #not added
    #remove the plastic jelly pads on the plate, see if readings improve.
    
    
