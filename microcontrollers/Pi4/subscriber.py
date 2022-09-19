import paho.mqtt.client as mqtt
import json
from time import sleep
import datetime

class Subscriber: #subs class for Rpi4

    def __init__(self): #init of data pts

        self.reception_delay=180 #s

    def on_connect(self, client, userdata, flags, rc): #mqtt broker connection fire

        print("Connected with result code: {}".format(rc))
        client.subscribe("weight")

        pass

    def make_json(self, weight_data): #makes json tfrom sensor read weight data 

        date_now=datetime.datetime.now()

        data={"weight":weight_data,"timestamp":date_now}

        fname="json_wdata_{}".format(date_now)
        with open("datasave/{}.json".format(fname),"w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        ffname="{}.json".format(fname)
        print("JSON file made: {}".format(ffname))

        pass 

    def on_message(self, client, user_data, msg): #published message recieved fired 

        w=[float(x) for x in msg.payload.decode("utf-8").split(",")]
        print("{}g".format(w))
        print("Weight data received")
        self.make_json(w)
        sleep(self.reception_delay) #3 min min. screen delay

        pass

    def main(self): #main run

        client=mqtt.Client()
        client.on_connect=self.on_connect
        client.on_message=self.on_message
        client.connect("localhost",1883,60) ##check for host ports 

        pass

if __name__ == "__main__": #runs full class

    sub=Subscriber()
    sub.main()

    #end #decoder run after main run from here, in separate manual script 
