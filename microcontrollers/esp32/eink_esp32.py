import board #ESP32 specific imports 
import displayio
import adafruit_ssd1680

import time
from PIL import Image 

class FeatherEInk:

    def __init__(self, fn):

        self.delay=3 #s
        self.filename=fn #load from input

    def png_to_bmp(self, filename): #png or jpg or jpeg to bitmap conversion

        file_in="barcode_imgs/"+filename+".png"
        img=Image.open(file_in)

        file_out="{}.bmp".format(filename)
        img.save("barcode_bitmaps/{}".format(file_out))

        print("Image converted to Bitmap on E-Ink 2.13.")

        pass

    def main(self): #main runner

        displayio.release_displays()
        spi = board.SPI()  # Uses SCK and MOSI
        epd_cs = board.D9
        epd_dc = board.D10
        epd_reset = board.D8
        epd_busy = board.D7

        display_bus = displayio.FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
        time.sleep(self.delay)

        display = adafruit_ssd1680.SSD1680(display_bus,width=250,height=122,busy_pin=epd_busy,highlight_color=0xFF0000,rotation=270)
        g = displayio.Group()

        self.png_to_bmp(self.filename)

        with open("barcode_bitmaps/{}.bmp".format(self.filename), "rb") as f:
            pic = displayio.OnDiskBitmap(f)

            t = displayio.TileGrid(pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter()))
            
            g.append(t)
            display.show(g)
            display.refresh()

            print("2.13 E-Ink Refreshed.")
            time.sleep(self.delay)
    
        pass

if __name__ == "__main__": #runs full class

    fn1="barcode_prod1_test" #fill input 

    fei=FeatherEInk(fn1)
    fei.main()

#end 
