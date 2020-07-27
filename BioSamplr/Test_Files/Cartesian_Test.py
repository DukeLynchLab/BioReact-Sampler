# Cartesian_Test.py

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used to locate the sample dispensing needle over each sample
# tube location using a given x,y coordinate.

# ----------Initialization/Imports----------
import time
from time import sleep

import RPi.GPIO as GPIO

import os
import shutil

from datetime import datetime, timedelta

import math

import csv

import glob


GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings



TEC = 17
                                     # Fan is always on to save a pin.
GPIO.setup(TEC, GPIO.OUT)            # Setup TEC pin as output.
TEC = GPIO.PWM(TEC, 100)
TEC.start(0)                         # start with TEC off



# Cartesian System

# Define Stepper Motor Variables and GPIO pins.
X_DIR = 20
X_STEP = 21
Y_DIR = 25
Y_STEP = 24

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
X_BUTTON = 16
Y_BUTTON = 12
GPIO.setup(X_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Y_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



# X,Y coordinates for sample tube locations given in microsteps.
y = 160

locations = {1: (27400,y),
             2: (40300,y),
             3: (52750,y),
             4: (65300,y),
             5: (78300,y),
             6: (27400,y),
             7: (40300,y),
             8: (52750,y),
             9: (65300,y),
             10: (78300,y)}


def autoHome():
    GPIO.output(SLEEP, GPIO.HIGH)
    sleep(0.05)
    while GPIO.input(Y_BUTTON) == 1:
        GPIO.output(Y_DIR,CW)
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)                
    while GPIO.input(Y_BUTTON) == 0:
        GPIO.output(Y_DIR,CCW)
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)
    GPIO.output(Y_DIR,CCW)
    for _ in range(665):
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)    
        
    while GPIO.input(X_BUTTON) == 0:
        GPIO.output(X_DIR,CCW)
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x)                
    while GPIO.input(X_BUTTON) == 1:
        GPIO.output(X_DIR,CW)
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x)
    for _ in range(10):
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x) 
        
#     GPIO.output(SLEEP, GPIO.LOW)



def Loc(sample):
    #Begin taking sample
    x = locations[sample][0]
    y = locations[sample][1]

    print("Moving to location %s." % (sample))
    
    # Move to Sample Location
    GPIO.output(SLEEP, GPIO.HIGH)
    sleep(0.05)
    
    autoHome()
    sleep(1)
    

    GPIO.output(X_DIR,CCW)                           # Move along x axis to location
    for _ in range(x):
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x)
    
    if sample >= 6:
        Direction = CCW
    else:
        Direction = CW
        
    GPIO.output(Y_DIR, Direction)                    # Turn y axis to location
    for _ in range(y):
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)
    

    sleep(10)
    
    
    if sample >= 6:
        Direction = CW
    else:
        Direction = CCW
            
    GPIO.output(Y_DIR, Direction)
    for a in range(y):
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)

    GPIO.output(X_DIR, CW)
    for _ in range(x):
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x)
        

    autoHome()
        
    GPIO.output(SLEEP, GPIO.LOW)                       # Turn steppers off



sample = 1
number_of_samples = 10


holding_duty_cycle = 60             # default duty cycle while other processes are running

try:
    
    sleep(2)
    
    TEC.ChangeDutyCycle(0)
    
    autoHome()
    
    for _ in range (number_of_samples):
        Loc(sample)
        sample += 1
        sleep(5)




except KeyboardInterrupt:
    TEC.ChangeDutyCycle(0)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

VALVE1 = 2
VALVE2 = 3

GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

GPIO.output(VALVE1, GPIO.LOW)             
GPIO.output(VALVE2, GPIO.LOW)