import board
import neopixel

PIXEL_PIN = board.D18
NUM_PIXELS = 30

ORDER = neopixel.RGBW
 
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)
pixels.fill((255, 255, 255, 255))
# pixels[0] = (255, 0, 0, 255)
pixels.show()

while(True):
	print("")