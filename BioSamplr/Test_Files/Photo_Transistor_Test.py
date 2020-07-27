# Photo_Transitor_Test.py

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used to display values read from the two fluid sensors of the BioSamplr system.
# These values are displayed as a value between 0 and 1.


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

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings

# Initiate cooling block: peltier, and thermal probe.

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
# mcp.read_adc(5)
MaxADCValue = 1023


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

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)             # start with secondary valve directed to air


# Define pump rates
slow_pump_rate = 20 #


def photo_sample():

    while True:
            ratios = []
            for i in range (100):
                value = mcp.read_adc(2)
                ratios.append(value / MaxADCValue)
            average = sum(ratios)/len(ratios)
            average = round(average, 4)
            
            ratios = []
            for i in range (100):
                value = mcp.read_adc(3)
                ratios.append(value / MaxADCValue)
            average2 = sum(ratios)/len(ratios)
            average2 = round(average2, 4)
            
            
            print ("Valve Sensor:", average, "Needle Sensor:", average2)
            
            sleep(1)


    
    
holding_duty_cycle = 0    



    
    
try:
    TEC.ChangeDutyCycle(holding_duty_cycle)
    
    GPIO.output(VALVE1, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(0.001)

    photo_sample()
    
    
    
    
    

except KeyboardInterrupt:
    TEC.ChangeDutyCycle(0)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
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