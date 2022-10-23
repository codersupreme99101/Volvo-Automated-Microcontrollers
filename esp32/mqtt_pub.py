import network
import time
import random
from custom_libs.simple import MQTTClient
from machine import Pin

import esp
esp.osdebug(None)
import gc
gc.collect()

WiFi_SSID = "Bellaire Dojo"  # Enter Wifi SSID
WiFi_PASS = "Z2wCAXMB" #"v7KTGKbe"  # Enter Wifi Pasword

SERVER = "mqtt3.thingspeak.com" # Enter Mqtt Broker Name

PORT = 1883
CHANNEL_ID = "1899502" #Enter Channel Id here
USER = "LzUbDCQNGyYsCi07ICoCPRk"  # Enter User Id here
CLIENT_ID = "LzUbDCQNGyYsCi07ICoCPRk" #Enter Client Id here
PASSWORD = "OFtbgUKZyCTgbjpFTPYzqMqs" #Enter Password here

counter = 0  # counter value initialised

#create topic to publish the message
topicOut = "channels/" + CHANNEL_ID + "/publish" 
    
   
#Call back function called when new message from the broker arrives
def callback(topic,msg):
    print(topic)
    print(msg)
        
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(WiFi_SSID, WiFi_PASS)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
time.sleep(10)

#create a client and connect to the mqtt broker

#client = MQTTClient(CLIENT_ID, SERVER,PORT,USER,PASSWORD)
client = MQTTClient(CLIENT_ID, SERVER,PORT,USER,PASSWORD,60) 
client.set_callback(callback)

client.connect()

#client.subscribe(topicIn)

print("Mqtt connected")
timer=0
status_code=400
    
while True:
    
    client.check_msg()
    counter=random.uniform(0,5000)
        
    #Publish the topic message to the broker
        
    p=100*(counter/5000)
    
    status_code=200
    msg="field1="+str(p)+"&field2="+str(counter)
    client.publish(topicOut, msg)
    print("Data Sent")
        
    print(str(counter)+"g "+str(p)+"%")
    
    time.sleep(1)
    timer+=1


