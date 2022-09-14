from time import sleep
from umqtt.simple import MQTTClient
from machine import Pin
from dht import DHT22 #replace with load cell 

SERVER="192.168.192.20" #MQTT server addr
CLIENT_ID="ESP32_LoadCell_Sensor"
TOPIC=b"weight"

client=MQTTClient(CLIENT_ID, SERVER)
client.connect()

sensor=DHT22(Pin(15, Pin.IN, Pin.PULL_UP))

while True:
    try:
        sensor.measure()
        t=sensor.weight()
        if isinstance(t,float):
            msg=b"{0:3.1f}".format(t)
            client.publish(TOPIC, msg)
            print(msg) ##
        else:
            print("Invalid sensor readings.")

    except OSError:
        print("Failed to read sensor.")
    
    sleep(3)

#mosquitto_sub -d -t "weight"
