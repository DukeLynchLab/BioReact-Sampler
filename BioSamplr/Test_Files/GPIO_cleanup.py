# GPIO_cleanup.py

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used to set all GPIO pins to LOW and turn off any
# process that may be running from the GPIO pins.


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

SLEEP = 23
Y_DIR = 25
GPIO.setup(Y_DIR, GPIO.OUT)
GPIO.setup(SLEEP, GPIO.OUT)

GPIO.output(SLEEP, GPIO.LOW)


TEC = 17
                                     # Fan is always on to save a pin.
GPIO.setup(TEC, GPIO.OUT)            # Setup TEC pin as output.
TEC = GPIO.PWM(TEC, 100)
TEC.start(0)                         # start with TEC off

# Pump Setup.
PUMP = 26
VALVE1 = 2
VALVE2 = 3

GPIO.setup(PUMP, GPIO.OUT)
GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

pump = GPIO.PWM(PUMP, 100)
pump.start(0)                             # start with pump off

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

VALVE1 = 2
VALVE2 = 3

GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)