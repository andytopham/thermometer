#!/usr/bin/python
# pwm.py
# Raspberry Pi PWM control.

import RPi.GPIO as GPIO

LED = 12
BRIGHT = 100		# usually 100
DULL = 15			# usually 15

class PWM():
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(LED, GPIO.OUT)
		self.pwm = GPIO.PWM(LED, 100)		# pin, freq
		self.pwm.start(0)
		self.pwm.ChangeDutyCycle(100)		# 0 to 100

	def duty_cycle(self, x):
		self.pwm.ChangeDutyCycle(x)
		return(0)

	def bright(self):
#		print ("setting bright")
		self.pwm.ChangeDutyCycle(BRIGHT)
	
	def dull(self):
#		print ("setting dull")
		self.pwm.ChangeDutyCycle(DULL)

