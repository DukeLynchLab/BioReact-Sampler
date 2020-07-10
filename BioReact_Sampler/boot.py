import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

VALVE1 = 2
VALVE2 = 3

GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)             # start with secondary valve directed to air