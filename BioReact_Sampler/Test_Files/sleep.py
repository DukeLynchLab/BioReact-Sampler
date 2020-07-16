import time
from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings



SLEEP = 23

GPIO.setup(SLEEP, GPIO.OUT)

GPIO.output(SLEEP, GPIO.HIGH)

sleep(300)

GPIO.cleanup()
