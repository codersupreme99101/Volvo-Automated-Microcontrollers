import os
import json

class Decoder: #decoder data for Rpi4

    def __init__(self): #init data 

        self.filepath="datasave"

    def json_to_nparr(self): #decodes all json files in dir. to np array for analysis 

        weight_nparr=[]
        datetime_arr=[]

        for filename in os.listdir(self.filepath):
            f = os.path.join(self.filepath, filename)
            if os.path.isfile(f):
                file=open(f)
                data=json.load(file)
                for i in data["weight"]: #json with data category weight and timestamp 
                    weight_nparr.append(i)
                for i in data["timestamp"]:
                    datetime_arr.append(i)

        print("JSON to Data Array Conversion Successful.")

        return weight_nparr, datetime_arr


if __name__ == "__main__": #runs full class

    dec=Decoder()
    dec.json_to_nparr()

    #end