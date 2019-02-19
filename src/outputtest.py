import board
import digitalio as dio

d18 = dio.DigitalInOut(board.D18)
d18.direction = dio.Direction.OUTPUT

d18.value = True

while(True):
	print("hi")