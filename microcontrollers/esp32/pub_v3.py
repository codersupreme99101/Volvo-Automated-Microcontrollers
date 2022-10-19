"""

from machine import Pin
import time
from custom_libs.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = "Bellaire Dojo" #'Cedar Lofts Dojo' #
password = "Z2wCAXMB" #'v7KTGKbe' #
mqtt_server = "8.8.8.8" #'172.16.10.169'  #Replace with your MQTT Broker IP

client_id = "ESP32_TEST"#ubinascii.hexlify(machine.unique_id())
topic_pub = b'esp32/hello'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'esp32/hello' and b'hello' in msg:
    print('ESP received hello message')

def connect_full():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  print('Connected to {} MQTT broker'.format(mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_full()
except OSError as e:
  restart_and_reconnect()

time_s=time.time()
while True:
  try:
    client.check_msg()
    
    time_diff=time.time()-time_s
    msg="hello {}".format(time_diff)
    
    client.publish(topic_pub, msg)
    print('Publishing message: {} on topic {}'.format(msg, topic_pub))
    time.sleep(3)
  except OSError as e:
    restart_and_reconnect()
    
#eth0 IP address: 192.168.1.23/24
#/dev/cu.SLAB_USBtoUART

"""

"""
from machine import Pin
import time
from custom_libs.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = "Bellaire Dojo" #'Cedar Lofts Dojo' #
password = "Z2wCAXMB" #'v7KTGKbe' #
mqtt_server = '8.8.8.8' #172.16.10.169 #Replace with your MQTT Broker IP

client_id = "ESP32_TEST"#ubinascii.hexlify(machine.unique_id())
topic_pub = b'esp32/hello'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'esp32/hello' and b'hello' in msg:
    print('ESP received hello message')

def connect_full():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  print('Connected to {} MQTT broker'.format(mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_full()
except OSError as e:
  restart_and_reconnect()

time_s=time.time()
while True:
  try:
    client.check_msg()
    
    time_diff=time.time()-time_s
    msg="hello {}".format(time_diff)
    
    client.publish(topic_pub, msg)
    print('Publishing message: {} on topic {}'.format(msg, topic_pub))
    time.sleep(3)
  except OSError as e:
    restart_and_reconnect()
    
#eth0 IP address: 192.168.1.23/24
#/dev/cu.SLAB_USBtoUART 
"""

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

#WRITE API: 8ZO2XKU716U0BAS0
#READ API: 8ZO2XKU716U0BAS0


counter = 0  # counter value initialised

#create topic to publish the message
topicOut = "channels/" + CHANNEL_ID + "/publish" 
    
   
#Call back function called when new message from the broker arrives
def calback(topic,msg):
    print(topic)
    print(msg)
    
    

#connect esp32 to wifi
#wifi_connect()
        
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
client.set_callback(calback)

client.connect()

#client.subscribe(topicIn)

print("Mqtt connected")
timer=0
    
while True:
    
    client.check_msg()
    counter=random.uniform(0,50)
        
    #Publish the topic message to the broker
        
    p=100*(counter/50)
    
    if timer%15==0:
        client.publish(topicOut, "field1="+str(p))
        print("Data Sent")
        
    print(str(counter)+"g "+str(p)+"%")
    
    time.sleep(1)
    timer+=1

