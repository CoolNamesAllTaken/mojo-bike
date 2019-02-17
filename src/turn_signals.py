import board
import time
import neopixel
import digitalio as dio

# Constants
TURN_SIGNAL_NUM_PIXELS = 18 # full strip including signal + brake
TURN_SIGNAL_FLASH_INTERVAL = 0.05 # in seconds
BRAKE_NUM_PIXELS = 6 # number of pixels to use in middle of turn signal strip
# BRAKE_FLASH_INTERVAL = 0.1 # in seconds

TURN_LEFT_BUTTON_PIN = board.D12
TURN_RIGHT_BUTTON_PIN = board.D21
BUTTON_DEBOUNCE_INTERVAL = 0.2 # in seconds
BUTTON_NUM_PIXELS = 2

PIXEL_PIN = board.D18
NUM_PIXELS = TURN_SIGNAL_NUM_PIXELS + BUTTON_NUM_PIXELS
PIXEL_ORDER = neopixel.GRBW
PIXEL_BRIGHTNESS = 1.0 # value between 0.0 and 1.0

## Pixel colors
RGBW_OFF = (0, 0, 0, 0)
RGBW_AMBER = (255, 90, 0, 0)
RGBW_RED = (255, 0, 0, 0)
RGBW_WHITE = (0, 0, 0, 255)

# Global Variables
## Hardware
turn_left_button = dio.DigitalInOut(TURN_LEFT_BUTTON_PIN)
turn_right_button = dio.DigitalInOut(TURN_RIGHT_BUTTON_PIN)
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS, auto_write=False, 
	pixel_order=PIXEL_ORDER)

## Turn Signal state variables
turning_left = True
turning_right = True
turn_signal_draw_time = time.monotonic() # next time to draw a turn signal blinker
turn_signal_num_active_pixels = 0

## Brake state variables
braking = True
# brake_draw_time = time.monotonic() # next time to draw a brake light
# brake_strobe_on = True

# debounce time is the next valid time that the button can be sampled
turn_left_button_debounce_time = time.monotonic()
turn_right_button_debounce_time = time.monotonic()

"""
Runs once at the beginning.  Used to set up hardware etc.
"""
def setup():
	turn_left_button.direction = dio.Direction.INPUT
	turn_right_button.direction = dio.Direction.INPUT

"""
Wheels on the bus go round n round.
"""
def loop():
	sample_buttons()
	draw_pixels()

"""
Polls and debounces the turn signal buttons, and uses them to set the turning_left and turning_right
global variables.
"""
def sample_buttons():
	global turn_left_button_debounce_time
	global turn_right_button_debounce_time
	global turning_left
	global turning_right

	if time.monotonic() > turn_left_button_debounce_time and not turn_left_button.value:
		# left turn button pressed when not debouncing
		turn_left_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
		if not turning_left:
			# start signaling left turn
			turning_left = True
			print("Turning Left")
		elif turning_left:
			# stop signaling left turn
			turning_left = False
			print("Stopped Turning Left")
	if time.monotonic() > turn_right_button_debounce_time and not turn_right_button.value:
		#right turn botton pressed when not debouncing
		turn_right_button_debounce_time = tume.monotonic() + BUTTON_DEBOUNCE_INTERVAL
		if not turning_right:
			# start signaling right turn
			turning_right = True
			print("Turning Right")
		elif turning_right:
			# stop signaling right turn
			turning_right = False
			print("Stopped Turning Right")

def draw_pixels():
	draw_turn_signal()
	draw_brake()
	

	pixels.show()

def draw_brake():
	global braking
	global brake_draw_time
	global brake_strobe_on

	if braking:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-(BRAKE_NUM_PIXELS//2), (TURN_SIGNAL_NUM_PIXELS//2)+(BRAKE_NUM_PIXELS//2)):
			pixels[i] = RGBW_RED

def draw_turn_signal():
	global turn_signal_draw_time
	global turn_signal_num_active_pixels

	if time.monotonic() > turn_signal_draw_time:
		turn_signal_draw_time = time.monotonic() + TURN_SIGNAL_FLASH_INTERVAL
		turn_signal_num_active_pixels += 1
		if turn_signal_num_active_pixels > TURN_SIGNAL_NUM_PIXELS//2:
			turn_signal_num_active_pixels = 0

	if turning_left:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1,(TURN_SIGNAL_NUM_PIXELS//2)-1-turn_signal_num_active_pixels,-1):
			pixels[i] = RGBW_AMBER;
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-turn_signal_num_active_pixels,-1,-1):
			pixels[i] = RGBW_OFF
	if turning_right:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2), TURN_SIGNAL_NUM_PIXELS//2+turn_signal_num_active_pixels):
			pixels[i] = RGBW_AMBER
		for i in range(TURN_SIGNAL_NUM_PIXELS//2+turn_signal_num_active_pixels, TURN_SIGNAL_NUM_PIXELS):
			pixels[i] = RGBW_OFF

def main():
	setup()
	while(True):
		loop()

if __name__ == '__main__':
	main()
