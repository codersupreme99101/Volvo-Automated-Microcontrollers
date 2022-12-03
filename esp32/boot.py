# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

from full_protocol import BinProtocol
import time

#"""

if __name__ == "__main__": #runs full class #here for now, in boot originally 
    
    id_no=0
    
    if id_no==0: #unique id
        
        time.sleep(5) #default time for system calibration on firmware level
    
        tqt=1 #s
        ml_m=10000 #g
        ct=15 #s

        bp=BinProtocol(tq=tqt, caltime=ct, max_lim=ml_m)
        bp.main()
        
#"""
