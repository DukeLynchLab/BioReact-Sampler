##################################################
############## BioReact Sampler v3 ###############
##################################################
# John Efromson
# Lynch Lab
# Duke University
# June 2020

## This code is meant to run the BioReactSampler on a set time schedule.
## Set time schedule is sample every X hours.
## Up to 10 samples can be taken before program termination.


## To control Raspberry Pi remotely use Microsoft Remote Desktop, SSH or VNC server
# SSH Directions: https://www.youtube.com/watch?v=wOFro6GwEFQ
# VNC Download at  realvnc.com


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
    path = 'BioReact_Sampler/Sample_Logs/Process_%s' % (process)
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
    
    while Tc >= setpoint-0.1:
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


# X,Y coordinates for sample tube locations given in microsteps.
y = 175

locations = {1: (4100,y),
             2: (6800,y),
             3: (9300,y),
             4: (11800,y),
             5: (14300,y),
             6: (4100,y),
             7: (6800,y),
             8: (9300,y),
             9: (11800,y),
             10: (14300,y)}




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
        
        
def sample_p1():
    GPIO.output(VALVE1, GPIO.HIGH)
    pump.ChangeDutyCycle(slow_pump_rate)
    sleep(0.001)
    hits = []
    while len(hits) <= 3:
        fluid_signal_1 = 0
        while fluid_signal_1 == 0:
            ratios = []
            for i in range (1000):
                value = mcp.read_adc(2)
                ratios.append(value / 1023)
            average = sum(ratios)/len(ratios)
            average = round(average, 3)
            print ("Waiting for Sample at Valves...")
            if average <= fluid_value_low or average >= fluid_value_high:                
                fluid_signal_1 = 1
                hits.append(average)
            sleep(0.05) 
    pump.ChangeDutyCycle(0)
    print ("Stopping at sensor 1.")
    sleep(2)
    
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
                value = mcp.read_adc(3)
                ratios.append(value / 1023)
            average2 = sum(ratios)/len(ratios)
            average2 = round(average2, 3)
            print ("Waiting for Sample at Needle...")
            if average2 <= fluid_value_low or average2 >= fluid_value_high:               
                fluid_signal_2 = 1
                hits.append(average2)
    pump.ChangeDutyCycle(0)
    print ("Stopping at sensor 2.")
    sleep(2)

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
    slow_clear(60)


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
        writer.writerow([sample, sample_start_time, "", Tc])
    
    autoHome()                                       # Align to waste/home
    
    GPIO.output(SLEEP, GPIO.LOW)
    
    slow_clear(45)                                          # clear tubing to waste
    get_temp()
    print ("Cooling block is currently ", Tc, " C.")
    
    sample_p1()                                      # Pump sample to first sensor near valves
    get_temp()
    print ("Cooling block is currently ", Tc, " C.")
    sample_p2()                                      # Pump sample to second sensor near needle
    get_temp()
    print ("Cooling block is currently ", Tc, " C.")
    
    pump.ChangeDutyCycle(slow_pump_rate)             # Pump purge volume to waste
    sleep(30)
    pump.ChangeDutyCycle(0)
    sleep(1)
    
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
    print ("Cooling block is currently ", Tc, " C at sampling time.")

    slow_clear(sample_size)                                   # Pump sample to sample location
    
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
        writer.writerow(["", "", sample_end_time, Tc2])
    
    sample_duration = sample_end_time - sample_start_time
    sample_duration_seconds = sample_duration.total_seconds()
    sample_duration_seconds = round(sample_duration_seconds, 1)
    print ("Sampling took", sample_duration_seconds, "seconds.")
    
    
    clean_air_clean()



GPIO.output(SLEEP, GPIO.LOW)



### System Control Variables

sample = 1
number_of_samples = 10
sample_size = 12                    # 12 is standard, 15 is microtube to the brim

MaxTempADC = 650.6436781609         # Change this value when calibrating Thermal Probes
                                    # MaxTempADC = (Vref3.3V / Vref5V) * 1023
                                    
                                    # Home = 653.2219653465

setpoint = 4                        # change this temperature setpoint not the next line
duty_cycle = 100                    # starting duty cycle for full power cooling
holding_duty_cycle = 60             # default duty cycle while other processes are running


fluid_value_low = 0.87              # values that fluid sensor is looking for when sensing fluid.
fluid_value_high = 0.93             # values are out of 1.0



try:
    sleep(2)
    
    process = input("Input Process #>>>")      # Define Process Number

    sample_interval = input("Define Sampling Interval (Entering 3 = Sample every 3 hours)>>>")
    sample_interval = sample_interval * 60 * 60    #convert to hours for sample interval
    sample_interval = 30 # temporary short sample interval overwriting input

    makeDir()
    print ("\n")
    sleep(2)
    
    # Begin Temperature Log
    with open('./BioReact_Sampler/Sample_Logs/Process_%s/Process_%s_Temp_Log.csv' % (process, process), 'w', newline='') as file:
        temp_log = './BioReact_Sampler/Sample_Logs/Process_%s/Process_%s_Temp_Log.csv' % (process, process)
        writer = csv.writer(file)
        writer.writerow(["Time", "Probe #1 - Temp (C)", "Probe #2 - Temp (C)"])   

    # Begin Sample Log.
    with open('./BioReact_Sampler/Sample_Logs/Process_%s/Process_%s_Sample_Log.csv' % (process, process), 'w', newline='') as file:
        sample_log = './BioReact_Sampler/Sample_Logs/Process_%s/Process_%s_Sample_Log.csv' % (process, process)
        writer = csv.writer(file)
        writer.writerow(["Sample Number", "Sample Start Time", "Sample End Time", "Cooling Block Temperature (C)", "Sample Interval = %s" % (sample_interval)])
        writer.writerow(["", "", "", "", ""])
        
    # TEC On    
    initial_control_temp()

    
    ### Start Sampling Process    
 
    for a in range (number_of_samples):
        get_temp()
        print ("Cooling Block Temperature Pre-Sample:", Tc, "C")
        Sample(sample)
        sample += 1                     # Increment sample number by 1
        get_temp()
        print ("Cooling Block Temperature Post-Sample:", Tc, "C")
        autoHome()
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
    GPIO.output(VALVE1, GPIO.LOW)
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print ("Exiting and Cleaning Up")
GPIO.cleanup()










# Pump Percent Max Rate in seconds per mL at different power levels
# 
# 20%: 2.173913043
# 30%: 1.013513514
# 40%: 0.769230769
# 50%: 0.678733032
# 60%: 0.630252101
# 70%: 0.596421471
# 80%: 0.573613767
# 90%: 0.562851782
#100%: 0.543478261
#
# 1mL/sec = 31.87908% Pump Max Rate
#
