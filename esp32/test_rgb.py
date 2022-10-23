from time import sleep
from machine import Pin

class rgb_test():
    
    def __init__(self):
        
        self.r=None
        self.g=None
        self.b=None
        self.red_pin=12
        self.green_pin=13
        self.blue_pin=14
        
        self.time_q=10
        
        
    def init_pins(self): #initializes pins to avoid re-init
        
        self.r=Pin(self.red_pin, Pin.OUT)
        self.g=Pin(self.green_pin, Pin.OUT)
        self.b=Pin(self.blue_pin, Pin.OUT)
                
        print("All Pins Set!")
        
        pass
    
    def set_rgb(self, r_v, g_v, b_v): #set rgb values 
        
        self.r.value(r_v)
        self.g.value(g_v)
        self.b.value(b_v)
        
        pass
    
    def run_test(self): #test
        
        while True:
            self.set_rgb(1,1,1)
            print("Color: White")
            sleep(self.time_q)
            self.set_rgb(0,0,1)
            print("Color: Blue")
            sleep(self.time_q)
            self.set_rgb(0,1,0)
            print("Color: Green")
            sleep(self.time_q)
            self.set_rgb(1,0,0)
            print("Color: Red")
            sleep(self.time_q)
    
    def main(self): #main
        
        self.init_pins()
        self.run_test()
        
        pass #assumed at 0 level, led still flashes red as per specs
    
if __name__ == "__main__": #runs full class

    tr=rgb_test()
    tr.main()
    
    
    
