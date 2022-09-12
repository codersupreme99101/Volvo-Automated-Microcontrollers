import paho.mqtt.client as mqtt
import numpy as np
import os
import json
import time 
import datetime

def compute_inclinedWeight(w):

    incline_deg=6 #edit #6 degree # 12 degree??

    incline_rad=incline_deg*np.pi/180

    return w/np.sin(incline_rad) #weight component read by sensor at back of ramp 

def on_connect(client, userdata, flags, rc): #mqtt broker connection fire

    print("Connected with result code: {}".format(rc))
    client.subscribe("weight")

def make_json(weight_data): #makes json tfrom sensor read weight data 

    date_now=datetime.datetime.now()

    data={"weight":weight_data,"timestamp":date_now}

    fname="json_wdata_{}".format(date_now)
    with open("datasave/{}.json".format(fname),"w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    ffname="{}.json".format(fname)
    print("JSON file made: {}".format(ffname))

    pass 

def on_message(client, user_data, msg): #published message recieved fired 

    w=[float(x) for x in msg.payload.decode("utf-8").split(",")]
    incline_w=compute_inclinedWeight(w)
    print("{}g".format(incline_w))
    print("Weight data received")
    make_json(incline_w)
    time.sleep(180) #3 min min. screen delay


def json_to_nparr(): #decodes all json files in dir. to np array for analysis 

    filepath="datasave"
    weight_nparr=[]
    datetime_arr=[]

    for filename in os.listdir(filepath):
        f = os.path.join(filepath, filename)
        if os.path.isfile(f):
            file=open(f)
            data=json.load(file)
            for i in data["weight"]: #json with data category weight and timestamp 
                weight_nparr.append(i)
            for i in data["timestamp"]:
                datetime_arr.append(i)

    print("JSON to Data Array Conversion Successful.")

    return weight_nparr, datetime_arr

#runner: 

client=mqtt.Client()
client.on_connect=on_connect
client.on_message=on_message
client.connect("localhost",1883,60) #check for host ports 
