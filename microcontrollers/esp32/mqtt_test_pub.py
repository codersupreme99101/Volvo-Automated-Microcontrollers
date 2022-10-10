from time import sleep
import time
from custom_libs.simple import MQTTClient
from machine import Pin

import network

ssid="Cedar Lofts Dojo"
passw="v7KTGKbe"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, passw)

print("Connected to WiFi")
sleep(10)

SERVER = '172.16.10.169'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'ESP32_ONLY'
TOPIC = 'color'

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

time_s=time.time()
while True:
    try:
        if True:  # Confirm sensor results are numeric
            msg = "{} hello".format(time.time()-time_s)
            client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
            print(msg)
        else:
            print('Invalid data.')
    except OSError:
        print('Failed to read data.')
    sleep(4)
    
#change eth0 address to static as well, keep that code active too. so that ssh/vnc server access into rpi4 with that address
#works first for then changes and subscriber testing 
