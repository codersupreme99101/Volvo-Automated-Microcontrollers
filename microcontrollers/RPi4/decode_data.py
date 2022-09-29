import os
import json
import numpy as np

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
                weight_nparr_i=[]
                datetime_arr_i=[]
                data=json.load(file)
                for i in data["weight"]: #json with data category weight and timestamp 
                    weight_nparr_i.append(i)
                for i in data["timestamp"]:
                    datetime_arr_i.append(i)
            weight_nparr.append(weight_nparr_i)
            datetime_arr.append(datetime_arr_i)

        print("JSON to Data Array Conversion Successful.")

        return np.array(weight_nparr), datetime_arr


if __name__ == "__main__": #runs full class

    dec=Decoder()
    wn, dn= dec.json_to_nparr()

    print("Retrieved Weight Data (g) = {}\n".format(wn))
    print("Retrieved timestamps (1:1) = {} (UTC)".format(dn))

    #end