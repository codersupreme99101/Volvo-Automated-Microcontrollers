import pah.mqtt.client as mqtt
import Adafruit_SSD3106
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def compute_inclinedWeight(w):

    incline_deg=0 #edit #6 degree 

    incline_rad=incline_deg*np.pi/180

    return w/np.sin(incline_rad) #weight component read by sensor at back of ramp 

#alternate display module 

disp=Adafruit_SSD1306.SSD1306_128_32(rst=0)
disp.begin()
FONT_PATH="path_to_image/imgname.ttf"
FONT=ImageFont.truetype(FONT_PATH, 22)

total_wt=5*1000 #kg #example #x1000 for g 

def display_data(weight_data):

    image=Image.new("1", (disp.width, disp.height))
    draw=ImageDraw.Draw(image)

    draw.text((0,8),"{0}kg".format(weight_data), font=FONT, fill=255)

    computed_msg=compute_inclinedWeight(weight_data)

    draw.rectangle((0,0,50,8),outline=255,fill=0)
    draw.rectangle((71,0,121,8),outline=255,fill=0)
    draw.rectangle((0,0,computed_msg, 8),outline=255,fill=1)
    computed_msg_percent=((weight_data)/total_wt)*100
    draw.rectangle((0,0,computed_msg_percent, 8),outline=255,fill=1)
    draw.rectangle((71,0,computed_msg_percent, 8),outline=255,fill=1)

    disp.clear()
    disp.image(image)
    disp.display()

def on_connect(client, userdata, flags, rc): #mqtt broker connection fire
    print("Connected with result code: {0}".format(rc))
    client.subscribe("weight")


def on_message(client, user_data, msg): #published message recieved fired 

    w=[float(x) for x in msg.payload.decode("utf-8").split(",")]
    cw=(w/total_wt)*100
    print("{0}kg {1}%".format(w/1000,cw))
    display_data(w)

client=mqtt.Client()
client.on_connect=on_connect
client.on_message=on_message
client.connect("localhost",1883,60)

