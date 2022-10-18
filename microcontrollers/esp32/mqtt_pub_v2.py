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
mqtt_server = '172.16.10.169'  #Replace with your MQTT Broker IP

client_id = "ESP32 TEST"#ubinascii.hexlify(machine.unique_id())
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

