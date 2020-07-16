### Cleaning Script

# ----------Initialization/Imports----------
import time
from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings


# Cartesian System

# Define Stepper Motor Variables and GPIO pins.
Y_DIR = 25
Y_STEP = 24
X_DIR = 20
X_STEP = 21

SLEEP = 23

# Define Stepper Direction: Clockwise = 1 and Counter clockwise = 2
CW = 1
CCW = 0

# Set Stepper control pins to outputs
GPIO.setup(X_DIR, GPIO.OUT)
GPIO.setup(X_STEP, GPIO.OUT)
GPIO.setup(Y_DIR, GPIO.OUT)
GPIO.setup(Y_STEP, GPIO.OUT)

GPIO.setup(SLEEP, GPIO.OUT)

# Setup pins for '1/32' microsteps.
MODE = (14,15,18)
GPIO.setup(MODE, GPIO.OUT)
RESOLUTION = {'Full': (0,0,0),
              'Half': (1,0,0),
              '1/4': (0,1,0),
              '1/8': (1,1,0),
              '1/16': (0,0,1),
              '1/32': (1,0,1)}
GPIO.output(MODE, RESOLUTION['1/32'])

delay_x = 0.0001 / 32   # / 32 to correct for 1/32 microsteps
delay_y = 0.01 / 32


# Endstop switch setup
Y_BUTTON = 16
X_BUTTON = 12
GPIO.setup(X_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Y_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Pump Setup.
PUMP = 13
VALVE1 = 5
VALVE2 = 27

GPIO.setup(PUMP, GPIO.OUT)
GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

pump = GPIO.PWM(PUMP, 100)
pump.start(0)                             # start with pump off

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)             # start with secondary valve directed to air


# Define pump rates
slow_pump_rate = 20 #

    
def slow_pump_1():
    GPIO.output(VALVE1, GPIO.HIGH)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(80)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    
def slow_pump_2():
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(80)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE2, GPIO.LOW)
    
def clean():     # both inlet tubes should be in water or cleaning solution to start
    print ("Tube washing will take approximately 5 minutes, 20 seconds, then you take both tubes out of cleaning solution.")
    print ("Followed by another 5 minute tube clearing.")
    slow_pump_1()
    slow_pump_2()
    print ("1/4 Finished")
    slow_pump_1()
    slow_pump_2()
    print ("Take both tubes out of water and press 'Enter'.")
    ready = input()
    if ready == "":
        pass
    else:
        exit()
    slow_pump_1()
    slow_pump_2()
    print ("3/4 Finished")
    slow_pump_1()
    slow_pump_2()
    print ("Cleaning cycle complete.")
    
    
    
try:
    print("Initiating cleaning cycle.")
    
    print ("Put both inlet tubes in clean water or cleaning solution and press 'Enter'.")
    ready = input()
    if ready == "":
        pass
    else:
        exit()

    sleep(2)

    clean()
    
    
    
    
    

except KeyboardInterrupt:
    pump.ChangeDutyCycle(0)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()    
    
    
