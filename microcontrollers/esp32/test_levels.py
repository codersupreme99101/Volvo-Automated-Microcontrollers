from time import sleep
from machine import Pin

class level_four():
    
    def __init__(self):
        
        self.r=None
        self.g=None
        self.b=None
        self.a=None
        self.red_pin=12
        self.green_pin=13
        self.blue_pin=14
        self.extra_pin=18
        
        self.time_q=10
        
    def init_pins(self): #initializes pins to avoid re-init
        
        self.r=Pin(self.red_pin, Pin.OUT) #Lowest 
        self.g=Pin(self.green_pin, Pin.OUT)
        self.b=Pin(self.blue_pin, Pin.OUT)
        self.a=Pin(self.extra_pin, Pin.OUT) #highest 
                
        print("All Pins Set!")
        
        pass
    
    def set_level(self, level): #set level 
        
        if level==1:
            self.r.value(1)
            self.g.value(0)
            self.b.value(0)
            self.a.value(0)
            
        elif level==2:
            self.r.value(1)
            self.g.value(1)
            self.b.value(0)
            self.a.value(0)
            
        elif level==3:
            self.r.value(1)
            self.g.value(1)
            self.b.value(1)
            self.a.value(0)
            
        elif level==4:
            self.r.value(1)
            self.g.value(1)
            self.b.value(1)
            self.a.value(1)
        
        pass
    
    def run_test(self): #test
        
        while True:
            self.set_level(1)
            print("Level 1")
            sleep(self.time_q)
            self.set_level(2)
            print("Level 2")
            sleep(self.time_q)
            self.set_level(3)
            print("Level 3")
            sleep(self.time_q)
            self.set_level(4)
            print("Level 4")
            sleep(self.time_q)


    def main(self): #main
        
        self.init_pins()
        self.run_test()
        
        pass #assumed at 0 level, lowest led is on, led still flashing at 0 as per specs
    
if __name__ == "__main__": #runs full class

    tr=level_four()
    tr.main()
    
