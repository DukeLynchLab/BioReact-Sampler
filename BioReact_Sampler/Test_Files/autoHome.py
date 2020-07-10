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


# Cartesian System

# Define Stepper Motor Variables and GPIO pins.
X_DIR = 25
X_STEP = 24
Y_DIR = 20
Y_STEP = 21

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
        
    GPIO.output(SLEEP, GPIO.LOW)



autoHome()


GPIO.cleanup()