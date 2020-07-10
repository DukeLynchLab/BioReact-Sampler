### LogTemp.py


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

#TEMPERATURE
# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
# mcp.read_adc(#)


def get_temp():
    values = []
    for _ in range(10000):        
        values.append(mcp.read_adc(0))
    value = sum(values) / len(values)
    value = 1/298.15 + 1/3470 * math.log((MaxTempADC / value) - 1 )
    value = 1/value
    global Tc
    Tc = value - 273.15
    Tc = round(Tc, 1)
    
def get_temp2():
    values = []
    for _ in range(10000):        
        values.append(mcp.read_adc(1))
    value = sum(values) / len(values)
    value = 1/298.15 + 1/3470 * math.log((MaxTempADC / value) - 1 )
    value = 1/value
    global Tc2
    Tc2 = value - 273.15
    Tc2 = round(Tc2, 1)

MaxTempADC = 671.5598409543         # Pi Powersupply = 643.0285714286
                                     # Autosampler Powersupply = 671.5598409543

try:
    sleep(2)
    
    while True:    
        
        get_temp()
        get_temp2()
        print ("Probe #1: ", Tc, "C ..... Probe #2: ", Tc2, "C")




    
    
except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()