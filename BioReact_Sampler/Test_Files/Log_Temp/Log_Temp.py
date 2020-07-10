### LogTemp.py


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

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering
GPIO.setwarnings(False)    # Turn off warnings

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

TEC = 17
                                     # Fan is always on.
GPIO.setup(TEC, GPIO.OUT)            # Setup TEC pin as output.
TEC = GPIO.PWM(TEC, 100)
TEC.start(0)                         # start with TEC off



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



def initial_control_temp():
    print ("Temperature Controller On")
    
    time = datetime.now()
    get_temp()
    duty_cycle = 100                    # starting duty cycle for full power cooling
        
    count = 0
    
    while Tc >= setpoint:
        time = datetime.now()
        
        TEC.ChangeDutyCycle(duty_cycle)
        get_temp()
        get_temp2()
        print (count, ": Probe #1: ", Tc, "C ..... Probe #2: ", Tc2, "C")
        with open(temp_log, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time, Tc, Tc2])
        if Tc < setpoint:
            duty_cycle = 0
            print ("TEC Duty Cycle is set to: ", duty_cycle)
        if Tc >= setpoint:
            duty_cycle = 100
            print ("TEC Duty Cycle is set to: ", duty_cycle)
        count += 1
        
        


def control_temp(secs):
    print ("Temperature Controller On")
    
    time = datetime.now()
    duty_cycle = 100                    # starting duty cycle for full power cooling
    
    control_stop_time = datetime.now() + timedelta(seconds=secs)
    
    count = 0
    
    while time <= control_stop_time:
        time = datetime.now()
        
        TEC.ChangeDutyCycle(duty_cycle)
        
        get_temp()
        get_temp2()
        print (count, ": Probe #1: ", Tc, "C ..... Probe #2: ", Tc2, "C")
        with open(temp_log, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time, Tc, Tc2])
            
        if Tc < setpoint:
            duty_cycle = 0
            print ("TEC Duty Cycle is set to: ", duty_cycle)
        if Tc >= setpoint:
            duty_cycle = 100
            print ("TEC Duty Cycle is set to: ", duty_cycle)
                    
        count += 1
                
        
setpoint = 4                        # change this temperature setpoint not the next line
duty_cycle = 100                    # starting duty cycle for full power cooling
holding_duty_cycle = 60             # default duty cycle while other processes are running


try:
    sleep(2)
    
    # Begin Temperature Log
    file_list = []
    for i in os.listdir('./.'):
        if 'Temp_Log_' in i:
            file_list.append(i)
    number_files = len(file_list)
    number = number_files + 1
        
    with open('./Temp_Log_%s.csv' % (number), 'w', newline='') as file:
        temp_log = './Temp_Log_%s.csv' % (number)
        writer = csv.writer(file)
        writer.writerow(["Time", "#1 Temp (C)", "#2 Temp (C)"])
    
    initial_control_temp()
    
        
    
        
    while True:    
        
        control_temp(1200)     # control the temperature for 20 minutes before stopping.




    
    
except KeyboardInterrupt:
    TEC.ChangeDutyCycle(0)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()