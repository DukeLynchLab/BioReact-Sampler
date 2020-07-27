# boot.py

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used as a boot process script that will set the
# initial position of the two valves of the BioSamplr system.

# This must be set up in the Pi's boot process by adding a line to the
# 'rc.local' file above the line 'exit 0' that reads:
# 'sudo python /home/pi/Desktop/BioSamplr/boot.py'


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

VALVE1 = 2
VALVE2 = 3

GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)             # start with secondary valve directed to air
