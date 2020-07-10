import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)     # Using BCM RPi numbering

SLEEP = 23
X_DIR = 25
GPIO.setup(X_DIR, GPIO.OUT)
GPIO.setup(SLEEP, GPIO.OUT)

GPIO.output(SLEEP, GPIO.LOW)


TEC = 17
                                     # Fan is always on to save a pin.
GPIO.setup(TEC, GPIO.OUT)            # Setup TEC pin as output.
TEC = GPIO.PWM(TEC, 100)
TEC.start(0)                         # start with TEC off


GPIO.cleanup()

