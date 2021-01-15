#!/usr/bin/python

import RPi.GPIO as GPIO
# from gpiozero import LED
from time import sleep

#led = LED(12)
p=12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(p, GPIO.OUT)
pwm = GPIO.PWM(p, 100)
pwm.start(0)

for dc in range(100):
    pwm.ChangeDutyCycle(dc)
    sleep(0.02)
for dc in range(100):
    pwm.ChangeDutyCycle(dc)
    sleep(0.02)
for dc in range(100):
    pwm.ChangeDutyCycle(dc)
    sleep(0.02)
for dc in range(100):
    pwm.ChangeDutyCycle(dc)
    sleep(0.02)	
	
while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
	