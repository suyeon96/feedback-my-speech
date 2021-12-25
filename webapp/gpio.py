#Writer: suyeon woo
#Date: 21.12.20
import RPi.GPIO as GPIO
import time

class Gpio(object):
	def __init__(self):
		GPIO.setmode(GPIO.BCM)

	def __del__(self):
		GPIO.cleanup()

	def set_outport(self, port):
		GPIO.setup(port, GPIO.OUT)
		GPIO.output(port, False)

	def led_on(self, port, sec):
		print('led on')
		GPIO.output(port, True)
		time.sleep(sec)
		GPIO.output(port, False)
