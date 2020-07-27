# Pump_Test.py

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used to run individual pump and valve functions.
# At the bottom, they can each be commented in and out to test
# functions separately and in different configurations.

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
# mcp.read_adc(5)

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
    
def slow_pump_1(secs):
    GPIO.output(VALVE1, GPIO.HIGH)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(secs)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    
def slow_pump_2(secs):
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(secs)
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE2, GPIO.LOW)
    
def clean_bolus():
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(5)
    pump.ChangeDutyCycle(0)
    sleep(1)
    
def air_bolus():
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(5)
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
        
    

def clean_air_clean():
    print ("Cleaning sample tubing.")
    clean_bolus()
    air_bolus()
    clean_bolus()
    air_bolus()
    clean_bolus()
    air_bolus()
    clean_bolus()
    slow_clear(60)
    
def valve_test():
    sleep(2)   
    GPIO.output(VALVE1, GPIO.HIGH)    
    sleep(5)    
    GPIO.output(VALVE2, GPIO.HIGH)    
    sleep(5)        
    GPIO.output(VALVE1, GPIO.LOW)    
    sleep(5)    
    GPIO.output(VALVE2, GPIO.LOW)    
    sleep(5)    
    GPIO.output(VALVE1, GPIO.HIGH)    
    sleep(5)    
    GPIO.output(VALVE2, GPIO.HIGH)    
    sleep(5)



def measure():
    ratios = []
    for i in range (100):
        value = mcp.read_adc(2)
        ratios.append(value / 1023)
    average = sum(ratios)/len(ratios)
    average = round(average, 3)
    if average <= v1_fluid_value_low or average >= v1_fluid_value_high:               
        hits1.append(average)
        
    ratios = []
    for i in range (100):
        value = mcp.read_adc(3)
        ratios.append(value / 1023)
    average = sum(ratios)/len(ratios)
    average = round(average, 3)
    if average <= v2_fluid_value_low or average >= v2_fluid_value_high:               
        hits2.append(average)
        
def measure_pump():
    global hits1
    global hits2
    hits1 = []
    hits2 = []
    GPIO.output(VALVE1, GPIO.HIGH)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)    
    for _ in range(sample_size):
        measure()
        sleep(0.1)    
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    




holding_duty_cycle = 0

v1_fluid_value_low = 0.945
v1_fluid_value_high = 0.962

v2_fluid_value_low = 0.95
v2_fluid_value_high = 0.968

sample_size = 60



try:

#     TEC.ChangeDutyCycle(100)

#     GPIO.output(VALVE1, GPIO.LOW)    
#     
#     GPIO.output(VALVE2, GPIO.LOW)
#     
#     sleep(100)

    
    valve_test()
#     
#     slow_clear(15)
# #     
#     
#     print("Pausing to start test.")
#     sleep(2) 
# # # 
#     slow_pump_2(20)
# # #     
# #     slow_clear(5)
# # #     
# #     slow_pump_2(40)
# #     
#     slow_clear(20)
# #     
#     measure_pump()
#     print (len(hits1), ".....", len(hits2))
# #     
#     if len(hits1) >= 30 and len(hits2) >= 30:
#         print ("Successful Sample!")
    
    
    
#     clean_air_clean()


#slow pump 1 15 sec



#     
#     sleep(3)
#     
#     sample_p2()

#     clean()
    
    
    
    
    

except KeyboardInterrupt:
    pump.ChangeDutyCycle(0)
    TEC.ChangeDutyCycle(0)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    
    GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

    VALVE1 = 2
    VALVE2 = 3

    GPIO.setup(VALVE1, GPIO.OUT)
    GPIO.setup(VALVE2, GPIO.OUT)

    GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
    GPIO.output(VALVE2, GPIO.LOW)
    
    print ("Exiting and Cleaning Up")


GPIO.cleanup()

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

VALVE1 = 2
VALVE2 = 3

GPIO.setup(VALVE1, GPIO.OUT)
GPIO.setup(VALVE2, GPIO.OUT)

GPIO.output(VALVE1, GPIO.LOW)             # start with primary valve directed to air
GPIO.output(VALVE2, GPIO.LOW)