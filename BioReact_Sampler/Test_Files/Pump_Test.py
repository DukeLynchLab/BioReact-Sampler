### Pump Script


# ----------Initialization/Imports----------
import time
from time import sleep

import RPi.GPIO as GPIO
#import gpiozero
import os
import shutil

from datetime import datetime, timedelta

import math

import csv

import glob

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
# mcp.read_adc(0)

MaxADCValue = 1023


GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings

# Initiate cooling block: peltier, and thermal probe.

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


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
pump_rate = 30.8   # 30.8% is 1mL/sec
pump_clear_rate = 60


def clear():                                              # clear sample tube
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(pump_clear_rate)
    sleep(15)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    
def slow_clear(secs):                                     # clear sample tube slowly!
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(secs)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    
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
    
def clean_bolus():
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(15)
    pump.ChangeDutyCycle(0)
    sleep(1)
    
def air_bolus():
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(15)
    pump.ChangeDutyCycle(0)
    sleep(1)
    
def clean():     # both inlet tubes should be in water or cleaning solution to start
    slow_pump_1()
    print ("1/8 Finished")
    slow_pump_2()
    print ("2/8 Finished")
    slow_pump_1()
    print ("3/8 Finished")
    slow_pump_2()
    print ("Take both tubes out of water and press 'Enter'.")
    ready = input()
    if ready == "":
        pass
    else:
        exit()
    slow_pump_1()
    print ("5/8 Finished")
    slow_pump_2()
    print ("6/8 Finished")
    slow_pump_1()
    print ("You're so close!")
    slow_pump_2()
    print ("Cleaning cycle complete.")
        
        
def sample_p1():
    GPIO.output(VALVE1, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(0.001)
    hits = []
    while len(hits) <= 3:
        fluid_signal_1 = 0
        while fluid_signal_1 == 0:
            ratios = []
            for i in range (100):
#                 value = adc.read_adc(1, gain=GAIN)
                value = mcp.read_adc(2)
                ratios.append(value / MaxADCValue)
            average = sum(ratios)/len(ratios)
            average = round(average, 3)
            print ("Valve Sensor Value:", average)
            if average <= fluid_value_low or average >= fluid_value_high:                
                fluid_signal_1 = 1
                hits.append(average)
    pump.ChangeDutyCycle(0)
    print ("Stopping at sensor 1 with values", hits)
    
def sample_p2():
    GPIO.output(VALVE1, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(0.001)
    hits = []
    while len(hits) <= 3:
        fluid_signal_2 = 0
        while fluid_signal_2 == 0:
            ratios = []
            for i in range (100):
#                 value = adc.read_adc(0, gain=GAIN)
                value = mcp.read_adc(3)
                ratios.append(value / MaxADCValue)
            average2 = sum(ratios)/len(ratios)
            average2 = round(average2, 3)
            print ("Needle Sensor Value:", average2)
            if average2 <= fluid_value_low or average2 >= fluid_value_high:               
                fluid_signal_2 = 1
                hits.append(average2)
    pump.ChangeDutyCycle(0)
    print ("Stopping at sensor 2 with values", hits)

def clean_air_clean():
    print ("Cleaning sample tubing.")
    clean_bolus()
    air_bolus()
    clean_bolus()
    air_bolus()
    clean_bolus()
    air_bolus()
    clean_bolus()
    slow_clear()
    
def valve_test():
    sleep(2)   
    GPIO.output(VALVE1, GPIO.HIGH)    
    sleep(3)    
    GPIO.output(VALVE2, GPIO.HIGH)    
    sleep(3)        
    GPIO.output(VALVE1, GPIO.LOW)    
    sleep(3)    
    GPIO.output(VALVE2, GPIO.LOW)    
    sleep(3)    
    GPIO.output(VALVE1, GPIO.HIGH)    
    sleep(3)    
    GPIO.output(VALVE2, GPIO.HIGH)    
    sleep(3)



holding_duty_cycle = 60

fluid_value_low = 0.87
fluid_value_high = 0.93



try:


    TEC.ChangeDutyCycle(100)
    
#     valve_test()
    
    slow_clear(70)
#     
#     sleep(2)
#     print("Pausing to start test.")
    
#     slow_pump_2()

#     slow_pump_1()
    
#     sample_p1()
#     
#     sleep(3)
#     
#     sample_p2()

#     clean()
    
    
    
    
    

except KeyboardInterrupt:
    pump.ChangeDutyCycle(0)
    TEC.ChangeDutyCycle(0)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()
