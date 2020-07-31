##########################################
############## BioSamplr v3 ##############
##########################################

# Author: John Efromson
# License: Attribution-ShareAlike 3.0

# Lynch Lab
# Duke University
# July 2020

# This code is used to run the BioSamplr on a set time schedule.
# Set time schedule is sample every X hours.
# Up to 10 samples can be taken before program termination.

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

#TEMPERATURE
# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


TEC = 17
                                     # Fan is always on to save a pin.
GPIO.setup(TEC, GPIO.OUT)            # Setup TEC pin as output.
TEC = GPIO.PWM(TEC, 100)
TEC.start(0)                         # start with TEC off


def makeDir():
    path = 'BioSamplr/Sample_Logs/Process_%s' % (process)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print ('Process_%s Exists: Continuing will overwrite process folder and any saved data.' % (process))
        delete = input ('Continue? (Y/N)')
        if delete is 'Y' or delete is 'y':
            shutil.rmtree(path)
            os.mkdir(path)
        elif delete is 'N' or delete is 'n':
            GPIO.cleanup()
            exit()



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


def initial_control_temp():
    print ("Temperature Controller On")
    
    time = datetime.now()
    get_temp()
    duty_cycle = 100                    # starting duty cycle for full power cooling
        
    count = 0
    
    while Tc > setpoint-0.1:
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
        
        TEC.ChangeDutyCycle(holding_duty_cycle)
        
        


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
y = 140

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
    print ("Tube washing will take approximately 5 minutes, 20 seconds, then you take both tubes out of cleaning solution.")
    print ("Followed by another 5 minute tube clearing.")
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
    

def measure():
    ratios = []
    for i in range (100):
        value = mcp.read_adc(3)
        ratios.append(value / 1023)
    average = sum(ratios)/len(ratios)
    average = round(average, 3)
    if average >= v1_fluid_value_low and average <= v1_fluid_value_high:               
        hits1.append(average)
        
    ratios = []
    for i in range (100):
        value = mcp.read_adc(2)
        ratios.append(value / 1023)
    average2 = sum(ratios)/len(ratios)
    average2 = round(average2, 3)
    if average2 <= v2_fluid_value_low or average2 >= v2_fluid_value_high:               
        hits2.append(average2)
        
    #print ("Avg1:", average, "Avg2:", average2)
        
def measure_pump():
    global hits1
    global hits2
    hits1 = []
    hits2 = []
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.output(VALVE2, GPIO.LOW)
    pump.ChangeDutyCycle(slow_pump_rate)    
    for _ in range(sample_size):
        measure()
        sleep(0.1)    
    pump.ChangeDutyCycle(0)
    GPIO.output(VALVE1, GPIO.LOW)
    

def clean_air_clean():
    print ("Cleaning sample tubing.")
    clean_bolus()
    air_bolus()
    clean_bolus()
    air_bolus()
    print ("Halfway cleansed.")
    clean_bolus()
    air_bolus()
    clean_bolus()
    slow_clear(30)


def autoHome():
    GPIO.output(SLEEP, GPIO.HIGH)
    sleep(0.001)
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
        
        



def Sample(sample):
    #Begin taking sample
    x = locations[sample][0]
    y = locations[sample][1]

    sample_start_time = datetime.now()
    get_temp()
    print ("Sample %s sampling started at" % (sample), sample_start_time)
    with open(sample_log, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([sample, sample_start_time, "", "", Tc])

    
    autoHome()                                       # Align to waste/home
    
    GPIO.output(SLEEP, GPIO.LOW)
    
    slow_clear(25)                                   # Start with clear tubing

    slow_pump_1(15)                                   # Pump purge volume
    
    slow_clear(25)                                   # Clear tubing
    
    slow_pump_1(10)                                  # Pull sample
    
    slow_clear(8)                                    # Move sample towards needle
    
    
    
    # Move to Sample Location
    GPIO.output(SLEEP, GPIO.HIGH)
    sleep(0.001)
    
    autoHome()
    

    GPIO.output(X_DIR,CCW)                           # Move along x axis to sample location
    for _ in range(x):
        GPIO.output(X_STEP, GPIO.HIGH)
        sleep(delay_x)
        GPIO.output(X_STEP, GPIO.LOW)
        sleep(delay_x)
    
    if sample >= 6:
        Direction = CCW
    else:
        Direction = CW
        
    GPIO.output(Y_DIR, Direction)                    # Turn y axis to sample location
    for _ in range(y):
        GPIO.output(Y_STEP, GPIO.HIGH)
        sleep(delay_y)
        GPIO.output(Y_STEP, GPIO.LOW)
        sleep(delay_y)
    

    sleep(1)
    get_temp()    
    sample_time = datetime.now()
    
    print ("Sampling Time:", sample_time)
    with open(sample_log, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["", "", sample_time, "", Tc, "", ""])
        
    success = 0
    measure_pump()
    # print ("Length of Hits1:", len(hits1), "   ,   ", "Length of Hits2:", len(hits2))
    
    if len(hits1) >= 20 and len(hits2) >= 20:
        success = 1
        print ("Successful Sample!")
    
    sleep(3)
    
    
    # move reverse to waste
    sleep(0.05)
    
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


    sample_end_time = datetime.now()
    get_temp()
    print ("Sampling completed at", sample_end_time)
    with open(sample_log, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["", "", "", sample_end_time, Tc])
    
    sample_duration = sample_end_time - sample_start_time
    sample_duration_seconds = sample_duration.total_seconds()
    sample_duration_seconds = round(sample_duration_seconds, 1)
    print ("Sampling took", sample_duration_seconds, "seconds.")
    
    if success == 1:
        with open(sample_log, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["", "", "", "", "", "", "Successful Sample!"])
        
    
    
    clean_air_clean()



GPIO.output(SLEEP, GPIO.LOW)



### System Control Variables

sample = 1
number_of_samples = 10
sample_size = 25                    # 100 is current standard          

MaxTempADC = 670.3182178218         # Pi Powersupply = 675.8308151093
                                    # BioSamplr #2 Powersupply = 670.3182178218
                                    # Change this value when calibrating Thermal Probes
                                    # MaxTempADC = (Vref3.3V / Vref5V) * 1023

setpoint = 23.5                        # change this temperature setpoint not the next line
holding_duty_cycle = 0              # default duty cycle while other processes are running

v1_fluid_value_low = 0.96          # values that fluid sensor is looking for when sensing fluid.
v1_fluid_value_high = 0.97         # values are out of 1.0
                         
v2_fluid_value_low = 0.95           # v1 is valve 1 bound values and v2 is valve 2 bound values
v2_fluid_value_high = 0.968




try:
    sleep(2)
    
    process = input("Input Process #>>>")      # Define Process Number

    sample_interval = input("Define Sampling Interval (Entering 3 = Sample every 3 hours)>>>")
    sample_interval = float(sample_interval) * 60 * 60    #convert to hours for sample interval

    makeDir()
    print ("\n")
    sleep(2)
    
    # Begin Temperature Log
    with open('./BioSamplr/Sample_Logs/Process_%s/Process_%s_Temp_Log.csv' % (process, process), 'w', newline='') as file:
        temp_log = './BioSamplr/Sample_Logs/Process_%s/Process_%s_Temp_Log.csv' % (process, process)
        writer = csv.writer(file)
        writer.writerow(["Time", "Probe #1 - Temp (C)", "Probe #2 - Temp (C)"])   

    # Begin Sample Log.
    with open('./BioSamplr/Sample_Logs/Process_%s/Process_%s_Sample_Log.csv' % (process, process), 'w', newline='') as file:
        sample_log = './BioSamplr/Sample_Logs/Process_%s/Process_%s_Sample_Log.csv' % (process, process)
        writer = csv.writer(file)
        writer.writerow(["Sample Number", "Sample Start Time", "Sampling Time", "Sample End Time", "Cooling Block Temperature (C)", "Sample Interval = %s" % (sample_interval), "Successful?"])
        writer.writerow(["", "", "", "", "", "", ""])
        
    # TEC On    
    initial_control_temp()
    
    TEC.ChangeDutyCycle(holding_duty_cycle)

    
    ### Start Sampling Process    
 
    for a in range (number_of_samples):
        get_temp()
        Sample(sample)
        sample += 1                     # Increment sample number by 1
        get_temp()
        autoHome()
        GPIO.output(SLEEP, GPIO.LOW)
        if sample <= number_of_samples:
            print ("Waiting until it's time to take Sample %s.\n" % (sample))
            control_temp(sample_interval)
            TEC.ChangeDutyCycle(holding_duty_cycle)



    print("Sampling Complete!\n")
    
    print("Don't worry I'll keep your samples cold until you return!")
    print("CTRL+C to End and Exit.")
    
    control_temp(3600 * 48)




except KeyboardInterrupt:
    TEC.ChangeDutyCycle(0)
    pump.ChangeDutyCycle(0)
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