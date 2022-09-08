import terminalio
from adafruit_magtag.magtag import MagTag

magtag = MagTag()

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        50,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=3,
)

magtag.set_text("Hello World")

#UPDATE : every 3 mins or more only 

