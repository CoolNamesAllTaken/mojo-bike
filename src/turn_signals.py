import board
import time
import neopixel
import digitalio as dio
import board
import busio
import adafruit_lsm9ds1

# Constants
TURN_SIGNAL_NUM_PIXELS = 16 # full strip including signal + brake
TURN_SIGNAL_FLASH_INTERVAL = 0.05 # in seconds
TURN_MIN_GYRO_Z = 10 # [deg/s] minimum rate of turn to trigger auto-turnoff of blinker
TURN_MIN_TIME = 3 # [sec] minimum turn duration to allow auto-turnoff of blinker

BRAKE_NUM_PIXELS = 8 # number of pixels to use in middle of turn signal strip
BRAKE_ACC_THRESHOLD = -4.0 # [m/s^2], x-axis

STROBE_NUM_PIXELS = 8 # number of pixels to use centered in the middle for strobing
STROBE_FLASH_INTERVAL = 0.1 # in seconds
STROBE_FLASH_PATTERN = [0, 0, 0, 1, 0, 1]

TURN_LEFT_BUTTON_PIN = board.D12
TURN_RIGHT_BUTTON_PIN = board.D21
BUTTON_DEBOUNCE_INTERVAL = 0.2 # in seconds
BUTTON_NUM_PIXELS = 1

PIXEL_PIN = board.D18
NUM_PIXELS = TURN_SIGNAL_NUM_PIXELS + BUTTON_NUM_PIXELS
PIXEL_ORDER = neopixel.GRBW
PIXEL_BRIGHTNESS = 1.0 # value between 0.0 and 1.0

BUTTON_PIXEL_INDEX = NUM_PIXELS - 1

## Pixel colors
RGBW_OFF = (0, 0, 0, 0)
RGBW_AMBER = (255, 90, 0, 0)
RGBW_RED = (255, 0, 0, 0)
RGBW_RED_DIM = (50, 0, 0, 0)
RGBW_WHITE = (0, 0, 0, 255)
RGBW_GREEN = (0, 255, 0, 0)
RGBW_BLUE = (0, 0, 255, 0)

# Global Variables
## Hardware
turn_left_button = dio.DigitalInOut(TURN_LEFT_BUTTON_PIN)
turn_right_button = dio.DigitalInOut(TURN_RIGHT_BUTTON_PIN)
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS, auto_write=False, 
	pixel_order=PIXEL_ORDER)

## Turn Signal state variables
turning_left = False
turning_right = False
### drawing variables
turn_signal_draw_time = time.monotonic() # next time to draw a turn signal blinker
turn_signal_num_active_pixels = 0
### booleans for auto-turnoff of blinkers
turn_gyro_z_triggered = False
turn_time_triggered = False
turn_start_time = time.monotonic()

## Brake state variables
braking = False
strobe_on = True
strobe_step = 0
strobe_step_time = time.monotonic() # next time to step in the strobe sequence

# debounce time is the next valid time that the button can be sampled
strobe_button_debounce_time = time.monotonic() # strobe "button" us just left and right simultaneously
turn_left_button_debounce_time = time.monotonic()
turn_right_button_debounce_time = time.monotonic()

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)
nine_dof_sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c) # acc, mag, gyro, temp

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
	read_nine_dof_sensor()
	blinker_auto_turnoff()
	draw_pixels()
	print_state()

"""
Polls and debounces the turn signal buttons, and uses them to set the turning_left and turning_right
global variables.
"""
def sample_buttons():
	global strobe_on
	global strobe_button_debounce_time
	global turn_left_button_debounce_time
	global turn_right_button_debounce_time
	global turning_left
	global turning_right

	if time.monotonic() > strobe_button_debounce_time and \
	not turn_left_button.value and not turn_right_button.value:
		# toggle strobe
		strobe_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
		turn_left_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
		turn_right_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
		strobe_on = not strobe_on
		turning_left = False
		turning_right = False
	else:
		# toggle turn signal
		if time.monotonic() > turn_left_button_debounce_time and not turn_left_button.value:
			# left turn button pressed when not debouncing
			turn_left_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
			if not turning_left:
				# start signaling left turn
				turning_left = True
				init_blinker_turnoff_triggers()
			elif turning_left:
				# stop signaling left turn
				turning_left = False
		if time.monotonic() > turn_right_button_debounce_time and not turn_right_button.value:
			#right turn botton pressed when not debouncing
			turn_right_button_debounce_time = time.monotonic() + BUTTON_DEBOUNCE_INTERVAL
			if not turning_right:
				# start signaling right turn
				turning_right = True
				init_blinker_turnoff_triggers()
			elif turning_right:
				# stop signaling right turn
				turning_right = False

"""
Utilizes helper functions to draw the rear LED strip.
"""
def draw_pixels():
	# draw things from lowest > highest priority
	if turning_right or turning_left:
		# disable strobe show more turn signal when turning
		draw_brake()
		draw_turn_signal()
	elif braking:
		# show more brake light and disable strobe when braking
		draw_turn_signal()
		draw_brake()
	else:
		# show more brake light normally
		draw_turn_signal()
		draw_brake()
		draw_strobe()

	draw_button()

"""
Illuminates the LED inside the handlebar button to indicate the current state.
"""
def draw_button():
	if turning_right and turning_left:
		pixels[BUTTON_PIXEL_INDEX] = RGBW_WHITE # white for hazard lights
	elif turning_right:
		pixels[BUTTON_PIXEL_INDEX] = RGBW_GREEN # green for right turn
	elif turning_left:
		pixels[BUTTON_PIXEL_INDEX] = RGBW_BLUE # blue for left turn
	elif braking:
		pixels[BUTTON_PIXEL_INDEX] = RGBW_RED # red for braking


	pixels.show()

"""
Draws brake lights on the rear LED strip.
"""
def draw_brake():
	global braking

	if braking:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-(BRAKE_NUM_PIXELS//2), (TURN_SIGNAL_NUM_PIXELS//2)+(BRAKE_NUM_PIXELS//2)):
			pixels[i] = RGBW_RED
	else:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-(BRAKE_NUM_PIXELS//2), (TURN_SIGNAL_NUM_PIXELS//2)+(BRAKE_NUM_PIXELS//2)):
			pixels[i] = RGBW_RED_DIM

"""
Draws white strobe lights on the rear LED strip.
"""
def draw_strobe():
	global strobe_step_time
	global strobe_step

	# increment the strobe
	if time.monotonic() > strobe_step_time:
		strobe_step_time = time.monotonic() + STROBE_FLASH_INTERVAL
		strobe_step += 1
		if strobe_step >= len(STROBE_FLASH_PATTERN):
			strobe_step = 0

	# draw the strobe
	if strobe_on:
		if STROBE_FLASH_PATTERN[strobe_step]:
			# add white to strobed LEDs
			for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-(STROBE_NUM_PIXELS//2), (TURN_SIGNAL_NUM_PIXELS//2)+(STROBE_NUM_PIXELS//2)):
				pixels[i] = (pixels[i][0], pixels[i][1], pixels[i][2], 255)

"""
Draws a marching turn signal on the rear LED strip.
"""
def draw_turn_signal():
	global turn_signal_draw_time
	global turn_signal_num_active_pixels

	if time.monotonic() > turn_signal_draw_time:
		turn_signal_draw_time = time.monotonic() + TURN_SIGNAL_FLASH_INTERVAL
		turn_signal_num_active_pixels += 1
		if turn_signal_num_active_pixels > TURN_SIGNAL_NUM_PIXELS//2:
			turn_signal_num_active_pixels = 0

	if turning_right:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1,(TURN_SIGNAL_NUM_PIXELS//2)-1-turn_signal_num_active_pixels,-1):
			pixels[i] = RGBW_AMBER;
		for i in range((TURN_SIGNAL_NUM_PIXELS//2)-1-turn_signal_num_active_pixels,-1,-1):
			pixels[i] = RGBW_OFF
	else:
		for i in range(0, TURN_SIGNAL_NUM_PIXELS//2):
			pixels[i] = RGBW_OFF
	if turning_left:
		for i in range((TURN_SIGNAL_NUM_PIXELS//2), TURN_SIGNAL_NUM_PIXELS//2+turn_signal_num_active_pixels):
			pixels[i] = RGBW_AMBER
		for i in range(TURN_SIGNAL_NUM_PIXELS//2+turn_signal_num_active_pixels, TURN_SIGNAL_NUM_PIXELS):
			pixels[i] = RGBW_OFF
	else:
		for i in range(TURN_SIGNAL_NUM_PIXELS//2, TURN_SIGNAL_NUM_PIXELS):
			pixels[i] = RGBW_OFF

"""
Read the Adafruit LSM9DS1 9dof board (accelerometer, magnetometer, gyro, temperature sensor).
"""
def read_nine_dof_sensor():
	global braking
	global turn_gyro_z_triggered

	accel_x, accel_y, accel_z = nine_dof_sensor.acceleration
	mag_x, mag_y, mag_z = nine_dof_sensor.magnetic
	gyro_x, gyro_y, gyro_z = nine_dof_sensor.gyro
	temp = nine_dof_sensor.temperature

	if accel_x < BRAKE_ACC_THRESHOLD:
		braking = True
	else:
		braking = False

	if turning_left or turning_right:
		if abs(gyro_z) > TURN_MIN_GYRO_Z:
			turn_gyro_z_triggered = True

"""
Initialize the turnoff triggers that are used for automatically disabling a blinker after a turn.
"""
def init_blinker_turnoff_triggers():
	global turn_gyro_z_triggered
	global turn_time_triggered
	global turn_start_time

	turn_gyro_z_triggered = False
	turn_time_triggered = False
	turn_start_time = time.monotonic()

"""
Checks relevant sensors to update automatic blinker turnoff triggers.
"""
def update_blinker_turnoff_triggers():
	global turn_time_triggered

	# gyro z trigger in read_nine_dof_sensor()
	if time.monotonic() - turn_start_time > TURN_MIN_TIME:
		turn_time_triggered = True

"""
Checks to see if a turn is finished.
Returns:
	True = turn triggers are all True, need to turn off blinker
	False = turn triggers have not all been hit
"""
def turn_started():
	if turn_gyro_z_triggered and turn_time_triggered:
		return True
	else:
		return False

"""
Master function for blinker auto turnoff
"""
def blinker_auto_turnoff():
	global turning_left
	global turning_right

	if turning_left and turning_right:
		# ignore hazard lights special case
		return

	update_blinker_turnoff_triggers()
	if turn_started():
		# make sure turn is completed before turning off blinker
		_, _, gyro_z = nine_dof_sensor.gyro
		if abs(gyro_z) < TURN_MIN_GYRO_Z:
			turning_left = False
			turning_right = False

"""
For Debugging
"""
def print_state():
	state_string = ""
	if turning_left:
		state_string += "L"
	if turning_right:
		state_string += "R"
	state_string += "  "
	if turn_gyro_z_triggered:
		state_string += "G"
	if turn_time_triggered:
		state_string += "T"
	print(state_string)

def main():
	setup()
	while(True):
		loop()

if __name__ == '__main__':
	main()
