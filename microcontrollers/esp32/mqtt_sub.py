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

ssid = 'Cedar Lofts Dojo' #"Bellaire Dojo"
password = 'v7KTGKbe' #"Z2wCAXMB"
mqtt_server = '172.16.10.169'  #Replace with your MQTT Broker IP

client_id = "ESP32 TEST"#ubinascii.hexlify(machine.unique_id())
topic_pub = b'esp32/hello'

topic_sub = b'hello' #check ... can be custom, for piggyback 

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())

def sub_cb(topic, msg):
    print((topic, msg))

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        new_message = client.check_msg()
        if new_message != 'None':
            client.publish(topic_pub, b'received')
        time.sleep(1)
    except OSError as e:
        restart_and_reconnect()
        
#/dev/cu.SLAB_USBtoUART5
