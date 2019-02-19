import board
import digitalio as dio

TURN_LEFT_BUTTON_PIN = board.D12
TURN_RIGHT_BUTTON_PIN = board.D21

print("Running buttontest!")

turn_left_button = dio.DigitalInOut(TURN_LEFT_BUTTON_PIN)
turn_left_button.direction = dio.Direction.INPUT
turn_right_button = dio.DigitalInOut(TURN_RIGHT_BUTTON_PIN)
turn_right_button.direction = dio.Direction.INPUT

while True:
	if not turn_left_button.value:
		print("Left turn!")
	if not turn_right_button.value:
		print("Right turn!")